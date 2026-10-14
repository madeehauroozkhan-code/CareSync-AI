"""
backend/orchestration/graph.py
--------------------------------
LangGraph StateGraph definition for the AI Healthcare Coordination Platform.

Transformed for dynamic planning, parallel agent execution, and intelligent routing.
"""

from __future__ import annotations
import time
from functools import wraps
from typing import Any, Dict, List

from langgraph.graph import END, START, StateGraph

from backend.core.logging import get_logger
from backend.orchestration.state import WorkflowState, create_initial_state
from backend.services.llm_service import llm_service
from backend.services.prompt_manager import prompt_manager

# Import Agents
from backend.agents.intake.agent import IntakeAgent, IntakeInput
from backend.agents.triage.agent import TriageAgent, TriageInput
from backend.agents.knowledge.agent import KnowledgeAgent, KnowledgeInput
from backend.agents.care_coordination.agent import CareCoordinationAgent, CareCoordinationInput
from backend.agents.ambulance.agent import AmbulanceAgent, AmbulanceInput
from backend.agents.community_response.agent import CommunityResponseAgent, CommunityInput
from backend.agents.followup_recovery.agent import FollowupAgent, FollowupInput
from backend.agents.explainability.agent import ExplainabilityAgent, ExplainabilityInput
from backend.agents.public_health_intelligence.agent import PublicHealthAgent, PublicHealthInput

logger = get_logger(__name__)

# Singletons for agents
intake_agent = IntakeAgent()
triage_agent = TriageAgent()
knowledge_agent = KnowledgeAgent()
care_coord_agent = CareCoordinationAgent()
ambulance_agent = AmbulanceAgent()
community_agent = CommunityResponseAgent()
followup_agent = FollowupAgent()
explainability_agent = ExplainabilityAgent()
public_health_agent = PublicHealthAgent()

# Agent icons for terminal + dashboard
AGENT_ICONS = {
    "intake": "📋", "triage": "🩺", "knowledge": "📚",
    "care_coordination": "🏥", "ambulance": "🚑", "community_response": "👥",
    "public_health": "📊", "followup": "📞", "explainability": "💡",
}

def record_agent_result(agent_name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(state: WorkflowState):
            icon = AGENT_ICONS.get(agent_name, "⚙️")
            start = time.time()
            print(f"\n[AGENT] ──── {agent_name.upper()} STARTED ────")
            logger.info(f"→ {agent_name} started")
            try:
                result = await func(state)
                if result is None:
                    result = {}
                exec_time = (time.time() - start) * 1000
                print(f"[OK] {agent_name.upper()} completed in {exec_time:.0f}ms")
                logger.info(f"✓ {agent_name} completed", execution_time_ms=round(exec_time, 1))

                result["agent_results"] = [{
                    "agent_name": agent_name,
                    "status": "completed",
                    "execution_time_ms": exec_time
                }]
                return result
            except Exception as e:
                exec_time = (time.time() - start) * 1000
                print(f"[FAIL] {agent_name.upper()} FAILED in {exec_time:.0f}ms — {e}")
                logger.error(f"✗ {agent_name} failed: {e}", execution_time_ms=round(exec_time, 1))
                return {
                    "agent_results": [{
                        "agent_name": agent_name,
                        "status": "failed",
                        "error": str(e),
                        "execution_time_ms": exec_time
                    }],
                    "error": str(e),
                    "error_agent": agent_name
                }
        return wrapper
    return decorator



async def node_context_loader(state: WorkflowState) -> Dict[str, Any]:
    logger.debug("Graph: context_loader executing")
    return {"workflow_status": "context_loaded"}


async def node_planner(state: WorkflowState) -> Dict[str, Any]:
    logger.debug("Graph: planner executing")
    raw_input = state.get("raw_input", "")
    metadata = state.get("metadata") or {}
    disaster_mode = metadata.get("disaster_mode", False)
    
    plan_json = None
    if llm_service.client:
        prompt = f"User input: {raw_input}\nDisaster Mode: {disaster_mode}"
        sys_prompt = prompt_manager.get_planner_system_prompt()
        plan_json = await llm_service.generate_json(prompt, sys_prompt)
        
    if plan_json and "workflow_objective" in plan_json:
        selected = plan_json.get("selected_agents", ["intake", "triage", "explainability"])
        objective = plan_json.get("workflow_objective", "Coordinate healthcare request")
    else:
        # Intelligent rule-based fallback when LLM is offline
        selected, objective, order, parallel_groups, reasoning, risk = _rule_based_plan(raw_input, disaster_mode)
        plan_json = {
            "workflow_objective": objective,
            "selected_agents": selected,
            "execution_order": order,
            "parallel_execution_groups": parallel_groups,
            "planner_reasoning": reasoning,
            "planner_confidence": 0.8,
            "fallback_plan": "Rule-based static routing",
            "risk_level": risk,
            "execution_plan": {"fallback": True}
        }
        
    if objective == "GREETING":
        return {
            "workflow_status": "completed",
            "workflow_objective": "GREETING",
            "selected_agents": [],
            "response_text": "Namaste! I am AI Sahayak. How can I assist you with your health today?",
            "execution_plan": plan_json,
            "plan_iteration": state.get("plan_iteration", 0) + 1,
        }
        
    return {
        "workflow_status": "planning_complete",
        "workflow_objective": objective,
        "selected_agents": selected,
        "execution_plan": plan_json,
        "plan_iteration": state.get("plan_iteration", 0) + 1,
    }


def _rule_based_plan(raw_input: str, disaster_mode: bool) -> tuple:
    """Rule-based planner fallback when LLM is unavailable."""
    text = raw_input.lower()
    
    # Comprehensive emergency keywords — covers all major health emergencies
    emergency_keywords = [
        "chest pain", "heart attack", "heart failure", "cardiac arrest", "stroke",
        "cannot breathe", "breathing difficulty", "breathless", "suffocating",
        "accident", "bleeding", "blood loss", "hemorrhage",
        "unconscious", "unresponsive", "fainted", "fainting", "collapsed",
        "seizure", "convulsion", "fits",
        "severe", "critical", "emergency", "dying", "life threatening",
        "snake bite", "snakebite", "dog bite", "animal bite",
        "burn", "burns", "scalding", "electric shock", "electrocution",
        "poisoning", "poison", "overdose", "drug overdose",
        "drowning", "choking", "asphyxiation",
        "fracture", "broken bone", "head injury", "spinal injury", "trauma",
        "allergic reaction", "anaphylaxis", "anaphylactic",
        "asthma attack", "severe asthma",
        "high fever", "105 fever", "104 fever", "very high fever",
        "vomiting blood", "blood in stool", "blood in urine",
        "miscarriage", "pregnancy emergency", "labor pain",
        "suicide", "self harm", "suicidal",
    ]
    
    disaster_keywords = [
        "earthquake", "flood", "cyclone", "hurricane", "tornado",
        "disaster", "mass casualty", "explosion", "building collapse",
        "tsunami", "landslide", "fire outbreak", "chemical spill",
    ]
    
    # Broader knowledge keywords — any health question triggers RAG
    knowledge_keywords = [
        "what is", "how to", "tell me about", "information", "guideline",
        "prevention", "treatment for", "symptoms of", "home remedy", "first aid",
        "medicine for", "cure for", "cause of", "reason for",
        "diet for", "precaution", "side effect", "risk of",
        "vaccine", "vaccination", "immunization",
        "scheme", "yojana", "government", "ayushman", "jan arogya",
    ]
    
    # Health symptom keywords — even without "emergency", these should
    # trigger the full pipeline (intake → triage → knowledge → care)
    health_keywords = [
        "fever", "cough", "cold", "headache", "pain", "ache",
        "diarrhea", "diarrhoea", "vomiting", "nausea",
        "dengue", "malaria", "typhoid", "cholera", "chikungunya", "tb", "tuberculosis",
        "diabetes", "sugar", "bp", "blood pressure", "hypertension",
        "infection", "swelling", "rash", "itching", "skin",
        "weakness", "fatigue", "dizziness", "vertigo",
        "stomach", "abdomen", "chest", "back pain", "joint pain",
        "anxiety", "depression", "insomnia", "stress",
        "pregnancy", "pregnant", "period", "menstrual",
        "injury", "wound", "cut", "bruise",
        "eye", "ear", "throat", "nose", "tooth", "dental",
        "cancer", "tumor", "lump",
        "breathing", "wheezing", "asthma",
        "heart", "cardiac", "palpitation",
        "kidney", "liver", "lung",
        "covid", "corona", "flu", "influenza",
        "bukhaar", "dard", "bukhar", "pet dard", "sir dard", "kamar dard",
        "ulti", "dast", "khansi", "sardi", "jukham",
        "saanp", "katna", "jalana", "chot",
    ]
    
    greeting_keywords = ["hi", "hello", "hey", "namaste", "pranam", "greetings"]
    
    is_emergency = any(kw in text for kw in emergency_keywords)
    is_disaster = disaster_mode or any(kw in text for kw in disaster_keywords)
    is_knowledge_only = any(kw in text for kw in knowledge_keywords) and not is_emergency
    is_health = any(kw in text for kw in health_keywords)
    
    # If the text is very short and matches a greeting exactly
    if not is_emergency and not is_knowledge_only and not is_disaster and not is_health:
        if len(text.strip().split()) <= 3 and any(kw in text for kw in greeting_keywords):
            return (
                [],
                "GREETING",
                [],
                [],
                "User provided a simple greeting.",
                "low"
            )
            
    if is_disaster:
        return (
            ["intake", "triage", "knowledge", "care_coordination", "ambulance", "followup", "community_response", "public_health", "explainability"],
            "Disaster response coordination",
            ["intake", "triage", "care_coordination", "ambulance", "followup", "explainability"],
            [["knowledge", "community_response", "public_health"]],
            "Disaster detected. Activating full spectrum response including public health and community agents.",
            "critical"
        )
    elif is_emergency:
        return (
            ["intake", "triage", "knowledge", "care_coordination", "ambulance", "followup", "explainability"],
            "Emergency healthcare coordination",
            ["intake", "triage", "care_coordination", "ambulance", "followup", "explainability"],
            [["knowledge"]],
            "Emergency keywords matched. Standard critical pathway activated.",
            "high"
        )
    elif is_health:
        # Any health symptom → full pipeline with knowledge (RAG)
        return (
            ["intake", "triage", "knowledge", "care_coordination", "followup", "explainability"],
            "Healthcare symptom assessment",
            ["intake", "triage", "care_coordination", "followup", "explainability"],
            [["knowledge"]],
            "Health symptoms detected. Running full assessment with RAG knowledge retrieval.",
            "moderate"
        )
    elif is_knowledge_only:
        return (
            ["knowledge", "explainability"],
            "Health information query",
            ["knowledge", "explainability"],
            [],
            "User is asking an informational query without explicit emergency.",
            "low"
        )
    else:
        return (
            ["intake", "triage", "knowledge", "care_coordination", "followup", "explainability"],
            "Standard healthcare coordination",
            ["intake", "triage", "care_coordination", "followup", "explainability"],
            [["knowledge"]],
            "Default routine healthcare coordination path.",
            "moderate"
        )


# ──────────────────────────────────────────────────────────────────
# Independent Parallel Nodes (Knowledge, Community, Public Health)
# ──────────────────────────────────────────────────────────────────

@record_agent_result("knowledge")
async def node_knowledge(state: WorkflowState) -> Dict[str, Any]:
    logger.debug("Graph: knowledge executing")
    triage_data = state.get("triage_data", {})
    symptoms = triage_data.get("symptoms", [])
    urgency = triage_data.get("urgency", "routine")
    
    k_in = KnowledgeInput(query=state.get("raw_input", ""), symptoms=symptoms, urgency=urgency)
    k_out = await knowledge_agent.process(k_in)
    return {"knowledge_data": k_out.model_dump()}


@record_agent_result("community_response")
async def node_community(state: WorkflowState) -> Dict[str, Any]:
    logger.debug("Graph: community executing")
    loc = state.get("location", {})
    c_in = CommunityInput(
        disaster_type="disaster",
        region="local area",
        latitude=loc.get("lat", 25.5941),
        longitude=loc.get("lng", 85.1376),
        severity="critical",
        needs=["medical_volunteers"]
    )
    c_out = await community_agent.activate(c_in)
    return {"community_data": c_out.model_dump()}


@record_agent_result("public_health")
async def node_public_health(state: WorkflowState) -> Dict[str, Any]:
    logger.debug("Graph: public_health executing")
    p_in = PublicHealthInput(
        cases=[{"symptoms": ["unknown"], "location": state.get("location", {}), "timestamp": "now"}]
    )
    p_out = await public_health_agent.analyze(p_in)
    return {"metadata": {"public_health_data": p_out.model_dump()}}


# ──────────────────────────────────────────────────────────────────
# Sequential Clinical Nodes
# ──────────────────────────────────────────────────────────────────

@record_agent_result("intake")
async def node_intake(state: WorkflowState) -> Dict[str, Any]:
    logger.debug("Graph: intake executing")
    loc = state.get("location", {})
    i_in = IntakeInput(text=state.get("raw_input", ""), latitude=loc.get("lat", 25.5941), longitude=loc.get("lng", 85.1376))
    i_out = await intake_agent.process(i_in)
    return {"intake_data": i_out.model_dump()}


@record_agent_result("triage")
async def node_triage(state: WorkflowState) -> Dict[str, Any]:
    from datetime import datetime, timezone
    logger.debug("Graph: triage executing")
    intake = state.get("intake_data", {})
    meta = state.get("metadata", {}) or {}
    t_in = TriageInput(symptoms=intake.get("symptoms", []), duration=intake.get("duration", ""), age=meta.get("age"))
    t_out = await triage_agent.process(t_in)
    
    obs = {
        "observation_type": "symptom_triage",
        "content": {"urgency": t_out.urgency, "symptoms": t_in.symptoms},
        "source_agent": "triage",
        "confidence": getattr(t_out, "confidence", 0.9),
        "timestamp": datetime.now(tz=timezone.utc).isoformat()
    }
    
    return {
        "triage_data": t_out.model_dump(),
        "emergency_detected": t_out.urgency == "critical",
        "clinical_observations": [obs]
    }


@record_agent_result("care_coordination")
async def node_care_coordination(state: WorkflowState) -> Dict[str, Any]:
    logger.debug("Graph: care_coord executing")
    triage = state.get("triage_data", {})
    intake = state.get("intake_data", {})
    loc = state.get("location", {})
    lat = loc.get("lat", 25.5941)
    lng = loc.get("lng", 85.1376)
    
    if not triage.get("needs_hospital"):
        return {}
        
    c_in = CareCoordinationInput(
        symptoms=intake.get("symptoms", []),
        urgency=triage.get("urgency", "routine"),
        required_specialization=triage.get("recommended_specialization"),
        patient_location={"lat": lat, "lng": lng}
    )
    c_out = await care_coord_agent.process(c_in)
    
    from datetime import datetime, timezone
    decision = {
        "decision_type": "hospital_routing",
        "decision": {"hospital": getattr(c_out, "recommended_hospital", None)},
        "rationale": getattr(c_out, "explanation", ""),
        "agent": "care_coordination",
        "timestamp": datetime.now(tz=timezone.utc).isoformat()
    }
    
    return {
        "care_coordination_data": c_out.model_dump(),
        "decisions": [decision]
    }


@record_agent_result("ambulance")
async def node_ambulance(state: WorkflowState) -> Dict[str, Any]:
    logger.debug("Graph: ambulance executing")
    care = state.get("care_coordination_data") or {}
    loc = state.get("location") or {}
    triage = state.get("triage_data") or {}
    
    if care.get("ambulance_dispatched") and care.get("recommended_hospital"):
        hosp = care["recommended_hospital"]
        a_in = AmbulanceInput(
            patient_lat=loc.get("lat", 25.5941), patient_lng=loc.get("lng", 85.1376),
            target_hospital_id=hosp.get("hospital_id", "H001"),
            target_hospital_name=hosp.get("hospital_name", "Unknown"),
            target_hospital_lat=hosp.get("hospital_lat", loc.get("lat", 25.5941)),
            target_hospital_lng=hosp.get("hospital_lng", loc.get("lng", 85.1376)),
            urgency=triage.get("urgency", "critical")
        )
        a_out = await ambulance_agent.dispatch(a_in)
        return {"ambulance_data": a_out.model_dump()}
    return {}


@record_agent_result("followup")
async def node_followup(state: WorkflowState) -> Dict[str, Any]:
    logger.debug("Graph: followup executing")
    care = state.get("care_coordination_data") or {}
    triage = state.get("triage_data") or {}
    profile = state.get("user_profile") or {}
    
    if care.get("recommended_hospital"):
        f_in = FollowupInput(
            case_id=state.get("workflow_id", "unknown"),
            patient_phone=profile.get("phone", "+1234567890"),  # Dummy for demo
            patient_name=profile.get("name", "Patient"),
            hospital_name=care["recommended_hospital"].get("hospital_name", ""),
            urgency=triage.get("urgency", "routine")
        )
        f_out = await followup_agent.schedule_followup(f_in)
        return {"followup_data": f_out.model_dump()}
    return {}


@record_agent_result("explainability")
async def node_explainability(state: WorkflowState) -> Dict[str, Any]:
    logger.debug("Graph: explainability executing")
    
    triage_data = state.get("triage_data", {})
    care_data = state.get("care_coordination_data", {})
    amb_data = state.get("ambulance_data", {})
    
    e_in = ExplainabilityInput(
        decision_point="workflow_summary",
        context_data={
            "triage": triage_data,
            "care_coordination": care_data,
            "ambulance": amb_data,
        },
        outcome={
            "urgency": triage_data.get("urgency", "unknown"),
            "hospital_recommended": bool(care_data),
            "ambulance_dispatched": bool(amb_data and amb_data.get("dispatched")),
        },
        language="en"
    )
    e_out = await explainability_agent.explain(e_in)
    
    meta = state.get("metadata", {}) or {}
    meta["explainability_data"] = e_out.model_dump()
    return {"metadata": meta}


async def node_join(state: WorkflowState) -> Dict[str, Any]:
    """Joins parallel branches before response generation."""
    logger.debug("Graph: join executing")
    return {"workflow_status": "agents_coordinated"}


async def node_response_composer(state: WorkflowState) -> Dict[str, Any]:
    from datetime import datetime, timezone
    from backend.services.multilingual_service import detect_language, translate_from_english

    print("\n[COMPOSER] ──── RESPONSE COMPOSER ────")
    logger.debug("Graph: response_composer executing")
    
    # If the planner already set a greeting response, just keep it!
    if state.get("workflow_objective") == "GREETING" and state.get("response_text"):
        return {
            "workflow_status": "completed",
            "completed_at": datetime.now(tz=timezone.utc).isoformat(),
        }
    
    response_parts = []
    
    # 1. Urgency Assessment
    triage = state.get("triage_data") or {}
    urgency = triage.get("urgency", "routine").upper()
    confidence = triage.get("confidence", 0)
    symptoms = triage.get("symptoms", [])
    
    if urgency in ["CRITICAL", "URGENT"]:
        response_parts.append(f"⚠️ **URGENCY LEVEL: {urgency}**\n• Please remain calm and follow the instructions below.")
    else:
        response_parts.append(f"🩺 **ASSESSMENT: {urgency}** (Confidence: {int(confidence*100)}%)")
    
    # Show detected symptoms
    if symptoms:
        sym_list = "\n".join([f"  • {s.replace('_', ' ').title()}" for s in symptoms])
        response_parts.append(f"**Detected Symptoms:**\n{sym_list}")
    
    # 2. Home Care (for routine)
    if urgency == "ROUTINE":
        home_advice = triage.get("home_care_advice")
        if home_advice:
            if isinstance(home_advice, list):
                advice_lines = "\n".join([f"  • {a}" for a in home_advice])
            else:
                advice_lines = f"  • {home_advice}"
            response_parts.append(f"🏠 **Home Care Advice:**\n{advice_lines}")
    
    # 3. Ambulance Information
    amb = state.get("ambulance_data") or {}
    if amb and amb.get("dispatched"):
        response_parts.append(
            f"🚑 **AMBULANCE DISPATCHED**\n"
            f"  • Status: {amb.get('status_message', 'En route')}\n"
            f"  • ETA: {amb.get('eta_minutes', 'Calculating')} minutes"
        )
        
    # 4. Hospital Recommendation
    care = state.get("care_coordination_data") or {}
    if care.get("recommended_hospital"):
        hosp = care["recommended_hospital"]
        response_parts.append(
            f"🏥 **Recommended Hospital:**\n"
            f"  • Name: {hosp.get('hospital_name', 'Nearest facility')}\n"
            f"  • ICU Available: {hosp.get('icu_beds_available', 'N/A')} beds\n"
            f"  • Distance: {hosp.get('distance_km', 'N/A')} km"
        )
        if care.get("explanation"):
            response_parts.append(f"  • Reason: {care.get('explanation')}")

    # 5. Explainability
    meta = state.get("metadata") or {}
    expl_data = meta.get("explainability_data") or {}
    if expl_data.get("short_explanation"):
        response_parts.append(f"💡 **Reasoning:** {expl_data['short_explanation']}")
        
    # 6. Follow-up
    followup = state.get("followup_data") or {}
    if followup:
        response_parts.append(f"📅 **Follow-Up:** We will check back with you in 24 hours.")
    
    # 7. Knowledge / RAG Insights — CLEAR SECTION with source citation
    kng = state.get("knowledge_data") or {}
    if kng and kng.get("synthesized_insight") and kng.get("status") == "success":
        insight = kng.get('synthesized_insight', '').strip()
        sources = kng.get('retrieved_documents', [])
        source_names = list(set(d.get('source', '') for d in sources if d.get('source')))
        
        rag_section = f"📚 **Medical Guidelines (from RAG Knowledge Base):**\n{insight}"
        if source_names:
            src_list = ", ".join(source_names[:3])
            rag_section += f"\n  📄 Sources: {src_list}"
        response_parts.append(rag_section)
        print(f"  📚 RAG returned {len(sources)} documents from: {source_names}")
    elif kng and kng.get("status") == "no_results":
        response_parts.append("📚 **Knowledge Base:** No specific guidelines found for this query in our database.")
        print("  📚 RAG: No matching documents found")
    elif kng and kng.get("status") == "error":
        print(f"  📚 RAG ERROR: {kng.get('synthesized_insight', '')}")

    # Fallback if no parts
    final_english_text = "\n\n".join(response_parts) if response_parts else "I have processed your request. Please describe your symptoms in more detail for a better assessment."
    
    print(f"  📝 Response length: {len(final_english_text)} chars")
    
    # 8. Dynamic Language Detection & Translation
    raw_input = state.get("raw_input", "")
    target_lang = await detect_language(raw_input)
    final_text = await translate_from_english(final_english_text, target_lang)
    
    print(f"  🌐 Language: {target_lang}")
    print("[OK] ──── RESPONSE COMPOSED ────\n")
    
    return {
        "workflow_status": "completed",
        "response_text": final_text,
        "response_language": target_lang,
        "completed_at": datetime.now(tz=timezone.utc).isoformat(),
    }


def node_error_handler(state: WorkflowState) -> Dict[str, Any]:
    logger.warning("Graph: error handler", error=state.get("error"))
    return {"workflow_status": "failed"}


# ──────────────────────────────────────────────────────────────────
# Routing logic
# ──────────────────────────────────────────────────────────────────

def route_from_planner(state: WorkflowState) -> List[str]:
    selected = state.get("selected_agents", [])
    routes = []
    
    # Clinical sequential pipeline entry
    if "intake" in selected:
        routes.append("intake")
    elif "knowledge" not in selected and "community_response" not in selected:
        routes.append("response_composer")
        
    # Parallel agents
    if "knowledge" in selected:
        routes.append("knowledge")
    if "community_response" in selected:
        routes.append("community")
    if "public_health" in selected:
        routes.append("public_health")
        
    return routes if routes else ["response_composer"]


def route_after_intake(state: WorkflowState) -> str:
    selected = state.get("selected_agents", [])
    if "triage" in selected:
        return "triage"
    return "join"

def route_after_triage(state: WorkflowState) -> str:
    selected = state.get("selected_agents", [])
    if "care_coordination" in selected:
        return "care_coordination"
    return "join"

def route_after_care(state: WorkflowState) -> str:
    selected = state.get("selected_agents", [])
    if "ambulance" in selected:
        return "ambulance"
    return "followup" if "followup" in selected else "join"

def route_after_ambulance(state: WorkflowState) -> str:
    selected = state.get("selected_agents", [])
    if "followup" in selected:
        return "followup"
    return "join"


def route_after_join(state: WorkflowState) -> str:
    from langgraph.graph import END
    
    selected = set(state.get("selected_agents", []))
    # explainability and response_composer run AFTER join, so they shouldn't block the join node
    required_to_complete = selected - {"explainability", "response_composer"}
    completed_results = state.get("agent_results", [])
    completed = set(res["agent_name"] for res in completed_results if res.get("status") in ("completed", "failed", "skipped"))
    
    # Check if all required agents have successfully completed
    if required_to_complete.issubset(completed):
        if "explainability" in selected:
            return "explainability"
        return "response_composer"
    
    # If not all agents are done, terminate this branch and wait for others
    return END


def build_healthcare_graph() -> StateGraph:
    graph = StateGraph(WorkflowState)

    graph.add_node("context_loader", node_context_loader)
    graph.add_node("planner", node_planner)
    
    # Parallel independent nodes
    graph.add_node("knowledge", node_knowledge)
    graph.add_node("community", node_community)
    graph.add_node("public_health", node_public_health)
    
    # Sequential clinical nodes
    graph.add_node("intake", node_intake)
    graph.add_node("triage", node_triage)
    graph.add_node("care_coordination", node_care_coordination)
    graph.add_node("ambulance", node_ambulance)
    graph.add_node("followup", node_followup)
    
    graph.add_node("join", node_join)
    graph.add_node("explainability", node_explainability)
    graph.add_node("response_composer", node_response_composer)
    graph.add_node("error_handler", node_error_handler)

    # Edges
    graph.add_edge(START, "context_loader")
    graph.add_edge("context_loader", "planner")
    
    # Planner splits to parallel branches
    graph.add_conditional_edges("planner", route_from_planner, ["intake", "knowledge", "community", "public_health", "response_composer"])
    
    # Clinical sequential pipeline
    graph.add_conditional_edges("intake", route_after_intake, ["triage", "join"])
    graph.add_conditional_edges("triage", route_after_triage, ["care_coordination", "join"])
    graph.add_conditional_edges("care_coordination", route_after_care, ["ambulance", "followup", "join"])
    graph.add_conditional_edges("ambulance", route_after_ambulance, ["followup", "join"])
    graph.add_edge("followup", "join")
    
    # Parallel nodes all join back
    graph.add_edge("knowledge", "join")
    graph.add_edge("community", "join")
    graph.add_edge("public_health", "join")
    
    # After join -> explainability -> response
    graph.add_conditional_edges("join", route_after_join, ["explainability", "response_composer", END])
    graph.add_edge("explainability", "response_composer")
    graph.add_edge("response_composer", END)

    from langgraph.checkpoint.memory import MemorySaver
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


_compiled_graph = None

def get_compiled_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_healthcare_graph()
    return _compiled_graph
