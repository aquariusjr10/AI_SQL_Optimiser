import time

import ollama
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Local AI Database Optimizer", page_icon="⚡", layout="centered"
)

st.title("Local AI Database Query Optimizer")
st.markdown("Running entirely on my local hardware via Ollama. Zero cloud APIs used.")

# Model Selection
model_choice = st.selectbox(
    "Choose your Local Model",
    ["qwen2.5-coder", "qwen3-coder", "qwen3-coder-next", "gpt-oss"],
)

# Input Area
query_input = st.text_area(
    "Raw SQL Query",
    height=200,
    placeholder="SELECT * FROM users u JOIN orders o ON u.id = o.user_id WHERE u.status = 'active'...",
)

if st.button("Optimize Query", type="primary", use_container_width=True):
    if not query_input.strip():
        st.warning("Please enter a SQL query to optimize.")
    else:
        with st.spinner(f"Analyzing via {model_choice}..."):
            # System prompt guiding the AI's behavior
            system_prompt = """
            You are a senior database optimization agent. The user will provide a raw SQL query.
            Analyze the query and strictly provide the following sections:
            1. **Bottlenecks:** Identify exactly why this query is slow.
            2. **Optimized Query:** Rewrite the query for maximum performance. Provide it in a markdown SQL block.
            3. **Indexing Strategy:** What specific indexes should the engineering team create?
            4. **Predicted Performance Impact:** Provide a concrete, estimated prediction of the impact.

            Keep the output concise, highly technical, and formatted beautifully in Markdown.
            """

            def stream_ollama_response():
                try:
                    stream = ollama.chat(
                        model=model_choice,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": query_input},
                        ],
                        stream=True,
                    )
                    for chunk in stream:
                        yield chunk["message"]["content"]
                except Exception as e:
                    yield f"\n\n**Error connecting to Ollama:** {e}"

            # 1. Start the timer
            start_time = time.perf_counter()

            st.subheader("Optimization Report")
            with st.container(border=True):
                # This function blocks until the stream is completely finished
                st.write_stream(stream_ollama_response())

            # 2. Stop the timer
            end_time = time.perf_counter()
            execution_time = end_time - start_time

            # 3. Display the result in a  banner
            st.success(
                f"Optimization generated in **{execution_time:.2f} seconds** running {model_choice} locally."
            )
