import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app) # simular requisição 

POKEMON_FAKE = {
    "id": 1,
    "name": "bulbasaur",
    "types": ["grass", "poison"],
    "height": 7,
    "weight": 69,
    "sprites":
        {
        "front_default": "https://example.com/front.png",
        "back_default": "https://example.com/back.png"
        }
}

LISTA_FAKE = {
    "data": [POKEMON_FAKE],
    "total": 1350,
    "limit": 20,
    "offset": 0,
    "next": "http://testserver/api/v1/pokemons?limit=20&offset=20",
    "previous": None
    
}

# ══════════════════════════════════════════════════════
# TESTES DO ENDPOINT: GET /api/v1/pokemons
# ══════════════════════════════════════════════════════

def test_list_pokemon_retorna_200():
    '''Esperado resultado 200 - para bem sucedido'''
    with patch("app.router.pokemon.get_pokemons", new_callable=AsyncMock) as mock:
        mock.return_value = LISTA_FAKE 
        response= client.get("/api/v1/pokemons")

    assert response.status_code == 200
    
    json = response.json()
    assert "data" in json
    assert "total" in json
    assert "limit" in json
    assert "offset" in json
    assert "next" in json
    assert "previous" in json

def test_list_pokemons_paginacao_parametros():
    '''teste para conferir o limit e o offset como parametros 
        o esperado é o service chamar com os valores corretors 
    '''
    with patch("app.router.pokemon.get_pokemons", new_callable=AsyncMock) as mock:
        mock.return_value = LISTA_FAKE
        
        response = client.get("/api/v1/pokemons?limit=10&offset=20")
        
        assert response.status_code == 200
        
        chamada = mock.call_args
        
        assert chamada.kwargs["limit"] == 10
        assert chamada.kwargs["offset"] == 20
        

def test_list_pokemons_limit_invalido():
    """
    Cenário: limit=0 — valor inválido (ge=1 no router).
    Esperado: status 422 (Unprocessable Entity).
    O FastAPI valida automaticamente via Query(ge=1).
    """
    response = client.get("/api/v1/pokemons?limit=0")
    assert response.status_code == 422


# ══════════════════════════════════════════════════════
# TESTES DO ENDPOINT: GET /api/v1/pokemons/{id}
# ══════════════════════════════════════════════════════

def test_get_pokemon_por_id_retorna_200():
    """
    Cenário: pokémon existe.
    Esperado: status 200 e dados corretos no JSON.
    """
    with patch("app.router.pokemon.get_pokemon_id", new_callable=AsyncMock) as mock:
        mock.return_value = POKEMON_FAKE

        response = client.get("/api/v1/pokemons/1")

    assert response.status_code == 200

    json = response.json()
    assert json["id"] == 1
    assert json["name"] == "bulbasaur"
    assert json["types"] == ["grass", "poison"]
    assert "sprites" in json


def test_get_pokemon_por_id_retorna_404():
    """
    Cenário: pokémon não existe (service retorna None).
    Esperado: status 404 com mensagem de erro.
    """
    with patch("app.router.pokemon.get_pokemon_id", new_callable=AsyncMock) as mock:
        mock.return_value = None  # simula "não encontrado"

        response = client.get("/api/v1/pokemons/99999")

    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"]


def test_get_pokemon_id_invalido():
    """
    Cenário: id não é um número inteiro.
    Esperado: status 422 — FastAPI valida o tipo automaticamente.
    """
    response = client.get("/api/v1/pokemons/abc")
    assert response.status_code == 422


# ══════════════════════════════════════════════════════
# TESTES DO ENDPOINT: GET /health
# ══════════════════════════════════════════════════════

def test_health_check():
   
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"  
    
    
