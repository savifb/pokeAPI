from pydantic import BaseModel, Field
from typing import Optional


class spriteSchema(BaseModel):
    front_default: Optional[str] = Field(None, description='url da imagem front')
    back_default: Optional[str] = Field(None, description='url da imagem back')


class PokemonSchema(BaseModel):
    id: int
    name: str                                        # ← era nome
    types: list[str] = Field(description='tipo do pokemon')  # ← era type
    height: int = Field(description='altura em decímetros')
    weight: int = Field(description='Peso em hectogramas')
    sprites: spriteSchema = Field(description='imagem do pokemon')
    model_config = {"from_attributes": True}


class pokemonListReponse(BaseModel):
    data: list[PokemonSchema] = Field(description='lista dos pokemons')  # ← era dados
    total: int = Field(description='total de pokemons')
    limit: int = Field(description='quantos pokemons solicitados por página')
    offset: int = Field(description='Posição da busca')
    next: Optional[str] = Field(None, description="URL da próxima página")
    previous: Optional[str] = Field(None, description="URL da página anterior")