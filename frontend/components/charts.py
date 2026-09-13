"""Plotly chart utilities for SlopeGuard Streamlit Dashboard."""


from typing import Any

import numpy as np
import plotly.express as px
import plotly.graph_objects as go


def create_gauge_chart(probability: float, risk_level: str) -> go.Figure:
    """Creates a gauge indicator chart showing landslide probability and risk tier."""
    # Color mapping for risk levels
    color_map = {
        "LOW": "#22C55E",
        "MEDIUM": "#EAB308",
        "HIGH": "#F97316",
        "CRITICAL": "#EF4444",
    }
    bar_color = color_map.get(risk_level, "#00F2FE")

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=round(probability * 100, 1),
            number={"suffix": "%", "font": {"size": 42, "color": "#F8FAFC", "family": "Outfit"}},
            title={
                "text": f"<b>Landslide Risk: {risk_level}</b>",
                "font": {"size": 18, "color": bar_color, "family": "Outfit"},
            },
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickwidth": 1,
                    "tickcolor": "#64748B",
                    "tickfont": {"color": "#94A3B8"},
                },
                "bar": {"color": bar_color, "thickness": 0.28},
                "bgcolor": "rgba(30, 41, 59, 0.5)",
                "borderwidth": 1,
                "bordercolor": "rgba(255, 255, 255, 0.1)",
                "steps": [
                    {"range": [0, 40], "color": "rgba(34, 197, 94, 0.15)"},
                    {"range": [40, 65], "color": "rgba(234, 179, 8, 0.15)"},
                    {"range": [65, 80], "color": "rgba(249, 115, 22, 0.15)"},
                    {"range": [80, 100], "color": "rgba(239, 68, 68, 0.2)"},
                ],
                "threshold": {
                    "line": {"color": "#EF4444", "width": 3},
                    "thickness": 0.8,
                    "value": 80,
                },
            },
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#F8FAFC", "family": "Outfit"},
        margin=dict(l=20, r=20, t=40, b=20),
        height=260,
    )
    return fig


def create_feature_importance_chart(manifest: dict[str, Any]) -> go.Figure:
    """Plots feature importances from model manifest."""
    importances = manifest.get("feature_importances", {})
    if not importances:
        # Fallback values from reviewed bundle
        importances = {
            "Elevation_m": 0.2378,
            "Slope_deg": 0.1736,
            "Soil_Sand_pct": 0.1639,
            "Soil_Clay_pct": 0.1308,
            "Rainfall_mm": 0.1094,
            "Rainfall_7day_antecedent_mm": 0.0996,
            "Rainfall_Event_ERA5_mm": 0.0601,
            "Aspect_deg": 0.0247,
        }

    sorted_features = sorted(importances.items(), key=lambda x: x[1], reverse=True)
    names = [x[0].replace("_", " ") for x in sorted_features]
    values = [round(x[1] * 100, 2) for x in sorted_features]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=names,
            orientation="h",
            marker=dict(
                color=values,
                colorscale="Blues",
                line=dict(color="rgba(255,255,255,0.2)", width=1),
            ),
            text=[f"{v:.1f}%" for v in values],
            textposition="auto",
        )
    )

    fig.update_layout(
        title={"text": "<b>Random Forest Feature Importances</b>", "font": {"size": 16}},
        xaxis_title="Importance Weight (%)",
        yaxis={"autorange": "reversed"},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#E2E8F0", "family": "Outfit"},
        margin=dict(l=20, r=20, t=40, b=20),
        height=320,
    )
    return fig


def create_confusion_matrix_chart(manifest: dict[str, Any]) -> go.Figure:
    """Plots the confusion matrix heatmap from model metrics."""
    metrics = manifest.get("metrics", {})
    cm = metrics.get("confusion_matrix", [[176, 39], [68, 61]])

    labels = ["No Landslide (0)", "Landslide (1)"]
    z = np.array(cm)

    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=labels,
            y=labels,
            colorscale="Viridis",
            text=z,
            texttemplate="%{text}",
            textfont={"size": 16, "color": "#FFFFFF"},
            colorbar={"title": "Samples"},
        )
    )

    fig.update_layout(
        title={"text": "<b>Test Holdout Confusion Matrix</b>", "font": {"size": 16}},
        xaxis_title="Predicted Class",
        yaxis_title="Ground Truth Label",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#E2E8F0", "family": "Outfit"},
        margin=dict(l=20, r=20, t=40, b=20),
        height=300,
    )
    return fig


def create_simulation_curve(
    client,
    cell: dict[str, Any],
    baseline_rainfall: float,
    multipliers: list[float] | None = None,
) -> go.Figure:
    """Computes and plots the risk curve across a range of rainfall multipliers."""
    if multipliers is None:
        multipliers = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]

    probs = []
    rainfalls = []
    for m in multipliers:
        res = client.simulate_rainfall(
            cell_code=cell["cell_code"],
            rainfall_multiplier=m,
            baseline_rainfall_mm=baseline_rainfall,
        )
        sim_rain = res.get("simulated_rainfall_mm", baseline_rainfall * m)
        pred = res.get("prediction", {})
        p = pred.get("probability", 0.0)
        rainfalls.append(sim_rain)
        probs.append(p * 100)

    fig = go.Figure()

    # Probability line
    fig.add_trace(
        go.Scatter(
            x=rainfalls,
            y=probs,
            mode="lines+markers",
            name="Model Probability (%)",
            line=dict(color="#00F2FE", width=3),
            marker=dict(size=8, color="#FFFFFF", line=dict(color="#0072FF", width=2)),
        )
    )

    # Threshold horizontal lines
    fig.add_hline(
        y=40,
        line_dash="dot",
        line_color="#EAB308",
        annotation_text="Medium (40%)",
        annotation_position="bottom right",
    )
    fig.add_hline(
        y=65,
        line_dash="dot",
        line_color="#F97316",
        annotation_text="High (65%)",
        annotation_position="bottom right",
    )
    fig.add_hline(
        y=80,
        line_dash="dot",
        line_color="#EF4444",
        annotation_text="Critical (80%)",
        annotation_position="bottom right",
    )

    fig.update_layout(
        title={
            "text": f"<b>Rainfall Surge Response Curve ({cell['cell_code']})</b>",
            "font": {"size": 16},
        },
        xaxis_title="Simulated Rainfall (mm)",
        yaxis_title="Landslide Probability (%)",
        yaxis_range=[0, 105],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#E2E8F0", "family": "Outfit"},
        margin=dict(l=20, r=20, t=40, b=20),
        height=320,
    )
    return fig
