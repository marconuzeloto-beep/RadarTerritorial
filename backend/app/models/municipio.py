from sqlalchemy import Column, Integer, String, Numeric
from geoalchemy2 import Geometry
from app.database.connection import Base


class Municipio(Base):
    __tablename__ = "municipios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo_ibge = Column(String(7), unique=True, nullable=False, index=True)
    nome = Column(String(100), nullable=False, index=True)
    uf = Column(String(2), nullable=False)
    latitude = Column(Numeric(10, 7), nullable=False)
    longitude = Column(Numeric(10, 7), nullable=False)
    geom = Column(Geometry("POINT", srid=4326), nullable=False)
    populacao = Column(Integer, nullable=True)
