from fastapi import FastAPI,Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List,Optional
import pandas as pd


from backend.utils import forecast_for_all, filter_data

# Load dataset
DATA_FILE_PATH = "../data/processed/dataset.csv"
data = pd.read_csv(DATA_FILE_PATH)

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow requests from the React app
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all HTTP headers
)

# Define Pydantic models for response validation

class MetricResponse(BaseModel):
    total_orders: int
    average_order_value: float
    total_revenue: float
    average_feedback_score: float
    cancellation_rate: float
    top_products: Dict[str, int]
    orders_by_location: Dict[str, int]
    weather_impact: Dict[str, float]

class ForecastItem(BaseModel):
    ds: str  # Date or datetime (ISO 8601 format)
    yhat: float  # Forecasted value

class ProductLocationForecast(BaseModel):
    product: str
    location: str
    forecast: List[ForecastItem]

class ForecastResponse(BaseModel):
    status: str
    data: Optional[List[ProductLocationForecast]] = None  # Make `data` optional
    message: Optional[str] = None  # Add error message for debugging

class OrdersByDateResponse(BaseModel):
    status: str
    data: Dict[str, int]

# Helper function to calculate dashboard metrics
def calculate_dashboard_metrics() -> MetricResponse:
    metrics = {
        "total_orders": int(data["Order_Volume"].sum()),
        "average_order_value": float(data["Average_Order_Value"].mean()),
        "total_revenue": float((data["Order_Volume"] * data["Average_Order_Value"]).sum()),
        "average_feedback_score": float(data["Feedback_Score"].mean()),
        "cancellation_rate": float(data["Cancellation_Rate"].mean()),
        "top_products": data["Product"].value_counts().head(5).to_dict(),
        "orders_by_location": data.groupby("Location")["Order_Volume"].sum().to_dict(),
        "weather_impact": data.groupby("Weather")["Order_Volume"].mean().to_dict(),
    }
    return MetricResponse(**metrics)

# Endpoint to get dashboard data
@app.get("/dashboard", response_model=MetricResponse)
async def get_dashboard_data():
    try:
        dashboard_data = calculate_dashboard_metrics()
        return dashboard_data
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/forecast")
async def get_forecast(
    products: Optional[List[str]] = Query(None),
    locations: Optional[List[str]] = Query(None),
    frequency: str = "daily"
):
    if data is None:
        return {"status": "error", "message": "Dataset could not be loaded."}
    
    try:
        filtered_data = filter_data(data, products, locations, frequency)
        if filtered_data.empty:
            return {"status": "error", "message": "No data available for the selected filters."}
        
        forecasts = forecast_for_all(filtered_data, frequency)
        print(forecasts)
        
        return {"status": "success", "data": forecasts}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Run the app with Uvicorn if needed
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
