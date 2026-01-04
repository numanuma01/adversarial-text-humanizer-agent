import streamlit as st
from graph import app as graph_app  # Import our compiled graph

st.set_page_config(page_title="GhostWriter", layout="wide")

st.title("Adversarial AI Humanizer")
st.markdown("This tool uses an **Agentic Loop** (Generator + Judge) to rewrite text until it evades AI detection.")

# Input Section
input_text = st.text_area("Paste AI-Generated Text Here:", height=200)
start_btn = st.button("Humanize Text")

if start_btn and input_text:
    with st.spinner("Agents are debating..."):
        # Initialize State
        initial_state = {
            "original_text": input_text,
            "current_text": input_text,
            "iteration_count": 0,
            "current_score": 1.0,
            "history": [],
            "feedback": ""
        }
        
        # Run the graph
        final_state = graph_app.invoke(initial_state)
        
        # Display Results
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original")
            st.info(final_state["original_text"])
            
        with col2:
            st.subheader("Humanized Result")
            st.success(final_state["current_text"])
            st.caption(f"Final AI Probability Score: {final_state['current_score']:.2f}")

        # Show the "Thinking Process"
        with st.expander("View Agent Iterations (Logs)"):
            for step in final_state['history']:
                st.markdown(f"**Iteration {step['iteration']}** (Score: {step['score']:.2f})")
                st.text(step['text'])
                st.divider()