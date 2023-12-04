from sqlalchemy import Integer,String,ForeignKey,Date,create_engine,UniqueConstraint
from sqlalchemy.orm import DeclarativeBase,sessionmaker
from sqlalchemy.orm import Mapped,mapped_column,relationship    
import datetime
import logging
from typing import List

class Base(DeclarativeBase):
        def __repr__(self):
            return f"{self.__class__.__name__}(id={self.id})"

class Designation(Base):
    __tablename__="hrms_designation"
    id : Mapped[int] = mapped_column(primary_key=True)
    title : Mapped[str] = mapped_column(String(50),unique=True)
    max_leaves : Mapped[int] = mapped_column(Integer)
    employee : Mapped[List["Employee"]] = relationship("Employee",back_populates="title")


class Employee(Base):
    __tablename__="hrms_employees"
    id : Mapped[int] = mapped_column(primary_key=True)
    fname: Mapped[str] =  mapped_column(String(50))
    lname: Mapped[str] =  mapped_column(String(50))
    title_id:Mapped[int] = mapped_column(ForeignKey('hrms_designation.id'))
    email: Mapped[str] =  mapped_column(String(120),unique=True)
    phone: Mapped[str] =  mapped_column(String(50))

    title :Mapped["Designation"] =relationship("Designation",back_populates="employee")

class Leave(Base):
    __tablename__="hrms_employee_leaves"
    __table_args__ = (        
        UniqueConstraint("employee_id", "date"),
        )
    id : Mapped[int] = mapped_column(primary_key=True)
    date : Mapped[datetime.date] = mapped_column(Date())
    employee_id : Mapped[int] = mapped_column(ForeignKey('hrms_employees.id'))
    reason : Mapped[str] = mapped_column(String(120))

def create_all(db_uri):
     logger = logging.getLogger('HR')
     engine = create_engine(db_uri)
     Base.metadata.create_all(engine)
     logging.info('Schema Created')

def get_session(db_uri):
     engine = create_engine(db_uri)
     Session = sessionmaker(bind=engine)
     session = Session()
     return session

     

