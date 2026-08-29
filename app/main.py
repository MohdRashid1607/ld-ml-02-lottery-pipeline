import json
import sqlite3
from datetime import datetime
from pathlib import Path
import pandas as pd
import streamlit as st

# Setup page configuration
st.set_page_config(
    page_title="Lottery Data & Weather Explorer",
    page_icon="🎰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished, research-oriented UI
st.markdown("""
<style>
    /* Global Typography & Spacing */
    .main-title {
        font-size: 2.1rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #9aa0a6;
        margin-bottom: 1.2rem;
    }
    .disclaimer-box {
        background-color: rgba(255, 171, 0, 0.08);
        border-left: 3px solid #ffab00;
        padding: 10px 14px;
        border-radius: 4px;
        font-size: 0.84rem;
        line-height: 1.4;
        margin-bottom: 1.5rem;
        color: #e8eaed;
    }
    
    /* KPI Card Styling */
    .kpi-container {
        display: flex;
        gap: 12px;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 6px;
        padding: 12px 14px;
        flex: 1;
        min-width: 120px;
    }
    .kpi-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #9aa0a6;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 1.7rem;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.2;
    }
    .kpi-subtext {
        font-size: 0.72rem;
        color: #80868b;
        margin-top: 2px;
    }

    /* Inspector Card Styling */
    .inspector-card {
        background-color: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 6px;
        padding: 16px;
        height: 100%;
    }
    .inspector-header {
        font-size: 0.95rem;
        font-weight: 600;
        color: #8ab4f8;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 8px;
        margin-bottom: 12px;
    }
    .inspector-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        font-size: 0.85rem;
    }
    .inspector-key {
        color: #9aa0a6;
    }
    .inspector-val {
        color: #e8eaed;
        font-weight: 500;
        text-align: right;
    }
    .section-divider {
        margin-top: 28px;
        margin-bottom: 24px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    /* Sidebar Section Headers */
    .sidebar-header {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #8ab4f8;
        font-weight: 600;
        margin-top: 14px;
        margin-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎰 Lottery Data Acquisition & Weather Enrichment Explorer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Official Draw Results, Location Provenance, and Historical Weather Data (LD-ML-02)</div>', unsafe_allow_html=True)

# Mandatory Responsible Use Disclaimer (Page 3 of Specification)
st.markdown("""
<div class="disclaimer-box">
    <strong>⚖️ Responsible Data Science & Research Notice:</strong><br>
    This platform is an evidence-based data engineering and quality-control product. 
    Lottery draws are mathematically independent and uniformly random. Historical ball frequencies, machine statistics, and weather correlations 
    are presented for descriptive/exploratory analysis only and <strong>do not predict future draw outcomes</strong>. No predictive picks or gambling advice are provided.
</div>
""", unsafe_allow_html=True)


@st.cache_data
def load_comprehensive_data():
    db_path = Path("data/lottery.db").resolve()
    if not db_path.exists():
        return pd.DataFrame(), pd.DataFrame()
        
    conn = sqlite3.connect(db_path)
    
    # 1. Fetch draw numbers aggregated
    numbers_query = """
        SELECT 
            draw_id,
            number_type,
            GROUP_CONCAT(value, ', ') as numbers_list
        FROM (
            SELECT draw_id, number_type, value 
            FROM draw_numbers 
            ORDER BY draw_id, number_type, position
        )
        GROUP BY draw_id, number_type
    """
    nums_df = pd.read_sql(numbers_query, conn)
    
    # Pivot numbers into main and bonus columns
    main_nums = nums_df[nums_df["number_type"] == "main"].set_index("draw_id")["numbers_list"].to_dict()
    bonus_nums = nums_df[nums_df["number_type"] == "bonus"].set_index("draw_id")["numbers_list"].to_dict()
    
    # 2. Fetch primary draw & weather details
    query = """
        SELECT 
            d.draw_id,
            g.name as game,
            d.draw_number,
            d.draw_date,
            d.draw_local_datetime,
            d.draw_datetime_utc,
            v.city,
            v.country_code,
            v.latitude,
            v.longitude,
            v.timezone,
            w.temperature_c,
            w.observed_at as weather_observed_at,
            w.provider as weather_provider,
            w.match_minutes,
            w.status as quality_status,
            d.source_url,
            d.scraped_at
        FROM draws d
        JOIN games g ON d.game_id = g.game_id
        LEFT JOIN venues v ON d.venue_id = v.venue_id
        LEFT JOIN weather_readings w ON d.draw_id = w.draw_id
        ORDER BY d.draw_number DESC
    """
    df = pd.read_sql(query, conn)
    
    # Individual ball numbers for frequency analysis
    raw_balls_query = """
        SELECT 
            d.draw_id,
            g.name as game,
            dn.number_type,
            dn.value as ball_number
        FROM draw_numbers dn
        JOIN draws d ON dn.draw_id = d.draw_id
        JOIN games g ON d.game_id = g.game_id
    """
    balls_df = pd.read_sql(raw_balls_query, conn)
    conn.close()
    
    # Map ball numbers to df
    df["main_numbers"] = df["draw_id"].map(main_nums).fillna("N/A")
    df["bonus_numbers"] = df["draw_id"].map(bonus_nums).fillna("N/A")
    
    # Format bonus label dynamically per game
    def format_bonus_label(row):
        if row["game"] == "euromillions":
            return f"Stars: {row['bonus_numbers']}"
        elif row["game"] == "thunderball":
            return f"Thunderball: {row['bonus_numbers']}"
        elif row["game"] == "set_for_life":
            return f"Life Ball: {row['bonus_numbers']}"
        return row["bonus_numbers"]

    df["bonus_display"] = df.apply(format_bonus_label, axis=1)
    
    # Format clean date object for filtering (with utc=True to handle mixed Paris/London timezones)
    df["parsed_date"] = pd.to_datetime(df["draw_local_datetime"], utc=True, errors="coerce")
    
    # Set default quality badge
    df["quality_badge"] = df["temperature_c"].apply(
        lambda x: "🟢 Verified (0m)" if pd.notna(x) else "🔴 Missing Enrichment"
    )
    
    return df, balls_df


df, balls_df = load_comprehensive_data()

if df.empty:
    st.error("⚠️ No data found in `data/lottery.db`. Please run the collectors and weather enrichment scripts first.")
    st.stop()

# ==========================================
# SIDEBAR FILTERS (Refined Hierarchy)
# ==========================================
st.sidebar.markdown("### 🔍 Search & Filters")

# Game Selection
st.sidebar.markdown('<div class="sidebar-header">Target Games</div>', unsafe_allow_html=True)
all_games = sorted(df["game"].unique())
selected_games = st.sidebar.multiselect("Select Games", options=all_games, default=all_games, label_visibility="collapsed")

# City Selection
st.sidebar.markdown('<div class="sidebar-header">Draw Cities</div>', unsafe_allow_html=True)
all_cities = sorted(df["city"].dropna().unique())
selected_cities = st.sidebar.multiselect("Draw Cities", options=all_cities, default=all_cities, label_visibility="collapsed")

# Weather Status Selection
st.sidebar.markdown('<div class="sidebar-header">Weather Status</div>', unsafe_allow_html=True)
status_options = ["All Records", "Enriched Only", "Missing Weather Only"]
selected_status = st.sidebar.radio("Weather Status", status_options, label_visibility="collapsed")

# Temperature Range Filter
st.sidebar.markdown('<div class="sidebar-header">Temperature Range (°C)</div>', unsafe_allow_html=True)
min_temp = float(df["temperature_c"].min()) if df["temperature_c"].notna().any() else 0.0
max_temp = float(df["temperature_c"].max()) if df["temperature_c"].notna().any() else 40.0

if min_temp < max_temp:
    temp_range = st.sidebar.slider(
        "Temperature Range (°C)",
        min_value=round(min_temp - 1.0, 1),
        max_value=round(max_temp + 1.0, 1),
        value=(round(min_temp - 1.0, 1), round(max_temp + 1.0, 1)),
        label_visibility="collapsed"
    )
else:
    temp_range = (min_temp, max_temp)

# Search Input
st.sidebar.markdown('<div class="sidebar-header">Search Query</div>', unsafe_allow_html=True)
search_query = st.sidebar.text_input("Search (Draw ID / Date)", placeholder="e.g. THUNDERBALL-3963", label_visibility="collapsed").strip().lower()

# Clear Filters Button
if st.sidebar.button("🔄 Reset All Filters", use_container_width=True):
    st.rerun()

# Apply Filters
filtered = df[
    (df["game"].isin(selected_games)) &
    (df["city"].isin(selected_cities))
]

if selected_status == "Enriched Only":
    filtered = filtered[filtered["temperature_c"].notna()]
elif selected_status == "Missing Weather Only":
    filtered = filtered[filtered["temperature_c"].isna()]

if selected_status != "Missing Weather Only" and df["temperature_c"].notna().any():
    filtered = filtered[
        (filtered["temperature_c"].isna()) |
        ((filtered["temperature_c"] >= temp_range[0]) & (filtered["temperature_c"] <= temp_range[1]))
    ]

if search_query:
    filtered = filtered[
        filtered["draw_id"].str.lower().str.contains(search_query) |
        filtered["draw_date"].str.lower().str.contains(search_query)
    ]

# ==========================================
# REFINED KPI CARDS
# ==========================================
total_filtered = len(filtered)
enriched_count = int(filtered["temperature_c"].notna().sum())
missing_count = int(filtered["temperature_c"].isna().sum())
enrichment_rate = (enriched_count / total_filtered * 100) if total_filtered > 0 else 0
avg_temp = filtered["temperature_c"].mean() if enriched_count > 0 else 0.0

kpi_cols = st.columns(5)
with kpi_cols[0]:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Filtered Draws</div>
        <div class="kpi-value">{total_filtered:,}</div>
        <div class="kpi-subtext">Total active records</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[1]:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Weather Enriched</div>
        <div class="kpi-value">{enriched_count:,}</div>
        <div class="kpi-subtext">Hourly match linked</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[2]:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Missing Weather</div>
        <div class="kpi-value">{missing_count:,}</div>
        <div class="kpi-subtext">Unmatched readings</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[3]:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Enrichment Rate</div>
        <div class="kpi-value">{enrichment_rate:.1f}%</div>
        <div class="kpi-subtext">Data quality metric</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[4]:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Avg Temperature</div>
        <div class="kpi-value">{avg_temp:.1f} °C</div>
        <div class="kpi-subtext">Across filtered venues</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

# ==========================================
# REUSABLE SECTION RENDERING FUNCTIONS
# ==========================================

def render_browse_table():
    st.markdown(f"#### 📋 Draw Results & Meteorological Records ({len(filtered)} matches)")
    display_cols = [
        "draw_id", "game", "draw_number", "draw_date", "main_numbers", "bonus_display",
        "city", "temperature_c", "quality_badge", "source_url"
    ]
    table_df = filtered[display_cols].copy()
    table_df.rename(columns={
        "draw_id": "Draw ID",
        "game": "Game",
        "draw_number": "Draw #",
        "draw_date": "Draw Date",
        "main_numbers": "Main Numbers",
        "bonus_display": "Bonus / Lucky Ball",
        "city": "Draw City",
        "temperature_c": "Temp (°C)",
        "quality_badge": "Weather Quality",
        "source_url": "Official Source"
    }, inplace=True)
    
    st.dataframe(
        table_df,
        column_config={
            "Official Source": st.column_config.LinkColumn("Results URL"),
            "Temp (°C)": st.column_config.NumberColumn(format="%.1f °C"),
            "Draw #": st.column_config.NumberColumn(format="%d")
        },
        hide_index=True,
        use_container_width=True,
        height=400
    )

def render_inspector(key_suffix=""):
    st.markdown("#### 🔍 Detailed Record Inspector & Lineage Breakdown")
    if not filtered.empty:
        selected_draw_id = st.selectbox(
            "Select a Draw ID to inspect complete provenance:", 
            options=filtered["draw_id"].unique(), 
            key=f"inspector_select_{key_suffix}"
        )
        draw_row = filtered[filtered["draw_id"] == selected_draw_id].iloc[0]
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="inspector-card">
                <div class="inspector-header">🎯 Draw Identification</div>
                <div class="inspector-row"><span class="inspector-key">Game:</span><span class="inspector-val">{draw_row['game'].upper()}</span></div>
                <div class="inspector-row"><span class="inspector-key">Draw Number:</span><span class="inspector-val">#{draw_row['draw_number']}</span></div>
                <div class="inspector-row"><span class="inspector-key">Draw Date:</span><span class="inspector-val">{draw_row['draw_date']}</span></div>
                <div class="inspector-row"><span class="inspector-key">Main Numbers:</span><span class="inspector-val"><code>{draw_row['main_numbers']}</code></span></div>
                <div class="inspector-row"><span class="inspector-key">Bonus Numbers:</span><span class="inspector-val"><code>{draw_row['bonus_display']}</code></span></div>
                <div class="inspector-row"><span class="inspector-key">Source Link:</span><span class="inspector-val"><a href="{draw_row['source_url']}" target="_blank">Official Site</a></span></div>
            </div>
            """, unsafe_allow_html=True)
            
        with c2:
            st.markdown(f"""
            <div class="inspector-card">
                <div class="inspector-header">📍 Venue & Geolocation</div>
                <div class="inspector-row"><span class="inspector-key">City & Country:</span><span class="inspector-val">{draw_row['city']} ({draw_row['country_code']})</span></div>
                <div class="inspector-row"><span class="inspector-key">Latitude:</span><span class="inspector-val">{draw_row['latitude']}</span></div>
                <div class="inspector-row"><span class="inspector-key">Longitude:</span><span class="inspector-val">{draw_row['longitude']}</span></div>
                <div class="inspector-row"><span class="inspector-key">Timezone:</span><span class="inspector-val"><code>{draw_row['timezone']}</code></span></div>
                <div class="inspector-row"><span class="inspector-key">Scheduled Local:</span><span class="inspector-val">{draw_row['draw_local_datetime']}</span></div>
                <div class="inspector-row"><span class="inspector-key">Normalized UTC:</span><span class="inspector-val">{draw_row['draw_datetime_utc']}</span></div>
            </div>
            """, unsafe_allow_html=True)
            
        with c3:
            st.markdown(f"""
            <div class="inspector-card">
                <div class="inspector-header">🌡️ Meteorological Reading</div>
                <div class="inspector-row"><span class="inspector-key">Air Temperature:</span><span class="inspector-val"><strong>{draw_row['temperature_c']} °C</strong></span></div>
                <div class="inspector-row"><span class="inspector-key">Observed Timestamp:</span><span class="inspector-val">{draw_row['weather_observed_at']}</span></div>
                <div class="inspector-row"><span class="inspector-key">Weather Provider:</span><span class="inspector-val">{draw_row['weather_provider']}</span></div>
                <div class="inspector-row"><span class="inspector-key">Match Delta:</span><span class="inspector-val">{draw_row['match_minutes']}m (Nearest Hour)</span></div>
                <div class="inspector-row"><span class="inspector-key">Quality Status:</span><span class="inspector-val">{draw_row['quality_badge']}</span></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No draws match the current filter selection.")

def render_visual_analytics(key_suffix=""):
    st.markdown("#### 📊 Descriptive Meteorological & Frequency Analytics")
    
    # Row 1: Primary Temperature Analysis (Key requirement)
    st.markdown("##### 1. Historical Temperature Progression & City Distribution")
    row1_c1, row1_c2 = st.columns([2, 1])
    
    with row1_c1:
        chart_df = filtered.dropna(subset=["temperature_c"]).sort_values("parsed_date")
        if not chart_df.empty:
            st.line_chart(chart_df.set_index("parsed_date")["temperature_c"], use_container_width=True)
            st.caption("Chronological air temperature (°C) at draw hour across filtered events.")
        else:
            st.info("No temperature readings available for current filter selection.")
            
    with row1_c2:
        if not filtered["temperature_c"].isna().all():
            city_temp_avg = filtered.groupby("city")["temperature_c"].agg(["mean", "min", "max", "count"]).reset_index()
            city_temp_avg.columns = ["City", "Mean (°C)", "Min (°C)", "Max (°C)", "Draws"]
            st.dataframe(city_temp_avg, hide_index=True, use_container_width=True)
            
    st.markdown("---")
    
    # Row 2: Volume by Game & Volume by City
    st.markdown("##### 2. Draw Volume Distribution")
    row2_c1, row2_c2 = st.columns(2)
    with row2_c1:
        st.markdown("**Draws Collected by Game**")
        st.bar_chart(filtered["game"].value_counts(), use_container_width=True)
    with row2_c2:
        st.markdown("**Draw Distribution by City**")
        st.bar_chart(filtered["city"].value_counts(), use_container_width=True)
        
    st.markdown("---")
    
    # Row 3: Ball Number Frequencies (Descriptive Only)
    st.markdown("##### 3. Most Frequent Main Numbers (Descriptive Only)")
    selected_game_freq = st.selectbox(
        "Select Game for Ball Frequency Analysis:", 
        options=selected_games if selected_games else all_games, 
        key=f"freq_game_select_{key_suffix}"
    )
    
    game_balls = balls_df[(balls_df["game"] == selected_game_freq) & (balls_df["number_type"] == "main")]
    if not game_balls.empty:
        freq_series = game_balls["ball_number"].value_counts().head(12)
        st.bar_chart(freq_series, use_container_width=True)
        st.caption(f"Top 12 drawn main numbers for **{selected_game_freq}** in collected sample. *Randomly distributed; not predictive.*")
    else:
        st.info("No ball number data available.")

def render_export_section(key_suffix=""):
    st.markdown("#### 📥 Schema Export & Delivery (CSV & JSON)")
    st.write(
        "Export the normalized, weather-enriched dataset adhering to the "
        "LD-ML-02 project specification (ISO 8601 timestamps, Celsius units, UTF-8 encoded)."
    )
    
    export_columns = [
        "draw_id", "game", "draw_number", "draw_date", "draw_local_datetime", 
        "timezone", "draw_datetime_utc", "main_numbers", "bonus_numbers", 
        "city", "country_code", "latitude", "longitude", "temperature_c", 
        "weather_observed_at", "match_minutes", "quality_status", 
        "source_url", "weather_provider", "scraped_at"
    ]
    export_df = filtered[[c for c in export_columns if c in filtered.columns]].copy()
    export_df["schema_version"] = "v1.0.0"
    export_df["time_basis"] = "scheduled_time"
    export_df["location_confidence"] = "verified_venue"
    
    c_csv, c_json = st.columns(2)
    with c_csv:
        csv_data = export_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Filtered Dataset as CSV",
            data=csv_data,
            file_name=f"lottery_weather_dataset_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            key=f"csv_download_btn_{key_suffix}",
            use_container_width=True
        )
        st.caption("Standard CSV format with UTF-8 encoding.")
        
    with c_json:
        json_data = export_df.to_json(orient="records", date_format="iso", indent=2)
        st.download_button(
            label="📥 Download Filtered Dataset as JSON",
            data=json_data,
            file_name=f"lottery_weather_dataset_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            key=f"json_download_btn_{key_suffix}",
            use_container_width=True
        )
        st.caption("Structured JSON array formatted with ISO 8601 timestamps.")

    st.markdown("##### Export Schema Sample Preview")
    st.dataframe(export_df.head(5), hide_index=True, use_container_width=True)


# ==========================================
# MULTI-TAB & ALL-IN-ONE NAVIGATION
# ==========================================
tab_all, tab_browse, tab_inspect, tab_analytics, tab_export = st.tabs([
    "📄 All-In-One Complete View",
    "📋 Browse Draws", 
    "🔍 Draw Inspector", 
    "📊 Analytics", 
    "📥 Export"
])

# 1. Complete All-In-One Page (All sections stacked)
with tab_all:
    render_browse_table()
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    render_inspector(key_suffix="all")
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    render_visual_analytics(key_suffix="all")
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    render_export_section(key_suffix="all")

# 2. Dedicated Browse Tab
with tab_browse:
    render_browse_table()

# 3. Dedicated Inspector Tab
with tab_inspect:
    render_inspector(key_suffix="tab")

# 4. Dedicated Analytics Tab
with tab_analytics:
    render_visual_analytics(key_suffix="tab")

# 5. Dedicated Export Tab
with tab_export:
    render_export_section(key_suffix="tab")
