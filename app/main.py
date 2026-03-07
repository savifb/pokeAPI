# baixando as importações necessárias ao fastapi 
from fastapi import FastAPI # inicializa app
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # roda quando a api inicia 
    print('conenctando ao banco de dados')
    # Shurdown - roda quando a api é desligada
    yield 
    print('encerrando conexão')
    
app = FastAPI(
    title="Pokémon API",
    description="...",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan, 
)

from app.router import routes_pokemon # importando os endpoints de pokemon

app.include_router(routes_pokemon.router, prefix="/api/v1") # incluindo os endpoints de pokemon na app