from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.pokemon import get_pokemon_id, get_pokemons
from app.schemas.pokemon import PokemonSchema, pokemonListReponse

router = APIRouter()


@router.get(
    "/pokemons",
    response_model=pokemonListReponse,
    summary="Lista pokémons paginados",
    description="""
Retorna uma lista paginada de pokémons.

**Fluxo de busca:**
1. Verifica o cache **Redis**
2. Se não tiver, busca no **banco PostgreSQL**
3. Se não tiver no banco, busca na **PokéAPI** e salva localmente

Use `limit` e `offset` para navegar entre as páginas.
    """,
    responses={
        200: {"description": "Lista retornada com sucesso"},
        422: {"description": "Parâmetros inválidos"}
    }
)
async def list_pokemons(
    request: Request,
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="Quantidade de pokémons por página (mín: 1, máx: 100)"
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Posição inicial da busca — ex: offset=20 pula os primeiros 20"
    ),
    db: AsyncSession = Depends(get_db)
):
    base_url = str(request.url).split("?")[0]
    return await get_pokemons(db=db, limit=limit, offset=offset, base_url=base_url)


@router.get(
    "/pokemons/{pokemon_id}",
    response_model=PokemonSchema,
    summary="Busca um pokémon pelo ID",
    description="""
Retorna os dados de um pokémon específico pelo seu ID.

**Fluxo de busca:**
1. Verifica o cache **Redis**
2. Se não tiver, busca no **banco PostgreSQL**
3. Se não tiver no banco, busca na **PokéAPI** e salva localmente

Retorna **404** se o pokémon não existir.
    """,
    responses={
        200: {"description": "Pokémon encontrado com sucesso"},
        404: {"description": "Pokémon não encontrado"},
        422: {"description": "ID inválido — deve ser um número inteiro"}
    }
)
async def get_pokemon(
    pokemon_id: int = Query(
        ...,
        description="ID numérico do pokémon — ex: 1 = Bulbasaur, 4 = Charmander, 7 = Squirtle"
    ),
    db: AsyncSession = Depends(get_db)
):
    pokemon = await get_pokemon_id(db=db, pokemon_id=pokemon_id)

    if not pokemon:
        raise HTTPException(
            status_code=404,
            detail=f"Pokémon com id {pokemon_id} não encontrado"
        )

    return pokemon