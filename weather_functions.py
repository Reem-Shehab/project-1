"""
Weather Tracker functions.
Built with %%writefile from weather_tracker.ipynb.
"""
import os
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt

CSV_FILE = "weather_data.csv"
COLUMNS = ["date", "temperature", "condition", "humidity", "wind_speed"]


# load_observations
def load_observations(filename=CSV_FILE):
    """Load all observations from the CSV, or an empty table if none yet."""
    if os.path.exists(filename):
        return pd.read_csv(filename)
    else:
        return pd.DataFrame(columns=COLUMNS)


# save_observation
def save_observation(new_data, filename=CSV_FILE):
    """Append one observation (a dict) to the CSV file, adding the derived season."""
    df_new = add_season_column(pd.DataFrame([new_data]))[COLUMNS + ["season"]]
    if not os.path.exists(filename):
        df_new.to_csv(filename, index=False)
    else:
        df_new.to_csv(filename, mode="a", header=False, index=False)


# 1. record_observation
def record_observation():
    """Ask for a new observation and save it."""
    print("\n=== Record a New Observation ===")

    while True:
        date = input("Enter the date (MM-DD-YYYY) or press Enter for today: ").strip()
        if not date:
            date = datetime.today().strftime("%m-%d-%Y")
            break
        try:
            entered = datetime.strptime(date, "%m-%d-%Y")
            if entered.date() > datetime.today().date():
                print("Date cannot be in the future. Please enter today or a past date.")
                continue
            date = entered.strftime("%m-%d-%Y")  # normalize to zero-padded MM-DD-YYYY
            break
        except ValueError:
            print("Invalid date format. Please use MM-DD-YYYY.")

    while True:
        try:
            temperature = float(input("Enter the temperature in Celsius: "))
            break
        except ValueError:
            print("Please enter a number only.")

    while True:
        condition = input("Enter the weather (Sunny, Cloudy, Rainy, Snowy): ").strip().capitalize()
        if condition == "Sunny" or condition == "Cloudy" or condition == "Rainy" or condition == "Snowy":
            break
        print("Please choose Sunny, Cloudy, Rainy or Snowy.")

    while True:
        try:
            humidity = float(input("Enter the humidity percentage (1-100): "))
            if 0 < humidity <= 100:
                break
            print("Humidity must be above 0 and at most 100 (no zero or negative).")
        except ValueError:
            print("Please enter a number only.")

    while True:
        try:
            wind_speed = float(input("Enter the wind speed in km/h: "))
            if wind_speed > 0:
                break
            print("Wind speed must be above 0 (no zero or negative).")
        except ValueError:
            print("Please enter a number only.")

    new_observation = {
        "date": date,
        "temperature": temperature,
        "condition": condition,
        "humidity": humidity,
        "wind_speed": wind_speed,
    }
    save_observation(new_observation)
    print(f"\nObservation for {date} saved successfully!")


# 2. view_statistics
def view_statistics():
    """Show average, minimum and maximum temperature and the most common condition."""
    df = load_observations()
    if df.empty:
        print("No observations recorded yet.")
        return

    avg_temp = round(df["temperature"].mean(), 1)
    minimum = df["temperature"].min()
    maximum = df["temperature"].max()
    common_condition = df["condition"].mode()[0]

    print("\n=== Weather Statistics ===")
    print(f"Average temperature: {avg_temp}C")
    print(f"Minimum temperature: {minimum}C")
    print(f"Maximum temperature: {maximum}C")
    print(f"Most common condition: {common_condition}")
    print(f"The highest temperature is {maximum}°C and the lowest is {minimum}°C.")


# 3. search_by_date
def search_by_date():
    """Ask for a date and show all observations from that date."""
    df = load_observations()
    if df.empty:
        print("No observations recorded yet.")
        return

    date = input("Enter the date to search (MM-DD-YYYY): ").strip()
    try:
        date = datetime.strptime(date, "%m-%d-%Y").strftime("%m-%d-%Y")
    except ValueError:
        print("Invalid date format. Please use MM-DD-YYYY.")
        return
    results = df[df["date"] == date]

    if results.empty:
        print(f"No observations found for {date}.")
    else:
        print(f"Observations on {date}:")
        print(results)


# 4. view_all
def view_all():
    """Show all recorded observations, including the derived season."""
    df = load_observations()
    if df.empty:
        print("No observations recorded yet.")
    else:
        print(add_season_column(df)[COLUMNS + ["season"]])


# 5. avg_temp_trend
def avg_temp_trend():
    """Bar chart of the average temperature trend by month, across all years."""
    df = load_observations()
    if df.empty:
        print("No observations recorded yet.")
        return

    # month from the parsed date
    df["month"] = pd.to_datetime(df["date"], format="%m-%d-%Y").dt.month
    monthly = df.groupby("month")["temperature"].mean()

    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    labels = [month_names[m - 1] for m in monthly.index]

    plt.figure(figsize=(8, 4))
    plt.bar(labels, monthly.values)
    plt.title("Average Temperature Trend by Month")
    plt.xlabel("Month")
    plt.ylabel("Average Temperature (C)")
    plt.tight_layout()
    plt.show()


# get_season
def get_season(m, d):
    """m = month name (from datetime, e.g. 'Dec'), d = day number and returns season """
    if (m == "Dec" and d >= 21) or (m == "Mar" and d <= 19) or (m in ("Jan", "Feb") and 0 < d <= 31):
        return "Winter"
    elif (m == "Mar" and d >= 20) or (m == "Jun" and d <= 20) or (m in ("Apr", "May") and 0 < d <= 31):
        return "Spring"
    elif (m == "Jun" and d >= 21) or (m == "Sep" and d <= 21) or (m in ("Jul", "Aug") and 0 < d <= 31):
        return "Summer"
    elif (m == "Sep" and d >= 22) or (m == "Dec" and d <= 20) or (m in ("Oct", "Nov") and 0 < d <= 31):
        return "Fall"


# add_season_column
def add_season_column(df):
    """Return a copy of df with a derived 'season' column, built from each date
    with get_season (alongside helper 'date_parsed', 'month' and 'day' columns)."""
    df = df.copy()
    df["date_parsed"] = pd.to_datetime(df["date"], format="%m-%d-%Y")
    df["month"] = df["date_parsed"].dt.strftime("%b")
    df["day"] = df["date_parsed"].dt.day
    df["season"] = df.apply(lambda r: get_season(r["month"], r["day"]), axis=1)
    return df


# 6. predict_tomorrow
def predict_tomorrow_result():
    """Return tomorrow's prediction as a dict. Returns None if there is no data,
    or a dict with an 'error' message if there are fewer than 3 observations."""
    df = load_observations()
    if df.empty:
        return None

    # add the derived season column
    df = add_season_column(df)
    df = df.sort_values("date_parsed")

    if len(df) < 3:
        return {"error": "Need at least 3 observations to see a trend."}

    recent = df.tail(4)

    # average day-to-day change of each value over the recent window
    def avg_step(col):
        v = recent[col].tolist()
        return sum(v[i + 1] - v[i] for i in range(len(v) - 1)) / (len(v) - 1)

    temp_step = avg_step("temperature")
    hum_step = avg_step("humidity")
    wind_step = avg_step("wind_speed")

    last_temp = recent["temperature"].tolist()[-1]

    # season and month of tomorrow (the day after the last record)
    tomorrow = recent["date_parsed"].tolist()[-1] + pd.Timedelta(days=1)
    tmr_month = tomorrow.strftime("%b")
    pred_season = get_season(tmr_month, tomorrow.day)

    # temperature as a RANGE:
    #   one by the recent trend, one by the average of that month across all years
    pred_trend = last_temp + temp_step
    pred_month_avg = df[df["month"] == tmr_month]["temperature"].mean()
    if pd.isna(pred_month_avg):
        pred_month_avg = pred_trend
    low = round(min(pred_trend, pred_month_avg), 1)
    high = round(max(pred_trend, pred_month_avg), 1)
    mid = round((low + high) / 2, 1)

    # condition predicted 2 ways, then validated - using the derived season column
    season_pool = df[df["season"] == pred_season]["condition"]
    by_season = season_pool.mode()[0] if not season_pool.empty else df["condition"].mode()[0]
    df["tdiff"] = (df["temperature"] - mid).abs()
    by_temp = df.sort_values("tdiff").head(10)["condition"].mode()[0]
    if by_season == by_temp:
        condition = by_season
        note = "high confidence (season and temperature agree)"
    else:
        condition = by_temp
        note = f"medium confidence (temperature suggests {by_temp}, season suggests {by_season})"

    def trend(step):
        # steady when the recent window ends where it started (net-zero change)
        if step > 1e-9:
            return "rising"
        if step < -1e-9:
            return "falling"
        return "steady"

    return {
        "season": pred_season,
        "temp_low": low,
        "temp_high": high,
        "temp_mid": mid,
        "condition": condition,
        "note": note,
        "temp_trend": trend(temp_step),
        "hum_trend": trend(hum_step),
        "wind_trend": trend(wind_step),
    }


def predict_tomorrow():
    """Predict tomorrow's temperature range and condition, then print the result."""
    result = predict_tomorrow_result()
    if result is None:
        print("No observations recorded yet.")
        return
    if "error" in result:
        print(result["error"])
        return

    print("\n=== Tomorrow's Prediction ===")
    print("Trend -> temperature", result["temp_trend"],
          "| humidity", result["hum_trend"],
          "| wind", result["wind_trend"])
    print("Season:", result["season"])
    print(f"Temperature: between {result['temp_low']}C and {result['temp_high']}C (about {result['temp_mid']}C)")
    print(f"Condition: likely {result['condition']} ({result['note']})")


# display_menu
def display_menu():
    """Show the menu and return the choice."""
    print("\n=== Weather Tracker ===")
    print("1. Record a new weather observation")
    print("2. View weather statistics")
    print("3. Search observations by date")
    print("4. View all observations")
    print("5. Average temperature trend by month")
    print("6. Predict tomorrow's weather")
    print("7. Exit")
    return input("Enter your choice (1-7): ")


# main
def main():
    """Run the menu loop."""
    print("Welcome to Weather Tracker!")
    while True:
        choice = display_menu()
        if choice == "1":
            record_observation()
        elif choice == "2":
            view_statistics()
        elif choice == "3":
            search_by_date()
        elif choice == "4":
            view_all()
        elif choice == "5":
            avg_temp_trend()
        elif choice == "6":
            predict_tomorrow()
        elif choice == "7":
            print("Thank you for using Weather Tracker. Goodbye!")
            break
        else:
            print("Please enter a number between 1 and 7.")
