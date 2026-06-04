from fastapi import APIRouter
from backend.app.models.query import QueryRequest, QueryResponse
from backend.app.rag.hybrid_retriever import get_hybrid_retriever
from backend.app.utils.guardrails import validate_query
from backend.app.config import get_settings, get_openai_client
from loguru import logger

router = APIRouter(prefix="/api", tags=["Query"])


@router.post("/query", response_model=QueryResponse)
async def query_incidents(request: QueryRequest):
    guard = validate_query(request.query)

    # Return a structured 200 response even when blocked so the UI can
    # render the GuardrailPanel with the reason instead of a generic 422.
    if not guard["valid"]:
        logger.info(f"Query blocked by guardrail: {guard['error']!r}")
        return QueryResponse(
            query=request.query,
            guardrail_result=guard,
            guardrail_warnings=[],
            incidents=[],
            root_cause_suggestion="",
            total_results=0,
        )

    retriever = get_hybrid_retriever()
    filters = request.filters.model_dump(exclude_none=True) if request.filters else {}
    incidents = retriever.search(query=request.query, k=request.top_k, filters=filters)

    root_cause_suggestion = ""
    if incidents:
        settings = get_settings()
        try:
            client = get_openai_client()
            ctx = "\n".join([
                f"[{inc.get('alarm_id','')}] {inc.get('incident_description','')} -> {inc.get('resolution_notes','')}"
                for inc in incidents[:5]
            ])
            resp = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                temperature=0.1,
                messages=[
                    {"role": "system", "content": "You are a telecom fault analysis expert. Give a concise 2-3 sentence root cause suggestion based on similar historical incidents."},
                    {"role": "user", "content": f"Query: {request.query}\n\nSimilar incidents:\n{ctx}"},
                ],
                max_tokens=300,
            )
            root_cause_suggestion = resp.choices[0].message.content or ""
        except Exception as e:
            logger.warning(f"Quick RCA failed: {e}")

    return QueryResponse(
        query=request.query,
        guardrail_result=guard,
        guardrail_warnings=guard.get("warnings", []),
        incidents=incidents,
        root_cause_suggestion=root_cause_suggestion,
        total_results=len(incidents),
    )
