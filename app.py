import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Global Air Quality Dashboard", layout="wide")

st.title("🌍 Global Air Quality Dashboard")
st.markdown("""
This dashboard explores global air quality using AQI values and
major air pollutants across countries and cities.
""")

@st.cache_data
def load_data():
    df = pd.read_csv("global air pollution dataset.csv")

    # Fix mixed types + missing values
    df["Country"] = df["Country"].fillna("Unknown").astype(str).str.strip()
    df["City"] = df["City"].fillna("Unknown").astype(str).str.strip()

    # Ensure numeric columns are numeric
    num_cols = ["AQI Value", "PM2.5 AQI Value", "CO AQI Value", "NO2 AQI Value", "Ozone AQI Value"]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Drop rows where AQI Value is missing after conversion
    df = df.dropna(subset=["AQI Value"])

    return df


df = load_data()

# ---------------- Sidebar Filters ----------------
st.sidebar.header("Filters")

# Country filter
country_list = ["All"] + sorted(df["Country"].dropna().unique().tolist())
selected_country = st.sidebar.selectbox("Select Country", country_list)

df_filt = df.copy()
if selected_country != "All":
    df_filt = df_filt[df_filt["Country"] == selected_country]

# City filter (depends on country selection)
city_list = ["All"] + sorted(df_filt["City"].dropna().unique().tolist())
selected_city = st.sidebar.selectbox("Select City", city_list)

if selected_city != "All":
    df_filt = df_filt[df_filt["City"] == selected_city]

# AQI Category filter
category_list = ["All"] + sorted(df_filt["AQI Category"].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Select AQI Category", category_list)

if selected_category != "All":
    df_filt = df_filt[df_filt["AQI Category"] == selected_category]

# AQI Range filter (slider)
min_aqi = float(df_filt["AQI Value"].min())
max_aqi = float(df_filt["AQI Value"].max())

aqi_range = st.sidebar.slider(
    "AQI Range",
    min_value=min_aqi,
    max_value=max_aqi,
    value=(min_aqi, max_aqi)
)

df_filt = df_filt[
    (df_filt["AQI Value"] >= aqi_range[0]) &
    (df_filt["AQI Value"] <= aqi_range[1])
]

# Pollutant selector (used in scatter plot)
pollutant_map = {
    "PM2.5": "PM2.5 AQI Value",
    "CO": "CO AQI Value",
    "NO2": "NO2 AQI Value",
    "Ozone": "Ozone AQI Value",
}
selected_pollutant = st.sidebar.selectbox("Select Pollutant (for scatter)", list(pollutant_map.keys()))
pollutant_col = pollutant_map[selected_pollutant]

st.caption(f"Showing {len(df_filt):,} rows after filters.")

# ---------------- KPI Metrics ----------------
col1, col2, col3 = st.columns(3)

col1.metric("Average AQI", round(df_filt["AQI Value"].mean(), 1) if len(df_filt) else 0)
col2.metric("Maximum AQI", int(df_filt["AQI Value"].max()) if len(df_filt) else 0)

most_common = df_filt["AQI Category"].mode()
col3.metric("Most Common Category", most_common.iloc[0] if len(most_common) else "N/A")

# ---------------- Visualization 1 ----------------
st.subheader("Top 10 Cities by Average AQI")

if len(df_filt):
    top_cities = (
        df_filt.groupby("City")["AQI Value"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )

    fig, ax = plt.subplots()
    top_cities.plot(kind="bar", ax=ax)
    ax.set_ylabel("Average AQI")
    ax.set_xlabel("City")
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig)
else:
    st.info("No data available for the selected filters.")

# ---------------- Visualization 2 ----------------
st.subheader("AQI Category Distribution")

if len(df_filt):
    fig2, ax2 = plt.subplots()
    df_filt["AQI Category"].value_counts().plot(kind="bar", ax=ax2)
    ax2.set_xlabel("AQI Category")
    ax2.set_ylabel("Count")
    st.pyplot(fig2)
else:
    st.info("No data available for the selected filters.")

# ---------------- Visualization 3 ----------------
st.subheader(f"{selected_pollutant} vs Overall AQI")

if len(df_filt):
    fig3, ax3 = plt.subplots()
    sns.scatterplot(
        data=df_filt,
        x=pollutant_col,
        y="AQI Value",
        alpha=0.4,
        ax=ax3
    )
    ax3.set_xlabel(pollutant_col)
    ax3.set_ylabel("Overall AQI Value")
    st.pyplot(fig3)
else:
    st.info("No data available for the selected filters.")

# ---------------- Data Preview ----------------
st.subheader("Dataset Preview")
st.dataframe(df_filt.head(50))
