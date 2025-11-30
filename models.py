from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class SaleResponse(BaseModel):
    class SaleResponse(BaseModel):
        id: int
        car_id: int
        brand: str
        model: str
        year: int
        color: str
        sale_price: float
        customer_name: str
        customer_phone: str
        sale_date: datetime

        class Config:
            from_attributes = True

class SaleCreate(BaseModel):
    car_id: int
    customer_name: str
    customer_phone: str
    sale_price: Optional[float] = None

class CarCreate(BaseModel):
    brand: str
    model: str
    year: int
    color: str
    price: float
    milage: Optional[float] = 0.0
    vin: str
    available: Optional[bool] = True

class CarUpdate(BaseModel):
    brand: str
    model: str
    year: int
    color: str
    price: float
    milage: float
    vin: str
    available: bool
