# app/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Iniciando aplicação...")

    # conecta ao banco e cria as tabelas
    from app.database import create_tables
    await create_tables()
    print("✅ Banco conectado")

    # testa o Redis
    from app.redis_client import check_connection
    redis_ok = await check_connection()
    if redis_ok:
        print("✅ Redis conectado")
    else:
        print("⚠️  Redis não disponível")

    yield

    print("🛑 Encerrando aplicação...")

app = FastAPI(
    title="Pokémon API",
    description="""
## API de Pokémons 🎮

API REST que consome dados da [PokéAPI](https://pokeapi.co) e os disponibiliza 
de forma paginada com cache local.

### Funcionalidades
- 📋 **Listagem paginada** de pokémons
- 🔍 **Busca por ID** de pokémon individual
- ⚡ **Cache Redis** para respostas rápidas
- 🗄️ **Banco PostgreSQL** para persistência local

### Fluxo de cache
```
Redis → PostgreSQL → PokéAPI
```
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# importa e registra o router
from app.router import pokemon as pokemon_router

app.include_router(
    pokemon_router.router,
    prefix="/api/v1",
    tags=["Pokémons"]
)


@app.get("/health", tags=["Health"])
def health_check():
    """Verifica se a API está no ar."""
    return {"status": "ok", "version": "1.0.0"}
