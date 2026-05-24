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
            system_prompt = """
            You are a senior database administrator. The user will provide a raw SQL query.
            Analyze the query and provide:
            1. **Bottlenecks:** Why is this query slow? (e.g., missing indexes, Cartesian products, full table scans).
            2. **Optimized Query:** Rewrite the query for maximum performance. Provide it in a markdown SQL block.
            3. **Indexing Strategy:** What indexes should the team create to support this new query?

            Keep the output concise, highly technical, and formatted beautifully in Markdown.
            """

            # Define a generator function to yield streaming chunks from Ollama natively
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
                        # Yield the text chunk to Streamlit
                        yield chunk["message"]["content"]
                except Exception as e:
                    yield f"\n\n**Error connecting to Ollama:** {e}\n\nMake sure Ollama is running and you have downloaded `{model_choice}`."

            # Render the streaming output directly into a visually distinct container
            st.subheader("Optimization Report")
            with st.container(border=True):
                st.write_stream(stream_ollama_response())
