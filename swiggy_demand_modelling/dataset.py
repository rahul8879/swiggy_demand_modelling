from pathlib import Path

import typer
from loguru import logger
from tqdm import tqdm
import pandas as pd
import random
from datetime import datetime, timedelta
from tqdm import tqdm
from swiggy_demand_modelling.config import PROCESSED_DATA_DIR, RAW_DATA_DIR

app = typer.Typer()

# Configuration
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)
locations = ["Koramangala", "Whitefield", "Indiranagar"]  # Example zones
products = ["Milk", "Bread", "Snacks", "Vegetables", "Fruits"]  # Product categories
promotions = {"Weekend Bonanza": [5, 6], "Midweek Madness": [2, 3]}  # Promotions mapped to weekdays
holidays = ["2023-01-26", "2023-08-15", "2023-10-02", "2023-11-12"]  # Example holidays

# Generate date range and initialize data
hourly_date_range = pd.date_range(start_date, end_date, freq="H")
data = []

# Utility functions
def generate_weather():
    weather_conditions = ["Clear", "Rainy", "Cloudy"]
    return random.choice(weather_conditions)

def generate_traffic():
    return random.choices(["Low", "Moderate", "High"], weights=[50, 30, 20])[0]

def is_holiday(date):
    return int(date.strftime("%Y-%m-%d") in holidays)

def is_promotion_active(day_of_week):
    for promo, days in promotions.items():
        if day_of_week in days:
            return promo
    return None

def generate_order_volume(hour, is_peak, weather, promotion):
    base_demand = 100 if not is_peak else 300
    weather_multiplier = 1.2 if weather == "Rainy" else 1.0
    promo_multiplier = 1.3 if promotion else 1.0
    return int(base_demand * weather_multiplier * promo_multiplier + random.uniform(-20, 20))

def generate_additional_features():
    return {
        "Customer_Rating": random.uniform(3.0, 5.0),
        "Distance_to_Customer": random.uniform(0.5, 15.0),
        "Warehouse_Stock_Level": random.randint(500, 10000),
        "Average_Preparation_Time": random.uniform(5, 20),
        "Delivery_Staff_Availability": random.randint(1, 50),
        "Temperature": random.uniform(15.0, 40.0),
        "Humidity": random.uniform(30.0, 90.0),
        "Air_Quality_Index": random.randint(50, 150),
        "Vehicle_Type": random.choice(["Bike", "Car", "Van"]),
        "Order_Priority": random.choice(["Low", "Medium", "High"]),
        "Coupon_Used": random.choice([True, False]),
        "Previous_Order_Cancellation": random.uniform(0.0, 0.2),
        "Delivery_Speed": random.uniform(10, 40),
        "Staff_Experience_Level": random.uniform(1, 5),
        "Fuel_Cost": random.uniform(50, 200),
        "Packaging_Cost": random.uniform(5, 20),
        "Customer_Loyalty_Points": random.randint(0, 5000),
        "Nearby_Competitors": random.randint(0, 10),
        "Seasonal_Demand_Factor": random.uniform(0.8, 1.5),
        "Payment_Type": random.choice(["Credit Card", "Debit Card", "Cash", "UPI"]),
        "Order_Frequency": random.randint(1, 10),
        "Average_Order_Value": random.uniform(100, 1000),
        "Distance_to_Warehouse": random.uniform(1, 20),
        "Customer_Age_Group": random.choice(["18-25", "26-35", "36-50", "50+"]),
        "Feedback_Score": random.uniform(3.0, 5.0),
        "Item_Returned": random.choice([True, False]),
        "Discount_Amount": random.uniform(0, 100),
        "Gift_Wrapping_Requested": random.choice([True, False]),
        "Time_Since_Last_Order": random.uniform(0, 30),
        "Weather_Severity": random.uniform(0.5, 2.0),
        "Traffic_Congestion_Index": random.uniform(0.5, 2.0),
        "Warehouse_Proximity_Score": random.uniform(1, 10)
    }



@app.command()
def main(
    # ---- REPLACE DEFAULT PATHS AS APPROPRIATE ----
    input_path: Path = RAW_DATA_DIR / "dataset.csv",
    output_path: Path = PROCESSED_DATA_DIR / "dataset.csv",
    # ----------------------------------------------
):
    
    # ---- REPLACE THIS WITH YOUR OWN CODE ----
    logger.info("Processing dataset...")
    with tqdm(total=50000, desc="Generating data") as pbar:
        while len(data) < 50000:
            for date in hourly_date_range:
                hour = date.hour
                day_of_week = date.weekday()  # Monday=0, Sunday=6
                is_peak = hour in [7, 8, 9, 18, 19, 20]  # Peak hours
                weather = generate_weather()
                traffic = generate_traffic()
                holiday_flag = is_holiday(date)
                promotion = is_promotion_active(day_of_week)

                for location in locations:
                    for product in products:
                        order_volume = generate_order_volume(hour, is_peak, weather, promotion)
                        additional_features = generate_additional_features()
                        row = {
                            "Date": date.date(),
                            "Hour": hour,
                            "Day_of_Week": date.strftime("%A"),
                            "Location": location,
                            "Product": product,
                            "Order_Volume": order_volume,
                            "Weather": weather,
                            "Traffic": traffic,
                            "Is_Holiday": holiday_flag,
                            "Promotion": promotion if promotion else "None",
                            "Delivery_Time": random.uniform(15, 40) + (5 if weather == "Rainy" else 0),
                            "Cancellation_Rate": random.uniform(0.01, 0.1) if weather == "Rainy" else random.uniform(0.0, 0.05),
                            **additional_features
                        }
                        data.append(row)
                        pbar.update(1)
                        if len(data) >= 50000:
                            break
                    if len(data) >= 50000:
                        break
                if len(data) >= 50000:
                    break
    forecasting_data = pd.DataFrame(data)
    forecasting_data.to_csv(output_path, index=False)
    logger.success("Processing dataset complete.")
    # -----------------------------------------

if __name__ == "__main__":
    app()
