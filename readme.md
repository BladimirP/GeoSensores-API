
# GeoSensores-API

GeoSensores-API es una aplicación diseñada para gestionar y monitorear datos de sensores geográficos utilizando una base de datos MongoDB. Este proyecto utiliza Python para crear una API RESTful, con soporte para Docker y un sistema de configuración de entorno.

## Estructura del Proyecto

La estructura de directorios es la siguiente:

```
/GeoSensores-API
│
├── /app
│   ├── /logs                     # Archivos de registro de eventos y errores
│   │   └── log                   # Archivo principal de registros
│   ├── routes.py                 # Definición y agrupación de las rutas de la API, incluidas las operaciones disponibles
│   └── schemas.py                # Definición de los esquemas de datos para validación y serialización en la API
│
├── /database                     # Mongodump de la base de datos GeoSensores
│   ├── beacons.bson              # Datos de la colección "beacons" en formato BSON
│   ├── beacons.metadata.json     # Metadatos de la colección "beacons"
│   ├── infoCards.bson            # Datos de la colección "infoCards" en formato BSON
│   ├── infoCards.metadata.json   # Metadatos de la colección "infoCards"
│   ├── logs.bson                 # Datos de la colección "logs" en formato BSON
│   ├── logs.metadata.json        # Metadatos de la colección "logs"
│   ├── treeCards.bson            # Datos de la colección "treeCards" en formato BSON
│   ├── treeCards.metadata.json   # Metadatos de la colección "treeCards"
│   ├── trees.bson                # Datos de la colección "trees" en formato BSON
│   ├── trees.metadata.json       # Metadatos de la colección "trees"
│   ├── users.bson                # Datos de la colección "users" en formato BSON
│   └── users.metadata.json       # Metadatos de la colección "users"
│
├── .env                          # Archivo de configuración de entorno con variables sensibles
├── main.py                       # Script principal para iniciar la aplicación, definiendo el servidor y los puntos de entrada
└── requirements.txt              # Archivo de dependencias necesarias para el entorno de Python
```

### Descripción de los archivos principales

mongorestore --db=GeoSensores --dir=/dump --drop
