"""
Weather Tracker - Streamlit app.
Run from the GroupProject folder:  streamlit run app.py

"""
import base64
from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st

import weather_functions as wf
import weather_visuals as wv

st.set_page_config(page_title="Weather Tracker", page_icon="🌦️", layout="wide")

# Icons for each weather condition and season.
CONDITION_ICONS = {"Sunny": "☀️", "Cloudy": "☁️", "Rainy": "🌧️", "Snowy": "❄️"}
SEASON_ICONS = {"Winter": "❄️", "Spring": "🌸", "Summer": "☀️", "Fall": "🍂"}


def render_scene(html, height):
    """Render a self-contained HTML scene inside an isolated iframe (via a data URI)."""
    src = "data:text/html;base64," + base64.b64encode(html.encode("utf-8")).decode("ascii")
    st.iframe(src, height=height)

st.title("🌦️ Weather Tracker")

# The menu is shown as tabs across the top, so every section is visible at once
# and the user just clicks (instead of opening a sidebar menu).
tab_record, tab_stats, tab_search, tab_all, tab_trend, tab_predict = st.tabs([
    "📝 Record",
    "📊 Statistics",
    "🔍 Search",
    "📋 All observations",
    "📈 Trend",
    "🔮 Predict",
])


# 1. Record a new observation
with tab_record:
    st.header("📝 Record a new observation")

    with st.form("record_form"):
        date = st.text_input("Date (MM-DD-YYYY)")
        temperature = st.number_input("🌡️ Temperature (Celsius)", step=1.0)
        condition = st.selectbox("Condition", ["Sunny", "Cloudy", "Rainy", "Snowy"])
        humidity = st.number_input("💧 Humidity (%)", min_value=0.0, max_value=100.0, step=1.0)
        wind_speed = st.number_input("🌬️ Wind speed (km/h)", min_value=0.0, step=1.0)
        submitted = st.form_submit_button("Save", icon=":material/save:")

    if submitted:
        try:
            entered = datetime.strptime(date, "%m-%d-%Y")
            date_ok = entered.date() <= datetime.today().date()
        except ValueError:
            entered = None
            date_ok = False

        if entered is None:
            st.error("Invalid date format. Please use MM-DD-YYYY.")
        elif not date_ok:
            st.error("Date cannot be in the future.")
        elif humidity <= 0:
            st.error("Humidity must be above 0 (no zero or negative).")
        elif wind_speed <= 0:
            st.error("Wind speed must be above 0 (no zero or negative).")
        else:
            wf.save_observation({
                "date": entered.strftime("%m-%d-%Y"),  # normalize to zero-padded MM-DD-YYYY
                "temperature": temperature,
                "condition": condition,
                "humidity": humidity,
                "wind_speed": wind_speed,
            })
            saved_date = entered.strftime("%m-%d-%Y")
            st.success(f"{CONDITION_ICONS.get(condition, '')} Observation for {saved_date} saved.")


# 2. View statistics
with tab_stats:
    st.header("📊 Weather statistics")
    df = wf.load_observations()
    if df.empty:
        st.info("No observations recorded yet.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("🌡️ Average", f"{round(df['temperature'].mean(), 1)} °C")
        col2.metric("❄️ Minimum", f"{df['temperature'].min()} °C")
        col3.metric("🔥 Maximum", f"{df['temperature'].max()} °C")

        common = df["condition"].mode()[0]
        col4, col5 = st.columns(2)
        col4.metric("Most common condition", f"{CONDITION_ICONS.get(common, '')} {common}")
        col5.metric("💧 Average humidity", f"{round(df['humidity'].mean(), 1)} %")

        st.caption(
            f"The highest temperature is {df['temperature'].max()} °C "
            f"and the lowest is {df['temperature'].min()} °C."
        )


# 3. Search by date  (search icon button next to the input, no placeholder text)
with tab_search:
    st.header("🔍 Search by date")

    col_input, col_button = st.columns([5, 1], vertical_alignment="bottom")
    date = col_input.text_input("Date to search (MM-DD-YYYY)")
    search = col_button.button("Search", icon=":material/search:", width="stretch")

    if search or date:
        df = wf.load_observations()
        results = df[df["date"] == date]
        if not date:
            st.info("Type a date, then press the search button.")
        elif results.empty:
            st.warning(f"No observations found for {date}.")
        else:
            for _, row in results.iterrows():
                icon = CONDITION_ICONS.get(row["condition"], "")
                st.write(f"{icon} **{row['date']}** — {row['condition']}, "
                         f"{row['temperature']} °C, humidity {row['humidity']} %, "
                         f"wind {row['wind_speed']} km/h")
            st.dataframe(results, width="stretch")


# 4. View all observations
with tab_all:
    st.header("📋 All observations")
    df = wf.load_observations()
    if df.empty:
        st.info("No observations recorded yet.")
    else:
        # include the derived season column
        df_show = wf.add_season_column(df)[wf.COLUMNS + ["season"]].copy()
        df_show.insert(0, "", df_show["condition"].map(CONDITION_ICONS).fillna(""))
        st.dataframe(df_show, width="stretch", hide_index=True)


# 5. Average temperature trend by month
with tab_trend:
    st.header("📈 Average temperature trend by month")
    df = wf.load_observations()
    if df.empty:
        st.info("No observations recorded yet.")
    else:
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        # month from the parsed date (tolerates non-zero-padded dates, e.g. "7-2-2026")
        df["month"] = pd.to_datetime(df["date"], format="%m-%d-%Y").dt.month
        monthly = df.groupby("month")["temperature"].mean().round(1)
        chart_df = pd.DataFrame({
            "Month": [month_names[m - 1] for m in monthly.index],
            "temp": monthly.values,
        })

        # Temperature is a diverging measure: colour cold -> warm (blue -> grey -> red),
        # centred on the yearly average, so the chart reads like a weather map.
        tmin, tmax = float(chart_df["temp"].min()), float(chart_df["temp"].max())
        mid = float(chart_df["temp"].mean())
        if tmin == tmax:                       # all months equal -> avoid a flat scale
            tmin, tmax = tmin - 1, tmax + 1
        if not (tmin < mid < tmax):
            mid = (tmin + tmax) / 2

        bars = alt.Chart(chart_df).mark_bar(
            cornerRadiusTopLeft=6, cornerRadiusTopRight=6, size=30,
        ).encode(
            x=alt.X("Month:N", sort=month_names,
                    axis=alt.Axis(labelAngle=0, title=None, domain=False, ticks=False,
                                  labelColor="#52514e", labelFontSize=12)),
            y=alt.Y("temp:Q", title="Average temperature (°C)",
                    axis=alt.Axis(gridColor="#e1e0d9", domain=False, ticks=False,
                                  labelColor="#898781", titleColor="#52514e")),
            color=alt.Color("temp:Q",
                            scale=alt.Scale(domain=[tmin, mid, tmax],
                                            range=["#2a78d6", "#f0efec", "#e34948"]),
                            legend=alt.Legend(title="°C", gradientLength=150)),
            tooltip=[alt.Tooltip("Month:N", title="Month"),
                     alt.Tooltip("temp:Q", title="Avg temperature", format=".1f")],
        )

        mean_rule = alt.Chart(pd.DataFrame({"avg": [mid]})).mark_rule(
            color="#898781", strokeDash=[4, 4], size=1,
        ).encode(y="avg:Q")

        chart = (bars + mean_rule).properties(width="container", height=380).configure_view(
            strokeWidth=0,
        )
        st.altair_chart(chart)
        st.caption("🌡️ Bars run blue (cooler) → red (warmer); the dashed line is the yearly average.")


# 6. Predict tomorrow  (uses the season-based prediction from weather_functions)
with tab_predict:
    st.header("🔮 Predict tomorrow's weather")
    result = wf.predict_tomorrow_result()

    if result is None:
        st.info("No observations recorded yet.")
    elif "error" in result:
        st.warning(result["error"])
    else:
        season = result["season"]
        cond = result["condition"]

        # Animated scene for the predicted condition (sun / rain / clouds / snow).
        render_scene(wv.weather_animation(cond, height=200), height=212)

        col1, col2, col3 = st.columns(3)
        col1.metric(f"{SEASON_ICONS.get(season, '')} Season", season)
        col2.metric(f"{CONDITION_ICONS.get(cond, '')} Condition", cond)
        col3.metric("🌡️ Temperature", f"{result['temp_mid']} °C",
                    help=f"between {result['temp_low']} °C and {result['temp_high']} °C")

        st.caption(result["note"])
        st.write(
            f"**Trends** — 🌡️ temperature {result['temp_trend']} · "
            f"💧 humidity {result['hum_trend']} · "
            f"🌬️ wind {result['wind_trend']}"
        )