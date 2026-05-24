# Local AI Database Query Optimizer

Built by Team Edgerunners for AI Hackathon for Builders.

We built this tool because debugging slow database queries is a massive time sink, but pasting production database schemas into cloud AI providers (like ChatGPT or Claude) is a massive security risk. 

This project solves both problems. It's an AI agent that runs 100% locally on your own hardware, analyzes poorly written SQL, and outputs a comprehensive optimization report. It doesn't send a single byte of data to the cloud.

## What it does
* **Bottleneck Analysis:** Breaks down why a query is slow (e.g., catching implicit Cartesian products or missing indexes).
* **Query Refactoring:** Rewrites the raw SQL into an optimized format.
* **Indexing Strategy:** Generates the exact `CREATE INDEX` SQL statements needed to support the new query.
* **Impact Prediction:** Estimates the performance gains before you actually deploy the changes.

## The Stack
We wanted the stack to be as fast as the queries it optimizes.
* **Frontend:** Python via Streamlit (with custom CSS overrides for the UI).
* **AI Engine:** Ollama running locally.
* **Model:** `qwen3-coder-next` (specifically chosen for its deep understanding of SQL and execution plans).
* **Environment:** `uv` for lightning-fast dependency management.

## How to run it locally

You will need to have Ollama installed on your machine first to run the local models.

1. **Pull the model:**
```bash
   ollama pull qwen3-coder-next
```
2. **Clone the repository:**
```bash
git clone https://github.com/aquariusjr10/AI_SQL_Optimiser.git
cd local-sql-optimizer
```
3. **Run the app:**
```bash
uv run streamlit run app.py
```
The application will automatically open in your default browser at http://localhost:8501.


## Team Edgerunners
* Kanishka S
* Deepak Jeganathan
