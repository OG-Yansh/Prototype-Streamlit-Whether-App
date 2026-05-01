import streamlit as st
import pandas as pd
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from prophet import Prophet
from prophet.plot import plot_plotly
import warnings

warnings.filterwarnings("ignore")

# ===================== DATA LOADING =====================

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/OG-Yansh/Prototype-Streamlit-Whether-App/main/datasets/DailyDelhiClimateTrain_delhi_2017.csv"
    data = pd.read_csv(url)

    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data = data.dropna()

    data["year"] = data["date"].dt.year
    data["month"] = data["date"].dt.month

    return data


@st.cache_data
def load_train():
    url = "https://raw.githubusercontent.com/OG-Yansh/Prototype-Streamlit-Whether-App/main/datasets/AQI_ttnagar_Epics.xlsx"
    train = pd.read_excel(url, engine="openpyxl")

    train["Date"] = pd.to_datetime(train["Date"], errors="coerce")
    train["AQI No."] = pd.to_numeric(train["AQI No."], errors="coerce")

    train = train.drop(["AQI Status", "Benzene (µg/m3)"], axis=1, errors="ignore")
    train = train.dropna()

    return train


# ===================== HISTORICAL WEATHER =====================

def plot_weather(data, y, title):
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=data, x="month", y=y, hue="year")
    ax.set_title(title)
    st.pyplot(fig)


def page1(data):
    st.header("Historical Weather (Delhi)")
    st.markdown("---")

    st.subheader("Mean Temperature")
    plot_weather(data, "meantemp", "Temperature Over Years")

    st.subheader("Humidity")
    plot_weather(data, "humidity", "Humidity Over Years")

    st.subheader("Wind Speed")
    plot_weather(data, "wind_speed", "Wind Speed Over Years")


# ===================== AQI HISTORICAL =====================

def page2(train):
    st.header("AQI Historical (TT Nagar, Bhopal)")
    st.markdown("---")

    st.subheader("AQI Over Time")
    fig = px.line(train, x="Date", y="AQI No.")
    st.plotly_chart(fig)

    st.subheader("AQI Seasonality")

    temp = train.copy()
    temp["year"] = temp["Date"].dt.year
    temp["month"] = temp["Date"].dt.month

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=temp, x="month", y="AQI No.", hue="year")
    ax.set_title("AQI Trend by Year")
    st.pyplot(fig)


# ===================== FORECAST CORE (FIXED) =====================

def prophet_forecast(df, date_col, value_col, title):
    df = df.rename(columns={date_col: "ds", value_col: "y"})

    # 🔥 FULL CLEANING (this fixes your crash)
    df["ds"] = pd.to_datetime(df["ds"], errors="coerce")
    df["y"] = pd.to_numeric(df["y"], errors="coerce")

    df = df.dropna()

    # Remove duplicates properly
    df = df.sort_values("ds")
    df = df.groupby("ds", as_index=False)["y"].mean()
    df = df.reset_index(drop=True)

    # Safety check
    if len(df) < 10:
        st.error("Not enough data for forecasting.")
        return pd.DataFrame()

    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=365)
    forecast = model.predict(future)

    fig = plot_plotly(model, forecast)
    fig.add_trace(go.Scatter(x=df["ds"], y=df["y"], name="Observed"))
    fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat"], name="Predicted"))

    fig.update_layout(title=title)
    st.plotly_chart(fig)

    return forecast


def date_lookup(forecast, label):
    if forecast.empty:
        return

    date_input = st.text_input(f"Enter date for {label} (YYYY-MM-DD):", key=label)

    if date_input:
        try:
            date = pd.to_datetime(date_input)
            result = forecast[forecast["ds"] == date]

            if not result.empty:
                st.success(f"{label} on {date.date()}: {result['yhat'].values[0]:.2f}")
            else:
                st.warning("No prediction available for that date.")

        except:
            st.error("Invalid date format. Use YYYY-MM-DD")


# ===================== AQI PREDICTION =====================

def page3(train):
    st.header("AQI Predictor")
    st.markdown("---")

    forecast = prophet_forecast(train, "Date", "AQI No.", "AQI Forecast")
    date_lookup(forecast, "AQI")


# ===================== WEATHER PREDICTION =====================

def page4(data):
    st.header("Weather Predictor (Delhi)")
    st.markdown("---")

    st.subheader("Temperature Forecast")
    f1 = prophet_forecast(data, "date", "meantemp", "Temperature Forecast")
    date_lookup(f1, "Temperature")

    st.subheader("Wind Speed Forecast")
    f2 = prophet_forecast(data, "date", "wind_speed", "Wind Speed Forecast")
    date_lookup(f2, "Wind Speed")

    st.subheader("Humidity Forecast")
    f3 = prophet_forecast(data, "date", "humidity", "Humidity Forecast")
    date_lookup(f3, "Humidity")


# ===================== MAIN APP =====================

data = load_data()
train = load_train()

# Sidebar
try:
    st.sidebar.image("aero purity.jpg")
except:
    pass

page = st.sidebar.selectbox(
    "Select Page",
    [
        "Historical Weather Data (Delhi)",
        "Historical AQI Data (TT Nagar Bhopal)",
        "AQI Predictor",
        "Weather Predictor",
    ],
)


def footer():
    st.markdown("---")
    st.write("Made by Priyansh")


if page == "Historical Weather Data (Delhi)":
    page1(data)
elif page == "Historical AQI Data (TT Nagar Bhopal)":
    page2(train)
elif page == "AQI Predictor":
    page3(train)
elif page == "Weather Predictor":
    page4(data)

footer()
