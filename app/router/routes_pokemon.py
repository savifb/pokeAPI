from fastapi import FastAPI
from models import pokemonEndPoints
from app.schemas.pokemon import PokemonListResponse
from fastapi import APIRouter
from app.database import get_sessao

router = APIRouter()


@router.get("/pokemons", response_model=PokemonListResponse)
async def get_pokemon(limit: int = 20, offset: int = 0):
    
    '''Listar pokemons  - a lógica está contida no service '''
    pass


@router.get("/pokemon/{pokemon_id}")
async def get_pokemon_by_id(pokemon_id: int):
    
    '''Buscar pokemon por id - a lógica está contida no service '''
    pass
    