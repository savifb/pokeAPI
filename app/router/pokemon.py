# app/routers/pokemon.py

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.pokemon import get_pokemon, get_pokemons
from app.schemas.pokemon import PokemonSchema, pokemonListReponse 
router = APIRouter()


# ─── GET /pokemons ────────────────────────────────────────
@router.get(
    "/pokemons",
    response_model=pokemonListReponse,
    summary="Lista pokémons",
    description="Retorna uma lista paginada de pokémons."
)
async def list_pokemons(
    request: Request,
    limit: int = Query(20, ge=1, le=100, description="Pokémons por página"),
    offset: int = Query(0, ge=0, description="Posição inicial"),
    db: AsyncSession = Depends(get_db)
):
    base_url = str(request.url).split("?")[0]
    return await get_pokemons(db=db, limit=limit, offset=offset, base_url=base_url)


# ─── GET /pokemons/{id} ───────────────────────────────────
@router.get(
    "/pokemons/{pokemon_id}",
    response_model=PokemonSchema,
    summary="Busca um pokémon pelo ID",
    description="Retorna os dados de um pokémon específico."
)
async def get_pokemon(
    pokemon_id: int,
    db: AsyncSession = Depends(get_db)
):
    pokemon = await get_pokemon(db=db, pokemon_id=pokemon_id)

    if not pokemon:
        raise HTTPException(
            status_code=404,
            detail=f"Pokémon com id {pokemon_id} não encontrado"
        )

    return pokemon