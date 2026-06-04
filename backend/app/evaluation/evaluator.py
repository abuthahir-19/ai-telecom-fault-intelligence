"""
Evaluation module — RAGAS-aligned RAG quality metrics.

Three dimensions measured with direct LLM-as-judge calls:
  1. Faithfulness         — is the answer grounded in retrieved incidents?
  2. Answer Relevancy     — does the answer address the original query?
  3. Context Precision    — are the retrieved incidents relevant to the query?

Why direct LLM calls instead of DeepEval's built-in metric objects:
  DeepEval's FaithfulnessMetric / AnswerRelevancyMetric internally make
  multiple sequential LLM calls whose combined JSON responses easily exceed
  the proxy's max_tokens=500 hard cap, causing truncated / invalid-JSON
  failures.  Each metric here is ONE focused call whose expected response
  is well under 300 tokens.

Also provides an LLM cross-encoder reranker (rerank_incidents).
"""

import json
import re
from typing import List, Dict, Any, Union
from loguru import logger

from backend.app.config import get_settings, get_openai_client


# ── JSON extraction helper ────────────────────────────────────────────────────

def _extract_json(text: str) -> str:
    """
    Pull a JSON object out of an LLM response that may contain:
      • Markdown code fences  (```json … ```)
      • Preamble text before the first {
      • Trailing prose after the closing }
    Returns the best candidate JSON string found, or the original text.
    """
    text = text.strip()
    # Strip markdown code fences
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        text = re.sub(r"\n?\s*```\s*$", "", text)
        text = text.strip()
    # If the response doesn't start with { or [, find the first JSON block
    if text and text[0] not in "{[":
        m = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
        if m:
            text = m.group(1)
    return text


def _safe_float(value: Any, default: float = 0.0) -> float:
    """Convert a value to float clamped to [0, 1]."""
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return default


# ── LLM Reranker ──────────────────────────────────────────────────────────────

RERANK_SYSTEM = (
    "You are a telecom network fault retrieval expert. "
    "Score how relevant the incident is to the user query on a scale 0.0-1.0. "
    'Return ONLY valid JSON: {"score": <float 0.0-1.0>, "reason": "<one sentence>"}. '
    "Scoring guide: "
    "1.0=exact technology+region+symptom match, "
    "0.7=same technology+similar symptoms, "
    "0.5=related technology or partial symptom match, "
    "0.2=tangentially related, "
    "0.0=completely unrelated."
)


def rerank_incidents(
    query: str,
    incidents: List[Dict[str, Any]],
    top_k: int = 10,
) -> List[Dict[str, Any]]:
    """
    LLM cross-encoder reranker.
    Blends: combined_score = 0.6 * judge_score + 0.4 * normalised_rrf_score
    """
    if not incidents:
        return []

    settings = get_settings()
    client = get_openai_client()
    scored = []

    for inc in incidents:
        snippet = (
            f"Technology: {inc.get('technology_type', '?')} | "
            f"Region: {inc.get('network_region', '?')} | "
            f"Vendor: {inc.get('device_vendor', '?')} | "
            f"Severity: {inc.get('severity', '?')}\n"
            f"Description: {str(inc.get('incident_description', ''))[:300]}"
        )
        try:
            resp = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                temperature=0.0,
                messages=[
                    {"role": "system", "content": RERANK_SYSTEM},
                    {"role": "user", "content": f"Query: {query}\n\nIncident:\n{snippet}"},
                ],
                max_tokens=80,
            )
            raw = _extract_json(resp.choices[0].message.content or "{}")
            data = json.loads(raw)
            judge_score = _safe_float(data.get("score"), 0.5)
            judge_reason = str(data.get("reason", ""))
        except Exception as e:
            logger.debug(f"Reranker error for {inc.get('alarm_id')}: {e}")
            judge_score, judge_reason = 0.5, ""

        rrf = float(inc.get("rrf_score", 0.0))
        combined = round(0.6 * judge_score + 0.4 * min(rrf * 200, 1.0), 4)
        inc = inc.copy()
        inc["judge_score"]   = round(judge_score, 3)
        inc["judge_reason"]  = judge_reason
        inc["combined_score"] = combined
        scored.append(inc)

    scored.sort(key=lambda x: x["combined_score"], reverse=True)
    logger.info(f"Reranked {len(scored)} incidents for: '{query[:60]}'")
    return scored[:top_k]


# ── RAG Evaluation (direct LLM-as-judge) ──────────────────────────────────────

def evaluate_analysis(
    query: str,
    retrieved_incidents: List[Dict[str, Any]],
    root_cause: str,
    recommendations: List[str],
) -> Dict[str, Any]:
    """
    Evaluates RAG output quality using three RAGAS-aligned metrics.

    Each metric is a single focused LLM call whose expected JSON response
    is under 300 tokens — safely within the proxy's max_tokens=500 limit.

    Weighted overall score:
        overall = 0.40 × faithfulness + 0.35 × answer_relevancy + 0.25 × context_precision
    """
    client     = get_openai_client()
    model_name = get_settings().OPENAI_MODEL

    # ── Shared helper ─────────────────────────────────────────────────────────
    def _judge(prompt: str) -> Dict[str, Any]:
        """One LLM call; returns parsed dict or {} on any failure."""
        try:
            resp = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a strict JSON-only evaluator. "
                            "Output a single JSON object. "
                            "No markdown, no code fences, no text outside the JSON."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                max_tokens=350,
            )
            raw = resp.choices[0].message.content or "{}"
            return json.loads(_extract_json(raw))
        except Exception as exc:
            logger.warning(f"[Eval] LLM call failed: {exc}")
            return {}

    # ── Compact input representations (keep prompts small) ───────────────────
    answer_text = (
        f"Root cause: {root_cause[:300]}\n"
        f"Recommendations: {' | '.join(recommendations[:5])}"
    )[:500]

    context_lines = "\n".join(
        f"[{inc.get('alarm_id','?')}] "
        f"{inc.get('technology_type','?')} | "
        f"{inc.get('network_region','?')} | "
        f"{inc.get('severity','?')} — "
        f"{str(inc.get('incident_description',''))[:120]}"
        for inc in retrieved_incidents[:5]
    )

    results: Dict[str, Any] = {
        "query": query,
        "faithfulness":     {},
        "answer_relevance": {},
        "context_precision":{},
        "overall_score":    0.0,
        "evaluation_summary": "",
    }
    f_score = rv_score = p_score = 0.0

    # ── 1. Faithfulness ───────────────────────────────────────────────────────
    # Is the generated answer grounded in the retrieved evidence?
    data = _judge(
        f"Query: {query[:150]}\n\n"
        f"Generated analysis:\n{answer_text}\n\n"
        f"Retrieved evidence:\n{context_lines}\n\n"
        "Task: Rate FAITHFULNESS (0.0–1.0).\n"
        "Faithfulness = fraction of key claims in the analysis that are supported "
        "by the retrieved evidence.\n"
        "1.0 = every claim is grounded | 0.0 = no claims are grounded\n\n"
        'Return exactly: {"faithfulness_score": <0.0-1.0>, '
        '"grounding_assessment": "<one sentence>", "issues": ["<issue1>"]}'
    )
    if data:
        f_score = _safe_float(data.get("faithfulness_score"))
        results["faithfulness"] = {
            "faithfulness_score":   round(f_score, 3),
            "grounding_assessment": str(data.get("grounding_assessment", "")),
            "issues":               list(data.get("issues", [])),
        }
        logger.info(f"Faithfulness: {f_score:.3f} — {data.get('grounding_assessment','')[:80]}")
    else:
        results["faithfulness"] = {
            "faithfulness_score": 0.0,
            "grounding_assessment": "Evaluation unavailable",
            "issues": [],
        }
        logger.warning("Faithfulness metric failed — LLM returned no data")

    # ── 2. Answer Relevancy ───────────────────────────────────────────────────
    # Does the generated answer directly address the original query?
    data = _judge(
        f"Query: {query[:150]}\n\n"
        f"Generated analysis:\n{answer_text}\n\n"
        "Task: Rate ANSWER RELEVANCY (0.0–1.0).\n"
        "Answer relevancy = how directly and completely the analysis addresses the query.\n"
        "1.0 = fully on-topic and complete | 0.0 = completely off-topic\n\n"
        'Return exactly: {"relevance_score": <0.0-1.0>, '
        '"relevance_assessment": "<one sentence>", "missing_aspects": ["<aspect1>"]}'
    )
    if data:
        rv_score = _safe_float(data.get("relevance_score"))
        results["answer_relevance"] = {
            "relevance_score":       round(rv_score, 3),
            "relevance_assessment":  str(data.get("relevance_assessment", "")),
            "missing_aspects":       list(data.get("missing_aspects", [])),
        }
        logger.info(f"Answer Relevancy: {rv_score:.3f} — {data.get('relevance_assessment','')[:80]}")
    else:
        results["answer_relevance"] = {
            "relevance_score": 0.0,
            "relevance_assessment": "Evaluation unavailable",
            "missing_aspects": [],
        }
        logger.warning("Answer Relevancy metric failed — LLM returned no data")

    # ── 3. Context Precision ──────────────────────────────────────────────────
    # What fraction of the retrieved incidents are genuinely relevant to the query?
    data = _judge(
        f"Query: {query[:150]}\n\n"
        f"Retrieved incidents:\n{context_lines}\n\n"
        "Task: Rate CONTEXT PRECISION (0.0–1.0).\n"
        "Context precision = fraction of retrieved incidents that are relevant to the query.\n"
        "1.0 = all retrieved incidents are relevant | 0.0 = none are relevant\n\n"
        'Return exactly: {"context_precision_score": <0.0-1.0>, '
        '"precision_assessment": "<one sentence>"}'
    )
    if data:
        p_score = _safe_float(data.get("context_precision_score"))
        results["context_precision"] = {
            "context_precision_score": round(p_score, 3),
            "precision_assessment":    str(data.get("precision_assessment", "")),
        }
        logger.info(f"Context Precision: {p_score:.3f} — {data.get('precision_assessment','')[:80]}")
    else:
        results["context_precision"] = {
            "context_precision_score": 0.0,
            "precision_assessment": "Evaluation unavailable",
        }
        logger.warning("Context Precision metric failed — LLM returned no data")

    # ── Overall score (RAGAS-aligned weights) ─────────────────────────────────
    overall = round(f_score * 0.40 + rv_score * 0.35 + p_score * 0.25, 3)
    results["overall_score"] = overall
    results["evaluation_summary"] = (
        f"Overall: {overall:.0%}  |  "
        f"Faithfulness: {f_score:.0%}  |  "
        f"Answer Relevancy: {rv_score:.0%}  |  "
        f"Context Precision: {p_score:.0%}"
    )
    logger.info(f"Evaluation complete — {results['evaluation_summary']}")
    return results
