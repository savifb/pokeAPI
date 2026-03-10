import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# ─────────────────────────────────────────────
# O que é conftest.py?
# É o arquivo de configuração do pytest.
# As "fixtures" definidas aqui ficam disponíveis
# automaticamente para todos os testes.
# Uma fixture é uma função que prepara algo
# antes do teste rodar — como um mock do banco.
# ─────────────────────────────────────────────

@pytest.fixture
def mock_db():
    """
    Simula a sessão do banco de dados (AsyncSession).
    Em vez de conectar num banco real, retornamos
    um objeto falso que aceita await.
    """
    db = AsyncMock()  # AsyncMock = objeto que suporta await
    return db


@pytest.fixture
def pokemon_dict():
    """
    Dicionário com dados de um pokémon — simula
    o que a PokeAPI retornaria após formatação.
    Usado em vários testes, então fica aqui no conftest.
    """
    return {
        "id": 1,
        "name": "bulbasaur",
        "height": 7,
        "weight": 69,
        "types": ["grass", "poison"],
        "sprites": {
            "front_default": "https://example.com/front.png",
            "back_default": "https://example.com/back.png"
        }
    }


@pytest.fixture
def pokemon_model(pokemon_dict):
    """
    Simula um objeto Pokemon do SQLAlchemy
    (o que viria do banco de dados).
    MagicMock cria um objeto com atributos configuráveis.
    """
    p = MagicMock()
    p.id = pokemon_dict["id"]
    p.name = pokemon_dict["name"]
    p.height = pokemon_dict["height"]
    p.weight = pokemon_dict["weight"]
    p.types = pokemon_dict["types"]
    p.sprite_front = pokemon_dict["sprites"]["front_default"]
    p.sprite_back = pokemon_dict["sprites"]["back_default"]
    return p