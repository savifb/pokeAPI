import httpx # fazer requisição para api do pokeapi

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func 
from app.models.pokemon import Pokemon
from app.schemas.pokemon import spriteSchema, pokemonListReponse, PokemonSchema
from app.redis_client import get_cache, set_cache, delete_cache, check_connection


import os 
from dotenv import load_dotenv

POKE_API_url = 'https://pokeapi.co/api/v2/'

'''---------------------------------- FORMATAR DADOS PARA API -------------------------------------------'''

def estrutura_dados_daAPI(dados: dict) -> dict:# recebe os dados da api
    return {
        "id": dados["id"],
        "name":dados["name"],
        "height": dados["height"],
        "weight": dados["weight"],
        
        "types": [t["type"]["name"] for t in dados["types"]],
        "sprites": {
            "front_default": dados["sprites"]["front_default"],
            "back_default": dados["sprites"]["back_default"],
        }
    }
'''----------------FORMATA PARA O BANCO RECEBER O OBJETO E O REDIS O JSON ----------------------'''
# função receberá um objeto do tipo pokemon (model.pokemon)
# e retornará um json/dicionário python para alocar no redis
def estrutura_no_banco(pokemon: Pokemon):
    
    return {
        "id": pokemon.id,
        "name": pokemon.name,
        "heigth": pokemon.height,
        "weight": pokemon.weight,
        "types" : pokemon.types,
        "sprites": {
            "front_default":pokemon.sprite_front,
            "back_default": pokemon.sprite_back
        }
    }
'''---------------------------------- BUSCA NA API -------------------------------------------'''
# requisição a PokeAPI 
async def buscar_na_PokeAPI(pokemon_id:int) -> dict | None:
    #async with httpx.AsyncClient() - > abre conexão com htpp e
    # fecha automaticamente mesmo se der erro
    # de maneira assíncrona
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{POKE_API_url}/pokemon/{pokemon_id}")

    if response.status_code == 404:
        return {"message" : "pokemon não encontrado"}
    
    response.raise_for_status() # qualquer outro erro 
    
    return estrutura_dados_daAPI(response.json())


'''-----------------------------------SALVAR NO BANCO DE DADOS---------------------------------'''
async def salvar_no_banco(db:AsyncSession, dados:dict) -> Pokemon:
    resultado = await db.execute(
        select(Pokemon).where(Pokemon.id==dados['id']) # resultado receberá o objeto do pokemon.id
    )
    pokemon = resultado.scalar_one_or_none() # retorna o pokemon ou none 
    if pokemon: # se existe no banco - então só atualiza os dados 
        pokemon.name = dados['name']
        pokemon.heigth = dados["heigth"]
        pokemon.weigth = dados["weight"]
        pokemon.types = dados["dados"]
        pokemon.sprites_front = dados["sprites"]["front_default"]
        pokemon.spretes_back = dados["sprites"]["back_default"]
    else:
        # caso não exista no banco vai ser criado
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
        await db.refresh()
        
        return pokemon

'''--------------------BUSCA POKEMON INDIVIDUAL--------------------------'''
async def get_pokemon(db:AsyncSession, pokemon_id:int) -> dict|None:
    #funcção que vai buscar o pokemon pelo id - passando pelo redis->banco->PokeAPi
    '''Primeiro averigua se tem no cache o dado'''
    cache = get_cache(pokemon_id) 
    if cache:
        return cache
    
    '''Averigua então se tem no banco'''
    resultado = await db.execute(select(Pokemon).where(Pokemon.id==pokemon.id))
    
    pokemon = resultado.scalar_one_or_none()
    #se tiver no banco então adiciona no cache
    if pokemon:
        dados = estrutura_dados_daAPI(pokemon)
        await set_cache(f"{pokemon_id}", dados)
        return dados
    '''vamos para api então'''
    #requisição da api
    dados = await buscar_na_PokeAPI(pokemon_id)
    
    if dados is None:
        return None # dado não existe em lugar nenhum

    await salvar_no_banco(db, dados)
    await set_cache(f'Pokemon:{pokemon_id}', dados)
    
    return dados 

async def get_pokemons(db: AsyncSession, limit: int, offset: int, base_url: str) -> dict:
    cache_key = f"pokemons: {limit}:{offset}"
    
    cache = await get_cache(cache_key)
    
    if cache:
        return cache
    
    total = await db.scalar(func.count()).select_from(Pokemon)
    
    if total > 0:
        resultado = await db.execute(
            select(Pokemon).order_by(id).limit(limit).offset(offset)
        )
        pokemons = resultado.scalarars().all()
    
        dados = [estrutura_no_banco[p] for p in pokemons]
    
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
        
    


'''
1) Verifica POKEMON redis/banco
2) Envia a requisição caso não tenha no redis e nem no banco 
3) Adiciona no banco o pokemon e no redis
'''

# Verifica Redis -> Verifica Banco -> Verifica API 
# Requisita API -> Adiciona Ao Banco -> Adiciona Ao Redis

# a tarefa do professor pede nome, type, height, weight, sprit_image_front, sprit_image_back
# na requisição é só esses dados que se deve buscar na api do pokerapi 

