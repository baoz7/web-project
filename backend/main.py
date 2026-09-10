from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

# TASK 1: The Prediction Function
def predict_price(area: float, bedrooms: int, location: str) -> float:
    base = 500000000 + (area * 15000000) + (bedrooms * 50000000)
    loc = location.lower()
    
    if loc == "hanoi":
        base *= 1.3
    elif loc == "hcmc":
        base *= 1.25
        
    return round(base / 1000000) * 1000000

# TASK 2: The GET Endpoint
# We use def instead of async def because there are no blocking I/O operations (like database calls) to await.
@app.get("/predict")
def get_prediction(area: float, bedrooms: int, location: str = "other"):
    price = predict_price(area, bedrooms, location)
    return {"area": area, "bedrooms": bedrooms, "location": location, "predicted_price": price}

# TASK 6: The Bonus POST Endpoint
class HouseInput(BaseModel):
    area: float
    bedrooms: int
    location: str = "other"

@app.post("/predict")
def post_prediction(house: HouseInput):
    price = predict_price(house.area, house.bedrooms, house.location)
    return {"area": house.area, "bedrooms": house.bedrooms, "location": house.location, "predicted_price": price}

# TASK 4: Mount the Frontend (Must be at the bottom!)
app.mount("/static", StaticFiles(directory="../frontend"), name="static")