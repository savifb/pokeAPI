from pydantic import BaseModel, Field
from typing import Optional


class spriteSchema(BaseModel):
    front_default: Optional[str] = Field(
        None,
        description="URL da imagem frontal do pokémon",
        example="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png"
    )
    back_default: Optional[str] = Field(
        None,
        description="URL da imagem traseira do pokémon",
        example="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/1.png"
    )


class PokemonSchema(BaseModel):
    id: int = Field(description="ID do pokémon", example=1)
    name: str = Field(description="Nome do pokémon", example="bulbasaur")
    types: list[str] = Field(description="Tipos do pokémon", example=["grass", "poison"])
    height: int = Field(description="Altura em decímetros", example=7)
    weight: int = Field(description="Peso em hectogramas", example=69)
    sprites: spriteSchema = Field(description="URLs das imagens do pokémon")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "bulbasaur",
                "types": ["grass", "poison"],
                "height": 7,
                "weight": 69,
                "sprites": {
                    "front_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/1.png",
                    "back_default": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/1.png"
                }
            }
        }
    }


class pokemonListReponse(BaseModel):
    data: list[PokemonSchema] = Field(description="Lista de pokémons retornados")
    total: int = Field(description="Total de pokémons disponíveis", example=1302)
    limit: int = Field(description="Quantidade de pokémons por página", example=20)
    offset: int = Field(description="Posição inicial da busca", example=0)
    next: Optional[str] = Field(
        None,
        description="URL da próxima página. Null se for a última.",
        example="/api/v1/pokemons?limit=20&offset=20"
    )
    previous: Optional[str] = Field(
        None,
        description="URL da página anterior. Null se for a primeira.",
        example=None
    )
