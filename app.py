import time

import ollama
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Local AI Database Optimizer", page_icon="⚡", layout="wide"
)

# --- CUSTOM CSS FOR GLASSMORPHISM & MATERIAL YOU ---
st.markdown(
    """
<style>
    /* 1. Animated Gradient Background for the main app */
    .stApp {
        background: linear-gradient(-45deg, #0f172a, #1e1b4b, #111827, #312e81);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 2. Make the header transparent so it doesn't clip the background */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* 3. Sidebar Glassmorphism */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.4) !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* 4. Text Area Material You Styling (Rounded, soft inner shadow) */
    .stTextArea textarea {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 24px !important;
        color: #e2e8f0 !important;
        padding: 20px !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
    }
    .stTextArea textarea:focus {
        border-color: #818cf8 !important;
        box-shadow: 0 0 0 2px rgba(129, 140, 248, 0.2) !important;
    }

    /* 5. Primary Button Material You Styling (Pill shape, glowing hover) */
    .stButton button {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 30px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6) !important;
        filter: brightness(1.1);
    }

    /* 6. Success/Info Banners Glassmorphism */
    div[data-testid="stAlert"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        color: #f8fafc !important;
    }

    /* 7. General Text Colors to pop against dark background */
    h1, h2, h3, h4, p, label {
        color: #f8fafc !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- HACKATHON HEADER ---
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 2rem; padding: 20px; background: rgba(255, 255, 255, 0.03); border-radius: 24px; border: 1px solid rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px);">
        <p style="color: #818cf8; font-size: 1.1rem; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 0;">
            🏆 AI Hackathon for Builders
        </p>
        <h1 style="font-size: 2.8rem; margin-top: 0.5rem; margin-bottom: 0.5rem; background: -webkit-linear-gradient(45deg, #a78bfa, #60a5fa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            AI-Powered Database Query Optimizer
        </h1>
        <p style="color: #cbd5e1; font-size: 1.1rem; margin-bottom: 0.5rem;">
            Built by <strong>Team Edgerunners </strong>
        </p>
        <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 0;">
             • Kanishka S
        </p>
        <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 0;">
             • Deepak Jeganathan
        </p>
    </div>
""",
    unsafe_allow_html=True,
)

# Sidebar Configuration
with st.sidebar:
    st.header("Configuration")
    model_choice = st.selectbox(
        "Local Model",
        ["qwen2.5-coder", "qwen3-coder", "qwen3-coder-next", "gpt-oss"],
        help="Make sure you have pulled the model locally using 'ollama pull <model-name>'",
    )

    st.write("---")
    st.markdown("###Quick Load Demo Queries")

    # Pre-baked bad queries
    examples = {
        "Select Example...": "",
        "1. Index-Killer (Functions in WHERE)": """SELECT order_id, customer_id, order_date \nFROM orders \nWHERE LOWER(status) = 'completed'\n  AND DATE(order_date) >= '2026-01-01'\n  AND customer_email LIKE '%@gmail.com';""",
        "2. Subquery Nightmare": """SELECT * \nFROM products p\nWHERE p.status = 'active'\n  AND (SELECT COUNT(*) FROM order_items oi WHERE oi.product_id = p.id) > 50\n  AND p.category_id IN (SELECT id FROM categories WHERE region_id = 4);""",
        "3. Implicit Cartesian Product": """SELECT u.username, p.title, c.comment_text\nFROM users u, posts p, comments c, likes l\nWHERE u.id = p.author_id\n  AND p.id = c.post_id\n  AND c.user_id = l.user_id\nORDER BY l.liked_at DESC LIMIT 100;""",
    }

    selected_example = st.selectbox(
        "Choose a terrible query to test:", list(examples.keys())
    )

# Set the query input based on the dropdown selection
initial_query = (
    examples[selected_example] if selected_example != "Select Example..." else ""
)

# Input Area
query_input = st.text_area(
    "Raw SQL Query",
    height=180,
    value=initial_query,
    placeholder="Paste your slow, unoptimized SQL query here...",
)

if st.button("Optimize Query", type="primary", use_container_width=True):
    if not query_input.strip():
        st.warning("Please enter a SQL query to optimize.")
    else:
        # Agent status updates
        st.toast("Agent connecting to database schema...")
        time.sleep(0.4)
        st.toast("Agent parsing execution plan...")
        time.sleep(0.4)

        with st.spinner(f"Analyzing via {model_choice}..."):
            system_prompt = """
            You are a senior database optimization agent. The user will provide a raw SQL query.
            Analyze the query and strictly provide the following sections:
            1. **Bottlenecks:** Identify exactly why this query is slow.
            2. **Optimized Query:** Rewrite the query for maximum performance. Provide it in a markdown SQL block.
            3. **Indexing Strategy:** What specific indexes should the engineering team create? Provide SQL CREATE INDEX statements.
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

            start_time = time.perf_counter()

            # Use columns to separate Before vs After visually if needed,
            # but we will stream the main report here cleanly.
            st.subheader("Optimization Report")

            # Store full response text to allow downloading later
            full_response = ""
            response_placeholder = st.empty()

            # Stream natively while capturing text
            for text_chunk in stream_ollama_response():
                full_response += text_chunk
                response_placeholder.markdown(full_response)

            end_time = time.perf_counter()
            execution_time = end_time - start_time

            st.success(
                f"Optimization generated in **{execution_time:.2f} seconds** running {model_choice} locally."
            )

            # Add Download Button for the report
            st.download_button(
                label="Download Optimization Report (.md)",
                data=full_response,
                file_name="sql_optimization_report.md",
                mime="text/markdown",
                use_container_width=True,
            )
