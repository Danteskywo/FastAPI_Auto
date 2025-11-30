from sqlalchemy.orm import Session 
from database import Auto, Sold
from models import CarCreate
from typing import List, Optional

class CarManager:
    def __init__(self, db : Session):
        self.db = db

    def get_available_cars(self):
        return self.db.query(Auto).filter(Auto.available == True).all()
    
    def get_car_by_id(self, id: int):
        return self.db.query(Auto).filter(Auto.id == id).first()

    def add_arrived_car(self, data:CarCreate) -> Auto:
        existing_car = self.db.query(Auto).filter(Auto.vin == data.vin).first()
        if existing_car:
            raise ValueError("Автомобиль с такм VIN уже существует")
        
        new_car = Auto(
            brand = data.brand,
            model=data.model,
            year=data.year,
            color=data.color,
            price=data.price,
            milage=data.milage,
            vin=data.vin,
            available=data.available
        )
        self.db.add(new_car)
        self.db.commit()
        self.db.refresh(new_car)
        return new_car
    

    def update_car_status(self, id: int, available: bool):
        car = self.db.query(Auto).filter(Auto.id == id).first()
        if car:
            car.available = available
            self.db.commit()
            return True
        return False

    
class SaleManager:
    def __init__(self, db: Session):
        self.db = db 
        
    def sell_car(self, sale_data):
        car = self.db.query(Auto).filter(Auto.id == sale_data.car_id).first()
        if not car:
            raise ValueError("Автомобиль не найден")
        if not car.available:
            raise ValueError("Автомобиль уже продан!")
        

        sale_price = sale_data.sale_price if sale_data.sale_price is not None else car.price

        # Создаем запись о продаже
        sale = Sold(
            car_id=car.id,
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
    
    def get_sales_history(self) -> List[Sold]:
        return self.db.query(Sold).all()
    
    def get_sale_by_id(self, id: int):
        return self.db.query(Sold).filter(Sold.id == id).first()