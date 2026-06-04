import json
from loguru import logger
from backend.app.models.agent_state import FaultAnalysisState
from backend.app.config import get_settings, get_openai_client


SYSTEM_PROMPT = """You are a senior telecom NOC engineer with expert knowledge of Ericsson, Nokia, Huawei, Cisco, and Juniper equipment.

Generate actionable troubleshooting and resolution recommendations.

Return ONLY a JSON object with this exact structure (no markdown, no extra text):
{
  "immediate_actions": ["step1", "step2"],
  "diagnostic_steps": ["step3", "step4"],
  "resolution_steps": ["step5", "step6"],
  "preventive_measures": ["step7", "step8"],
  "escalation_path": "Contact L3 support if unresolved within X hours"
}

Guidelines:
- 2-3 concise steps per section
- Include vendor-specific tools where relevant
- Order from least-disruptive to most invasive"""


def resolution_node(state: FaultAnalysisState) -> dict:
    """Agent 4: Generates vendor-aware, technology-specific step-by-step remediation."""
    logger.info("[ResolutionAgent] Generating recommendations")

    settings = get_settings()
    client = get_openai_client()

    incidents = state.get("retrieved_incidents", [])
    vendors = list({inc.get("device_vendor", "") for inc in incidents if inc.get("device_vendor")})
    technologies = list({inc.get("technology_type", "") for inc in incidents if inc.get("technology_type")})

    historical_res = []
    for inc in incidents[:5]:
        res = inc.get("resolution_notes", "")
        if res:
            historical_res.append(f"[{inc.get('alarm_id','?')}]: {str(res)[:200]}")

    user_msg = (
        f"Fault: {state['query']}\n\n"
        f"Root cause: {state.get('root_cause', 'N/A')}\n\n"
        f"Service impact: {state.get('service_impact', 'N/A')}\n\n"
        f"Vendors: {', '.join(vendors)}\n"
        f"Technologies: {', '.join(technologies)}\n\n"
        f"Historical resolutions:\n" + "\n".join(historical_res) +
        "\n\nGenerate structured resolution recommendations as JSON."
    )

    recommendations = []
    try:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            temperature=0.1,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            max_tokens=500,
        )
        parsed = json.loads(response.choices[0].message.content or "{}")

        for section_key, label in [
            ("immediate_actions", "IMMEDIATE"),
            ("diagnostic_steps", "DIAGNOSTIC"),
            ("resolution_steps", "RESOLUTION"),
            ("preventive_measures", "PREVENTIVE"),
        ]:
            for step in parsed.get(section_key, []):
                recommendations.append(f"[{label}] {step}")
        escalation = parsed.get("escalation_path", "")
        if escalation:
            recommendations.append(f"[ESCALATION] {escalation}")

    except Exception as e:
        logger.error(f"[ResolutionAgent] LLM call failed: {e}")
        recommendations = [f"[ESCALATION] Resolution generation failed: {str(e)}. Escalate to L3 support."]

    trace_entry = (
        f"[Agent 4 - Resolution] Generated {len(recommendations)} steps. "
        f"Vendors: {', '.join(vendors[:3])}. Technologies: {', '.join(technologies[:3])}."
    )

    return {
        "recommendations": recommendations,
        "reasoning_trace": state.get("reasoning_trace", []) + [trace_entry],
    }
