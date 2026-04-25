import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

# ── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title="India Location DB — Admin Dashboard",
    page_icon="🇮🇳",
    layout="wide"
)

# ── DB Connection ─────────────────────────────────────────
@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host     = "localhost",
        port     = 5432,
        database = "india_location_db",
        user     = "postgres",
        password = "root"
    )

@st.cache_data
def run_query(query):
    conn = get_connection()
    return pd.read_sql(query, conn)

# ── Header ────────────────────────────────────────────────
st.title("🇮🇳 India Location DB — Admin Dashboard")
st.markdown("**Production-grade location data platform | All India Villages**")
st.divider()

# ── Row 1: KPI Cards ──────────────────────────────────────
st.subheader("📌 Database Overview")

counts = run_query("""
    SELECT
        (SELECT COUNT(*) FROM states)        AS total_states,
        (SELECT COUNT(*) FROM districts)     AS total_districts,
        (SELECT COUNT(*) FROM sub_districts) AS total_subdistricts,
        (SELECT COUNT(*) FROM villages)      AS total_villages
""")

col1, col2, col3, col4 = st.columns(4)
col1.metric("🗺️ States",         f"{counts['total_states'][0]:,}")
col2.metric("🏙️ Districts",       f"{counts['total_districts'][0]:,}")
col3.metric("🏘️ Sub-Districts",   f"{counts['total_subdistricts'][0]:,}")
col4.metric("🏡 Villages",        f"{counts['total_villages'][0]:,}")

st.divider()

# ── Row 2: Top 10 States by Villages ─────────────────────
st.subheader("📊 Top 10 States by Village Count")

villages_by_state = run_query("""
    SELECT s.name AS state, COUNT(v.id) AS total_villages
    FROM states s
    JOIN districts d      ON d.state_id       = s.id
    JOIN sub_districts sd ON sd.district_id   = d.id
    JOIN villages v       ON v.sub_district_id = sd.id
    GROUP BY s.name
    ORDER BY total_villages DESC
    LIMIT 10
""")

fig1 = px.bar(
    villages_by_state,
    x="total_villages",
    y="state",
    orientation="h",
    color="total_villages",
    color_continuous_scale="Blues",
    labels={"total_villages": "Village Count", "state": "State"},
    text="total_villages"
)
fig1.update_layout(
    yaxis=dict(autorange="reversed"),
    coloraxis_showscale=False,
    height=420
)
fig1.update_traces(texttemplate="%{text:,}", textposition="outside")
st.plotly_chart(fig1, use_container_width=True)

st.divider()

# ── Row 3: Two Charts Side by Side ───────────────────────
col_left, col_right = st.columns(2)

# Chart 3 — Districts per State
with col_left:
    st.subheader("🏙️ Districts per State")
    districts_by_state = run_query("""
        SELECT s.name AS state, COUNT(d.id) AS total_districts
        FROM states s
        JOIN districts d ON d.state_id = s.id
        GROUP BY s.name
        ORDER BY total_districts DESC
        LIMIT 15
    """)
    fig2 = px.bar(
        districts_by_state,
        x="state",
        y="total_districts",
        color="total_districts",
        color_continuous_scale="Greens",
        labels={"total_districts": "Districts", "state": "State"},
        text="total_districts"
    )
    fig2.update_layout(
        xaxis_tickangle=-45,
        coloraxis_showscale=False,
        height=420
    )
    fig2.update_traces(texttemplate="%{text}", textposition="outside")
    st.plotly_chart(fig2, use_container_width=True)

# Chart 4 — Sub Districts per State
with col_right:
    st.subheader("🏘️ Top 10 States by Sub-Districts")
    subdists_by_state = run_query("""
        SELECT s.name AS state, COUNT(sd.id) AS total_subdistricts
        FROM states s
        JOIN districts d      ON d.state_id     = s.id
        JOIN sub_districts sd ON sd.district_id = d.id
        GROUP BY s.name
        ORDER BY total_subdistricts DESC
        LIMIT 10
    """)
    fig3 = px.bar(
        subdists_by_state,
        x="state",
        y="total_subdistricts",
        color="total_subdistricts",
        color_continuous_scale="Oranges",
        labels={"total_subdistricts": "Sub-Districts", "state": "State"},
        text="total_subdistricts"
    )
    fig3.update_layout(
        xaxis_tickangle=-45,
        coloraxis_showscale=False,
        height=420
    )
    fig3.update_traces(texttemplate="%{text}", textposition="outside")
    st.plotly_chart(fig3, use_container_width=True)

st.divider()

# ── Row 4: Avg Villages per District ─────────────────────
st.subheader("📈 Average Villages per District (Top 10 States)")

avg_villages = run_query("""
    SELECT
        s.name AS state,
        COUNT(DISTINCT d.id) AS districts,
        COUNT(v.id) AS villages,
        ROUND(COUNT(v.id)::NUMERIC / COUNT(DISTINCT d.id), 0) AS avg_villages_per_district
    FROM states s
    JOIN districts d       ON d.state_id        = s.id
    JOIN sub_districts sd  ON sd.district_id    = d.id
    JOIN villages v        ON v.sub_district_id = sd.id
    GROUP BY s.name
    ORDER BY avg_villages_per_district DESC
    LIMIT 10
""")

fig4 = px.bar(
    avg_villages,
    x="state",
    y="avg_villages_per_district",
    color="avg_villages_per_district",
    color_continuous_scale="Purples",
    labels={"avg_villages_per_district": "Avg Villages", "state": "State"},
    text="avg_villages_per_district"
)
fig4.update_layout(
    xaxis_tickangle=-45,
    coloraxis_showscale=False,
    height=400
)
fig4.update_traces(texttemplate="%{text:,}", textposition="outside")
st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ── Row 5: State Explorer ─────────────────────────────────
st.subheader("🔍 State Explorer — Drill Down")

states_list = run_query("SELECT name FROM states ORDER BY name")
selected_state = st.selectbox("Select a State to explore:", states_list["name"].tolist())

if selected_state:
    col_a, col_b, col_c = st.columns(3)

    state_stats = run_query(f"""
        SELECT
            COUNT(DISTINCT d.id)  AS districts,
            COUNT(DISTINCT sd.id) AS subdistricts,
            COUNT(v.id)           AS villages
        FROM states s
        JOIN districts d       ON d.state_id        = s.id
        JOIN sub_districts sd  ON sd.district_id    = d.id
        JOIN villages v        ON v.sub_district_id = sd.id
        WHERE s.name = '{selected_state}'
    """)

    col_a.metric("Districts",     f"{state_stats['districts'][0]:,}")
    col_b.metric("Sub-Districts", f"{state_stats['subdistricts'][0]:,}")
    col_c.metric("Villages",      f"{state_stats['villages'][0]:,}")

    # Top districts in selected state
    top_districts = run_query(f"""
        SELECT d.name AS district, COUNT(v.id) AS villages
        FROM states s
        JOIN districts d       ON d.state_id        = s.id
        JOIN sub_districts sd  ON sd.district_id    = d.id
        JOIN villages v        ON v.sub_district_id = sd.id
        WHERE s.name = '{selected_state}'
        GROUP BY d.name
        ORDER BY villages DESC
        LIMIT 10
    """)

    fig5 = px.bar(
        top_districts,
        x="district",
        y="villages",
        color="villages",
        color_continuous_scale="Teal",
        title=f"Top Districts in {selected_state} by Village Count",
        labels={"villages": "Village Count", "district": "District"},
        text="villages"
    )
    fig5.update_layout(
        xaxis_tickangle=-45,
        coloraxis_showscale=False,
        height=400
    )
    fig5.update_traces(texttemplate="%{text:,}", textposition="outside")
    st.plotly_chart(fig5, use_container_width=True)

st.divider()
st.caption("🇮🇳 India Location DB | Data Source: MDDS 2011 Census | Built for B2B API Platform")