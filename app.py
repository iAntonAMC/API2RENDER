from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from databases import Database

# Definir el esquema de la tabla
metadata = MetaData()

personas = Table(
    "personas",
    metadata,
    Column("id_persona", Integer, primary_key=True, index=True),
    Column("nombre", String(100)),
    Column("email", String(100)),
    Column("telefono", String(15)),
)

# URL de la base de datos (deberías usar la URL interna de Render)
DATABASE_URL = "postgresql://pruebapostdb_user:Q7VByH0IrglzFARHfwIWscYD6Eyt7DKi@dpg-cse0cpm8ii6s73cp44m0-a.oregon-postgres.render.com/pruebapostdb"

# Configurar la base de datos
database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)

# Definir la aplicación FastAPI
app = FastAPI()

# Modelo para el endpoint
class Personas(BaseModel):
    nombre: str
    email: str
    telefono: str

# Crear tablas al iniciar la aplicación
@app.on_event("startup")
async def startup():
    metadata.create_all(engine)  # Crea la tabla si no existe
    await database.connect()     # Conecta la base de datos

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()  # Desconecta la base de datos

# Rutas
@app.get("/")
async def root():
    return {"message": "Hola mundo desde FastAPI"}

# Crear nueva persona
@app.post("/postpersonas/")
async def create_persona(persona: Personas):
    query = personas.insert().values(
        nombre=persona.nombre,
        email=persona.email,
        telefono=persona.telefono
    )
    last_record_id = await database.execute(query)
    return {"message": "Persona creada exitosamente", "id_persona": last_record_id}

@app.get("/personas/")
async def get_personas():
    query = personas.select()
    results = await database.fetch_all(query)
    return results
