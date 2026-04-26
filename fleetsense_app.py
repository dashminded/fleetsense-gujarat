"""
FleetSense Gujarat — Streamlit App
Bus Fleet Demand Forecasting for Gujarat Private Bus Operators

Run: streamlit run fleetsense_app.py
Requirements: pip install streamlit pandas plotly prophet
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import warnings
warnings.filterwarnings('ignore')

# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="FleetSense Gujarat — Fleet Demand Forecasting",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS (SmartPolicy style, adapted for blue-orange transport theme) ──
st.markdown("""
<style>
    .block-container { padding-top: 2rem !important; padding-bottom: 0.5rem !important; }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f4f7fb 0%, #ffffff 100%);
        border-right: 1px solid #d6e4f7;
    }
    section[data-testid="stSidebar"] > div { padding-top: 2.5rem !important; }
    section[data-testid="stSidebar"] h2 {
        color: #1a4f8a !important;
        font-weight: 700 !important;
        font-size: 22px !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p { color: #4a6a8a; }
    section[data-testid="stSidebar"] hr {
        margin: 0.8rem 0; border: none; height: 2px;
        background: linear-gradient(90deg, #1a6db5 0%, transparent 100%);
    }
    section[data-testid="stSidebar"] .stMarkdown strong {
        color: #1a4f8a; font-size: 12px;
        text-transform: uppercase; letter-spacing: 0.5px;
    }

    /* ── KPI result box ── */
    .result-box {
        background: linear-gradient(135deg, #1a4f8a 0%, #1a6db5 100%);
        padding: 20px 24px; border-radius: 12px;
        color: white; text-align: center;
        box-shadow: 0 4px 12px rgba(26, 79, 138, 0.2);
    }
    .result-label {
        font-size: 11px; opacity: 0.85;
        letter-spacing: 1px; text-transform: uppercase; margin-bottom: 4px;
    }
    .result-amount { font-size: 38px; font-weight: 700; letter-spacing: -1px; }
    .result-sub    { font-size: 13px; opacity: 0.75; margin-top: 4px; }

    /* ── Alert boxes ── */
    .alert-red {
        background: linear-gradient(135deg, #c0392b 0%, #e74c3c 100%);
        padding: 16px 20px; border-radius: 10px; color: white;
        box-shadow: 0 3px 10px rgba(192, 57, 43, 0.2);
    }
    .alert-green {
        background: linear-gradient(135deg, #1e8449 0%, #27ae60 100%);
        padding: 16px 20px; border-radius: 10px; color: white;
        box-shadow: 0 3px 10px rgba(30, 132, 73, 0.2);
    }
    .alert-orange {
        background: linear-gradient(135deg, #d35400 0%, #e67e22 100%);
        padding: 16px 20px; border-radius: 10px; color: white;
        box-shadow: 0 3px 10px rgba(211, 84, 0, 0.2);
    }
    .alert-blue {
        background: linear-gradient(135deg, #1a4f8a 0%, #1a6db5 100%);
        padding: 16px 20px; border-radius: 10px; color: white;
        box-shadow: 0 3px 10px rgba(26, 79, 138, 0.2);
    }
    .alert-label  { font-size: 11px; opacity: 0.85; letter-spacing: 1px; text-transform: uppercase; }
    .alert-value  { font-size: 28px; font-weight: 700; }
    .alert-detail { font-size: 12px; opacity: 0.8; margin-top: 2px; }

    /* ── Section header ── */
    .section-header {
        font-size: 13px; font-weight: 600;
        color: #1a4f8a; margin: 12px 0 6px 0;
        padding: 6px 10px; border-left: 3px solid #1a6db5;
        background: linear-gradient(90deg, rgba(26,109,181,0.07) 0%, transparent 100%);
        border-radius: 0 6px 6px 0;
    }

    /* ── Info box ── */
    .info-box {
        background: #eef4fb; border-left: 4px solid #1a6db5;
        padding: 14px 16px; border-radius: 8px; margin: 12px 0;
    }
    .info-box h4 { color: #1a4f8a; margin-top: 0; font-size: 14px; }

    /* ── Festival tag ── */
    .fest-tag {
        display: inline-block;
        background: #fff3cd; color: #856404;
        border: 1px solid #ffc107;
        padding: 3px 10px; border-radius: 20px;
        font-size: 12px; font-weight: 600;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0; padding: 10px 20px;
        background-color: #f0f4f9; color: #555;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1a4f8a 0%, #1a6db5 100%);
        color: white !important;
    }

    /* ── Buttons ── */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1a4f8a 0%, #1a6db5 100%);
        border: none; border-radius: 8px; font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(26, 109, 181, 0.25);
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(26, 109, 181, 0.35);
    }

    /* ── Download buttons ── */
    .stDownloadButton > button {
        border-radius: 8px; transition: all 0.3s ease;
        border: 1.5px solid #d6e4f7;
    }
    .stDownloadButton > button:hover {
        background-color: #eef4fb !important;
        border-color: #1a6db5 !important; color: #1a4f8a !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(26, 109, 181, 0.2);
    }

    div[data-testid="stNumberInput"] { margin-bottom: -4px; }
    div[data-testid="stSelectbox"]   { margin-bottom: -4px; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  DATA LOADING
# ══════════════════════════════════════════════════════════════

@st.cache_data
def load_data():
    """Load all 4 CSVs. Update DATA_PATH to your folder."""
    # DATA_PATH = "E:/New Projects/Fleet Management/"   # ← update if needed
    import os
    import pandas as pd

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_PATH = os.path.join(BASE_DIR, "data")

    df = pd.read_csv(os.path.join(DATA_PATH, "daily_bookings.csv"), parse_dates=["date"])
    routes   = pd.read_csv(os.path.join(DATA_PATH + "routes.csv"))
    buses    = pd.read_csv(os.path.join(DATA_PATH + "bus_inventory.csv"))
    festivals= pd.read_csv(os.path.join(DATA_PATH + "festivals.csv"))

    # Try loading forecast if it exists (generated from Jupyter notebook)
    try:
        forecast = pd.read_csv(DATA_PATH + "fleet_forecast_90days.csv",
                               parse_dates=["forecast_date"])
    except FileNotFoundError:
        forecast = None

    return df, routes, buses, festivals, forecast

df, routes_df, buses_df, festivals_df, forecast_df = load_data()


# ══════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════

ROUTE_NAMES   = sorted(df["route_name"].unique().tolist())
ROUTE_TIER    = df.drop_duplicates("route_name").set_index("route_name")["route_tier"].to_dict()
ROUTE_DIST    = df.drop_duplicates("route_name").set_index("route_name")["distance_km"].to_dict()
BASE_BUSES    = routes_df.set_index("route_name")["base_buses_per_day"].to_dict()
BASE_PRICE    = routes_df.set_index("route_name")["base_nonac_price_inr"].to_dict()

GUJARAT_FESTIVALS_2025 = {
    date(2025, 1, 14): "Uttarayan",
    date(2025, 3, 14): "Holi",
    date(2025, 3, 30): "Eid al-Fitr",
    date(2025, 4, 6):  "Ram Navami",
    date(2025, 5, 1):  "Gujarat Sthapana Divas",
    date(2025, 8, 15): "Independence Day",
    date(2025, 8, 16): "Janmashtami",
    date(2025, 9, 25): "Navratri Start",
    date(2025, 9, 26): "Navratri",
    date(2025, 9, 27): "Navratri",
    date(2025, 9, 28): "Navratri",
    date(2025, 9, 29): "Navratri",
    date(2025, 9, 30): "Navratri",
    date(2025, 10, 1): "Navratri",
    date(2025, 10, 2): "Navratri",
    date(2025, 10, 3): "Navratri",
    date(2025, 10, 4): "Navratri End",
    date(2025, 10, 20):"Diwali",
    date(2025, 10, 21):"Gujarati New Year",
    date(2025, 10, 22):"Diwali Holiday",
    date(2025, 12, 25):"Christmas",
    date(2025, 12, 31):"New Year Eve",
}

def get_festival(d):
    """Check if a date is a festival day."""
    for fd, fname in GUJARAT_FESTIVALS_2025.items():
        if abs((d - fd).days) <= 1:
            return fname
    return None

def predict_occupancy(route, selected_date):
    """
    Rule-based occupancy predictor using historical patterns.
    Falls back to this when Prophet forecast CSV is not available.
    """
    dow    = selected_date.weekday()   # 0=Mon, 6=Sun
    month  = selected_date.month
    fest   = get_festival(selected_date)

    # Base occupancy from historical data
    route_hist = df[df["route_name"] == route]
    base_occ   = route_hist["occupancy_rate"].mean()

    # Day-of-week multiplier
    dow_mult = {0:0.83, 1:0.80, 2:0.86, 3:0.90, 4:1.05, 5:1.32, 6:1.28}[dow]

    # Season multiplier
    season_mult = {1:1.10, 2:1.05, 3:1.08, 4:1.05, 5:1.20, 6:1.25,
                   7:0.88, 8:0.90, 9:0.93, 10:1.30, 11:1.25, 12:1.15}[month]

    # Festival multiplier
    fest_mult = 1.85 if fest and "Navratri" in fest else \
                1.95 if fest and "Diwali"   in fest else \
                1.85 if fest and "Uttarayan" in fest else \
                1.60 if fest else 1.0

    raw_occ = base_occ * dow_mult * season_mult * fest_mult
    return float(np.clip(raw_occ, 0.10, 1.0)), fest

def recommend_buses(occ_rate, base_buses):
    if occ_rate >= 0.92:
        return "Add 2 Buses", base_buses + 2, "alert-red"
    elif occ_rate >= 0.80:
        return "Add 1 Bus",   base_buses + 1, "alert-orange"
    elif occ_rate < 0.45:
        return "Remove 1 Bus", max(1, base_buses - 1), "alert-green"
    else:
        return "Keep As-Is",  base_buses, "alert-blue"

def get_demand_color(occ):
    if occ >= 0.90: return "#e74c3c"
    elif occ >= 0.75: return "#e67e22"
    elif occ >= 0.55: return "#1a6db5"
    else: return "#27ae60"

def estimate_revenue(occ, route, bus_type="Non-AC Seater"):
    cap = {"Non-AC Seater": 45, "AC Seater Volvo": 41, "Non-AC Sleeper": 32, "AC Sleeper": 32}
    pmult = {"Non-AC Seater": 1.0, "AC Seater Volvo": 2.5, "Non-AC Sleeper": 1.5, "AC Sleeper": 3.0}
    seats   = cap.get(bus_type, 45)
    price   = BASE_PRICE.get(route, 200) * pmult.get(bus_type, 1.0)
    booked  = int(occ * seats)
    return int(price * booked), booked, seats


# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## 🚌 FleetSense")
    st.caption("Gujarat Bus Fleet Demand Forecasting System")
    st.markdown("---")

    st.markdown("**📍 Select Route**")
    selected_route = st.selectbox(
        "Route", ROUTE_NAMES,
        label_visibility="collapsed"
    )

    st.markdown("**📅 Select Date**")
    selected_date = st.date_input(
        "Date", value=date.today() + timedelta(days=1),
        min_value=date.today(),
        max_value=date.today() + timedelta(days=90),
        label_visibility="collapsed"
    )

    st.markdown("**🚍 Bus Type**")
    bus_type = st.selectbox(
        "Bus Type",
        ["Non-AC Seater", "AC Seater Volvo", "Non-AC Sleeper", "AC Sleeper"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Route info card
    tier = ROUTE_TIER.get(selected_route, "Tier2")
    dist = ROUTE_DIST.get(selected_route, 0)
    base = BASE_BUSES.get(selected_route, 3)

    st.markdown("**📊 Route Info**")
    st.markdown(f"""
    <div class="info-box">
        <table style="width:100%; font-size:13px; border-collapse:collapse;">
            <tr><td style="color:#666; padding:2px 0;">Distance</td>
                <td style="text-align:right; font-weight:600; color:#1a4f8a;">{dist} km</td></tr>
            <tr><td style="color:#666; padding:2px 0;">Route Tier</td>
                <td style="text-align:right; font-weight:600; color:#1a4f8a;">{tier}</td></tr>
            <tr><td style="color:#666; padding:2px 0;">Base Buses/Day</td>
                <td style="text-align:right; font-weight:600; color:#1a4f8a;">{base}</td></tr>
            <tr><td style="color:#666; padding:2px 0;">Base Non-AC Price</td>
                <td style="text-align:right; font-weight:600; color:#1a4f8a;">₹{BASE_PRICE.get(selected_route, 0)}</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    predict_btn = st.button("🔮 Get Forecast", type="primary", use_container_width=True)

    st.markdown("---")
    st.caption("📁 Data: 2 years | 12 routes | 59 buses")
    st.caption("🔬 Model: Facebook Prophet + Rule Engine")


# ══════════════════════════════════════════════════════════════
#  MAIN AREA — HEADER
# ══════════════════════════════════════════════════════════════

st.markdown("# 🚌 FleetSense Gujarat")
st.markdown("**Demand-Driven Bus Fleet Allocation for Gujarat Private Bus Operators**")
st.divider()

# ── Top-level KPI cards ───────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

total_rev  = df["total_revenue_inr"].sum()
total_cost = df["total_operational_cost_inr"].sum()
net_profit = df["profit_loss_inr"].sum()
avg_occ    = df["occupancy_rate"].mean() * 100

with col1:
    st.markdown(f"""
    <div class="result-box">
        <div class="result-label">Total Revenue (2 Years)</div>
        <div class="result-amount">₹{total_rev/1e7:.1f}Cr</div>
        <div class="result-sub">Across 12 routes</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="result-box" style="background: linear-gradient(135deg,#1e8449 0%,#27ae60 100%);">
        <div class="result-label">Net Profit (2 Years)</div>
        <div class="result-amount">₹{net_profit/1e7:.1f}Cr</div>
        <div class="result-sub">After all operational costs</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="result-box" style="background: linear-gradient(135deg,#d35400 0%,#e67e22 100%);">
        <div class="result-label">Avg Fleet Occupancy</div>
        <div class="result-amount">{avg_occ:.1f}%</div>
        <div class="result-sub">Optimal target: 75–85%</div>
    </div>""", unsafe_allow_html=True)

with col4:
    high_demand_days = len(df[df["demand_label"].isin(["High","Overcrowded"])]["date"].unique())
    st.markdown(f"""
    <div class="result-box" style="background: linear-gradient(135deg,#6c3483 0%,#9b59b6 100%);">
        <div class="result-label">High-Demand Days</div>
        <div class="result-amount">{high_demand_days}</div>
        <div class="result-sub">Unique dates in 2 years</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════

tab1, tab2, tab3 = st.tabs([
    "🔮 Route Forecast",
    "📊 Fleet Dashboard",
    "📅 30-Day Planner"
])


# ──────────────────────────────────────────────────────────────
#  TAB 1 — ROUTE FORECAST
# ──────────────────────────────────────────────────────────────
with tab1:
    st.markdown(f"### Demand Forecast — {selected_route}")
    st.caption(f"Date: **{selected_date.strftime('%A, %d %B %Y')}**  |  Bus Type: **{bus_type}**")

    if predict_btn:
        occ_rate, festival = predict_occupancy(selected_route, selected_date)
        action, rec_buses, alert_cls = recommend_buses(occ_rate, BASE_BUSES.get(selected_route, 3))
        rev, booked, seats = estimate_revenue(occ_rate, selected_route, bus_type)

        # ── Festival badge ──
        if festival:
            st.markdown(f'<span class="fest-tag">🎉 Festival Day: {festival}</span><br><br>',
                        unsafe_allow_html=True)

        # ── Main result cards ──
        r1, r2, r3 = st.columns(3)

        with r1:
            color = get_demand_color(occ_rate)
            label = "Overcrowded" if occ_rate>=0.90 else "High" if occ_rate>=0.75 \
                    else "Normal" if occ_rate>=0.55 else "Low"
            st.markdown(f"""
            <div class="result-box" style="background: linear-gradient(135deg,{color}cc,{color});">
                <div class="result-label">Forecasted Occupancy</div>
                <div class="result-amount">{occ_rate*100:.1f}%</div>
                <div class="result-sub">Demand: {label}</div>
            </div>""", unsafe_allow_html=True)

        with r2:
            st.markdown(f"""
            <div class="{alert_cls}">
                <div class="alert-label">Fleet Recommendation</div>
                <div class="alert-value">{rec_buses} Buses</div>
                <div class="alert-detail">Action: {action}</div>
            </div>""", unsafe_allow_html=True)

        with r3:
            st.markdown(f"""
            <div class="result-box" style="background: linear-gradient(135deg,#6c3483 0%,#9b59b6 100%);">
                <div class="result-label">Est. Revenue ({bus_type})</div>
                <div class="result-amount">₹{rev:,}</div>
                <div class="result-sub">{booked}/{seats} seats filled</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Occupancy gauge chart ──
        col_gauge, col_table = st.columns([1, 1])

        with col_gauge:
            st.markdown('<div class="section-header">📊 Occupancy Gauge</div>', unsafe_allow_html=True)
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=occ_rate * 100,
                delta={"reference": df[df["route_name"]==selected_route]["occupancy_rate"].mean()*100,
                       "suffix": "%", "valueformat": ".1f"},
                title={"text": f"{selected_route}", "font": {"size": 14}},
                number={"suffix": "%", "font": {"size": 36}},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1},
                    "bar":  {"color": get_demand_color(occ_rate)},
                    "steps": [
                        {"range": [0,  45], "color": "#d5f5e3"},
                        {"range": [45, 55], "color": "#fdebd0"},
                        {"range": [55, 80], "color": "#d6eaf8"},
                        {"range": [80, 90], "color": "#fdebd0"},
                        {"range": [90,100], "color": "#fadbd8"},
                    ],
                    "threshold": {
                        "line": {"color": "#1a4f8a", "width": 3},
                        "thickness": 0.8,
                        "value": df[df["route_name"]==selected_route]["occupancy_rate"].mean()*100
                    }
                }
            ))
            fig_gauge.update_layout(height=280, margin=dict(t=40, b=10, l=20, r=20))
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col_table:
            st.markdown('<div class="section-header">💰 Cost-Revenue Breakdown</div>', unsafe_allow_html=True)

            # Get average costs for this route
            route_costs = df[df["route_name"] == selected_route].iloc[0]
            dist_km     = ROUTE_DIST.get(selected_route, 200)

            breakdown = pd.DataFrame({
                "Item": ["Ticket Revenue", "Fuel Cost", "Driver Cost",
                         "Conductor Cost", "Toll Cost", "Maintenance", "NET PROFIT"],
                "Amount (₹)": [
                    rev,
                    -int(route_costs["fuel_cost_inr"]),
                    -int(route_costs["driver_cost_inr"]),
                    -int(route_costs["conductor_cost_inr"]),
                    -int(route_costs["toll_cost_inr"]),
                    -int(route_costs["maintenance_cost_inr"]),
                    rev - int(route_costs["total_operational_cost_inr"])
                ]
            })
            breakdown["Amount (₹)"] = breakdown["Amount (₹)"].apply(
                lambda x: f"{'▲' if x>0 else '▼'} ₹{abs(x):,}"
            )
            st.dataframe(
                breakdown,
                use_container_width=True,
                hide_index=True,
                height=265
            )

        # ── Historical pattern for selected route ──
        st.markdown('<div class="section-header">📈 Historical Demand Pattern — This Route</div>',
                    unsafe_allow_html=True)

        route_hist = (
            df[df["route_name"] == selected_route]
              .groupby("date")["occupancy_rate"]
              .mean()
              .reset_index()
        )

        fig_hist = px.area(
            route_hist, x="date", y="occupancy_rate",
            title=f"Daily Occupancy Rate — {selected_route} (2023–2024)",
            labels={"occupancy_rate": "Avg Occupancy Rate", "date": "Date"},
            color_discrete_sequence=["#1a6db5"],
            template="plotly_white"
        )
        fig_hist.add_hline(y=0.80, line_dash="dash", line_color="orange",
                           annotation_text="Add Bus Threshold (80%)")
        fig_hist.add_hline(y=0.55, line_dash="dash", line_color="green",
                           annotation_text="Remove Bus Threshold (55%)")
        fig_hist.update_layout(yaxis_tickformat=".0%", height=300,
                                margin=dict(t=40, b=10))
        st.plotly_chart(fig_hist, use_container_width=True)

    else:
        # Placeholder before prediction
        st.markdown("""
        <div style="border: 2px dashed #d6e4f7; border-radius: 12px;
                    padding: 60px 20px; text-align: center; color: #aaa; background: #f9fbfe;">
            <div style="font-size: 48px;">🔮</div>
            <div style="font-size: 18px; margin-top: 12px; color: #1a4f8a; font-weight: 600;">
                Select a route and date, then click Get Forecast
            </div>
            <div style="font-size: 13px; margin-top: 8px; color: #888;">
                Get instant fleet recommendation + cost-revenue breakdown
            </div>
        </div>""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
#  TAB 2 — FLEET DASHBOARD
# ──────────────────────────────────────────────────────────────
with tab2:
    st.markdown("### Fleet Performance Dashboard — 2023–2024")

    # ── Row 1: Revenue by route + Occupancy by route ──
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-header">💰 Total Revenue by Route</div>', unsafe_allow_html=True)
        rev_by_route = (
            df.groupby("route_name")["total_revenue_inr"]
              .sum()
              .reset_index()
              .sort_values("total_revenue_inr", ascending=True)
        )
        fig_rev = px.bar(
            rev_by_route, x="total_revenue_inr", y="route_name",
            orientation="h",
            labels={"total_revenue_inr": "Total Revenue (₹)", "route_name": ""},
            color="total_revenue_inr",
            color_continuous_scale=["#d6eaf8", "#1a4f8a"],
            template="plotly_white"
        )
        fig_rev.update_layout(height=380, margin=dict(t=10,b=10),
                               coloraxis_showscale=False)
        fig_rev.update_xaxes(tickformat=",.0f")
        st.plotly_chart(fig_rev, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-header">📊 Avg Occupancy % by Route</div>', unsafe_allow_html=True)
        occ_by_route = (
            df.groupby("route_name")["occupancy_rate"]
              .mean()
              .reset_index()
              .sort_values("occupancy_rate", ascending=True)
        )
        occ_by_route["pct"] = (occ_by_route["occupancy_rate"] * 100).round(1)
        colors = ["#e74c3c" if x < 55 else "#e67e22" if x < 65
                  else "#1a6db5" if x < 80 else "#27ae60"
                  for x in occ_by_route["pct"]]
        fig_occ = px.bar(
            occ_by_route, x="pct", y="route_name",
            orientation="h",
            labels={"pct": "Avg Occupancy (%)", "route_name": ""},
            template="plotly_white"
        )
        fig_occ.update_traces(marker_color=colors)
        fig_occ.add_vline(x=75, line_dash="dash", line_color="#1a4f8a",
                          annotation_text="Target 75%")
        fig_occ.update_layout(height=380, margin=dict(t=10, b=10))
        st.plotly_chart(fig_occ, use_container_width=True)

    # ── Row 2: Monthly trend + Bus type profit ──
    col_l2, col_r2 = st.columns(2)

    with col_l2:
        st.markdown('<div class="section-header">📅 Monthly Revenue Trend — 2023 vs 2024</div>',
                    unsafe_allow_html=True)
        month_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                     7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
        monthly = (
            df.groupby(["year","month"])["total_revenue_inr"]
              .sum().reset_index()
        )
        monthly["month_name"] = monthly["month"].map(month_map)
        fig_monthly = px.bar(
            monthly, x="month_name", y="total_revenue_inr",
            color="year", barmode="group",
            labels={"total_revenue_inr":"Revenue (₹)","month_name":"Month"},
            color_discrete_sequence=["#1a6db5","#e67e22"],
            template="plotly_white"
        )
        fig_monthly.update_layout(height=320, margin=dict(t=10,b=10))
        fig_monthly.update_yaxes(tickformat=",.0f")
        st.plotly_chart(fig_monthly, use_container_width=True)

    with col_r2:
        st.markdown('<div class="section-header">🚌 Bus Type Profitability</div>', unsafe_allow_html=True)
        bus_profit = (
            df.groupby("bus_type")
              .agg(avg_profit=("profit_loss_inr","mean"),
                   avg_occ=("occupancy_rate","mean"))
              .reset_index()
        )
        fig_bus = px.scatter(
            bus_profit, x="avg_occ", y="avg_profit",
            text="bus_type", size=[30]*len(bus_profit),
            labels={"avg_occ":"Avg Occupancy","avg_profit":"Avg Profit per Trip (₹)"},
            color="avg_profit",
            color_continuous_scale=["#e74c3c","#f39c12","#27ae60"],
            template="plotly_white"
        )
        fig_bus.update_traces(textposition="top center", marker_sizemin=20)
        fig_bus.update_xaxes(tickformat=".0%")
        fig_bus.update_layout(height=320, margin=dict(t=10,b=10),
                               coloraxis_showscale=False)
        st.plotly_chart(fig_bus, use_container_width=True)

    # ── Row 3: Festival impact + Demand label pie ──
    col_l3, col_r3 = st.columns(2)

    with col_l3:
        st.markdown('<div class="section-header">🎉 Top 8 Festivals by Avg Occupancy</div>',
                    unsafe_allow_html=True)
        fest_data = (
            df[df["is_festival"]==1]
              .groupby("festival_name")["occupancy_rate"]
              .mean()
              .reset_index()
              .sort_values("occupancy_rate", ascending=False)
              .head(8)
        )
        normal_avg = df[df["is_festival"]==0]["occupancy_rate"].mean()
        fig_fest = px.bar(
            fest_data, x="occupancy_rate", y="festival_name",
            orientation="h",
            labels={"occupancy_rate":"Avg Occupancy","festival_name":""},
            color="occupancy_rate",
            color_continuous_scale=["#f7dc6f","#e67e22","#e74c3c"],
            template="plotly_white"
        )
        fig_fest.add_vline(x=normal_avg, line_dash="dash", line_color="#1a4f8a",
                           annotation_text=f"Normal Day: {normal_avg:.0%}")
        fig_fest.update_xaxes(tickformat=".0%")
        fig_fest.update_layout(height=320, margin=dict(t=10,b=10),
                                coloraxis_showscale=False)
        st.plotly_chart(fig_fest, use_container_width=True)

    with col_r3:
        st.markdown('<div class="section-header">📦 Demand Distribution Across All Trips</div>',
                    unsafe_allow_html=True)
        demand_dist = df["demand_label"].value_counts().reset_index()
        demand_dist.columns = ["label","count"]
        color_map = {"Low":"#27ae60","Normal":"#1a6db5",
                     "High":"#e67e22","Overcrowded":"#e74c3c"}
        fig_pie = px.pie(
            demand_dist, names="label", values="count",
            color="label", color_discrete_map=color_map,
            hole=0.45, template="plotly_white"
        )
        fig_pie.update_traces(textposition="outside", textinfo="percent+label")
        fig_pie.update_layout(height=320, margin=dict(t=10,b=10),
                               showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)


# ──────────────────────────────────────────────────────────────
#  TAB 3 — 30-DAY PLANNER
# ──────────────────────────────────────────────────────────────
with tab3:
    st.markdown(f"### 30-Day Fleet Planner — {selected_route}")
    st.caption("Rule-based forecast for the next 30 days. Green = reduce buses, Orange = add 1, Red = add 2.")

    # Generate 30-day outlook
    planner_rows = []
    for i in range(30):
        d      = date.today() + timedelta(days=i+1)
        occ, fest = predict_occupancy(selected_route, d)
        action, rec_buses, _ = recommend_buses(occ, BASE_BUSES.get(selected_route, 3))
        rev, booked, seats   = estimate_revenue(occ, selected_route)
        planner_rows.append({
            "Date":            d.strftime("%d %b %Y"),
            "Day":             d.strftime("%A"),
            "Festival":        fest if fest else "—",
            "Forecast Occ %":  round(occ * 100, 1),
            "Recommendation":  action,
            "Rec. Buses":      rec_buses,
            "Est. Revenue ₹":  rev,
        })

    planner_df = pd.DataFrame(planner_rows)

    # ── Summary row ──
    add2  = (planner_df["Recommendation"] == "Add 2 Buses").sum()
    add1  = (planner_df["Recommendation"] == "Add 1 Bus").sum()
    keep  = (planner_df["Recommendation"] == "Keep As-Is").sum()
    remove= (planner_df["Recommendation"] == "Remove 1 Bus").sum()

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("🔴 Add 2 Buses", f"{add2} days", help="Very high demand days")
    with m2:
        st.metric("🟠 Add 1 Bus", f"{add1} days", help="High demand days")
    with m3:
        st.metric("🔵 Keep As-Is", f"{keep} days", help="Normal demand days")
    with m4:
        st.metric("🟢 Remove 1 Bus", f"{remove} days", help="Low demand — save fuel cost")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Forecast bar chart for 30 days ──
    st.markdown('<div class="section-header">📊 30-Day Occupancy Forecast</div>', unsafe_allow_html=True)

    bar_colors = []
    for _, row in planner_df.iterrows():
        occ_val = row["Forecast Occ %"]
        if occ_val >= 90:   bar_colors.append("#e74c3c")
        elif occ_val >= 80: bar_colors.append("#e67e22")
        elif occ_val >= 55: bar_colors.append("#1a6db5")
        else:               bar_colors.append("#27ae60")

    fig_plan = go.Figure()
    fig_plan.add_trace(go.Bar(
        x=planner_df["Date"],
        y=planner_df["Forecast Occ %"],
        marker_color=bar_colors,
        text=planner_df["Recommendation"],
        textposition="outside",
        textfont=dict(size=9),
    ))
    fig_plan.add_hline(y=80, line_dash="dash", line_color="orange",
                       annotation_text="Add Bus (80%)")
    fig_plan.add_hline(y=55, line_dash="dash", line_color="green",
                       annotation_text="Remove Bus (55%)")
    fig_plan.update_layout(
        height=380, template="plotly_white",
        xaxis_tickangle=-45, yaxis_title="Forecasted Occupancy (%)",
        margin=dict(t=20, b=10), showlegend=False
    )
    st.plotly_chart(fig_plan, use_container_width=True)

    # ── Full 30-day table ──
    st.markdown('<div class="section-header">📋 Full 30-Day Schedule</div>', unsafe_allow_html=True)
    st.dataframe(planner_df, use_container_width=True, hide_index=True, height=400)

    # ── Download button ──
    csv_out = planner_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download 30-Day Plan as CSV",
        data=csv_out,
        file_name=f"fleetsense_{selected_route.replace('→','_')}_{date.today()}.csv",
        mime="text/csv",
        use_container_width=True
    )

    # ── If forecast CSV from Prophet exists, show it ──
    if forecast_df is not None:
        st.markdown("---")
        st.markdown("### 🔮 Prophet Model Forecast (from Jupyter Notebook)")
        route_fc = forecast_df[forecast_df["route_name"] == selected_route].copy()
        if not route_fc.empty:
            fig_prophet = go.Figure()
            fig_prophet.add_trace(go.Scatter(
                x=route_fc["forecast_date"], y=route_fc["upper_bound"] * 100,
                fill=None, mode="lines",
                line=dict(color="rgba(26,109,181,0.2)"), name="Upper Bound"
            ))
            fig_prophet.add_trace(go.Scatter(
                x=route_fc["forecast_date"], y=route_fc["lower_bound"] * 100,
                fill="tonexty", mode="lines",
                line=dict(color="rgba(26,109,181,0.2)"),
                fillcolor="rgba(26,109,181,0.1)", name="Confidence Band"
            ))
            fig_prophet.add_trace(go.Scatter(
                x=route_fc["forecast_date"], y=route_fc["forecast_occ_pct"],
                mode="lines+markers",
                line=dict(color="#1a6db5", width=2),
                name="Prophet Forecast"
            ))
            fig_prophet.add_hline(y=80, line_dash="dash", line_color="orange")
            fig_prophet.add_hline(y=55, line_dash="dash", line_color="green")
            fig_prophet.update_layout(
                height=350, template="plotly_white",
                yaxis_title="Forecasted Occupancy (%)",
                margin=dict(t=20, b=10)
            )
            st.plotly_chart(fig_prophet, use_container_width=True)
        else:
            st.info(f"No Prophet forecast found for {selected_route}. Run the Jupyter notebook first.")
