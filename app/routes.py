from . import schemas
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import APIRouter, HTTPException, Request, status
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import logging
import os

# Variables de Entorno
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
DATABASE_HOST = os.getenv("DATABASE_HOST")
MY_DATABASE = os.getenv("DATABASE_NAME")
EMAIL = os.getenv("EMAIL")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# Conexion MongoDB
client = AsyncIOMotorClient(DATABASE_HOST)
db = client[MY_DATABASE] 

users_collection = db.get_collection('users')
logs_collection = db.get_collection('logs')
infocards_collection = db.get_collection('infoCards')
treecards_collection = db.get_collection('treeCards')
trees_collection = db.get_collection('trees')
beacons_collection = db.get_collection('beacons')

# Inicialización de sistema de Loggin
logger = logging.getLogger("API_SENSORES")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("./app/logs/log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Inicialización de la aplicación FastAPI
router = APIRouter()

def serialize_mongo_document(document):
    if document:
        document["_id"] = str(document["_id"])
    return document


def enviar_correo(destinatario, asunto, cuerpo):
    # Configuración del servidor SMTP
    servidor_smtp = "smtp.gmail.com"
    puerto_smtp = 587

    # Crear el mensaje
    mensaje = MIMEMultipart()
    mensaje['From'] = EMAIL
    mensaje['To'] = destinatario
    mensaje['Subject'] = asunto
    mensaje.attach(MIMEText(cuerpo, 'plain'))

    try:
        # Conectar al servidor y enviar el correo
        servidor = smtplib.SMTP(servidor_smtp, puerto_smtp)
        servidor.starttls()  # Iniciar la conexión TLS
        servidor.login(EMAIL, EMAIL_PASS)
        servidor.send_message(mensaje)
        servidor.quit()
        return True
    
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return False

# Ruta para autenticación
@router.post("/auth")
async def login(auth: schemas.Auth, request: Request):
    try:
        # Buscar al usuario en la base de datos
        user = await users_collection.find_one({"email": auth.email})

        if (user is None):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid email"
            )

        if (user['password'] != auth.password):
            # Si el usuario no existe o la contraseña es incorrecta, devolver 404
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid password"
            )
        
        # Loggear el login exitoso
        logger.info(f"../auth, FROM: {request.client.host}, DETAIL: Successful login for {auth.email}")
        return serialize_mongo_document(user)
        
    except HTTPException as e:
        logger.error(f"../auth, FROM: {request.client.host}, STATUS: {e.status_code}")
        raise

@router.put("/change_password_and_name")
async def update_password_and_name(entry: schemas.Pass, request: Request):
    try:
        # Actualizar la contraseña y el nombre del usuario usando el email
        updated_user = await users_collection.find_one_and_update(
            {"email": entry.email},
            {"$set": {
                "password": entry.password,  # Contraseña ya encriptada
                "isEnable": False           # Nuevo nombre del usuario
            }},
            return_document=True
        )

        if updated_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Error updating user or user not found"
            )

        return {
            "message": "User updated successfully",
            "user_id": str(updated_user["_id"])
        }

    except HTTPException as e:
        logger.error(f"../change_password_and_name, FROM: {request.client.host}, STATUS: {e.status_code}")
        raise
    except Exception as e:
        logger.error(f"../change_password_and_name, FROM: {request.client.host}, ERROR: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/recovery_account")
async def recovery(entry: schemas.Recovery, request: Request):
    try:

        user = await users_collection.find_one({"email": entry.email})

        # Definir asunto y cuerpo del correo según el idioma
        language = user.get("language", "en").lower()

        if language == "en":
            subject = "GeoSensors Password Recovery"
            body = (
                f"Hello,\n\n"
                f"Your new code to log in is: {entry.code}. Please do not share this code with anyone for security reasons.\n\n"
                f"Thank you,\nGeoSensors Team"
            )
        else:  # Asumimos "es" para español
            subject = "Recuperación de contraseña GeoSensores"
            body = (
                f"Hola,\n\n"
                f"Su nuevo código para iniciar sesión es: {entry.code}. Por favor, no comparta este código con nadie por razones de seguridad.\n\n"
                f"Gracias,\nEquipo de GeoSensores"
            )

        # Enviar el correo
        if not enviar_correo(updated_user["email"], subject, body):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error sending recovery email"
            )
        
        # Actualizar la contraseña del usuario usando el email
        updated_user = await users_collection.find_one_and_update(
            {"email": entry.email},
            {"$set": {
                "password": entry.password,
                "isEnable": False
            }},
            return_document=True
        )

        if updated_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid email"
            )
        
        return str(updated_user["_id"])

    except HTTPException as e:
        logger.error(f"../recovery_account, FROM: {request.client.host}, STATUS: {e.status_code}")
        raise
    except Exception as e:
        logger.error(f"../recovery_account, FROM: {request.client.host}, ERROR: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    
    
# Ruta para crear un nuevo usuario
@router.post("/sign_up", status_code=201)
async def create_user(user: schemas.User, request: Request):
    try:
        # Verificar si el usuario ya existe
        existing_user = await users_collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        result = await users_collection.insert_one(user.dict())
        logger.info(f"../register, FROM: {request.client.host}, STATUS: 200, DETAIL: Successful login for {result.inserted_id}")

        return str(result.inserted_id)
    
    except HTTPException as e:
        logger.error(f"../register, FROM: {request.client.host}, STATUS: {e.status_code}")
        raise

@router.get("/resources")
async def get_collections(request: Request):
    try:
        # Obtener los documentos y serializarlos
        beacons = [serialize_mongo_document(doc) for doc in await beacons_collection.find().to_list(length=None)]
        infocards = [serialize_mongo_document(doc) for doc in await infocards_collection.find().to_list(length=None)]
        trees = [serialize_mongo_document(doc) for doc in await trees_collection.find().to_list(length=None)]
        treecards = [serialize_mongo_document(doc) for doc in await treecards_collection.find().to_list(length=None)]

        logger.info(f"../resources, FROM: {request.client.host}, STATUS: 200")

        return {
                "beacons": beacons,
                "infoCards": infocards,
                "trees": trees,
                "treeCards": treecards
            }
    
    except HTTPException as e:
        logger.error(f"../resources, FROM: {request.client.host}, STATUS: {e.status_code}")
        raise e
    
@router.post("/log_hito")
async def insert_log_hito(log: schemas.LogHito, request: Request):
    try:
        result = await logs_collection.insert_one(log.dict())

        logger.info(f"../log_hito, FROM: {request.client.host}, STATUS: 200, DETAIL: {result.inserted_id}")

        return str(result.inserted_id)
    
    except HTTPException as e:
        logger.error(f"../log_hito, FROM: {request.client.host}, STATUS: {e.status_code}")
        raise e
    
@router.post("/log_prox")
async def insert_log_priximidad(log: schemas.LogProximidad, request: Request):
    try:  
        result = await logs_collection.insert_one(log.dict())

        logger.info(f"../log_proximidad, FROM: {request.client.host}, STATUS: 200, DETAIL: {result.inserted_id}")

        return str(result.inserted_id)
    
    except HTTPException as e:
        logger.error(f"../log_proximidad, FROM: {request.client.host}, STATUS: {e.status_code}")
        raise e

#__________ GeoSensores - Admin __________

@router.get("/beacons")
async def get_all_beacons(request: Request):
    try:
        beacons = [serialize_mongo_document(doc) for doc in await beacons_collection.find().to_list(length=None)]
        logger.info(f"Access GET: ../beacons, FROM: {request.client.host}, STATUS: 200")
        return beacons
    except Exception as e:
        logger.error(f"Access GET: ../beacons, FROM: {request.client.host}, STATUS: 500, ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/beacon/{beacon_id}")
async def get_beacon(beacon_id: str, request: Request):
    try:
        beacon = await beacons_collection.find_one({"_id": ObjectId(beacon_id)})
        if not beacon:
            raise HTTPException(status_code=404, detail="Beacon not found")
        logger.info(f"Access GET: ../beacon, FROM: {request.client.host}, STATUS: 200, DETAIL: {beacon_id}")
        return serialize_mongo_document(beacon)
    except HTTPException as e:
        logger.error(f"Access GET: ../beacon, FROM: {request.client.host}, STATUS: {e.status_code}")
        raise e
    except Exception as e:
        logger.error(f"Access GET: ../beacon, FROM: {request.client.host}, STATUS: 500, ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/beacon")
async def create_beacon(beacon: schemas.Beacon, request: Request):
    try:
        existing_beacon = await beacons_collection.find_one({"uuid": beacon.uuid})
        if existing_beacon:
            raise HTTPException(status_code=400, detail="UUID already exist.")

        result = await beacons_collection.insert_one(beacon.dict(by_alias=True))
        
        # Agrega el ID insertado al objeto beacon
        created_beacon = beacon.dict(by_alias=True)
        created_beacon["_id"] = str(result.inserted_id)

        logger.info(f"Access POST: ../beacon, FROM: {request.client.host}, STATUS: 201, DETAIL: {result.inserted_id}")
        return created_beacon
    
    except HTTPException as e:
        logger.error(f"Access POST: ../beacon, FROM: {request.client.host}, STATUS: {e.status_code}, ERROR: {e.detail}")
        raise e
    
    except Exception as e:
        logger.error(f"Access POST: ../beacon, FROM: {request.client.host}, STATUS: 500, ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/beacon/{beacon_id}")
async def update_beacon(beacon_id: str, beacon: schemas.Beacon, request: Request):
    try:
        result = await beacons_collection.update_one({"_id": ObjectId(beacon_id)}, {"$set": beacon.dict(by_alias=True)})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Beacon not found")
        
        # Agrega el ID insertado al objeto beacon
        updated_beacon = beacon.dict(by_alias=True)
        updated_beacon["_id"] = beacon_id

        logger.info(f"Access PUT: ../beacon, FROM: {request.client.host}, STATUS: 200, DETAIL: {beacon_id}")
        
        return updated_beacon
    
    except HTTPException as e:
        logger.error(f"Access PUT: ../beacon, FROM: {request.client.host}, STATUS: {e.status_code}")
        raise e
    except Exception as e:
        logger.error(f"Access PUT: ../beacon, FROM: {request.client.host}, STATUS: 500, ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/beacon/{beacon_id}")
async def delete_beacon(beacon_id: str, request: Request):
    try:
        result = await beacons_collection.delete_one({"_id": ObjectId(beacon_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Beacon not found")
        logger.info(f"Access DELETE: ../beacon, FROM: {request.client.host}, STATUS: 200, DETAIL: {beacon_id}")
        return beacon_id
    except HTTPException as e:
        logger.error(f"Access DELETE: ../beacon, FROM: {request.client.host}, STATUS: {e.status_code}")
        raise e
    except Exception as e:
        logger.error(f"Access DELETE: ../beacon, FROM: {request.client.host}, STATUS: 500, ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    