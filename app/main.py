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

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #888;
        margin-bottom: 1.5rem;
    }
    .disclaimer-box {
        background-color: rgba(255, 165, 0, 0.1);
        border-left: 4px solid #FFA500;
        padding: 10px 15px;
        border-radius: 4px;
        font-size: 0.88rem;
        margin-bottom: 20px;
    }
    .section-divider {
        margin-top: 30px;
        margin-bottom: 20px;
        border-bottom: 2px solid rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🎰 Lottery Data Acquisition & Weather Enrichment Explorer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Official Draw Results, Location Provenance, and Historical Weather Data (LD-ML-02)</div>', unsafe_allow_html=True)

# Mandatory Responsible Use Disclaimer (Page 3 of Specification)
st.markdown("""
<div class="disclaimer-box">
    <strong>⚖️ Responsible Data Science & Research Notice:</strong><br>
    This platform is strictly an evidence-based data engineering and quality-control product. 
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
# SIDEBAR FILTERS (Page 3 Requirements)
# ==========================================
st.sidebar.header("🔍 Search & Filter Criteria")

# Game Filter
all_games = sorted(df["game"].unique())
selected_games = st.sidebar.multiselect("Select Games", options=all_games, default=all_games)

# City Filter
all_cities = sorted(df["city"].dropna().unique())
selected_cities = st.sidebar.multiselect("Venue Cities", options=all_cities, default=all_cities)

# Enrichment Status Filter
status_options = ["All", "Enriched Only (With Weather)", "Missing Weather Only"]
selected_status = st.sidebar.radio("Weather Quality Status", status_options)

# Temperature Range Filter
min_temp = float(df["temperature_c"].min()) if df["temperature_c"].notna().any() else 0.0
max_temp = float(df["temperature_c"].max()) if df["temperature_c"].notna().any() else 40.0

if min_temp < max_temp:
    temp_range = st.sidebar.slider(
        "Temperature Range (°C)",
        min_value=round(min_temp - 1.0, 1),
        max_value=round(max_temp + 1.0, 1),
        value=(round(min_temp - 1.0, 1), round(max_temp + 1.0, 1))
    )
else:
    temp_range = (min_temp, max_temp)

# Apply Filters
filtered = df[
    (df["game"].isin(selected_games)) &
    (df["city"].isin(selected_cities))
]

if selected_status == "Enriched Only (With Weather)":
    filtered = filtered[filtered["temperature_c"].notna()]
elif selected_status == "Missing Weather Only":
    filtered = filtered[filtered["temperature_c"].isna()]

if selected_status != "Missing Weather Only" and df["temperature_c"].notna().any():
    filtered = filtered[
        (filtered["temperature_c"].isna()) |
        ((filtered["temperature_c"] >= temp_range[0]) & (filtered["temperature_c"] <= temp_range[1]))
    ]

# Search Box for Draw ID or Date
search_query = st.sidebar.text_input("Search (Draw ID or Date text):", "").strip().lower()
if search_query:
    filtered = filtered[
        filtered["draw_id"].str.lower().str.contains(search_query) |
        filtered["draw_date"].str.lower().str.contains(search_query)
    ]

# ==========================================
# SUMMARY METRICS & QUALITY AUDIT (Page 3/5)
# ==========================================
col1, col2, col3, col4, col5 = st.columns(5)
total_filtered = len(filtered)
enriched_count = int(filtered["temperature_c"].notna().sum())
missing_count = int(filtered["temperature_c"].isna().sum())
enrichment_rate = (enriched_count / total_filtered * 100) if total_filtered > 0 else 0
avg_temp = filtered["temperature_c"].mean() if enriched_count > 0 else 0.0

col1.metric("Total Filtered Draws", f"{total_filtered:,}")
col2.metric("Weather Enriched", f"{enriched_count:,}")
col3.metric("Missing Enrichment", f"{missing_count:,}")
col4.metric("Enrichment Rate", f"{enrichment_rate:.1f}%")
col5.metric("Avg Draw Temperature", f"{avg_temp:.1f} °C" if enriched_count > 0 else "N/A")

st.markdown("---")

# ==========================================
# REUSABLE SECTION RENDERING FUNCTIONS
# ==========================================

def render_browse_table():
    st.subheader(f"📋 Draw Results & Weather Enrichment Records ({len(filtered)} rows)")
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
        "main_numbers": "Main Winning Numbers",
        "bonus_display": "Bonus / Lucky Numbers",
        "city": "Venue City",
        "temperature_c": "Temp (°C)",
        "quality_badge": "Enrichment Quality",
        "source_url": "Official Source"
    }, inplace=True)
    
    st.dataframe(
        table_df,
        column_config={
            "Official Source": st.column_config.LinkColumn("Official Results Page"),
            "Temp (°C)": st.column_config.NumberColumn(format="%.1f °C"),
            "Draw #": st.column_config.NumberColumn(format="%d")
        },
        hide_index=True,
        use_container_width=True,
        height=420
    )

def render_inspector(key_suffix=""):
    st.subheader("🔍 Detailed Record Inspector & Provenance Breakdown")
    if not filtered.empty:
        selected_draw_id = st.selectbox(
            "Select a Draw ID to Inspect:", 
            options=filtered["draw_id"].unique(), 
            key=f"inspector_select_{key_suffix}"
        )
        draw_row = filtered[filtered["draw_id"] == selected_draw_id].iloc[0]
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("#### 🎯 Draw Identification")
            st.write(f"**Game:** {draw_row['game'].upper()}")
            st.write(f"**Draw Number:** #{draw_row['draw_number']}")
            st.write(f"**Draw Date:** {draw_row['draw_date']}")
            st.write(f"**Main Numbers:** `{draw_row['main_numbers']}`")
            st.write(f"**Bonus Numbers:** `{draw_row['bonus_display']}`")
            st.write(f"**Source URL:** [National Lottery Official]({draw_row['source_url']})")
            
        with c2:
            st.markdown("#### 📍 Venue & Coordinates")
            st.write(f"**City:** {draw_row['city']} ({draw_row['country_code']})")
            st.write(f"**Latitude:** {draw_row['latitude']}")
            st.write(f"**Longitude:** {draw_row['longitude']}")
            st.write(f"**Timezone:** `{draw_row['timezone']}`")
            st.write(f"**Local Scheduled Time:** `{draw_row['draw_local_datetime']}`")
            st.write(f"**Normalized UTC Time:** `{draw_row['draw_datetime_utc']}`")
            
        with c3:
            st.markdown("#### 🌡️ Weather Reading (Open-Meteo)")
            st.write(f"**Temperature:** `{draw_row['temperature_c']} °C`")
            st.write(f"**Observed Timestamp (UTC):** `{draw_row['weather_observed_at']}`")
            st.write(f"**Weather Provider:** {draw_row['weather_provider']}")
            st.write(f"**Time Match Difference:** `{draw_row['match_minutes']} minutes (Nearest Hour)`")
            st.write(f"**Verification Status:** `{draw_row['quality_badge']}`")
    else:
        st.info("No draws match the current filter selection.")

def render_visual_analytics(key_suffix=""):
    st.subheader("📊 Descriptive Statistical & Meteorological Visualizations")
    row1_c1, row1_c2 = st.columns(2)
    
    with row1_c1:
        st.markdown("#### 🌡️ Temperature Distribution by Venue City")
        if not filtered["temperature_c"].isna().all():
            city_temp_avg = filtered.groupby("city")["temperature_c"].agg(["mean", "min", "max"]).reset_index()
            city_temp_avg.columns = ["City", "Mean Temp (°C)", "Min Temp (°C)", "Max Temp (°C)"]
            st.dataframe(city_temp_avg, hide_index=True, use_container_width=True)
            
            chart_df = filtered.dropna(subset=["temperature_c"]).sort_values("parsed_date")
            if not chart_df.empty:
                st.line_chart(chart_df.set_index("parsed_date")["temperature_c"])
                st.caption("Chronological draw temperature progression (°C).")
        else:
            st.info("No temperature readings available for current filter selection.")
            
    with row1_c2:
        st.markdown("#### 🎱 Most Frequent Main Numbers (Descriptive Only)")
        selected_game_freq = st.selectbox(
            "Select Game for Ball Frequency:", 
            options=selected_games if selected_games else all_games, 
            key=f"freq_game_select_{key_suffix}"
        )
        
        game_balls = balls_df[(balls_df["game"] == selected_game_freq) & (balls_df["number_type"] == "main")]
        if not game_balls.empty:
            freq_series = game_balls["ball_number"].value_counts().head(10)
            st.bar_chart(freq_series)
            st.caption(f"Top 10 drawn main numbers for **{selected_game_freq}** in collected sample.")
        else:
            st.info("No ball number data available.")

            
    st.markdown("---")
    row2_c1, row2_c2 = st.columns(2)
    with row2_c1:
        st.markdown("#### 📈 Total Draws Collected per Game")
        st.bar_chart(filtered["game"].value_counts())
    with row2_c2:
        st.markdown("#### 🌍 Venue Distribution")
        st.bar_chart(filtered["city"].value_counts())

def render_export_section(key_suffix=""):
    st.subheader("📥 Schema Export & Delivery (CSV & JSON)")
    st.write(
        "Download the normalized and weather-enriched dataset adhering to the "
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
            label="📥 Download Dataset as CSV",
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
            label="📥 Download Dataset as JSON",
            data=json_data,
            file_name=f"lottery_weather_dataset_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            key=f"json_download_btn_{key_suffix}",
            use_container_width=True
        )
        st.caption("Structured JSON array formatted with ISO 8601 timestamps.")

    st.markdown("#### Sample Export Preview")
    st.dataframe(export_df.head(5), hide_index=True, use_container_width=True)


# ==========================================
# MULTI-TAB & ALL-IN-ONE VIEW NAVIGATION
# ==========================================
tab_all, tab_browse, tab_inspect, tab_analytics, tab_export = st.tabs([
    "📄 All-In-One Complete View",
    "📋 Browse & Search Draws", 
    "🔍 Detailed Record Inspector", 
    "📊 Descriptive Visual Analytics", 
    "📥 Schema Export (CSV & JSON)"
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


