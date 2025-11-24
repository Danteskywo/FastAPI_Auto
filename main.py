from fastapi import FastAPI, Depends, Body, HTTPException
from fastapi.responses import Response, JSONResponse, FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from datebase import *


class SaleCreate(BaseModel):
    car_id : int
    customer_name : str
    customer_phone : str
    sale_price : Optional[float] = None

class SaleManager:
    def __init__(self, db : Session):
        self.db = db 
        
    def sell_car(self, sale_data : SaleCreate) -> Sale:
        car = self.db.query(Auto).filter(Auto.id == sale_data.car_id).first()
        if not car:
            raise ValueError("Автомобиль не найден")
        if not car.available:
            raise ValueError("Автомобиль продан!")
        
        sale_price = sale_data.sale_price if sale_data.sale_price is not None else car.price

        sale = Sale(
            car_id = car.id,
            brand=car.brand,
            model=car.model,
            year=car.year,
            color=car.color,
            sale_price=sale_price,
            customer_name=sale_data.customer_name,
            customer_phone=sale_data.customer_phone
        )
        car.available = False

        self.db.add(sale)
        self.db.commit()
        self.db.refresh(sale)

        return sale

class CarCreate(BaseModel):
    brand : str
    model : str
    year : int
    color : str
    price : float
    milage: Optional[float] = 0.0
    vin: str
    available : Optional[bool] = True

class CarUpdate(BaseModel):
    brand: str
    model: str
    year: int
    color: str
    price: float
    milage: float
    vin: str
    available: bool

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def main():
    return FileResponse("public/index.html")

@app.get("/api/cars")
def get_cars(db: Session = Depends(get_db)):
    return db.query(Auto).all()

@app.get("/api/cars/{id}")
def get_car(id: int, db:Session = Depends(get_db)):
    car = db.query(Auto).filter(Auto.id == id).first()
    if car == None:
        return HTTPException(status_code=404, content={"message":"Автомобиль не найден"})
    return car

@app.post("/api/cars")
def create_car(data: CarCreate, db: Session = Depends(get_db)):
    
    existing_car = db.query(Auto).filter(Auto.vin == data.vin).first()
    if existing_car:
        raise HTTPException(status_code=400, detail="Автомобиль с таким VIN уже существует")
    
    car = Auto(
        brand=data.brand,
        model=data.model,
        year=data.year,
        color=data.color,
        price=data.price,
        milage=data.milage,
        vin=data.vin,
        available=data.available
    )
    db.add(car)
    db.commit()
    db.refresh(car)
    return car

@app.post("/api/sales")
def create_sale(sale_data: SaleCreate, db: Session = Depends(get_db)):
    sale_manager = SaleManager(db)
    try:
        sale = sale_manager.sell_car(sale_data)
        return sale 
    except ValueError as e : 
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/sales")
def get_sales(db: Session = Depends(get_db)):
    return db.query(Sale).all()


@app.put("/api/cars/{id}")
def edit_car(id: int, data: CarUpdate, db: Session = Depends(get_db)):
    car = db.query(Auto).filter(Auto.id == id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="Автомобиль не найден")
    
    # Проверяем уникальность VIN (если изменился)
    if data.vin != car.vin:
        existing_car = db.query(Auto).filter(Auto.vin == data.vin).first()
        if existing_car:
            raise HTTPException(status_code=400, detail="Автомобиль с таким VIN уже существует")
    
    car.brand = data.brand
    car.model = data.model
    car.year = data.year
    car.color = data.color
    car.price = data.price
    car.milage = data.milage
    car.vin = data.vin
    car.available = data.available
    
    db.commit()
    db.refresh(car)
    return car


@app.delete("/api/cars/{id}")
def delete_car(id, db: Session = Depends(get_db)):
    car = db.query(Auto).filter(Auto.id == id).first()
    if car == None:
        return JSONResponse(status_code=404, content={"message":"Автомобиль не найден"})
    db.delete(car)
    db.commit()
    return car