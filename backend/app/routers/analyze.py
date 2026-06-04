from fastapi import APIRouter, HTTPException
from backend.app.models.query import AnalysisRequest, AnalysisResponse
from backend.app.models.agent_state import FaultAnalysisState
from backend.app.utils.guardrails import validate_query
from backend.app.graph.workflow import get_workflow
from loguru import logger

router = APIRouter(prefix="/api", tags=["Analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_fault(request: AnalysisRequest):
    guard = validate_query(request.query)

    # Return a structured 200 response even when blocked so the UI can
    # render the GuardrailPanel with the reason instead of a generic 422.
    if not guard["valid"]:
        logger.info(f"Analysis blocked by guardrail: {guard['error']!r}")
        return AnalysisResponse(
            query=request.query,
            guardrail_result=guard,
            retrieved_incidents=[],
            correlated_alarms=[],
            root_cause="",
            service_impact="",
            recommendations=[],
            reasoning_trace=[],
            severity_escalated=False,
        )

    filters = request.filters.model_dump(exclude_none=True) if request.filters else {}

    initial_state: FaultAnalysisState = {
        "query": request.query,
        "metadata_filters": filters,
        "guardrail_result": guard,
        "retrieved_incidents": [],
        "correlated_alarms": [],
        "root_cause": "",
        "service_impact": "",
        "recommendations": [],
        "reasoning_trace": [],
        "severity_escalated": False,
    }

    try:
        workflow = get_workflow()
        final_state = workflow.invoke(initial_state)
        logger.info(f"Analysis complete for: '{request.query[:60]}'")
        return AnalysisResponse(
            query=final_state["query"],
            guardrail_result=final_state["guardrail_result"],
            retrieved_incidents=final_state.get("retrieved_incidents", []),
            correlated_alarms=final_state.get("correlated_alarms", []),
            root_cause=final_state.get("root_cause", ""),
            service_impact=final_state.get("service_impact", ""),
            recommendations=final_state.get("recommendations", []),
            reasoning_trace=final_state.get("reasoning_trace", []),
            severity_escalated=final_state.get("severity_escalated", False),
        )
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
