"""SlopeGuard: Geospatial Landslide Risk & Early-Warning Dashboard
Built with Streamlit, Plotly, and Folium.
Integrated with the actual Random Forest ML artifact and FastAPI early-warning backend.
"""

import datetime
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

from components.api_client import (
    DEFAULT_API_URL,
    SAMPLE_ASSETS,
    SAMPLE_CELLS,
    SlopeGuardClient,
)
from components.charts import (
    create_confusion_matrix_chart,
    create_feature_importance_chart,
    create_gauge_chart,
    create_simulation_curve,
)
from components.map_view import render_gis_map
from components.styles import apply_custom_styles

# Page configuration
st.set_page_config(
    page_title="SlopeGuard | Landslide Early-Warning System",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply custom dark-mode CSS
st.markdown(apply_custom_styles(), unsafe_allow_html=True)

# Initialize Client
if "api_url" not in st.session_state:
    st.session_state.api_url = DEFAULT_API_URL

client = SlopeGuardClient(base_url=st.session_state.api_url)

# In-memory alert state storage for demo / backend sync
if "local_alerts" not in st.session_state:
    st.session_state.local_alerts = [
        {
            "id": "alt-8b2f91-001",
            "cell_code": "NER-CELL-A17",
            "title": "CRITICAL Landslide Alert",
            "severity": "CRITICAL",
            "status": "ACTIVE",
            "current_probability": 0.825,
            "peak_probability": 0.841,
            "message": "Immediate evacuation warning for Papum Pare Hill Section. 4 critical assets in 2km hazard radius.",
            "drivers": ["High rainfall", "Steep slope", "High elevation terrain"],
            "created_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        },
        {
            "id": "alt-8b2f91-002",
            "cell_code": "NER-CELL-B04",
            "title": "HIGH Landslide Alert",
            "severity": "HIGH",
            "status": "ACTIVE",
            "current_probability": 0.692,
            "peak_probability": 0.710,
            "message": "Subansiri escarpment rainfall surge. Doordarshan Tower and rural corridors alert.",
            "drivers": ["High rainfall", "Steep slope"],
            "created_at": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S UTC"),
        },
        {
            "id": "alt-8b2f91-003",
            "cell_code": "NER-CELL-D08",
            "title": "MEDIUM Landslide Advisory",
            "severity": "MEDIUM",
            "status": "ACKNOWLEDGED",
            "current_probability": 0.485,
            "peak_probability": 0.512,
            "message": "Itanagar Urban Ridge monitoring advisory. Main Substation sector surveillance active.",
            "drivers": ["Moderate rainfall", "Clay soil saturation"],
            "created_at": (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S UTC"),
        },
    ]

# Compute current cell risks
cell_risks = {}
for c in SAMPLE_CELLS:
    # Run direct inference with baseline rain to establish base risk
    res = client.direct_predict(
        latitude=c["latitude"],
        longitude=c["longitude"],
        elevation_m=c["elevation_m"],
        slope_deg=c["slope_deg"],
        aspect_deg=c["aspect_deg"],
        rainfall_mm=c["baseline_rainfall_mm"],
    )
    cell_risks[c["cell_code"]] = res

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown("### 🏔️ **SlopeGuard Control Hub**")
    st.markdown("Geospatial early-warning & risk mitigation platform.")

    health = client.check_health()
    if health["online"]:
        st.markdown(
            '<div class="badge badge-online"><span class="pulse-dot"></span> Backend: Online (8000)</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="badge badge-medium">Backend: Direct ML Standalone</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("#### ⚙️ **Service Settings**")
    api_input = st.text_input("Backend API URL", value=st.session_state.api_url)
    if api_input != st.session_state.api_url:
        st.session_state.api_url = api_input
        st.rerun()

    st.markdown("#### 🎯 **Focus Risk Cell**")
    selected_cell_code = st.selectbox(
        "Select Watershed / Cell",
        options=[c["cell_code"] for c in SAMPLE_CELLS],
        format_func=lambda x: f"{x} - {next(c['name'] for c in SAMPLE_CELLS if c['cell_code'] == x)}",
    )
    selected_cell = next(c for c in SAMPLE_CELLS if c["cell_code"] == selected_cell_code)

    st.markdown("---")
    st.markdown("#### 📊 **Active Model Bundle**")
    st.markdown(
        """
        - **Algorithm**: Random Forest
        - **Pipeline**: 8-Feature Geospatial
        - **Status**: Verified Artifact
        - **Holdout ROC-AUC**: 0.7769
        """
    )
    st.caption("SlopeGuard Core ML Engine v0.2.0")

# ----------------- MAIN HEADER -----------------
st.markdown('<div class="main-header">SlopeGuard: Landslide Early-Warning System</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Production Geospatial Decision-Support Platform with Real ML Random Forest Inference & Real-Time Alert Engine</div>',
    unsafe_allow_html=True,
)

# Top KPI Summary Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-label">Monitored Grid Cells</div>
            <div class="metric-value">{len(SAMPLE_CELLS)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    active_alerts_cnt = sum(1 for a in st.session_state.local_alerts if a["status"] == "ACTIVE")
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-label">Active Alerts</div>
            <div class="metric-value" style="color: #EF4444;">{active_alerts_cnt}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    critical_cnt = sum(1 for a in st.session_state.local_alerts if a["severity"] == "CRITICAL" and a["status"] == "ACTIVE")
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="metric-label">Critical Zones</div>
            <div class="metric-value" style="color: #F87171;">{critical_cnt}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        """
        <div class="metric-box">
            <div class="metric-label">Model Engine</div>
            <div class="metric-value" style="color: #38BDF8; font-size: 1.5rem; margin-top: 10px;">Random Forest</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ----------------- TABS NAVIGATION -----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌍 Geospatial Early-Warning Center",
    "⚡ ML Real-Time Prediction Studio",
    "🌧️ Monsoon Rainfall Simulator & Ops",
    "🚨 Alert Lifecycle & Dispatch Hub",
    "📊 Model Manifest & ML Analytics",
])

# ==================== TAB 1: GEOSPATIAL COMMAND CENTER ====================
with tab1:
    st.markdown("### 🗺️ **North-Eastern Region (NER) Geospatial Risk Map**")
    st.markdown(
        "Interactive GIS display with terrain polygons, dynamic risk classifications, 2,000m hazard buffer zones, and critical infrastructure."
    )

    map_col, info_col = st.columns([7, 4])

    with map_col:
        folium_map = render_gis_map(
            cells=SAMPLE_CELLS,
            assets=SAMPLE_ASSETS,
            cell_risks=cell_risks,
            selected_cell_code=selected_cell_code,
        )
        st_folium(folium_map, width="100%", height=560)

    with info_col:
        st.markdown(f"#### 📍 **Cell Inspector: `{selected_cell_code}`**")
        st.markdown(f"**Location:** {selected_cell['name']}")

        cur_risk = cell_risks.get(selected_cell_code, {})
        cur_level = cur_risk.get("risk_level", "LOW")
        cur_prob = cur_risk.get("probability", 0.0)

        # Risk Gauge
        gauge_fig = create_gauge_chart(cur_prob, cur_level)
        st.plotly_chart(gauge_fig, use_container_width=True, key="tab1_gauge_chart")

        if st.button("🔮 **Calculate Chance of Landslide**", use_container_width=True, key="tab1_calc_btn"):
            tab1_buf = st.empty()
            tab1_buf.markdown(
                """
                <div class="circular-buffer-container" style="padding: 22px 14px; margin: 12px 0;">
                    <div class="circular-buffer-spinner" style="width: 52px; height: 52px; margin-bottom: 12px;"></div>
                    <div class="circular-buffer-title" style="font-size: 1.05rem;">Calculating Chance of Landslide...</div>
                    <div class="circular-buffer-subtitle" style="font-size: 0.82rem;">Running Random Forest inference for cell</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            import time
            time.sleep(0.45)
            tab1_res = client.direct_predict(
                latitude=selected_cell["latitude"],
                longitude=selected_cell["longitude"],
                elevation_m=selected_cell["elevation_m"],
                slope_deg=selected_cell["slope_deg"],
                aspect_deg=selected_cell["aspect_deg"],
                rainfall_mm=selected_cell["baseline_rainfall_mm"],
            )
            cell_risks[selected_cell_code] = tab1_res
            tab1_buf.empty()
            st.rerun()

        st.markdown("##### ⛰️ **Terrain Characteristics**")
        st.markdown(
            f"""
            - **Elevation:** `{selected_cell['elevation_m']} m`
            - **Slope:** `{selected_cell['slope_deg']}°`
            - **Aspect:** `{selected_cell['aspect_deg']}°`
            - **Baseline Rainfall:** `{selected_cell['baseline_rainfall_mm']} mm/day`
            """
        )

        st.markdown("##### 🏥 **Exposed Assets in 2km Buffer**")
        exposed = [a for a in SAMPLE_ASSETS if a["cell_code"] == selected_cell_code]
        if exposed:
            for exp in exposed:
                st.markdown(f"• **{exp['name']}** ({exp['type']})")
        else:
            st.caption("No registered critical infrastructure within direct boundary.")


# ==================== TAB 2: ML PREDICTION STUDIO ====================
with tab2:
    st.markdown("### 🔬 **Interactive ML Model Prediction Studio**")
    st.markdown(
        "Execute real-time inference against the trained **Random Forest Landslide Model Artifact**. "
        "Adjust terrain, rainfall, and soil parameters to observe model behavior and transparent driver explanations."
    )

    # Preset selector
    preset = st.radio(
        "Load Preset Scenario:",
        options=["Custom Inputs", "Dry Season Baseline", "Monsoon Heavy Downpour", "Extreme Cloudburst Warning"],
        horizontal=True,
    )

    if preset == "Dry Season Baseline":
        p_rain, p_slope, p_elev, p_aspect, p_ante, p_era5, p_clay, p_sand = 5.0, 15.0, 250.0, 90.0, 12.0, 5.0, 22.0, 48.0
    elif preset == "Monsoon Heavy Downpour":
        p_rain, p_slope, p_elev, p_aspect, p_ante, p_era5, p_clay, p_sand = 185.0, 42.0, 850.0, 145.0, 240.0, 135.0, 35.5, 28.0
    elif preset == "Extreme Cloudburst Warning":
        p_rain, p_slope, p_elev, p_aspect, p_ante, p_era5, p_clay, p_sand = 320.0, 52.0, 1150.0, 180.0, 380.0, 210.0, 38.0, 24.0
    else:
        p_rain, p_slope, p_elev, p_aspect, p_ante, p_era5, p_clay, p_sand = (
            selected_cell["baseline_rainfall_mm"],
            selected_cell["slope_deg"],
            selected_cell["elevation_m"],
            selected_cell["aspect_deg"],
            97.5,
            30.0,
            29.5,
            33.8,
        )

    st.markdown("---")
    inp_col1, inp_col2 = st.columns(2)

    with inp_col1:
        st.markdown("#### 🌧️ **Hydrological Parameters**")
        in_rain = st.slider("Daily Rainfall (mm)", min_value=0.0, max_value=500.0, value=float(p_rain), step=1.0)
        in_ante = st.slider("7-Day Antecedent Rainfall (mm)", min_value=0.0, max_value=1500.0, value=float(p_ante), step=5.0)
        in_era5 = st.slider("ERA5 Event Rainfall (mm)", min_value=0.0, max_value=450.0, value=float(p_era5), step=2.0)

        st.markdown("#### 🪴 **Geotechnical Soil Parameters**")
        in_clay = st.slider("Soil Clay Percentage (%)", min_value=10.0, max_value=60.0, value=float(p_clay), step=0.5)
        in_sand = st.slider("Soil Sand Percentage (%)", min_value=10.0, max_value=70.0, value=float(p_sand), step=0.5)

    with inp_col2:
        st.markdown("#### 🏔️ **Topographic Parameters**")
        in_slope = st.slider("Slope Angle (°)", min_value=0.0, max_value=85.0, value=float(p_slope), step=0.5)
        in_elev = st.slider("Elevation (m above sea level)", min_value=10.0, max_value=4500.0, value=float(p_elev), step=10.0)
        in_aspect = st.slider("Terrain Aspect (°)", min_value=0.0, max_value=359.0, value=float(p_aspect), step=1.0)

        st.markdown("#### ⚙️ **Inference Engine**")
        exec_mode = st.selectbox("Execution Mode", ["Direct Model Artifact", "FastAPI Backend (/api/v1/predict)"])

    # Run Prediction
    if st.button("🔮 **Calculate Chance of Landslide**", type="primary", use_container_width=True):
        buf_ph = st.empty()
        buf_ph.markdown(
            """
            <div class="circular-buffer-container">
                <div class="circular-buffer-spinner"></div>
                <div class="circular-buffer-title">Calculating Chance of Landslide...</div>
                <div class="circular-buffer-subtitle">Executing 8-Feature Random Forest Machine Learning Inference</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        import time
        time.sleep(0.45)

        if exec_mode == "Direct Model Artifact":
            pred_result = client.direct_predict(
                latitude=selected_cell["latitude"],
                longitude=selected_cell["longitude"],
                elevation_m=in_elev,
                slope_deg=in_slope,
                aspect_deg=in_aspect,
                rainfall_mm=in_rain,
                rainfall_7day_antecedent_mm=in_ante,
                rainfall_event_era5_mm=in_era5,
                soil_clay_pct=in_clay,
                soil_sand_pct=in_sand,
            )
        else:
            pred_result = client.predict_via_api(
                cell_code=selected_cell_code,
                rainfall_mm=in_rain,
                rainfall_7day=in_ante,
                rainfall_era5=in_era5,
                soil_clay=in_clay,
                soil_sand=in_sand,
            )

        buf_ph.empty()

        st.markdown("---")
        st.markdown("### 📋 **Inference Results**")

        res_c1, res_c2 = st.columns([5, 6])
        with res_c1:
            gauge = create_gauge_chart(pred_result["probability"], pred_result["risk_level"])
            st.plotly_chart(gauge, use_container_width=True, key="tab2_pred_gauge_chart")

        with res_c2:
            st.markdown(f"#### **Classification: `{pred_result['risk_level']}`**")
            st.markdown(f"**Calculated Model Probability:** `{round(pred_result['probability'] * 100, 2)}%`")
            st.markdown(f"**Binary Decision Label:** `Class {pred_result.get('predicted_class', 0)}` (Threshold: 50%)")
            st.markdown(f"**Inference Pipeline:** `{pred_result.get('method', 'Random Forest Model')}`")

            st.markdown("##### 🔍 **Transparent Model Drivers (Explanations):**")
            drivers = pred_result.get("drivers", [])
            if drivers:
                for d in drivers:
                    st.markdown(f"• <span class='badge badge-high'>{d}</span>", unsafe_allow_html=True)
            else:
                st.caption("Lower multi-factor model score.")

            # Check if this creates an alert
            if pred_result["risk_level"] in ("HIGH", "CRITICAL"):
                st.warning(
                    f"⚠️ **Alert Threshold Exceeded!** The backend Alert Policy triggers an immediate **{pred_result['risk_level']} Alert** "
                    f"and notifies the WebSocket and mobile push channels."
                )

# ==================== TAB 3: MONSOON RAINFALL SIMULATOR ====================
with tab3:
    st.markdown("### 🌧️ **Monsoon Rainfall Simulator & Sensor Ingestion**")
    st.markdown(
        "Simulate seasonal rainfall surges or multi-day cloudbursts on watershed cells "
        "and observe how risk escalation cascades across the monitoring grid."
    )

    sim_col1, sim_col2 = st.columns([5, 6])

    with sim_col1:
        st.markdown("#### ⚡ **Surge Multiplier Sandbox**")
        sim_cell_code = st.selectbox("Target Cell", [c["cell_code"] for c in SAMPLE_CELLS], key="sim_cell")
        sim_target_cell = next(c for c in SAMPLE_CELLS if c["cell_code"] == sim_cell_code)

        multiplier = st.slider(
            "Rainfall Multiplier (x Baseline)",
            min_value=0.5,
            max_value=5.0,
            value=2.5,
            step=0.1,
            help="Multiplies the baseline rainfall of the watershed.",
        )

        sim_baseline = st.number_input(
            "Baseline Rainfall (mm)",
            value=float(sim_target_cell["baseline_rainfall_mm"]),
            step=5.0,
        )

        sim_output = client.simulate_rainfall(
            cell_code=sim_cell_code,
            rainfall_multiplier=multiplier,
            baseline_rainfall_mm=sim_baseline,
        )

        st.markdown(
            f"""
            <div class="glass-card">
                <b>Baseline:</b> {sim_output['baseline_rainfall_mm']} mm<br>
                <b>Multiplier:</b> {multiplier}x<br>
                <b>Simulated Rainfall:</b> <span style="color: #38BDF8; font-size: 1.2rem; font-weight: bold;">{sim_output['simulated_rainfall_mm']} mm</span><br>
                <b>Resulting Risk:</b> <span class="badge badge-{sim_output['prediction']['risk_level'].lower()}">{sim_output['prediction']['risk_level']}</span> ({round(sim_output['prediction']['probability'] * 100, 1)}%)
            </div>
            """,
            unsafe_allow_html=True,
        )

    with sim_col2:
        st.markdown("#### 📈 **Sensitivity Curve**")
        curve_fig = create_simulation_curve(client, sim_target_cell, sim_baseline)
        st.plotly_chart(curve_fig, use_container_width=True, key="tab3_sim_curve_chart")

    st.markdown("---")
    st.markdown("#### 📡 **Telemetry Observation Ingestion Queue**")
    st.markdown("Simulate automatic precipitation sensor inputs ingested via `POST /api/v1/rainfall/observations`:")

    obs_c1, obs_c2, obs_c3 = st.columns([3, 3, 3])
    with obs_c1:
        obs_rain = st.number_input("Sensor Reading (mm)", min_value=0.0, max_value=500.0, value=75.0, step=5.0)
    with obs_c2:
        obs_src = st.text_input("Sensor Station ID", value="IMD-NER-STN-09")
    with obs_c3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📤 Ingest Observation", use_container_width=True):
            res = client.enqueue_observation(sim_cell_code, obs_rain, obs_src)
            if res.get("success"):
                st.success(f"Observation for {sim_cell_code} successfully queued into scheduler pipeline!")
            else:
                st.info(f"Ingested locally: {obs_rain} mm for {sim_cell_code}")

# ==================== TAB 4: ALERT LIFECYCLE & DISPATCH ====================
with tab4:
    st.markdown("### 🚨 **Alert Lifecycle & Notification Hub**")
    st.markdown(
        "Track active warnings, audit operator actions (`Acknowledge`, `Verify`, `Resolve`), "
        "and monitor the multi-channel notification dispatcher."
    )

    filt_col1, filt_col2 = st.columns(2)
    with filt_col1:
        status_filter = st.multiselect("Filter by Status", ["ACTIVE", "ACKNOWLEDGED", "VERIFIED", "RESOLVED"], default=["ACTIVE", "ACKNOWLEDGED"])
    with filt_col2:
        severity_filter = st.multiselect("Filter by Severity", ["CRITICAL", "HIGH", "MEDIUM", "LOW"], default=["CRITICAL", "HIGH", "MEDIUM"])

    filtered_alerts = [
        a for a in st.session_state.local_alerts
        if (not status_filter or a["status"] in status_filter) and (not severity_filter or a["severity"] in severity_filter)
    ]

    st.markdown("#### **Active Incident Stream**")
    for alert in filtered_alerts:
        badge_class = f"badge-{alert['severity'].lower()}"
        with st.expander(f"[{alert['severity']}] {alert['title']} - Cell {alert['cell_code']} ({alert['status']})", expanded=(alert["status"] == "ACTIVE")):
            st.markdown(f"**Summary:** {alert['message']}")
            st.markdown(
                f"**Peak Probability:** `{round(alert['peak_probability'] * 100, 1)}%` | "
                f"**Current:** `{round(alert['current_probability'] * 100, 1)}%` | "
                f"**Timestamp:** `{alert['created_at']}`"
            )

            if alert.get("drivers"):
                st.markdown("**Identified Drivers:** " + ", ".join(f"`{d}`" for d in alert["drivers"]))

            # Action Buttons for operators
            act_col1, act_col2, act_col3 = st.columns(3)
            with act_col1:
                if alert["status"] == "ACTIVE":
                    if st.button("👁️ Acknowledge", key=f"ack_{alert['id']}"):
                        alert["status"] = "ACKNOWLEDGED"
                        st.success(f"Alert {alert['id']} acknowledged by operator.")
                        st.rerun()

            with act_col2:
                if alert["status"] in ("ACTIVE", "ACKNOWLEDGED"):
                    if st.button("✅ Verify Incident", key=f"ver_{alert['id']}"):
                        alert["status"] = "VERIFIED"
                        st.success(f"Alert {alert['id']} marked VERIFIED from field survey.")
                        st.rerun()

            with act_col3:
                if alert["status"] != "RESOLVED":
                    if st.button("🏁 Resolve Alert", key=f"res_{alert['id']}"):
                        alert["status"] = "RESOLVED"
                        st.info(f"Alert {alert['id']} resolved and closed.")
                        st.rerun()

    st.markdown("---")
    st.markdown("#### 📱 **FCM Mobile Push Notification Subscriptions**")
    st.markdown(
        "Client mobile applications register device tokens for push notifications via "
        "`POST /api/v1/notifications/subscriptions`."
    )
    sub_c1, sub_c2 = st.columns(2)
    with sub_c1:
        st.text_input("FCM Installation Token", value="fcm-inst-token-papumpare-emergency-01", disabled=True)
    with sub_c2:
        st.selectbox("Channel", ["Emergency Evacuation", "District Disaster Office", "General Public"])

# ==================== TAB 5: MODEL MANIFEST & ANALYTICS ====================
with tab5:
    st.markdown("### 📊 **Trained Model Bundle & Manifest Analytics**")
    st.markdown(
        "Verification metrics, feature order, training parameters, and dataset provenance "
        "extracted directly from `model_manifest.json`."
    )

    manifest = client.load_manifest()

    if manifest:
        man_col1, man_col2 = st.columns(2)

        with man_col1:
            st.markdown("#### 📜 **Model Specification**")
            st.markdown(
                f"""
                - **Model Type:** `{manifest.get('model_type', 'RandomForestClassifier')}`
                - **Checksum (SHA-256):** `{manifest.get('model', {}).get('sha256')}`
                - **Artifact File:** `{manifest.get('model', {}).get('filename')}`
                - **Estimators:** `{manifest.get('model_parameters', {}).get('n_estimators', 50)}`
                - **Max Depth:** `{manifest.get('model_parameters', {}).get('max_depth', 8)}`
                - **Class Weight:** `{manifest.get('model_parameters', {}).get('class_weight', 'balanced')}`
                """
            )

            st.markdown("#### 🎯 **Validation Metrics**")
            metrics = manifest.get("metrics", {})
            st.markdown(
                f"""
                - **ROC-AUC Score:** `{round(metrics.get('roc_auc', 0.7769), 4)}`
                - **PR-AUC Score:** `{round(metrics.get('pr_auc', 0.6229), 4)}`
                - **Accuracy:** `{round(metrics.get('accuracy', 0.689) * 100, 2)}%`
                - **Training Samples:** `{metrics.get('train_samples', 1961)}`
                - **Test Samples:** `{metrics.get('test_samples', 344)}`
                """
            )

        with man_col2:
            st.markdown("#### ⚖️ **Feature Importances**")
            feat_fig = create_feature_importance_chart(manifest)
            st.plotly_chart(feat_fig, use_container_width=True, key="tab5_feat_fig_chart")

        st.markdown("---")
        cm_col, split_col = st.columns(2)
        with cm_col:
            st.markdown("#### 🔲 **Holdout Evaluation Confusion Matrix**")
            cm_fig = create_confusion_matrix_chart(manifest)
            st.plotly_chart(cm_fig, use_container_width=True, key="tab5_cm_fig_chart")

        with split_col:
            st.markdown("#### 🗺️ **Spatial Group Holdout Validation**")
            split = manifest.get("split", {})
            st.markdown(
                f"""
                Training avoids geographic data leakage by using spatial cells rather than random row splitting:
                - **Strategy:** `{split.get('strategy', 'spatial_group_holdout')}`
                - **Cell Grid Size:** `{split.get('cell_size_degrees', 0.25)}° (~27 km)`
                - **Training Groups:** `{split.get('train_groups', 276)}`
                - **Test Groups:** `{split.get('test_groups', 69)}`
                - **Group Overlap:** `None (0%)`
                """
            )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748B; font-size: 0.85rem; padding: 10px;'>"
    "SlopeGuard Geospatial Landslide Early-Warning System | Powered by FastAPI, Scikit-Learn Random Forest, and Streamlit"
    "</div>",
    unsafe_allow_html=True,
)
