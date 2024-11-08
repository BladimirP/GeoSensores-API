from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Carga las variables de entorno desde el archivo .env
load_dotenv()


# Inicializar la aplicación FastAPI
app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir solicitudes desde este origen
    allow_credentials=True,  # Permitir cookies o credenciales
    allow_methods=["*"],  # Permitir todos los métodos HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)


# Carga los endpoint
from app.routes import router
app.include_router(router)

# Ejecucion de la API
if __name__ == "__main__":
    # Configuración del entorno
    host = os.getenv("API_HOST")
    port = int(os.getenv("API_PORT"))

    # Ejecutar la aplicación con Uvicorn
    uvicorn.run(app, host=host, port=port)