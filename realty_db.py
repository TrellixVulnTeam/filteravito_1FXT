# -*- coding: utf-8 -*-
import urllib

import pyodbc
from sqlalchemy.ext.automap import automap_base

from sqlalchemy import create_engine, MetaData, Table, Column, String, ForeignKey, Integer
#Create and engine and get the metadata
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import create_session, relationship,sessionmaker
#from sqlalchemy. access import Integer
from sqlalchemy.dialects import registry
#registry.register("access", "sqlalchemy_access.pyodbc", "AccessDialect_pyodbc")
#registry.register("access.pyodbc", "sqlalchemy_access.pyodbc", "AccessDialect_pyodbc")


Base = declarative_base()

connection_string = (
    r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
    # r'UID=admin;UserCommitSync=Yes;Threads=3;SafeTransactions=0;'
    # r'PageTimeout=5;MaxScanRows=8;MaxBufferSize=2048;FIL=MS Access;'
    # r'DriverId=25;DefaultDir=C:\REALTYDB;'
    r'DBQ=C:\REALTYDB\realty.accdb;'
    r'ExtendedAnsiSQL=1')
# engine = create_engine(connection_string)
connection_url = f"access+pyodbc:///?odbc_connect={urllib.parse.quote_plus(connection_string)}"

# engine = create_engine(connection_string)
class Person(Base):
    __tablename__ = 'person'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

class RealtyItem(Base):
    __tablename__ = 'Запись'
    # __table__ = Table(__tablename__, metadata, autoload=True,autoload_with=engine)
    #__table__ = init_table('Запись')
    # __mapper_args__ = {
    #     'primary_key': ['Объект*']
    # }
    floor=Column('Этаж*', String(255), primary_key=True)
    phone=Column('Телефон 1*', String(255), primary_key=True)
    #agent_name=Column('Организация*', Integer, )
    s_property=Column('S общ*/объекта', String(255), primary_key=True)
    s_land=Column('S уч, сот', String(255), primary_key=True)
    address=Column('Адрес', String(255), primary_key=True)
    company_id = Column('Организация*',Integer, ForeignKey('Организации.Код'),primary_key=True)
    rooms=Column('Объект*', Integer,ForeignKey('Число комнат.Код'), primary_key=True)
    forsale_forrent=Column('Актуальность*', Integer,ForeignKey('Продано, на задатке, не отвечает.Код'), primary_key=True)
    source=Column('Источник', Integer,ForeignKey('Источники.Код'))

class Company(Base):
    __tablename__ = "Организации"
    id = Column('Код', Integer, primary_key=True)
     #realty_id = Column(Integer, ForeignKey('users.id'))
    properties = relationship("RealtyItem", backref="Организации",\
                     cascade="all, delete, delete-orphan")

class Rooms(Base):
    __tablename__ = "Число комнат"
    id = Column('Код', Integer, primary_key=True)
    description = Column('Объект', Integer, primary_key=True)
    properties = relationship("RealtyItem", backref="Число комнат", \
                          cascade="all, delete, delete-orphan")

class RealtyStatus(Base):
    __tablename__ = "Продано, на задатке, не отвечает"
    id = Column('Код', Integer, primary_key=True)
    status = Column('Продано', String(255))
    properties = relationship("RealtyItem", backref="Продано, на задатке, не отвечает", \
                              cascade="all, delete, delete-orphan")

class AdvertismentSource(Base):
    __tablename__ = "Источники"
    id = Column('Код', Integer, primary_key=True)
    source = Column('Источник/Реклама', String(255))

    properties = relationship("RealtyItem", backref="Источники", \
                          cascade="all, delete, delete-orphan")

# user_table = Table('Запись', metadata,
#             Column('id', Integer, primary_key=True),
#             Column('name', String),
#         )

engine = create_engine(connection_url)
metadata = MetaData(bind=engine)
ABase = automap_base(metadata=metadata)
ABase.prepare()
metadata.reflect(bind=engine)
session = create_session(bind=engine)
# ex_table = metadata.tables
#cl = ABase.classes.items()
#print(ex_table)
#q = session.query(RealtyItem,Company).filter(Company.id=='1').filter(RealtyItem.company_id==Company.id).all()
r = RealtyItem()

# r.company_id
# r.rooms
# r.address
# r.floor
# r.s_property
# r.s_land
# r.phone

q = session.query(RealtyItem).filter_by(company_id=2).all()
print([i.phone for i in q])
session.close()
engine.dispose()


