import httpx # fazer requisição para api do pokeapi

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import seclect, func 
from app.models.pokemon import Pokemon
from app.schemas.pokemon import spriteSchema, pokemonListReponse, PokemonSchema
from app.redis_client import get_cache, set_cache, delete_cache, check_connection


import os 
from dotenv import load_dotenv

POKE_API_url = 'https://pokeapi.co/api/v2/'

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


'''

1) Verifica POKEMON redis/banco
2) Envia a requisição caso não tenha no redis e nem no banco 
3) Adiciona no banco o pokemon e no redis
'''

# Verifica Redis -> Verifica Banco -> Verifica API 
# Requisita API -> Adiciona Ao Banco -> Adiciona Ao Redis

# a tarefa do professor pede nome, type, height, weight, sprit_image_front, sprit_image_back
# na requisição é só esses dados que se deve buscar na api do pokerapi 

