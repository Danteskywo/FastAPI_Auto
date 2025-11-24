from sqlalchemy.orm import Session 
from database import Auto, Sold
from typing import List, Optional

class CarManager:
    def __init__(self, db : Session):
        self.db = db

    def add_arrived_car(self, car_data) -> Auto:
        existing_car = self.db.query(Auto).filter(Auto.vin == car_data.vin).first()
        if existing_car:
            raise ValueError("Автомобиль с такм VIN уже существует")
        
        car = Auto(
            brand = car_data.brand,
            model=car_data.model,
            year=car_data.year,
            color=car_data.color,
            price=car_data.price,
            milage=car_data.milage,
            vin=car_data.vin,
            available=car_data.available
        )
        self.db.add(car)
        self.db.commit()
        self.db.refresh(car)
    
    def get_available_cars(self) -> List[Auto]:
        return self.db.query(Auto).filter(Auto.available == True).all()
    
    def get_car_by_id(self, car_id : int) -> Optional[Auto]:
        return self.db.query(Auto).filter(Auto.id == car_id).first()
        # if car:
        #     car.available = available
        #     self.db.commit()
        #     return True
        # return False
    def update_car_availability(self, car_id : int, available: bool) -> bool:
        car = self.db.query(Auto).filter(Auto.id == car_id).first()
        if car : 
            car.available = available
            self.db.commit()
            return True
        return False
    
    def delete_car(self, car_id:int) -> bool:
        car = self.db.query(Auto).filter(Auto.id == car_id).first()
        if car:
            self.db.delete(car)
            self.db.commit()
            return True
        return False
    
class SaleManager:
    def __init__(self, db: Session):
        self.db = db

    def sell_car(self, car_id: int, customer_data: dict) -> Sold:
        car = self.db.query(Auto).filter(Auto.id == car_id).first()
        if not car :
            raise ValueError("Автомобиль не найден!")
        if not car.available:
            raise ValueError("Автомобиль уже продан!")
        
        sale = Sold(
            car_id=car.id,
            brand=car.brand,
            model=car.model,
            year=car.year,
            color=car.color,
            sale_price=car.price,  
            customer_name=customer_data['customer_name'],
            customer_phone=customer_data['customer_phone']
        )

        car.available = False

        self.db.add(sale)
        self.db.commit()
        self.db.refresh(sale)

        return sale
    def get_sales_history(self) -> List[Sold]:
        return self.db.query(Sold).all()
    
    def get_sale_by_id(self, sale_id: int) -> Optional[Sold]:
        return self.db.query(Sold).filter(Sold.id == sale_id).first()
    


        