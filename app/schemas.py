from pydantic import BaseModel, Field
from typing import Optional

class PathModel(BaseModel):
    path: str

#_________ Account _________

class Auth(BaseModel):
    email: str
    password: str

class User(BaseModel):
    firstName: str
    lastName: str
    birthday: str
    password: str
    type: str
    email: str
    language: str
    isEnable: bool

class Recovery(BaseModel):
    email: str
    password: str
    code: str

class Pass(BaseModel):
    email: str
    password: str

#__________ Loggs __________

class FechaHora(BaseModel):
    tiempo: str
    zona_horaria: str

#_______ Proximidad ________

class Proximidad(BaseModel):
    idUsuario: str
    idSensor: str

class LogProximidad(BaseModel):
    origen: str
    fuente: str
    contenido: Proximidad
    fechaHora: FechaHora

#__________ Hito ___________

class Hito(BaseModel):
    idHito: str
    idSensor: Optional[str] = None
    idUsuario: str
    coleccion: str

class LogHito(BaseModel):
    origen: str
    fuente: str
    contenido: Proximidad
    fechaHora: FechaHora

#_________ Beacon __________

class Geometry(BaseModel):
    type: str
    coordinates: list

class Beacon(BaseModel):
    uuid: str
    brand: str
    model: str
    acquisition_date: str
    activation_date: str
    battery: int
    scope: int
    geometry: Geometry