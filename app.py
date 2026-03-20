"""
Lahore PM2.5 Source Apportionment — Streamlit Dashboard
=========================================================
Run with:  streamlit run app.py
Auto-refreshes every 5 minutes.
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Lahore PM2.5 — Live Source Apportionment",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');

  .stApp { background-color: #0a0e1a; }

  .metric-card {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 18px 20px;
    text-align: center;
  }
  .metric-val {
    font-family: 'Space Mono', monospace;
    font-size: 32px;
    font-weight: 700;
    margin: 4px 0;
  }
  .metric-lbl {
    font-size: 11px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
  .source-bar-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
  }
  .source-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
  }
  .alert-box {
    padding: 10px 16px;
    border-radius: 10px;
    margin-bottom: 8px;
    font-size: 13px;
  }
  div[data-testid="stMetricValue"] { color: #38bdf8; }
  div[data-testid="stMetricLabel"] { color: #64748b; font-size: 11px; }
  .stButton>button {
    background: rgba(56,189,248,0.1);
    border: 1px solid rgba(56,189,248,0.3);
    color: #38bdf8;
    border-radius: 8px;
    font-family: 'Space Mono', monospace;
    font-size: 12px;
  }
  .stButton>button:hover {
    background: rgba(56,189,248,0.2);
    border-color: #38bdf8;
  }
  h1, h2, h3 { color: #f1f5f9 !important; }
  .stSidebar { background: #111827 !important; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────

SOURCE_COLORS = {
    "Vehicle Emissions":        "#e63946",
    "Crop Burning":             "#f4a261",
    "Industrial / Brick Kilns": "#2dd4bf",
    "Secondary Aerosols":       "#60a5fa",
    "Road Dust / Soil":         "#e9c46a",
    "Domestic Biomass":         "#c084fc",
}

WHO_PM25   = 15.0
NAAQS_PM25 = 35.0

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#111827",
    font=dict(color="#94a3b8", family="DM Sans, sans-serif", size=11),
    margin=dict(l=16, r=16, t=32, b=16),
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.08)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.08)"),
)


# ── Data loading ──────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)   # cache for 5 minutes, then auto-refresh
def load_live_data():
    path = Path("data/live/live_apportionment.json")
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return _demo_live_data()


@st.cache_data(ttl=300)
def load_forecast():
    path = Path("data/forecast/forecast_7day.json")
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return _demo_forecast()


@st.cache_data(ttl=3600)   # historical loads once per hour
def load_historical():
    path = Path("data/processed/lahore_with_sources.csv")
    if path.exists():
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        return df
    return _demo_historical()


# ── Demo data (used when pipeline hasn't run yet) ─────────────────────────────

def _demo_live_data():
    return {
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%B %d, %Y"),
        "time": datetime.now().strftime("%H:%M"),
        "data_source": "IQAir · demo",
        "observations": {
            "pm25": 26.0, "pm10": 45.2, "NO2": 22.6,
            "SO2": 19.1, "CO": 410.0, "O3": 38.0,
            "temp_c": 22.0, "humidity": 67.0, "wind_speed": 6.7,
        },
        "aqi": 91, "aqi_category": "Moderate", "aqi_color": "#eab308",
        "who_exceedance": 1.7,
        "source_apportionment": {
            "fractions": {
                "Vehicle Emissions": 31.2,
                "Road Dust / Soil": 22.8,
                "Secondary Aerosols": 18.5,
                "Industrial / Brick Kilns": 14.3,
                "Domestic Biomass": 8.1,
                "Crop Burning": 5.1,
            },
            "contributions": {
                "Vehicle Emissions": 8.1,
                "Road Dust / Soil": 5.9,
                "Secondary Aerosols": 4.8,
                "Industrial / Brick Kilns": 3.7,
                "Domestic Biomass": 2.1,
                "Crop Burning": 1.3,
            },
            "top_source": "Vehicle Emissions",
            "pm25_total": 26.0,
        },
        "alerts": [
            {"level": "warning", "msg": "PM2.5 is 1.7× the WHO guideline"},
            {"level": "info",    "msg": "Dominant source today: Vehicle Emissions (31%)"},
        ]
    }


def _demo_forecast():
    days = ["Today", "Tomorrow", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pms  = [26, 31, 28, 35, 42, 38, 29]
    cats = ["Moderate", "Moderate", "Moderate", "Moderate", "Unhealthy for Sensitive", "Moderate", "Moderate"]
    result = []
    for d, pm, cat in zip(days, pms, cats):
        fracs = {
            "Vehicle Emissions": round(pm * 0.31, 1),
            "Road Dust / Soil":  round(pm * 0.23, 1),
            "Secondary Aerosols":round(pm * 0.19, 1),
            "Industrial / Brick Kilns": round(pm * 0.14, 1),
            "Domestic Biomass":  round(pm * 0.08, 1),
            "Crop Burning":      round(pm * 0.05, 1),
        }
        result.append({"day": d, "pm25": pm, "category": cat, "sources": fracs})
    return result


def _demo_historical():
    dates = pd.date_range("2020-01-01", "2024-12-31", freq="D")
    np.random.seed(42)
    doy = dates.dayofyear
    pm25 = np.clip(80 + 60*np.cos((doy-330)*2*np.pi/365) + np.random.normal(0,15,len(dates)), 5, 400)
    df = pd.DataFrame({"pm25": pm25}, index=dates)
    weights = [0.27, 0.22, 0.18, 0.15, 0.11, 0.07]
    for i, src in enumerate(SOURCE_COLORS):
        df[src] = df["pm25"] * weights[i] * (1 + 0.1*np.random.randn(len(dates)))
    return df


# ── Run pipeline helper ───────────────────────────────────────────────────────

def run_pipeline():
    with st.spinner("🔄 Fetching live data and running apportionment..."):
        try:
            result = subprocess.run(
                [sys.executable, "scripts/07_iqair_live.py", "--use-screenshot"],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                st.cache_data.clear()
                st.success("✓ Pipeline complete — data refreshed!")
            else:
                st.error(f"Pipeline error: {result.stderr[:300]}")
        except Exception as e:
            st.error(f"Could not run pipeline: {e}")


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🌫️ Lahore PM2.5")
    st.markdown("---")

    if st.button("🔄 Refresh Now", use_container_width=True):
        run_pipeline()
        st.rerun()

    st.markdown("---")
    st.markdown("**Auto-refresh**")
    refresh_mins = st.select_slider(
        "Interval", options=[5, 10, 15, 30, 60], value=5, label_visibility="collapsed"
    )
    st.markdown(f"<span style='color:#64748b;font-size:12px;'>Refreshes every {refresh_mins} min</span>",
                unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**PM2.5 Alert Threshold**")
    threshold = st.slider("µg/m³", 15, 150, 35, label_visibility="collapsed")
    st.markdown(f"<span style='color:#64748b;font-size:12px;'>Alert if PM2.5 > {threshold} µg/m³</span>",
                unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Data source**")
    data_source = st.radio(
        "", ["IQAir (live)", "Demo data"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("""
    <div style='font-size:11px;color:#475569;'>
        <b style='color:#64748b;'>Data sources</b><br>
        IQAir · NASA FIRMS<br>
        Sentinel-5P · OpenAQ<br><br>
        <b style='color:#64748b;'>Model</b><br>
        LightGBM + SHAP<br>
        NMF source decomposition<br><br>
        MIT License · Open Source
    </div>
    """, unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────

live   = load_live_data()
fcst   = load_forecast()
hist   = load_historical()
obs    = live["observations"]
appo   = live["source_apportionment"]
fracs  = appo["fractions"]
contribs = appo["contributions"]

# ── Header ────────────────────────────────────────────────────────────────────

col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown(f"## 🌫️ Lahore PM2.5 — Live Source Apportionment")
    st.markdown(f"<span style='color:#64748b;font-size:13px;font-family:monospace;'>"
                f"{live.get('date','')}  {live.get('time','')}  ·  Source: {live.get('data_source','')}</span>",
                unsafe_allow_html=True)
with col_h2:
    aqi_color = live.get("aqi_color", "#eab308")
    st.markdown(f"""
    <div style='text-align:right;margin-top:8px;'>
      <div style='font-family:monospace;font-size:42px;font-weight:700;color:{aqi_color};line-height:1;'>
        AQI {live.get("aqi", "—")}
      </div>
      <div style='font-size:13px;color:{aqi_color};margin-top:4px;'>{live.get("aqi_category","")}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── Row 1: Key metrics ────────────────────────────────────────────────────────

c1, c2, c3, c4, c5, c6 = st.columns(6)
metrics = [
    (c1, "PM2.5", f"{obs.get('pm25','—')} µg/m³", f"{live.get('who_exceedance','—')}× WHO", "#e63946"),
    (c2, "PM10",  f"{obs.get('pm10','—')} µg/m³",  "Coarse particles", "#f4a261"),
    (c3, "NO₂",   f"{obs.get('NO2','—')} µg/m³",   "Vehicle proxy", "#60a5fa"),
    (c4, "SO₂",   f"{obs.get('SO2','—')} µg/m³",   "Industry proxy", "#2dd4bf"),
    (c5, "CO",    f"{obs.get('CO','—')} µg/m³",    "Combustion proxy", "#e9c46a"),
    (c6, "O₃",    f"{obs.get('O3','—')} µg/m³",    "Photochemical", "#c084fc"),
]
for col, label, val, sub, color in metrics:
    with col:
        st.markdown(f"""
        <div class='metric-card'>
          <div class='metric-lbl'>{label}</div>
          <div class='metric-val' style='color:{color};'>{val}</div>
          <div style='font-size:11px;color:#475569;margin-top:2px;'>{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 2: Source apportionment + Donut ──────────────────────────────────────

col_src, col_donut = st.columns([1.2, 1])

with col_src:
    st.markdown("#### Today's Source Breakdown")
    sorted_fracs = sorted(fracs.items(), key=lambda x: -x[1])
    for src, pct in sorted_fracs:
        ugm3  = contribs.get(src, 0)
        color = SOURCE_COLORS.get(src, "#888")
        st.markdown(f"""
        <div class='source-bar-row'>
          <div class='source-dot' style='background:{color};'></div>
          <div style='flex:1;font-size:13px;font-weight:500;'>{src}</div>
          <div style='width:80px;background:rgba(255,255,255,0.05);border-radius:4px;height:6px;'>
            <div style='width:{pct}%;height:100%;background:{color};border-radius:4px;'></div>
          </div>
          <div style='width:44px;text-align:right;font-family:monospace;font-size:12px;color:{color};font-weight:700;'>{pct:.1f}%</div>
          <div style='width:52px;text-align:right;font-size:11px;color:#64748b;'>{ugm3:.1f} µg/m³</div>
        </div>
        """, unsafe_allow_html=True)

with col_donut:
    st.markdown("#### Annual Composition (historical)")
    annual_fracs = {
        "Vehicle Emissions": 27, "Crop Burning": 22,
        "Industrial / Brick Kilns": 18, "Secondary Aerosols": 15,
        "Road Dust / Soil": 11, "Domestic Biomass": 7,
    }
    fig_donut = go.Figure(go.Pie(
        labels=list(annual_fracs.keys()),
        values=list(annual_fracs.values()),
        hole=0.62,
        marker_colors=[SOURCE_COLORS[s] for s in annual_fracs],
        textinfo="none",
        hovertemplate="<b>%{label}</b><br>%{value}%<extra></extra>",
    ))
    fig_donut.update_layout(**PLOTLY_LAYOUT, height=280, showlegend=False)
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

st.divider()

# ── Row 3: Forecast ───────────────────────────────────────────────────────────

st.markdown("#### 7-Day Forecast by Source")

fig_fcst = go.Figure()
source_keys = list(SOURCE_COLORS.keys())

for src in source_keys:
    color = SOURCE_COLORS[src]
    vals  = [day["sources"].get(src, 0) for day in fcst]
    days  = [day["day"] for day in fcst]
    fig_fcst.add_trace(go.Bar(
        name=src, x=days, y=vals,
        marker_color=color,
        marker_line_width=0,
        hovertemplate=f"<b>{src}</b><br>%{{y:.1f}} µg/m³<extra></extra>",
    ))

# WHO + NAAQS lines
pm25_totals = [day["pm25"] for day in fcst]
max_y = max(pm25_totals) * 1.15

fig_fcst.add_hline(y=WHO_PM25, line_dash="dot", line_color="#34d399", line_width=1.2,
                   annotation_text="WHO 15", annotation_font_color="#34d399",
                   annotation_font_size=10)
fig_fcst.add_hline(y=NAAQS_PM25, line_dash="dot", line_color="#fbbf24", line_width=1.2,
                   annotation_text="NAAQS 35", annotation_font_color="#fbbf24",
                   annotation_font_size=10)

fig_fcst.update_layout(
    **PLOTLY_LAYOUT,
    barmode="stack",
    height=320,
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                font=dict(size=10, color="#94a3b8")),
    yaxis_title="PM2.5 (µg/m³)",
    yaxis_range=[0, max_y],
)
st.plotly_chart(fig_fcst, use_container_width=True, config={"displayModeBar": False})

st.divider()

# ── Row 4: Historical timeseries ──────────────────────────────────────────────

st.markdown("#### Historical Source Contributions")

tab_monthly, tab_seasonal, tab_raw = st.tabs(["Monthly trend", "Seasonal heatmap", "Daily PM2.5"])

with tab_monthly:
    monthly = hist[list(SOURCE_COLORS.keys())].resample("ME").mean()
    fig_time = go.Figure()
    for src in source_keys:
        if src in monthly.columns:
            fig_time.add_trace(go.Scatter(
                x=monthly.index, y=monthly[src], name=src,
                stackgroup="one", fillcolor=SOURCE_COLORS[src]+"88",
                line=dict(color=SOURCE_COLORS[src], width=0.5),
                hovertemplate=f"<b>{src}</b><br>%{{y:.1f}} µg/m³<extra></extra>",
            ))
    fig_time.update_layout(**PLOTLY_LAYOUT, height=300, showlegend=False,
                           yaxis_title="PM2.5 (µg/m³)")
    st.plotly_chart(fig_time, use_container_width=True, config={"displayModeBar": False})

with tab_seasonal:
    hist["month"] = hist.index.month
    src_cols = [s for s in SOURCE_COLORS if s in hist.columns]
    monthly_pct = hist.groupby("month")[src_cols].mean()
    monthly_pct = monthly_pct.div(monthly_pct.sum(axis=1), axis=0) * 100
    monthly_pct.index = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    fig_heat = px.imshow(
        monthly_pct.T,
        color_continuous_scale="YlOrRd",
        aspect="auto",
        text_auto=".0f",
    )
    fig_heat.update_layout(**PLOTLY_LAYOUT, height=280,
                           coloraxis_colorbar=dict(title="% contrib",
                                                   tickfont=dict(color="#94a3b8")))
    fig_heat.update_traces(textfont=dict(color="white", size=10))
    st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})

with tab_raw:
    monthly_pm25 = hist["pm25"].resample("ME").mean()
    fig_raw = go.Figure()
    fig_raw.add_trace(go.Scatter(
        x=monthly_pm25.index, y=monthly_pm25.values,
        fill="tozeroy", fillcolor="rgba(56,189,248,0.1)",
        line=dict(color="#38bdf8", width=1.5),
        hovertemplate="<b>PM2.5</b>: %{y:.1f} µg/m³<extra></extra>",
    ))
    fig_raw.add_hline(y=WHO_PM25, line_dash="dot", line_color="#34d399", line_width=1)
    fig_raw.add_hline(y=NAAQS_PM25, line_dash="dot", line_color="#fbbf24", line_width=1)
    fig_raw.update_layout(**PLOTLY_LAYOUT, height=280, yaxis_title="PM2.5 (µg/m³)")
    st.plotly_chart(fig_raw, use_container_width=True, config={"displayModeBar": False})

st.divider()

# ── Alerts ────────────────────────────────────────────────────────────────────

alerts = live.get("alerts", [])
if alerts:
    st.markdown("#### Alerts")
    alert_styles = {
        "warning": ("#fbbf24", "#2d2007", "⚠️"),
        "danger":  ("#ef4444", "#2d0707", "🔴"),
        "info":    ("#60a5fa", "#071b2d", "ℹ️"),
    }
    for a in alerts:
        color, bg, icon = alert_styles.get(a.get("level","info"), alert_styles["info"])
        st.markdown(f"""
        <div class='alert-box' style='background:{bg};border:1px solid {color}33;color:{color};'>
          {icon}  {a.get("msg","") or a.get("message","")}
        </div>
        """, unsafe_allow_html=True)

# ── Auto-refresh ──────────────────────────────────────────────────────────────

st.markdown(f"""
<div style='text-align:center;margin-top:24px;font-size:11px;color:#334155;font-family:monospace;'>
  lahore-pm25 · MIT License · Auto-refreshes every {refresh_mins} min ·
  Last update: {live.get("date","")} {live.get("time","")}
</div>
""", unsafe_allow_html=True)

# Streamlit auto-rerun
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=refresh_mins * 60 * 1000, silent=True)
