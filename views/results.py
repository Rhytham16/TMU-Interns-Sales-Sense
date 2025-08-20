import streamlit as st

st.title("📊 Sales Call Analysis Results")

if 'analysis_results' in st.session_state and st.session_state.analysis_results:
    results = st.session_state.analysis_results

    # Debug section (remove in production)
    with st.expander("🔍 Debug Info", expanded=False):
        st.json(results)

    # Executive Summary Section
    st.markdown("## 📋 Executive Summary")
    summary = results.get("summary", "No summary available.")
    st.write(summary)

    # Metrics Section - FULLY COMPATIBLE with backend
    if "metrics" in results:
        metrics = results["metrics"]
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

    # Strengths Section
    st.markdown("## ✅ Strengths Identified")
    strengths = results.get("strengths", [])
    if strengths and isinstance(strengths, list) and len(strengths) > 0:
        # Filter out default messages
        meaningful_strengths = [s for s in strengths if s not in ["No specific strengths identified.", "Call completed successfully"]]
        if meaningful_strengths:
            for strength in meaningful_strengths:
                st.write(f"• {strength}")
        else:
            for strength in strengths[:2]:  # Show first 2 even if defaults
                st.write(f"• {strength}")
    else:
        st.write("No specific strengths identified.")

    # Areas for Improvement - MATCHES BACKEND KEY
    st.markdown("## 🎯 Areas for Improvement")
    areas = results.get("improvement_areas", [])  # This key matches backend output
    if areas and isinstance(areas, list) and len(areas) > 0:
        meaningful_areas = [a for a in areas if a not in ["No specific improvement areas identified.", "No specific areas for improvement."]]
        if meaningful_areas:
            for area in meaningful_areas:
                st.write(f"• {area}")
        else:
            for area in areas[:2]:  # Show defaults if that's all we have
                st.write(f"• {area}")
    else:
        st.write("No specific improvement areas identified.")

    # Customer Objections
    objections = results.get("customer_objections", [])
    if objections and len(objections) > 0:
        st.markdown("## 🚫 Customer Objections & Responses")
        for i, obj in enumerate(objections, 1):
            if isinstance(obj, dict):
                objection_title = obj.get('objection', 'Unknown')
                with st.expander(f"Objection {i}: {objection_title}"):
                    # Handle both possible quote keys
                    quote = obj.get('moment_quote', obj.get('moment', 'No quote available'))
                    response = obj.get('suggested_response', 'No suggestion available')
                    st.write(f"**Customer said:** \"{quote}\"")
                    st.write(f"**Suggested response:** {response}")
            else:
                st.write(f"• {obj}")

    # Next Steps
    st.markdown("## 🎯 Recommended Next Steps")
    next_steps = results.get("next_steps", [])
    if next_steps and len(next_steps) > 0:
        for step in next_steps:
            if isinstance(step, dict):
                owner = step.get('owner', '').title()
                action = step.get('action', step.get('step', 'No action specified'))
                due_by = step.get('due_by', '')
                success_criteria = step.get('success_criteria', '')
                
                if owner and due_by:
                    st.write(f"• **{owner}**: {action} (Due: {due_by})")
                elif action:
                    st.write(f"• {action}")
                else:
                    st.write(f"• {step}")
            else:
                st.write(f"• {step}")
    else:
        st.write("No specific next steps identified.")

    # Coaching Tips
    st.markdown("## 💡 Coaching Tips")
    tips = results.get("coaching_tips", [])
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

    # Notable Quotes
    quotes = results.get("notable_quotes", [])
    if quotes and len(quotes) > 0:
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

    # Processing Info
    if "processing_time" in results:
        st.caption(f"⏱️ Analysis completed in {results['processing_time']} using {results.get('agents_used', 'multi-agent system')}")

    # Action Buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        if st.button("🔄 Analyze Another Call", use_container_width=True):
            if 'analysis_results' in st.session_state:
                del st.session_state.analysis_results
            st.session_state.upload_ready = False
            st.switch_page("views/upload.py")

    with col2:
        if st.button("🏠 Go Home", use_container_width=True):
            st.switch_page("views/home.py")

    with col3:
        if st.button("📋 Export Results", use_container_width=True):
            st.balloons()
            st.success("Results formatted for export!")

else:
    st.info("📤 No analysis results found. Please upload a call and analyze it first.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📤 Go to Upload", type="primary", use_container_width=True):
            st.switch_page("views/upload.py")
    with col2:
        if st.button("🏠 Go Home", use_container_width=True):
            st.switch_page("views/home.py")
