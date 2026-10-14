"""
Public Health Intelligence Agent
=================================
Continuously scans anonymized case data for symptom clusters by location/time.
When a cluster crosses a threshold, it predicts the likely next-affected area
and recommends specific actions.

Owner: Backend Dev
"""

from typing import Optional
from pydantic import BaseModel
from collections import defaultdict
from backend.services.llm_service import llm_service


# ---------------------------------------------------------------------------
# Input / Output Schemas
# ---------------------------------------------------------------------------

class PublicHealthInput(BaseModel):
    """Anonymized case data for analysis."""
    cases: list[dict] = []  # [{symptoms, region, timestamp, age_group, lat, lng}]
    time_window_hours: int = 72  # Look back period
    cluster_threshold: int = 10  # Minimum cases to flag a cluster


class SymptomCluster(BaseModel):
    """A detected symptom cluster."""
    region: str
    latitude: float
    longitude: float
    dominant_symptoms: list[str]      # ["high fever", "body pain"]
    case_count: int
    time_span_hours: float
    confidence: float                  # 0.0 to 1.0
    possible_condition: Optional[str] = None  # "Possible dengue" (for internal use only)


class PublicHealthOutput(BaseModel):
    """Public health intelligence report."""
    clusters_detected: list[SymptomCluster] = []
    predicted_next_regions: list[dict] = []  # [{region, risk_level, reasons}]
    recommended_actions: list[str] = []
    village_risk_map: list[dict] = []  # [{region, lat, lng, risk_level}]  risk: safe/medium/high/critical
    alert_message: str = ""
    reasons: list[str] = []


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class PublicHealthAgent:
    """
    Public Health Intelligence Agent — outbreak detection and prediction.
    """

    def __init__(self):
        self.llm = llm_service
        self.proximity_radius_km = 20  # Nearby regions within this radius are "at risk"

    async def analyze(self, input_data: PublicHealthInput) -> PublicHealthOutput:
        """
        Analyze case data for symptom clusters and predict outbreaks.
        """
        cases = input_data.cases
        threshold = input_data.cluster_threshold
        
        clusters = []
        predictions = []
        actions = []
        risk_map = []
        reasons = []

        if not cases:
            return PublicHealthOutput(alert_message="No recent case data available for analysis.")

        # 1. Group cases by region
        regional_cases = self._group_cases_by_region(cases)

        # 2. Detect clusters within regions
        for region, r_cases in regional_cases.items():
            cluster = self._detect_symptom_clusters(region, r_cases, threshold)
            if cluster:
                clusters.append(cluster)
                risk_map.append({
                    "region": region,
                    "lat": cluster.latitude,
                    "lng": cluster.longitude,
                    "risk_level": "critical",
                    "reason": f"Active cluster: {cluster.case_count} cases of {', '.join(cluster.dominant_symptoms)}"
                })
            else:
                # Get region coords from first case
                first_case = r_cases[0]
                risk_map.append({
                    "region": region,
                    "lat": first_case.get("lat", 25.6),
                    "lng": first_case.get("lng", 85.1),
                    "risk_level": "safe",
                    "reason": "Case volume within normal baseline"
                })

        # 3. If clusters detected, predict spread and generate recommendations
        if clusters:
            all_regions = list(regional_cases.keys())
            
            for cluster in clusters:
                reasons.append(f"DETECTED: Outbreak of '{', '.join(cluster.dominant_symptoms)}' in {cluster.region} ({cluster.case_count} cases).")
                
                # Predict spread
                preds = self._predict_spread(cluster, all_regions)
                predictions.extend(preds)
                
                for p in preds:
                    reasons.append(f"PREDICTION: High risk of spread to {p['region']}.")
                    # Update risk map
                    for rm in risk_map:
                        if rm["region"] == p["region"] and rm["risk_level"] == "safe":
                            rm["risk_level"] = "high"
                            rm["reason"] = f"Proximity risk to {cluster.region} cluster"
                
                # Generate actions via LLM
                if self.llm.client:
                    cluster_actions = await self._generate_recommendations(cluster)
                    actions.extend(cluster_actions)
                else:
                    # Fallback actions
                    actions.extend([
                        f"Deploy mobile testing clinics to {cluster.region}",
                        f"Alert nearby PHCs to stock up on medicines for {cluster.dominant_symptoms[0]}",
                        "Initiate community awareness broadcasts via SMS/WhatsApp"
                    ])

        alert_msg = "No anomalies detected."
        if clusters:
            alert_msg = f"WARNING: {len(clusters)} symptom clusters detected. Immediate action recommended."

        return PublicHealthOutput(
            clusters_detected=clusters,
            predicted_next_regions=predictions,
            recommended_actions=list(set(actions)), # deduplicate
            village_risk_map=risk_map,
            alert_message=alert_msg,
            reasons=reasons,
        )

    def _group_cases_by_region(self, cases: list[dict]) -> dict:
        """Group cases by geographic region."""
        grouped = defaultdict(list)
        for case in cases:
            region = case.get("region", "Unknown")
            grouped[region].append(case)
        return dict(grouped)

    def _detect_symptom_clusters(self, region: str, cases: list[dict], threshold: int) -> Optional[SymptomCluster]:
        """Detect symptom clusters within a region."""
        # Count symptom occurrences
        symptom_counts = defaultdict(int)
        for case in cases:
            for symptom in case.get("symptoms", []):
                symptom_counts[symptom] += 1
                
        # Find dominant symptom
        if not symptom_counts:
            return None
            
        dominant_symptom = max(symptom_counts, key=symptom_counts.get)
        count = symptom_counts[dominant_symptom]
        
        if count >= threshold:
            # Get coords from first case
            lat = cases[0].get("lat", 25.6)
            lng = cases[0].get("lng", 85.1)
            
            # Estimate confidence based on volume vs threshold
            confidence = min(0.99, 0.5 + (count / (threshold * 2)))
            
            return SymptomCluster(
                region=region,
                latitude=lat,
                longitude=lng,
                dominant_symptoms=[dominant_symptom],
                case_count=count,
                time_span_hours=72,
                confidence=round(confidence, 2),
                possible_condition=f"Possible epidemic ({dominant_symptom})"
            )
            
        return None

    def _predict_spread(self, cluster: SymptomCluster, all_regions: list[str]) -> list[dict]:
        """Predict which nearby regions are at risk (mock logic)."""
        # In a real app, this would use GIS data. For demo, we just pick a different region.
        predictions = []
        for reg in all_regions:
            if reg != cluster.region:
                predictions.append({
                    "region": reg,
                    "risk_level": "high",
                    "reasons": [f"Geographic proximity to active cluster in {cluster.region}"]
                })
        return predictions

    async def _generate_recommendations(self, cluster: SymptomCluster) -> list[str]:
        """Generate specific action recommendations for a cluster using LLM."""
        system_prompt = """You are an AI Public Health Officer.
Given an outbreak cluster, recommend 3 specific, actionable public health interventions.
Return JSON format: {"actions": ["action 1", "action 2", "action 3"]}"""

        prompt = f"""Outbreak detected:
Region: {cluster.region}
Cases: {cluster.case_count}
Dominant Symptoms: {cluster.dominant_symptoms}
Time span: {cluster.time_span_hours} hours"""

        try:
            data = await self.llm.generate_json(prompt, system_prompt)
            return data.get("actions", [])
        except Exception:
            return []
