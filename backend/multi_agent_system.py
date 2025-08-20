# backend/multi_agent_system.py
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"backend\.env")

import os
import json
import time
from typing import TypedDict, Dict, Any
from concurrent.futures import ThreadPoolExecutor

try:
    from langchain_openai import ChatOpenAI
    from langgraph.graph import StateGraph, START, END
    from langchain_core.prompts import ChatPromptTemplate
    LANGCHAIN_AVAILABLE = True
    print("✅ LangChain packages loaded successfully")
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    print(f"❌ LangChain import error: {e}")
    raise ImportError(f"Required LangChain packages not available: {e}")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in backend/.env")

class MultiAgentState(TypedDict):
    context: str
    transcript: str
    summary: str
    analysis: str
    coaching: str
    final_result: Dict[str, Any]

# -------------------- Safe JSON Parsing --------------------
def safe_json_parse(text: str, agent_name: str = "Unknown") -> Dict[str, Any]:
    """Safe JSON parsing with comprehensive error handling"""
    if not text or text.strip() == "":
        print(f"⚠️ {agent_name}: Empty response received")
        return {}
    
    cleaned_text = text.strip()
    
    # Remove code fences using unicode escapes to avoid backtick issues
    if len(cleaned_text) >= 7 and cleaned_text[:7].lower() == "\u0060\u0060\u0060json":
        cleaned_text = cleaned_text[7:].lstrip()
    elif len(cleaned_text) >= 3 and cleaned_text[:3] == "\u0060\u0060\u0060":
        cleaned_text = cleaned_text[3:].lstrip()
    
    if len(cleaned_text) >= 3 and cleaned_text[-3:] == "\u0060\u0060\u0060":
        cleaned_text = cleaned_text[:-3].rstrip()
    
    try:
        result = json.loads(cleaned_text)
        print(f"✅ {agent_name}: JSON parsed successfully")
        return result
    except json.JSONDecodeError as e:
        print(f"❌ {agent_name}: JSON parsing failed - {e}")
        print(f"🔍 Raw content: {cleaned_text[:200]}...")
        
        # Attempt repair
        try:
            fixed_text = cleaned_text.replace('\\"', '"').replace("\\n", "\n").replace("\\t", "\t")
            result = json.loads(fixed_text)
            print(f"✅ {agent_name}: JSON repaired and parsed")
            return result
        except:
            print(f"❌ {agent_name}: JSON repair failed")
            return {}

# -------------------- LLM Builder --------------------
def build_optimized_llm() -> ChatOpenAI:
    return ChatOpenAI(
        openai_api_key=OPENAI_API_KEY,
        model="gpt-3.5-turbo",
        temperature=0.2,
        max_tokens=800,
        timeout=40,
        streaming=False
    )

# -------------------- Enhanced Prompts --------------------
summary_prompt = ChatPromptTemplate.from_template("""
You are a senior sales call analyst. Produce a manager-ready executive summary.

CONTEXT:
{context}

TRANSCRIPT:
{transcript}

Write a single paragraph (8-10 sentences) covering:
- Call purpose & stage
- Customer situation and explicit pains/constraints/metrics (quote concrete values if present)
- Buying criteria that emerged (e.g., integrations, security, pricing band, decision process, timeline,
                                                   stakeholders)
- Key rep behaviors (discovery depth, value framing, tailoring, objection handling)
- Outcome and specific next steps (owner + timeframe if present)

Rules:
- Use only transcript-grounded facts; do not invent details.
- Prefer concrete details over generic language.
- No bullet points. One tight paragraph.
""")

analysis_prompt = ChatPromptTemplate.from_template("""
Analyze this sales call and return ONLY valid JSON. No extra text.

CONTEXT:
{context}

TRANSCRIPT:
{transcript}

Return this exact structure, filled from the transcript (no placeholders):
{
  "metrics": {
    "overall_sentiment": "positive|neutral|negative",
    "sentiment_rationale": "1–2 sentences with short quotes supporting sentiment",
    "rep_talk_ratio_percent": 60"analyze the transcript deeply and provide the rep's talk time as a 
                                                   percentage of total call time and this can vary from one call to another",
    "customer_talk_ratio_percent": 40""analyze the transcript deeply and provide the customer's talk time as a 
                                                   percentage of total call time and this can vary from one call to another",
    "questions_asked_by_rep": 0"analyze the transcript deeply and provide the number of questions asked by the rep",
    "objections_detected": 0"analyze the transcript deeply and provide the number of objections detected in the call",
    "followups_committed": 0""analyze the transcript deeply and provide the number of follow-ups committed in the call"
  },
  "strengths": [
    "Transcript-evidenced strengths (min 4-5) and max depends upon duration of the call and they can vary from one call to 
                                                   another depending on the rep's performance and the detailed anaysis of the call"
  ],
  "areas_to_improve": [
    "Transcript-evidenced improvement areas (min 3-4) and
                                                 max depends upon duration of the call and they can vary from one call to another depending on the rep's performance and the detailed anaysis of the call"
  ],
  "customer_objections": [
    {
      "objection": "what the concern is (price/timing/integration/security/etc.) depending on the call analysis",
      "moment_quote": "verbatim customer quote",
      "rep_response_quality": "good|adequate|weak",
      "suggested_response": "precision response tailored to this objection"
    }
  ],
  "notable_quotes": [
    {
      "speaker": "customer|rep",
      "quote": "verbatim impactful line",
      "why_it_matters": "what it reveals about needs, intent, risk, or alignment"
    }
  ]
}

Constraints:
- Derive everything from transcript only.
- rep_talk_ratio_percent + customer_talk_ratio_percent MUST equal 100.
- If a list has no items, return [] (do not fabricate).
- Return JSON only.
""")

coaching_prompt = ChatPromptTemplate.from_template("""
                                                   ROLE: You are a senior sales coach with deep expertise in 
                                                   B2B sales.You have access to the call transcript and context.
                                                   You will provide coaching to the sales rep based on the detailed
                                                    call analysis.Provide actionable, transcript-grounded coaching
                                                   that the rep can apply in future calls.
Provide coaching as JSON only, based on the transcript and grounded in the transcript context.

CONTEXT:
{context}

TRANSCRIPT:
{transcript}
                                                   
SUMMARY:
{summary}

Return ONLY this JSON:
{
  "improvement_areas": [
    {
      "skill": "Discovery|Qualification|Value Framing|Storytelling|Objection Handling|Negotiation|Closing|
                                                   Next-Step Control and others based on the call analysis",
      "issue_observed": "short, transcript-grounded gap or other issue based on the analysis",
      "behavior_change": "precise behavior to adopt or avoid in future calls",
      "practice_drill": "short practical exercise with pass criteria",
      "ready_to_use_prompts": [
        "context-aware question/talk track",
        "optional alternative"
      ]
    }
  ],
  "next_steps": [
    {
      "owner": "rep|prospect|both",
      "action": "specific follow-up  basesd on the call analysis",
      "due_by": "timeframe from transcript or recommended timebox",
      "success_criteria": "observable outcome"
    }
  ],
  "coaching_tips": [
    {
      "skill": "same skill taxonomy",
      "tip": "2-3 high-leverage advice aligned to the gap and context so the rep can apply it in future calls"
    }
  ]
}

Rules:
- No placeholders. Omit items not supported by summary/transcript.
- JSON only. No surrounding text.
""")

# -------------------- Agent Functions --------------------
def run_agent_with_timing(agent_func, state, agent_name) -> Dict[str, str]:
    start_time = time.time()
    try:
        result = agent_func(state)
        elapsed = time.time() - start_time
        print(f"✅ {agent_name}: {elapsed:.1f}s")
        return result
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ {agent_name} failed in {elapsed:.1f}s: {str(e)}")
        return {}

def summary_agent_node(state: MultiAgentState) -> Dict[str, str]:
    llm = build_optimized_llm()
    transcript = state.get("transcript", "")[:3000]
    messages = summary_prompt.format_messages(
        context=state.get("context", ""),
        transcript=transcript
    )
    response = llm.invoke(messages)
    summary = getattr(response, 'content', "").strip()
    return {"summary": summary}

def analysis_agent_node(state: MultiAgentState) -> Dict[str, str]:
    llm = build_optimized_llm()
    transcript = state.get("transcript", "")[:3500]
    messages = analysis_prompt.format_messages(
        context=state.get("context", ""),
        transcript=transcript
    )
    response = llm.invoke(messages)
    analysis_text = getattr(response, "content", "").strip()

    data = safe_json_parse(analysis_text, "Analysis Agent")
    
    if not data or "metrics" not in data:
        # Retry with simpler prompt
        retry_prompt = ChatPromptTemplate.from_template("""
Return only JSON with keys: metrics, strengths, areas_to_improve, customer_objections, notable_quotes.
Based on context: {context} and transcript: {transcript}
""")
        messages2 = retry_prompt.format_messages(context=state.get("context", ""), transcript=transcript)
        response2 = llm.invoke(messages2)
        analysis_text2 = getattr(response2, "content", "").strip()
        data = safe_json_parse(analysis_text2, "Analysis Agent (Retry)") or {}

    # Validate and normalize data
    metrics = data.get("metrics", {})
    if "rep_talk_ratio_percent" in metrics and "customer_talk_ratio_percent" in metrics:
        try:
            rep_ratio = int(metrics["rep_talk_ratio_percent"])
            cust_ratio = int(metrics["customer_talk_ratio_percent"])
            total = rep_ratio + cust_ratio
            if total != 100 and total > 0:
                metrics["rep_talk_ratio_percent"] = round(100 * rep_ratio / total)
                metrics["customer_talk_ratio_percent"] = 100 - metrics["rep_talk_ratio_percent"]
        except:
            metrics["rep_talk_ratio_percent"] = 50
            metrics["customer_talk_ratio_percent"] = 50
    
    # Set defaults
    if not metrics.get("overall_sentiment"):
        metrics["overall_sentiment"] = "neutral"
        metrics["sentiment_rationale"] = "Neutral tone observed throughout conversation"
    
    metrics.setdefault("questions_asked_by_rep", 0)
    metrics.setdefault("objections_detected", 0)
    metrics.setdefault("followups_committed", 0)

    normalized = {
        "metrics": metrics,
        "strengths": data.get("strengths", []),
        "areas_to_improve": data.get("areas_to_improve", []),
        "customer_objections": data.get("customer_objections", []),
        "notable_quotes": data.get("notable_quotes", [])
    }
    
    return {"analysis": json.dumps(normalized, ensure_ascii=False)}

def coaching_agent_node(state: MultiAgentState) -> Dict[str, str]:
    llm = build_optimized_llm()
    transcript = state.get("transcript", "")[:2500]
    messages = coaching_prompt.format_messages(
        context=state.get("context", ""),
        summary=state.get("summary", "")
    )
    response = llm.invoke(messages)
    coaching_text = getattr(response, "content", "").strip()

    data = safe_json_parse(coaching_text, "Coaching Agent")
    
    if not data or not any(data.get(key, []) for key in ["improvement_areas", "next_steps", "coaching_tips"]):
        # Provide meaningful fallback
        data = {
            "improvement_areas": [{
                "skill": "Next-Step Control",
                "issue_observed": "Follow-up specifics not explicitly confirmed",
                "behavior_change": "Always confirm next step owner and timeline",
                "practice_drill": "Practice explicit closes in next 3 mock calls",
                "ready_to_use_prompts": [
                    "Shall we schedule our next call for Thursday at 2pm?",
                    "What would success look like for our next conversation?"
                ]
            }],
            "next_steps": [{
                "owner": "rep",
                "action": "Send follow-up email with call summary",
                "due_by": "Within 24 hours",
                "success_criteria": "Email confirmation received"
            }],
            "coaching_tips": [{
                "skill": "Discovery",
                "tip": "Ask 3-5 open-ended questions early in each call"
            }]
        }
    
    return {"coaching": json.dumps(data, ensure_ascii=False)}

def parallel_processing_node(state: MultiAgentState) -> MultiAgentState:
    print("🚀 Starting parallel execution of all 3 agents...")
    with ThreadPoolExecutor(max_workers=3) as executor:
        f_sum = executor.submit(run_agent_with_timing, summary_agent_node, state, "Summary Agent")
        f_ana = executor.submit(run_agent_with_timing, analysis_agent_node, state, "Analysis Agent")
        f_coa = executor.submit(run_agent_with_timing, coaching_agent_node, state, "Coaching Agent")

        summary_result = f_sum.result()
        analysis_result = f_ana.result()
        coaching_result = f_coa.result()

    updated_state = {**state}
    updated_state.update(summary_result)
    updated_state.update(analysis_result)
    updated_state.update(coaching_result)
    return updated_state

def combine_results_node(state: MultiAgentState) -> MultiAgentState:
    """FRONTEND-COMPATIBLE result combination with proper key mapping"""
    analysis_data = safe_json_parse(state.get("analysis", "{}"), "Final Analysis")
    coaching_data = safe_json_parse(state.get("coaching", "{}"), "Final Coaching")

    # Extract and validate data
    metrics = analysis_data.get("metrics", {})
    strengths = analysis_data.get("strengths", [])
    areas_to_improve = analysis_data.get("areas_to_improve", [])
    objections = analysis_data.get("customer_objections", [])
    quotes = analysis_data.get("notable_quotes", [])
    
    # From coaching data - note the key mapping
    improvement_areas = coaching_data.get("improvement_areas", [])
    next_steps = coaching_data.get("next_steps", [])
    coaching_tips = coaching_data.get("coaching_tips", [])

    # Set final defaults for UI
    if not metrics.get("overall_sentiment"):
        metrics["overall_sentiment"] = "neutral"
        metrics["sentiment_rationale"] = "No explicit sentiment detected"
    
    metrics.setdefault("rep_talk_ratio_percent", 50)
    metrics.setdefault("customer_talk_ratio_percent", 50)
    metrics.setdefault("questions_asked_by_rep", 0)
    metrics.setdefault("objections_detected", len(objections))
    metrics.setdefault("followups_committed", len(next_steps))

    # Provide non-empty arrays for better UI display
    if not strengths:
        strengths = ["Call completed successfully", "Professional tone maintained"]
    if not areas_to_improve and not improvement_areas:
        areas_to_improve = ["Continue practicing discovery questions", "Work on closing techniques"]
    if not next_steps:
        next_steps = ["Follow up within 48 hours", "Send meeting summary"]
    if not coaching_tips:
        coaching_tips = [{"skill": "General", "tip": "Keep building rapport with prospects"}]

    # Map coaching improvement_areas to frontend's expected improvement_areas key
    if improvement_areas and not areas_to_improve:
        areas_to_improve = [area.get("behavior_change", "Improve communication") for area in improvement_areas if isinstance(area, dict)]

    final_result = {
        "summary": state.get("summary", "Call analysis completed"),
        "metrics": metrics,
        "strengths": strengths,
        "improvement_areas": areas_to_improve,  # This matches your frontend expectation
        "customer_objections": objections,
        "next_steps": next_steps,
        "coaching_tips": coaching_tips,
        "notable_quotes": quotes
    }

    return {"final_result": final_result}

# -------------------- Graph Building --------------------
def build_fast_multi_agent_graph():
    graph = StateGraph(state_schema=MultiAgentState)
    graph.add_node("parallel_processing", parallel_processing_node)
    graph.add_node("combine_results", combine_results_node)
    graph.add_edge(START, "parallel_processing")
    graph.add_edge("parallel_processing", "combine_results")
    graph.add_edge("combine_results", END)
    return graph.compile()

_fast_multi_agent_graph = None

def analyze_call_multi_agent_fast(context: str, transcript: str) -> Dict[str, Any]:
    """Entry point for multi-agent analysis - fully integrated with frontend"""
    global _fast_multi_agent_graph
    if _fast_multi_agent_graph is None:
        print("🔧 Building multi-agent graph...")
        _fast_multi_agent_graph = build_fast_multi_agent_graph()
        print("✅ Multi-agent graph ready")

    if len(transcript) > 5000:
        transcript = transcript[:5000] + "... [truncated]"

    initial_state: MultiAgentState = {
        "context": context or "",
        "transcript": transcript or "",
        "summary": "",
        "analysis": "",
        "coaching": "",
        "final_result": {}
    }

    print(f"🎯 Processing transcript ({len(transcript)} chars)...")
    start = time.time()
    try:
        result_state: MultiAgentState = _fast_multi_agent_graph.invoke(initial_state)
        total = time.time() - start
        out = result_state.get("final_result", {})
        out["processing_time"] = f"{total:.1f}s"
        out["agents_used"] = "Summary + Analysis + Coaching (parallel, frontend-integrated)"
        return out
    except Exception as e:
        print(f"❌ Multi-agent failure: {e}")
        return {
            "summary": f"Analysis failed: {str(e)}",
            "metrics": {
                "overall_sentiment": "neutral",
                "rep_talk_ratio_percent": 0,
                "customer_talk_ratio_percent": 0,
                "questions_asked_by_rep": 0,
                "objections_detected": 0,
                "followups_committed": 0
            },
            "strengths": ["System attempted analysis"],
            "improvement_areas": ["Technical issue encountered"],
            "customer_objections": [],
            "next_steps": ["Contact support"],
            "coaching_tips": [{"skill": "Technical", "tip": "Try again or contact support"}],
            "notable_quotes": [],
            "processing_time": "error",
            "agents_used": "Error fallback"
        }
