"""GIS Map Visualizer for Plan-A Streamlit Dashboard.
Renders interactive maps showing landslide risk cells and exposed infrastructure.
"""

from typing import Any

import folium
from folium import plugins


def render_gis_map(
    cells: list[dict[str, Any]],
    assets: list[dict[str, Any]],
    cell_risks: dict[str, dict[str, Any]] | None = None,
    selected_cell_code: str | None = None,
) -> folium.Map:
    """Builds a rich Folium GIS map with risk cells, buffers, and infrastructure."""
    if cell_risks is None:
        cell_risks = {}

    # Center around North-East India (Papum Pare, Arunachal Pradesh)
    center_lat = 27.18
    center_lon = 93.74

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    # Add alternate tile layer (satellite / topographic)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Esri Satellite",
    ).add_to(m)
    folium.TileLayer(
        tiles="OpenStreetMap",
        name="OpenStreetMap",
    ).add_to(m)

    # Color codes based on risk
    color_map = {
        "LOW": "#22C55E",
        "MEDIUM": "#EAB308",
        "HIGH": "#F97316",
        "CRITICAL": "#EF4444",
    }

    # Render risk cells
    for cell in cells:
        code = cell["cell_code"]
        risk_info = cell_risks.get(code, {})
        level = risk_info.get("risk_level", "LOW")
        prob = risk_info.get("probability", 0.15)
        color = color_map.get(level, "#3B82F6")

        is_selected = selected_cell_code == code
        weight = 4 if is_selected else 2
        fill_opacity = 0.55 if is_selected else 0.35

        popup_html = f"""
        <div style="font-family: Arial; font-size: 13px; color: #1E293B; width: 220px;">
            <h4 style="margin:0 0 6px 0; color: #0F172A;">{cell['name']} ({code})</h4>
            <b>Risk Level:</b> <span style="color: {color}; font-weight: bold;">{level}</span><br>
            <b>Probability:</b> {round(prob * 100, 1)}%<br>
            <b>Elevation:</b> {cell['elevation_m']} m<br>
            <b>Slope:</b> {cell['slope_deg']}°<br>
            <b>Aspect:</b> {cell['aspect_deg']}°<br>
            <b>Baseline Rain:</b> {cell['baseline_rainfall_mm']} mm/day
        </div>
        """

        folium.Polygon(
            locations=cell["polygon"],
            color=color,
            weight=weight,
            fill=True,
            fill_color=color,
            fill_opacity=fill_opacity,
            tooltip=f"{cell['name']} ({code}) - {level}",
            popup=folium.Popup(popup_html, max_width=250),
        ).add_to(m)

        # Center marker with pulse-like circle
        folium.CircleMarker(
            location=[cell["latitude"], cell["longitude"]],
            radius=6,
            color=color,
            fill=True,
            fill_color="#FFFFFF",
            fill_opacity=0.9,
            weight=2,
            tooltip=f"{code} Centroid",
        ).add_to(m)

        # If high or critical, draw exposure impact radius (2000m buffer)
        if level in ("HIGH", "CRITICAL") or is_selected:
            folium.Circle(
                location=[cell["latitude"], cell["longitude"]],
                radius=2000,
                color=color,
                weight=1,
                fill=True,
                fill_color=color,
                fill_opacity=0.1,
                dash_array="5, 5",
                tooltip=f"2km Exposure Buffer ({code})",
            ).add_to(m)

    # Render critical assets
    asset_icons = {
        "SCHOOL": ("graduation-cap", "blue"),
        "HOSPITAL": ("plus-square", "red"),
        "ROAD": ("road", "orange"),
        "BRIDGE": ("arrows-alt-h", "purple"),
        "POWER": ("bolt", "cadetblue"),
        "COMMUNICATION": ("signal", "darkgreen"),
    }

    for asset in assets:
        icon_name, icon_color = asset_icons.get(asset["type"], ("info-sign", "blue"))
        popup_asset = f"""
        <div style="font-family: Arial; font-size: 13px; color: #1E293B;">
            <b>{asset['name']}</b><br>
            <i>Type:</i> {asset['type']}<br>
            <i>Code:</i> {asset['asset_code']}<br>
            <i>Nearest Risk Cell:</i> {asset['cell_code']}
        </div>
        """
        folium.Marker(
            location=[asset["latitude"], asset["longitude"]],
            popup=folium.Popup(popup_asset, max_width=220),
            tooltip=f"{asset['type']}: {asset['name']}",
            icon=folium.Icon(icon=icon_name, prefix="fa", color=icon_color),
        ).add_to(m)

    folium.LayerControl(position="topright").add_to(m)
    plugins.Fullscreen().add_to(m)
    return m
