# backend/multi_agent_system.py

from dotenv import load_dotenv
load_dotenv(dotenv_path=r"backend\.env")

import os
import json
import time
import re
import logging
from typing import TypedDict, Dict, Any
from concurrent.futures import ThreadPoolExecutor

try:
    from langchain_openai import ChatOpenAI
    from langgraph.graph import StateGraph, START, END
    from langchain_core.prompts import ChatPromptTemplate
    print("✅ LangChain packages loaded successfully")
except ImportError as e:
    print(f"❌ LangChain import error: {e}")
    raise

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY in backend/.env")

class MultiAgentState(TypedDict):
    context: str
    transcript: str
    summary: str
    analysis: str
    coaching: str
    final_result: Dict[str, Any]

# ==================== BULLETPROOF JSON PARSING ====================
def safe_json_parse(text: str, agent_name: str = "Unknown") -> Dict[str, Any]:
    """Robust JSON parser that handles all fragment and error cases"""
    if not text or not text.strip():
        print(f"⚠️ {agent_name}: Empty response received")
        return {}
    
    s = text.strip()
    
    # Remove markdown code fences
    json_fence_start = '```json'
    json_fence_end = '```'
    
    if s.startswith(json_fence_start):
        s = s[len(json_fence_start):].lstrip()
    if s.endswith(json_fence_end):
        s = s[:-len(json_fence_end)].rstrip()
    
    # Try direct parse first
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        print(f"🔧 {agent_name}: Attempting to repair JSON fragment")
    
    # Repair partial JSON by wrapping in braces if needed
    if not (s.startswith('{') and s.endswith('}')):
        s = '{' + s + '}'
    
    # Remove trailing commas using raw string
    comma_pattern = r',\s*(?=[}\]])'
    s = re.sub(comma_pattern, '', s)
    
    # Balance braces and brackets
    open_braces = s.count('{')
    close_braces = s.count('}')
    open_brackets = s.count('[')
    close_brackets = s.count(']')
    
    if open_braces > close_braces:
        s += '}' * (open_braces - close_braces)
    elif close_braces > open_braces:
        s = '{' * (close_braces - open_braces) + s
        
    if open_brackets > close_brackets:
        s += ']' * (open_brackets - close_brackets)
    elif close_brackets > open_brackets:
        s = '[' * (close_brackets - open_brackets) + s

    # Final parse attempt
    try:
        result = json.loads(s)
        print(f"✅ {agent_name}: JSON successfully repaired")
        return result
    except json.JSONDecodeError as e:
        print(f"❌ {agent_name}: JSON repair failed - {e}")
        print(f"🔍 Fragment: {s[:100]}...")
        return {}

# ==================== LLM & PROMPTS ====================
def build_optimized_llm() -> ChatOpenAI:
    return ChatOpenAI(
        openai_api_key=OPENAI_API_KEY,
        model="gpt-3.5-turbo",
        temperature=0.2,
        max_tokens=800,
        timeout=45,
        streaming=False
    )

summary_prompt = ChatPromptTemplate.from_template("""
You are a senior sales call analyst. Produce a manager-ready executive summary.

CONTEXT:
{context}

TRANSCRIPT:
{transcript}

Write a single paragraph (8-10 sentences) covering:
- Call purpose & stage
- Customer situation and explicit pains/constraints/metrics (quote concrete values if present)
- Buying criteria that emerged (e.g., integrations, security, pricing band, decision process, timeline, stakeholders)
- Key rep behaviors (discovery depth, value framing, tailoring, objection handling)
- Outcome and specific next steps (owner + timeframe if present)

Rules:
- Use only transcript-grounded facts; do not invent details.
- Prefer concrete details over generic language.
- No bullet points. One tight paragraph.
""")

analysis_prompt = ChatPromptTemplate.from_template("""
Analyze this sales call and return ONLY valid JSON.

CONTEXT:
{context}

TRANSCRIPT:
{transcript}

Return exactly this JSON structure:
```json
{{
  "metrics": {{
    "overall_sentiment": "positive|neutral|negative",
    "sentiment_rationale": "evidence with quotes",
    "rep_talk_ratio_percent": 50,
    "customer_talk_ratio_percent": 50,
    "questions_asked_by_rep": 0,
    "objections_detected": 0,
    "followups_committed": 0
  }},
  "strengths": ["transcript-evidenced strengths"],
  "areas_to_improve": ["transcript-evidenced improvement areas"],
  "customer_objections": [
    {{
      "objection": "price|timing|integration|security|other",
      "moment_quote": "verbatim quote",
      "rep_response_quality": "good|adequate|weak",
      "suggested_response": "tailored response"
    }}
  ],
  "notable_quotes": [
    {{
      "speaker": "customer|rep",
      "quote": "verbatim line",
      "why_it_matters": "what it reveals"
    }}
  ]
}}
```

Constraints:
- Derive everything from transcript only.
- rep_talk_ratio_percent + customer_talk_ratio_percent MUST equal 100.
- Return JSON only.
""")

coaching_prompt = ChatPromptTemplate.from_template("""
You are a senior B2B sales coach. Provide coaching that the rep can apply in future calls.

CONTEXT:
{context}

SUMMARY:
{summary}

Return exactly this JSON structure:
```json
{{
  "improvement_areas": [
    {{
      "skill": "Discovery|Qualification|Value Framing|Objection Handling|Closing|Next-Step Control",
      "issue_observed": "transcript-grounded gap",
      "behavior_change": "precise behavior to adopt",
      "practice_drill": "practical exercise with pass criteria",
      "ready_to_use_prompts": ["context-aware question", "alternative"]
    }}
  ],
  "next_steps": [
    {{
      "owner": "rep|prospect|both",
      "action": "specific follow-up",
      "due_by": "timeframe",
      "success_criteria": "observable outcome"
    }}
  ],
  "coaching_tips": [
    {{
      "skill": "skill name",
      "tip": "high-leverage advice"
    }}
  ]
}}
```

Rules: Return JSON only. No surrounding text.
""")

# ==================== HARDENED AGENTS ====================
def run_agent_with_timing(agent_func, state, agent_name) -> Dict[str, str]:
    start = time.time()
    try:
        result = agent_func(state)
        print(f"✅ {agent_name}: {time.time() - start:.1f}s")
        return result
    except Exception as e:
        print(f"❌ {agent_name} failed: {e}")
        return {}

def summary_agent_node(state: MultiAgentState) -> Dict[str, str]:
    llm = build_optimized_llm()
    transcript = state.get("transcript", "")[:3000]
    response = llm.invoke(summary_prompt.format_messages(
        context=state.get("context", ""),
        transcript=transcript
    ))
    summary = getattr(response, 'content', "").strip()
    return {"summary": summary}

def analysis_agent_node(state: MultiAgentState) -> Dict[str, str]:
    llm = build_optimized_llm()
    transcript = state.get("transcript", "")[:3500]
    response = llm.invoke(analysis_prompt.format_messages(
        context=state.get("context", ""),
        transcript=transcript
    ))
    text = getattr(response, "content", "").strip()
    
    data = safe_json_parse(text, "Analysis Agent")
    
    # Guaranteed structure even if parse failed
    if not isinstance(data, dict):
        data = {}
    
    # Ensure required keys with defaults
    data.setdefault('metrics', {
        'overall_sentiment': 'neutral',
        'sentiment_rationale': 'No explicit sentiment detected',
        'rep_talk_ratio_percent': 50,
        'customer_talk_ratio_percent': 50,
        'questions_asked_by_rep': 0,
        'objections_detected': 0,
        'followups_committed': 0
    })
    data.setdefault('strengths', ["Call completed successfully", "Professional tone maintained"])
    data.setdefault('areas_to_improve', ["Continue practicing discovery questions", "Work on closing techniques"])
    data.setdefault('customer_objections', [])
    data.setdefault('notable_quotes', [])
    
    # Normalize talk ratios
    metrics = data['metrics']
    try:
        rep_ratio = int(metrics.get('rep_talk_ratio_percent', 50))
        cust_ratio = int(metrics.get('customer_talk_ratio_percent', 50))
        total = rep_ratio + cust_ratio
        if total != 100 and total > 0:
            metrics['rep_talk_ratio_percent'] = round(100 * rep_ratio / total)
            metrics['customer_talk_ratio_percent'] = 100 - metrics['rep_talk_ratio_percent']
    except:
        metrics['rep_talk_ratio_percent'] = 50
        metrics['customer_talk_ratio_percent'] = 50
    
    return {"analysis": json.dumps(data, ensure_ascii=False)}

def coaching_agent_node(state: MultiAgentState) -> Dict[str, str]:
    llm = build_optimized_llm()
    response = llm.invoke(coaching_prompt.format_messages(
        context=state.get("context", ""),
        summary=state.get("summary", "")
    ))
    text = getattr(response, "content", "").strip()
    
    data = safe_json_parse(text, "Coaching Agent")
    
    # Guaranteed structure even if parse failed
    if not isinstance(data, dict):
        data = {}
    
    # Ensure required keys with meaningful defaults
    data.setdefault('improvement_areas', [{
        'skill': 'Next-Step Control',
        'issue_observed': 'Follow-up specifics not explicitly confirmed',
        'behavior_change': 'Always confirm next step owner and timeline',
        'practice_drill': 'Practice explicit closes in mock calls',
        'ready_to_use_prompts': ['Shall we schedule our next call?', 'What would success look like?']
    }])
    data.setdefault('next_steps', [{
        'owner': 'rep',
        'action': 'Follow up with call summary',
        'due_by': 'Within 24 hours',
        'success_criteria': 'Email confirmation received'
    }])
    data.setdefault('coaching_tips', [{
        'skill': 'Discovery',
        'tip': 'Ask 3-5 open-ended questions early in each call'
    }])
    
    return {"coaching": json.dumps(data, ensure_ascii=False)}

# ==================== ORCHESTRATION ====================
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
    analysis_data = safe_json_parse(state.get("analysis", "{}"), "Final Analysis")
    coaching_data = safe_json_parse(state.get("coaching", "{}"), "Final Coaching")

    # Extract with safe defaults
    metrics = analysis_data.get("metrics", {})
    strengths = analysis_data.get("strengths", ["Call completed successfully"])
    areas_to_improve = analysis_data.get("areas_to_improve", ["Continue practicing discovery"])
    objections = analysis_data.get("customer_objections", [])
    quotes = analysis_data.get("notable_quotes", [])
    
    next_steps = coaching_data.get("next_steps", ["Follow up within 48 hours"])
    coaching_tips = coaching_data.get("coaching_tips", [{"skill": "General", "tip": "Keep building rapport"}])
    improvement_areas = coaching_data.get("improvement_areas", [])

    # Ensure metrics exist
    metrics.setdefault("overall_sentiment", "neutral")
    metrics.setdefault("rep_talk_ratio_percent", 50)
    metrics.setdefault("customer_talk_ratio_percent", 50)
    metrics.setdefault("questions_asked_by_rep", 0)
    metrics.setdefault("objections_detected", len(objections))
    metrics.setdefault("followups_committed", len(next_steps) if isinstance(next_steps, list) else 0)

    # Map coaching improvement_areas to frontend format if needed
    if improvement_areas and not areas_to_improve:
        areas_to_improve = [area.get("behavior_change", "Improve communication") for area in improvement_areas if isinstance(area, dict)]

    final_result = {
        "summary": state.get("summary", "Call analysis completed"),
        "metrics": metrics,
        "strengths": strengths,
        "improvement_areas": areas_to_improve,  # This matches your frontend
        "customer_objections": objections,
        "next_steps": next_steps,
        "coaching_tips": coaching_tips,
        "notable_quotes": quotes
    }
    return {"final_result": final_result}

# ==================== GRAPH SETUP ====================
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
    global _fast_multi_agent_graph
    if _fast_multi_agent_graph is None:
        print("🔧 Building multi-agent graph...")
        _fast_multi_agent_graph = build_fast_multi_agent_graph()
        print("✅ Multi-agent graph ready")

    if transcript and len(transcript) > 5000:
        transcript = transcript[:5000] + "... [truncated]"

    initial_state: MultiAgentState = {
        "context": context or "",
        "transcript": transcript or "",
        "summary": "",
        "analysis": "",
        "coaching": "",
        "final_result": {}
    }

    print(f"🎯 Processing transcript ({len(transcript or '')} chars)...")
    start = time.time()
    try:
        result_state: MultiAgentState = _fast_multi_agent_graph.invoke(initial_state)
        total = time.time() - start
        out = result_state.get("final_result", {})
        out["processing_time"] = f"{total:.1f}s"
        out["agents_used"] = "Summary + Analysis + Coaching (parallel, JSON-safe)"
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
