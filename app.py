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

country_list = ["All"] + sorted(df["Country"].unique().tolist())
selected_country = st.sidebar.selectbox("Select Country", country_list)


if selected_country != "All":
    df = df[df["Country"] == selected_country]

# ---------------- KPI Metrics ----------------
col1, col2, col3 = st.columns(3)

col1.metric("Average AQI", round(df["AQI Value"].mean(), 1))
col2.metric("Maximum AQI", int(df["AQI Value"].max()))

most_common = df["AQI Category"].mode()
col3.metric("Most Common Category", most_common.iloc[0] if len(most_common) else "N/A")


# ---------------- Visualization 1 ----------------
st.subheader("Top 10 Cities by Average AQI")

top_cities = (
    df.groupby("City")["AQI Value"]
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

# ---------------- Visualization 2 ----------------
st.subheader("AQI Category Distribution")

fig2, ax2 = plt.subplots()
df["AQI Category"].value_counts().plot(kind="bar", ax=ax2)
ax2.set_xlabel("AQI Category")
ax2.set_ylabel("Count")
st.pyplot(fig2)

# ---------------- Visualization 3 ----------------
st.subheader("PM2.5 vs Overall AQI")

fig3, ax3 = plt.subplots()
sns.scatterplot(
    data=df,
    x="PM2.5 AQI Value",
    y="AQI Value",
    alpha=0.4,
    ax=ax3
)
ax3.set_xlabel("PM2.5 AQI Value")
ax3.set_ylabel("Overall AQI Value")
st.pyplot(fig3)

# ---------------- Data Preview ----------------
st.subheader("Dataset Preview")
st.dataframe(df.head(50))

