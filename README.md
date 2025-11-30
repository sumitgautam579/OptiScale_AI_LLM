# OptiScale_AI_LLM

> OptiScale – Cloud Cost Optimization AI Agent built with Google's Agent Development Kit (ADK)

This project implements an **LLM-powered FinOps assistant** that helps teams:
- Ingest and profile their cloud cost data
- Identify top cost drivers
- Propose optimization levers (rightsizing, reservations, storage tiering, etc.)
- Estimate potential savings and impact
- Summarize everything in an executive-friendly format

The agent is implemented using **Google ADK** and exposes a single `root_agent` that orchestrates a set of deterministic tools.

---

## 1. High-level design

### 1.1 Problem

Cloud costs grow quickly and are often:
- Spread across many services (compute, storage, networking, managed services)
- Hard to interpret for non-FinOps stakeholders
- Missing a clear optimization roadmap (what to do next, where to start, who owns it)

We want an AI helper that can:
1. Take in cost data (CSV or summarized table).
2. Profile the spend by service, project/account, and tags.
3. Propose concrete optimization actions and rough savings.
4. Provide an executive summary that is easy to share with leadership.

### 1.2 Solution

We build a **single multi-tool LLM agent**:

- **Root agent: `root_agent`**
  - Model: `gemini-2.0-flash`
  - Role: primary interactive assistant (chat)
  - Tools:
    - `load_and_profile_costs` – parse CSV text and compute basic spend profile.
    - `estimate_savings_from_actions` – calculate savings for optimization ideas.
    - `compare_two_cost_scenarios` – compare baseline vs. optimized scenarios.
    - `generate_exec_summary_outline` – build an outline for stakeholder comms.

The LLM uses these tools to perform deterministic parts (math, aggregation), and then uses its own reasoning to explain and propose actions.

---

## 2. How to run locally

### 2.1 Prerequisites

- Python **3.10+**
- `pip` installed
- A **Gemini API key** from Google AI Studio

Docs: search “Python Quickstart for ADK” in Google’s Agent Development Kit docs.

### 2.2 Setup

From this project root:

```bash
# 1) Create virtual env
python -m venv .venv

# 2) Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# or Windows CMD
.venv\Scripts\activate.bat


# 3) Install dependencies
pip install -r requirements.txt
