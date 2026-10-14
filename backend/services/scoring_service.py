"""
scoring_service.py
-------------------
Core intelligence for the Care Coordination Agent.

Computes a weighted score (0-100) for every candidate hospital based on
distance, bed capacity, specialization match, historical wait time, and
ICU availability -- instead of simply picking the nearest one. Every score
comes with a human-readable list of reasons, so the system can always
explain *why* it picked what it picked.
"""

import math
from typing import List, Dict, Any

# Weights are fixed, documented constants for the hackathon demo.
# In production these could be tuned/learned from historical outcome data.
WEIGHTS = {
    "distance": 0.25,
    "capacity": 0.25,
    "specialization": 0.25,
    "wait_time": 0.15,
    "icu": 0.10,
}

REQUIRED_SPECIALIZATION_BY_SYMPTOM = {
    "chest_pain": "cardiology",
    "breathing_difficulty": "cardiology",
    "fracture": "orthopedics",
    "pregnancy": "gynecology",
    "child_fever": "pediatrics",
    "accident": "trauma",
    "stroke_signs": "neurology",
}


def haversine_distance_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Great-circle distance between two lat/lng points, in kilometers."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def estimate_eta_minutes(distance_km: float, avg_speed_kmph: float = 30) -> int:
    """Simple ETA model. In production this would call a live traffic/maps API."""
    return max(2, round((distance_km / avg_speed_kmph) * 60))


def _normalize(value: float, worst: float, best: float) -> float:
    """Scale a raw value into a 0-1 range where 1 = best."""
    if best == worst:
        return 1.0
    score = (value - worst) / (best - worst)
    return max(0.0, min(1.0, score))


def get_required_specialization(symptom_tags: List[str]) -> str:
    """Maps detected symptom tags to the specialization most relevant to them."""
    for tag in symptom_tags:
        if tag in REQUIRED_SPECIALIZATION_BY_SYMPTOM:
            return REQUIRED_SPECIALIZATION_BY_SYMPTOM[tag]
    return "general"


def score_hospital(hospital: Dict[str, Any], patient_lat: float, patient_lng: float,
                    required_specialization: str, is_critical: bool) -> Dict[str, Any]:
    """Computes a 0-100 score for a single hospital, with reasoning."""
    distance_km = haversine_distance_km(patient_lat, patient_lng, hospital["lat"], hospital["lng"])
    distance_score = _normalize(30 - distance_km, 0, 30)

    free_beds = hospital["total_beds"] - hospital["occupied_beds"]
    occupancy_ratio = hospital["occupied_beds"] / hospital["total_beds"]
    capacity_score = _normalize(1 - occupancy_ratio, 0, 1)

    has_specialization = required_specialization in hospital.get("specializations", [])
    specialization_score = 1.0 if has_specialization else 0.3

    wait_score = _normalize(60 - hospital["avg_wait_time_minutes"], 0, 60)
    icu_score = _normalize(hospital["icu_beds_available"], 0, 10) if is_critical else 0.5

    total_score = (
        WEIGHTS["distance"] * distance_score
        + WEIGHTS["capacity"] * capacity_score
        + WEIGHTS["specialization"] * specialization_score
        + WEIGHTS["wait_time"] * wait_score
        + WEIGHTS["icu"] * icu_score
    ) * 100

    reasons = []
    if has_specialization:
        reasons.append(f"Has required specialization ({required_specialization})")
    else:
        reasons.append(f"No {required_specialization} specialist on record")

    if occupancy_ratio > 0.9:
        reasons.append(f"Hospital is near-full ({hospital['occupied_beds']}/{hospital['total_beds']} beds occupied)")
    else:
        reasons.append(f"Capacity available ({free_beds} free beds)")

    if is_critical:
        if hospital["icu_beds_available"] > 0:
            reasons.append(f"ICU beds available ({hospital['icu_beds_available']})")
        else:
            reasons.append("No ICU beds currently available")

    eta = estimate_eta_minutes(distance_km)
    reasons.append(f"ETA ~{eta} min ({distance_km:.1f} km away)")
    reasons.append(f"Average historical wait time: {hospital['avg_wait_time_minutes']} min")

    return {
        "hospital_id": hospital["id"],
        "hospital_name": hospital["name"],
        "hospital_lat": hospital["lat"],
        "hospital_lng": hospital["lng"],
        "total_score": round(total_score, 1),
        "proximity_score": round(distance_score * 100, 1),
        "capacity_score": round(capacity_score * 100, 1),
        "specialization_score": round(specialization_score * 100, 1),
        "wait_time_score": round(wait_score * 100, 1),
        "icu_score": round(icu_score * 100, 1),
        "distance_km": round(distance_km, 1),
        "eta_minutes": eta,
        "free_beds": free_beds,
        "icu_beds_available": hospital["icu_beds_available"],
        "has_specialization": has_specialization,
        "reasons": reasons,
    }


def rank_hospitals(hospitals: List[Dict[str, Any]], patient_lat: float, patient_lng: float,
                    required_specialization: str, is_critical: bool) -> List[Dict[str, Any]]:
    """Scores and ranks all candidate hospitals, best first."""
    scored = [
        score_hospital(h, patient_lat, patient_lng, required_specialization, is_critical)
        for h in hospitals
    ]
    scored.sort(key=lambda x: x["total_score"], reverse=True)
    return scored
