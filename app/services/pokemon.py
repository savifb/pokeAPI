import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.pokemon import Pokemon
from app.schemas.pokemon import spriteSchema, pokemonListReponse, PokemonSchema
from app.redis_client import get_cache, set_cache, delete_cache, check_connection
import os
from dotenv import load_dotenv

POKE_API_url = 'https://pokeapi.co/api/v2'

def estrutura_dados_daAPI(dados: dict) -> dict:
    return {
        "id": dados["id"],
        "name": dados["name"],
        "height": dados["height"],
        "weight": dados["weight"],
        "types": [t["type"]["name"] for t in dados["types"]],
        "sprites": {
            "front_default": dados["sprites"]["front_default"],
            "back_default": dados["sprites"]["back_default"],
        }
    }

def estrutura_no_banco(pokemon: Pokemon):
    return {
        "id": pokemon.id,
        "name": pokemon.name,
        "height": pokemon.height,
        "weight": pokemon.weight,
        "types": pokemon.types,
        "sprites": {
            "front_default": pokemon.sprite_front,
            "back_default": pokemon.sprite_back
        }
    }

async def buscar_na_PokeAPI(pokemon_id: int) -> dict | None:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{POKE_API_url}/pokemon/{pokemon_id}")

    if response.status_code == 404:
        return None

    response.raise_for_status()
    return estrutura_dados_daAPI(response.json())

async def salvar_no_banco(db: AsyncSession, dados: dict) -> Pokemon:
    resultado = await db.execute(
        select(Pokemon).where(Pokemon.id == dados['id'])
    )
    pokemon = resultado.scalar_one_or_none()

    if pokemon:
        pokemon.name = dados["name"]
        pokemon.height = dados["height"]
        pokemon.weight = dados["weight"]
        pokemon.types = dados["types"]
        pokemon.sprite_front = dados["sprites"]["front_default"]
        pokemon.sprite_back = dados["sprites"]["back_default"]
    else:
        pokemon = Pokemon(
            id=dados["id"],
            name=dados["name"],
            height=dados["height"],
            weight=dados["weight"],
            types=dados["types"],
            sprite_front=dados["sprites"]["front_default"],
            sprite_back=dados["sprites"]["back_default"],
        )
        db.add(pokemon)

    await db.commit()
    await db.refresh(pokemon)
    return pokemon

async def get_pokemon_id(db: AsyncSession, pokemon_id: int) -> dict | None:
    cache = await get_cache(f"Pokemon:{pokemon_id}")
    if cache:
        return cache

    resultado = await db.execute(select(Pokemon).where(Pokemon.id == pokemon_id))
    pokemon = resultado.scalar_one_or_none()

    if pokemon:
        dados = estrutura_no_banco(pokemon)
        await set_cache(f"Pokemon:{pokemon_id}", dados)
        return dados

    dados = await buscar_na_PokeAPI(pokemon_id)

    if dados is None:
        return None

    await salvar_no_banco(db, dados)
    await set_cache(f'Pokemon:{pokemon_id}', dados)
    return dados

async def get_pokemons(db: AsyncSession, limit: int, offset: int, base_url: str) -> dict:
    cache_key = f"pokemons:{limit}:{offset}"

    cache = await get_cache(cache_key)
    if cache:
        return cache

    # ✅ Bug 1 corrigido — query montada antes do await
    total = await db.scalar(select(func.count()).select_from(Pokemon))

    if total > 0:
        resultado = await db.execute(
            # ✅ Bug 6 corrigido — Pokemon.id em vez de id
            select(Pokemon).order_by(Pokemon.id).limit(limit).offset(offset)
        )
        # ✅ Bug 5 corrigido — scalars() e chamada de função
        pokemons = resultado.scalars().all()
        dados = [estrutura_no_banco(p) for p in pokemons]

    else:
        dados = []
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{POKE_API_url}/pokemon",
                params={"limit": limit, "offset": offset}
            )
            response.raise_for_status()
            resultados = response.json()["results"]
            total = response.json()["count"]

            for item in resultados:
                detalhe = await client.get(item["url"])
                detalhe.raise_for_status()
                pokemon_formatado = estrutura_dados_daAPI(detalhe.json())
                await salvar_no_banco(db, pokemon_formatado)
                dados.append(pokemon_formatado)

    resposta = {
        "data": dados,
        "total": total,
        "limit": limit,
        "offset": offset,
        "next": f"{base_url}?limit={limit}&offset={offset + limit}"
                if offset + limit < total else None,
        "previous": f"{base_url}?limit={limit}&offset={offset - limit}"
                    if offset > 0 else None,
    }

    await set_cache(cache_key, resposta)
    return resposta