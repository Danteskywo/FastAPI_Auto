from fastapi import FastAPI, Depends, Body, HTTPException
from fastapi.responses import Response, JSONResponse, FileResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from database import *
from managers import CarManager, SaleManager
from models import CarCreate, CarUpdate, SaleCreate, SaleResponse


# class SaleResponse(BaseModel):
#     id : int
#     car_id : int
#     brand : str
#     model : str
#     year : int
#     color : str
#     sale_price : float
#     customer_name : str
#     customer_phone : str
#     sale_date: datetime

#     class Config:
#         from_attributes = True

# class SaleCreate(BaseModel):
#     car_id : int
#     customer_name : str
#     customer_phone : str
#     sale_price : Optional[float] = None

# class SaleManager:
#     def __init__(self, db : Session):
#         self.db = db 
        
#     def sell_car(self, sale_data : SaleCreate) -> Sold:
#         car = self.db.query(Auto).filter(Auto.id == sale_data.car_id).first()
#         if not car:
#             raise ValueError("Автомобиль не найден")
#         if not car.available:
#             raise ValueError("Автомобиль продан!")
        
#         sale_price = sale_data.sale_price if sale_data.sale_price is not None else car.price

#         sale = Sold(
#             car_id = car.id,
#             brand=car.brand,
#             model=car.model,
#             year=car.year,
#             color=car.color,
#             sale_price=sale_price,
#             customer_name=sale_data.customer_name,
#             customer_phone=sale_data.customer_phone
#         )
#         car.available = False

#         self.db.add(sale)
#         self.db.commit()
#         self.db.refresh(sale)

#         return sale

# class CarCreate(BaseModel):
#     brand : str
#     model : str
#     year : int
#     color : str
#     price : float
#     milage: Optional[float] = 0.0
#     vin: str
#     available : Optional[bool] = True

# class CarUpdate(BaseModel):
#     brand: str
#     model: str
#     year: int
#     color: str
#     price: float
#     milage: float
#     vin: str
#     available: bool

# Base.metadata.create_all(bind=engine)

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

@app.get("/api/cars/available")
def get_available_cars(db: Session = Depends(get_db)):
    car_manager = CarManager(db)
    return car_manager.get_available_cars()


@app.get("/api/cars/{id}")
def get_car(id: int, db:Session = Depends(get_db)):
    car_manager = CarManager(db)
    car = car_manager.get_car_by_id(id)
    if car is None:
        raise HTTPException(status_code=404, detail="Автомобиль не найден!")
    return car

@app.post("/api/cars")
def create_car(data: CarCreate, db: Session = Depends(get_db)):
    car_manager = CarManager(db)
    try:
        return car_manager.add_arrived_car(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/cars/{id}")
def edit_car(id: int, data: CarUpdate, db: Session = Depends(get_db)):
    car = db.query(Auto).filter(Auto.id == id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="Автомобиль не найден")
    
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
def delete_car(id: int, db: Session = Depends(get_db)):
    car = db.query(Auto).filter(Auto.id == id).first()
    if car is None:
        return JSONResponse(status_code=404, content={"message": "Автомобиль не найден"})
    db.delete(car)
    db.commit()
    return car

@app.post("/api/sales", response_model=SaleResponse)
def create_sale(data: SaleCreate, db: Session = Depends(get_db)):
    sale_manager = SaleManager(db)
    try:
        customer_data = {
            'customer_name': data.customer_name,
            'customer_phone': data.customer_phone
        }
        sale = sale_manager.sell_car(data.car_id, customer_data)
        return sale
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/sales", response_model=List[SaleResponse])
def get_sales(db: Session = Depends(get_db)):
    sale_manager = SaleManager(db)
    return sale_manager.get_sales_history()

@app.get("/api/sales/{id}", response_model=SaleResponse)
def get_sale(id: int, db: Session = Depends(get_db)):
    sale_manager = SaleManager(db)
    sale = sale_manager.get_sale_by_id(id)
    if sale is None:
        raise HTTPException(status_code=404, detail="Продажа не найдена")
    return sale

@app.patch("/api/cars/{id}/status")
def update_car_status(id: int, available: bool, db: Session = Depends(get_db)):
    
    car_manager = CarManager(db)
    success = car_manager.update_car_status(id, available)
    if not success:
        raise HTTPException(status_code=404, detail="Автомобиль не найден")
    return {"message": "Статус автомобиля обновлен"}

@app.put("/api/cars/{id}")
def edit_car(id: int, data: CarUpdate, db: Session = Depends(get_db)):
    car = db.query(Auto).filter(Auto.id == id).first()
    if car is None:
        raise HTTPException(status_code=404, detail="Автомобиль не найден")
    
    
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