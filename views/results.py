import streamlit as st
import json

st.title("📊 Sales Call Analysis Results")

if 'analysis_results' in st.session_state and st.session_state.analysis_results:
    results = st.session_state.analysis_results

    # Debug section (optional)
    with st.expander("🔍 Debug Info", expanded=False):
        st.json(results)

    # Executive Summary Section
    st.markdown("## 📋 Executive Summary")
    summary = results.get("summary", "No summary available.")
    st.write(summary)

    # Cache Status Display
    if results.get("cached", False):
        st.success("⚡ **Cache Hit!** This analysis was retrieved instantly from cache - no processing required!")
    else:
        st.info("🔄 **Fresh Analysis** - This file was processed and cached for future use")

    # Processing Info
    if "processing_time" in results:
        cache_indicator = " (cached)" if results.get("cached", False) else ""
        agents_info = results.get('agents_used', 'multi-agent system')
        st.caption(f"⏱️ Analysis completed in {results['processing_time']}{cache_indicator} using {agents_info}")

    # --- Metrics Section ---
    metrics = results.get("metrics", {})
    if metrics:
        st.markdown("---")
        st.markdown("## 📈 Call Metrics")

        col1, col2, col3 = st.columns(3)
        with col1:
            sentiment = metrics.get("overall_sentiment", "Unknown").title()
            st.metric("Overall Sentiment", sentiment)
        with col2:
            rep_ratio = metrics.get("rep_talk_ratio_percent", 0)
            st.metric("Rep Talk Time", f"{rep_ratio}%")
        with col3:
            questions = metrics.get("questions_asked_by_rep", 0)
            st.metric("Questions Asked", questions)

        col4, col5 = st.columns(2)
        with col4:
            objections = metrics.get("objections_detected", 0)
            st.metric("Objections Detected", objections)
        with col5:
            followups = metrics.get("followups_committed", 0)
            st.metric("Follow-ups Committed", followups)
    else:
        st.warning("⚠️ Metrics data not available")

    # --- Strengths Identified ---
    strengths = results.get("strengths", [])
    st.markdown("---")
    st.markdown("## ✅ Strengths Identified")
    if strengths and isinstance(strengths, list) and len(strengths) > 0:
        for strength in strengths:
            st.write(f"• {strength}")
    else:
        st.write("No specific strengths identified.")

    # --- Areas for Improvement ---
    areas = results.get("improvement_areas", [])
    st.markdown("---")
    st.markdown("## 🎯 Areas for Improvement")
    if areas and isinstance(areas, list) and len(areas) > 0:
        for area in areas:
            st.write(f"• {area}")
    else:
        st.write("No specific improvement areas identified.")

    # --- Customer Objections ---
    objections = results.get("customer_objections", [])
    if objections and len(objections) > 0:
        st.markdown("---")
        st.markdown("## 🚫 Customer Objections & Responses")
        for i, obj in enumerate(objections, 1):
            if isinstance(obj, dict):
                objection_title = obj.get('objection', 'Unknown').title()
                with st.expander(f"Objection {i}: {objection_title}"):
                    quote = obj.get('moment_quote', obj.get('moment', 'No quote available'))
                    response = obj.get('suggested_response', 'No suggestion available')
                    st.write(f"**Customer said:** \"{quote}\"")
                    st.write(f"**Suggested response:** {response}")
            else:
                st.write(f"• {obj}")

    # --- Recommended Next Steps ---
    next_steps = results.get("next_steps", [])
    st.markdown("---")
    st.markdown("## 🎯 Recommended Next Steps")
    if next_steps and len(next_steps) > 0:
        for step in next_steps:
            if isinstance(step, dict):
                owner = step.get('owner', '').title()
                action = step.get('action', step.get('step', 'No action specified'))
                due_by = step.get('due_by', '')
                
                if owner and action and due_by:
                    st.write(f"• **{owner}**: {action} (Due: {due_by})")
                elif action:
                    st.write(f"• {action}")
                else:
                    st.write(f"• {step}")
            else:
                st.write(f"• {step}")
    else:
        st.write("No specific next steps identified.")

    # --- Coaching Tips ---
    tips = results.get("coaching_tips", [])
    st.markdown("---")
    st.markdown("## 💡 Coaching Tips")
    if tips and len(tips) > 0:
        for tip in tips:
            if isinstance(tip, dict):
                skill = tip.get('skill', 'General')
                advice = tip.get('tip', 'No advice available')
                st.write(f"**{skill}:** {advice}")
            else:
                st.write(f"• {tip}")
    else:
        st.write("No coaching tips available.")

    # --- Notable Quotes ---
    quotes = results.get("notable_quotes", [])
    if quotes and len(quotes) > 0:
        st.markdown("---")
        st.markdown("## 💬 Notable Quotes")
        for quote in quotes:
            if isinstance(quote, dict):
                speaker = quote.get('speaker', 'Unknown').title()
                text = quote.get('quote', quote.get('text', ''))
                why_matters = quote.get('why_it_matters', '')
                if text:
                    st.write(f"> **{speaker}:** \"{text}\"")
                    if why_matters:
                        st.caption(f"*{why_matters}*")
            else:
                st.write(f"> \"{quote}\"")

    # --- Action Buttons ---
    st.markdown("---")
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("🔄 Analyze Another Call", type="secondary", use_container_width=True):
            if 'analysis_results' in st.session_state:
                del st.session_state.analysis_results
            st.switch_page("views/upload.py")

    with col2:
        if st.button("🏠 Go Home", type="secondary", use_container_width=True):
            st.switch_page("views/home.py")

else:
    st.info("📤 No analysis results found. Please upload a call and analyze it first.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📤 Go to Upload", type="primary", use_container_width=True):
            st.switch_page("views/upload.py")
    with col2:
        if st.button("🏠 Go Home", use_container_width=True):
            st.switch_page("views/home.py")
