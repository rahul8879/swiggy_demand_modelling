from prophet import Prophet
import pandas as pd
def filter_data(data, products=None, locations=None, frequency="daily"):
    if products and products != "all":
        data = data[data["Product"].isin(products)]
    if locations and locations != "all":
        data = data[data["Location"].isin(locations)]
    data["Date"] = pd.to_datetime(data["Date"])
    if frequency == "daily":
        resampled_data = data.groupby(["Date", "Product", "Location"])["Order_Volume"].sum().reset_index()
    elif frequency == "hourly":
        data["Datetime"] = data["Date"] + pd.to_timedelta(data["Hour"], unit="h")
        resampled_data = data.groupby(["Datetime", "Product", "Location"])["Order_Volume"].sum().reset_index()
    elif frequency == "monthly":
        data["Month"] = data["Date"].dt.to_period("M")
        resampled_data = data.groupby(["Month", "Product", "Location"])["Order_Volume"].sum().reset_index()
        resampled_data["Month"] = resampled_data["Month"].dt.to_timestamp()
    else:
        raise ValueError("Invalid frequency. Choose from 'daily', 'hourly', or 'monthly'.")
    return resampled_data


def forecast_for_all(filtered_data, frequency):
    results = []
    grouped_data = filtered_data.groupby(["Product", "Location"])

    for (product, location), group in grouped_data:
        # Prepare actual data (last 30 days)
        group = group[["Date" if frequency == "daily" else "Datetime", "Order_Volume"]]
        group.columns = ["ds", "y"]
        group["ds"] = pd.to_datetime(group["ds"])  # Ensure proper datetime format

        # Get the last 30 days of actual values
        actual_data = group.sort_values("ds").tail(30)  # Extract last 30 days
        actual_data["ds"] = actual_data["ds"].astype(str)  # Convert 'ds' to string

        # Train the model on all available data
        model = Prophet()
        model.fit(group)

        # Forecast future demand for the next 30 days
        future = model.make_future_dataframe(periods=30, freq="D" if frequency == "daily" else "H")
        forecast = model.predict(future)
        forecast = forecast[forecast["ds"] > group["ds"].max()]  # Only include future dates
        forecast["ds"] = forecast["ds"].astype(str)  # Convert 'ds' to string
        forecast_data = forecast[["ds", "yhat"]].to_dict(orient="records")

        # Combine actual and forecast data in the response
        results.append({
            "product": product,
            "location": location,
            "actual": actual_data.to_dict(orient="records"),  # Add actual data
            "forecast": forecast_data  # Add forecast data
        })

    return results


