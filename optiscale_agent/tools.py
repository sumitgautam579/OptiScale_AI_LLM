
from __future__ import annotations

import io
from typing import Dict, Any

import pandas as pd


def load_and_profile_costs(
    csv_text: str,
    cloud_provider: str = "aws",
    currency: str = "USD",
) -> Dict[str, Any]:
    """
    Parse and profile a cloud billing CSV.

    Args:
        csv_text: Full CSV contents as text, including header row.
                  The CSV should contain at least one column whose name contains "cost".
                  Common useful columns: service, product, project, account, environment, tags.
        cloud_provider: One of "aws", "gcp", "azure" or similar descriptor.
        currency: 3-letter currency code, e.g. "USD", "EUR", "INR".

    Returns:
        A dict with aggregated metrics for the LLM to reason over:
        {
          "currency": str,
          "cloud_provider": str,
          "row_count": int,
          "total_cost": float,
          "cost_column": str,
          "cost_by_service": {service: cost, ...},
          "cost_by_project": {project: cost, ...} or {},
          "detected_columns": [col1, col2, ...],
          "notes": str
        }

    The agent should use this tool whenever the user pastes or uploads
    raw billing data and asks for analysis.
    """
    if not csv_text.strip():
        raise ValueError("csv_text is empty. Provide billing CSV contents as text.")

    df = pd.read_csv(io.StringIO(csv_text))
    if df.empty:
        raise ValueError("Parsed CSV is empty. Check the input format.")

    # Normalize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    detected_columns = list(df.columns)

    # Find the first "cost" column
    cost_cols = [c for c in df.columns if "cost" in c]
    if not cost_cols:
        raise ValueError(
            "No cost column found. Expected a column containing 'cost' in its name."
        )
    cost_col = cost_cols[0]

    # Convert cost to numeric
    df[cost_col] = pd.to_numeric(df[cost_col], errors="coerce").fillna(0.0)

    total_cost = float(df[cost_col].sum())
    row_count = int(len(df))

    # Detect a service column
    service_cols = [c for c in df.columns if "service" in c or "product" in c]
    cost_by_service = {}
    if service_cols:
        svc_col = service_cols[0]
        cost_by_service = (
            df.groupby(svc_col)[cost_col]
            .sum()
            .sort_values(ascending=False)
            .round(2)
            .head(20)
            .to_dict()
        )

    # Detect a project/account column
    project_cols = [c for c in df.columns if "project" in c or "account" in c]
    cost_by_project = {}
    if project_cols:
        prj_col = project_cols[0]
        cost_by_project = (
            df.groupby(prj_col)[cost_col]
            .sum()
            .sort_values(ascending=False)
            .round(2)
            .head(20)
            .to_dict()
        )

    notes = (
        "Use this structured profile to explain top spend drivers, identify hotspots, "
        "and propose concrete optimization levers. Always clearly state assumptions."
    )

    return {
        "currency": currency,
        "cloud_provider": cloud_provider,
        "row_count": row_count,
        "total_cost": round(total_cost, 2),
        "cost_column": cost_col,
        "cost_by_service": cost_by_service,
        "cost_by_project": cost_by_project,
        "detected_columns": detected_columns,
        "notes": notes,
    }


def estimate_savings_from_actions(
    baseline_monthly_cost: float,
    expected_reduction_percent: float,
) -> Dict[str, Any]:
    """
    Estimate financial impact of a set of optimization actions.

    Args:
        baseline_monthly_cost: Current monthly cloud spend (e.g. 15000.0).
        expected_reduction_percent: Expected % reduction (e.g. 20.0 means 20%).

    Returns:
        {
          "baseline_monthly_cost": float,
          "expected_reduction_percent": float,
          "monthly_savings": float,
          "projected_annual_savings": float
        }

    The agent should:
      - Use this tool when it has a rough estimate of percentage savings.
      - Explain to the user that this is an estimate, not a precise forecast.
    """
    if baseline_monthly_cost < 0:
        raise ValueError("baseline_monthly_cost cannot be negative.")
    if expected_reduction_percent < 0:
        raise ValueError("expected_reduction_percent cannot be negative.")

    monthly_savings = baseline_monthly_cost * (expected_reduction_percent / 100.0)
    annual_savings = monthly_savings * 12.0

    return {
        "baseline_monthly_cost": round(baseline_monthly_cost, 2),
        "expected_reduction_percent": round(expected_reduction_percent, 2),
        "monthly_savings": round(monthly_savings, 2),
        "projected_annual_savings": round(annual_savings, 2),
    }


def compare_two_cost_scenarios(
    baseline_cost: float,
    scenario_a_cost: float,
    scenario_b_cost: float,
) -> Dict[str, Any]:
    """
    Compare baseline vs. two alternative cost scenarios.

    Args:
        baseline_cost: Cost of current state.
        scenario_a_cost: Cost of scenario A (e.g., rightsizing only).
        scenario_b_cost: Cost of scenario B (e.g., rightsizing + reservations).

    Returns:
        {
          "baseline_cost": float,
          "scenario_a_cost": float,
          "scenario_b_cost": float,
          "scenario_a_delta": float,
          "scenario_b_delta": float,
          "scenario_a_savings_percent": float,
          "scenario_b_savings_percent": float
        }

    The agent can use this to explain trade-offs between two proposed plans.
    """
    if baseline_cost <= 0:
        raise ValueError("baseline_cost must be > 0 for meaningful comparison.")

    def _calc(cost: float) -> Dict[str, float]:
        delta = baseline_cost - cost
        pct = (delta / baseline_cost) * 100.0
        return {
            "delta": round(delta, 2),
            "pct_savings": round(pct, 2),
        }

    a = _calc(scenario_a_cost)
    b = _calc(scenario_b_cost)

    return {
        "baseline_cost": round(baseline_cost, 2),
        "scenario_a_cost": round(scenario_a_cost, 2),
        "scenario_b_cost": round(scenario_b_cost, 2),
        "scenario_a_delta": a["delta"],
        "scenario_b_delta": b["delta"],
        "scenario_a_savings_percent": a["pct_savings"],
        "scenario_b_savings_percent": b["pct_savings"],
    }


def generate_exec_summary_outline(goal: str, audience: str = "cxo") -> Dict[str, Any]:
    """
    Generate a structured outline for an executive summary.

    Args:
        goal: Main objective of the communication, e.g.
              "Reduce AWS EC2 spend by 30% in 3 months without impacting SLAs."
        audience: Target persona, e.g. "cxo", "engineering", "finance".

    Returns:
        {
          "title": str,
          "audience": str,
          "sections": [
            {"heading": str, "bullets": [str, ...]},
            ...
          ]
        }

    The LLM should then expand this outline into full narrative text.
    """
    title = "Cloud Cost Optimization – Executive Summary"
    sections = [
        {
            "heading": "1. Context & Objectives",
            "bullets": [
                "Briefly describe current cloud cost baseline and growth trend.",
                f"State the primary goal: {goal}",
                "Clarify time horizon and acceptable risk/constraints.",
            ],
        },
        {
            "heading": "2. Key Cost Drivers",
            "bullets": [
                "Top 5 services/projects contributing to spend.",
                "Patterns by environment (prod, non-prod) and region.",
                "Any anomalous spikes or waste patterns detected.",
            ],
        },
        {
            "heading": "3. Recommended Optimization Levers",
            "bullets": [
                "Rightsizing and decommissioning opportunities.",
                "Commitment-based discounts (Savings Plans / CUDs / Reservations).",
                "Storage and data transfer optimizations.",
                "Governance and tagging improvements.",
            ],
        },
        {
            "heading": "4. Impact & Timeline",
            "bullets": [
                "Estimated monthly and annual savings (ranges).",
                "Phased rollout plan (Phase 1, 2, 3).",
                "Risks, dependencies, and owners.",
            ],
        },
        {
            "heading": "5. Next Steps",
            "bullets": [
                "Decision points required from leadership.",
                "Initial actions for engineering / platform teams.",
                "How success will be tracked and reported.",
            ],
        },
    ]

    return {
        "title": title,
        "audience": audience,
        "goal": goal,
        "sections": sections,
    }
