from pydantic import BaseModel, Field
from typing import Optional
import json
import os


# pokemon individual - - conforme get/pokemon/{id}
class spriteSchema(BaseModel):
    front_default: Optional[str] = Field(None, description='url da imagem front')
    back_default: Optional[str] = Field(None, description='url da imagem back')
    


class PokemonSchema(BaseModel):
    id: int 
    nome: str
    type: list[str] = Field(description='tipo do pokemon')
    height: int = Field(description='altura em decímetros')
    weight: int = Field(description='Peso em hectogramas')
    sprites: spriteSchema = Field(description='imagem do pokemon')
    model_config = {"from_attributes": True}


# schema para resposta paginada ao usuário - todos os pokemons

class pokemonListReponse(BaseModel):
    dados: list[PokemonSchema] = Field(description='lista dos pokemons')
    total: int = Field(description='total de pokemons')
    limit: int = Field(description='quantos pokemons solicitados por página')
    offset: int = Field(description='Posição da busca')
    # link para a próxima página
    # None se já for a última página
    next: Optional[str] = Field(None, description="URL da próxima página")

    # link para a página anterior
    # None se já for a primeira página
    previous: Optional[str] = Field(None, description="URL da página anterior")

