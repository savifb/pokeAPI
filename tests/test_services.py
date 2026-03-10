import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# ─────────────────────────────────────────────
# O que é patch?
# patch() substitui temporariamente uma função
# real por um mock durante o teste.
# Quando o teste termina, a função original volta.
#
# Exemplo:
# with patch("app.services.pokemon.get_cache", return_value=None):
#     # aqui get_cache sempre retorna None
#     # o código real de get_cache nunca roda
# ─────────────────────────────────────────────


# ══════════════════════════════════════════════════════
# TESTES DA FUNÇÃO: estrutura_dados_daAPI
# ══════════════════════════════════════════════════════

def test_estrutura_dados_daAPI_formata_corretamente():
    """
    Testa se a função formata corretamente o JSON cru da PokeAPI.
    É uma função pura (sem banco, sem Redis) — o teste mais simples possível.
    """
    from app.services.pokemon import estrutura_dados_daAPI

    # dados crus como a PokeAPI retorna
    dados_brutos = {
        "id": 1,
        "name": "bulbasaur",
        "height": 7,
        "weight": 69,
        "types": [
            {"type": {"name": "grass"}},
            {"type": {"name": "poison"}}
        ],
        "sprites": {
            "front_default": "https://example.com/front.png",
            "back_default": "https://example.com/back.png"
        }
    }

    resultado = estrutura_dados_daAPI(dados_brutos)

    # assert = "afirmo que isso é verdade"
    # se for falso, o teste falha
    assert resultado["id"] == 1
    assert resultado["name"] == "bulbasaur"
    assert resultado["types"] == ["grass", "poison"]  # lista simples, não objetos
    assert resultado["height"] == 7
    assert resultado["sprites"]["front_default"] == "https://example.com/front.png"


# ══════════════════════════════════════════════════════
# TESTES DA FUNÇÃO: estrutura_no_banco
# ══════════════════════════════════════════════════════

def test_estrutura_no_banco_formata_corretamente(pokemon_model):
    """
    Testa se a função converte um objeto Pokemon (do banco)
    em dicionário corretamente.
    pokemon_model vem do conftest.py (fixture).
    """
    from app.services.pokemon import estrutura_no_banco

    resultado = estrutura_no_banco(pokemon_model)

    assert resultado["id"] == 1
    assert resultado["name"] == "bulbasaur"
    assert resultado["types"] == ["grass", "poison"]
    assert resultado["sprites"]["front_default"] == "https://example.com/front.png"


# ══════════════════════════════════════════════════════
# TESTES DA FUNÇÃO: get_pokemon_id
# ══════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_get_pokemon_id_retorna_cache_quando_existe(mock_db, pokemon_dict):
    """
    Cenário: o pokémon está no Redis.
    Esperado: retorna direto do cache, sem tocar no banco.

    patch() substitui get_cache por um mock que retorna pokemon_dict.
    Assim simulamos "tem cache" sem precisar de Redis real.
    """
    with patch("app.services.pokemon.get_cache", new_callable=AsyncMock) as mock_cache:
        mock_cache.return_value = pokemon_dict  # simula cache existente

        from app.services.pokemon import get_pokemon_id
        resultado = await get_pokemon_id(db=mock_db, pokemon_id=1)

    assert resultado["name"] == "bulbasaur"
    mock_cache.assert_called_once_with("Pokemon:1")  # confirmamos que buscou no cache
    mock_db.execute.assert_not_called()  # banco NÃO foi tocado


@pytest.mark.asyncio
async def test_get_pokemon_id_busca_no_banco_quando_sem_cache(mock_db, pokemon_model, pokemon_dict):
    """
    Cenário: sem cache, mas pokémon existe no banco.
    Esperado: busca no banco, salva no cache, retorna dados.
    """
    # mock_db.execute retorna um resultado que tem scalar_one_or_none()
    mock_resultado = MagicMock()
    mock_resultado.scalar_one_or_none.return_value = pokemon_model
    mock_db.execute.return_value = mock_resultado

    with patch("app.services.pokemon.get_cache", new_callable=AsyncMock) as mock_get, \
         patch("app.services.pokemon.set_cache", new_callable=AsyncMock) as mock_set:

        mock_get.return_value = None  # sem cache

        from app.services.pokemon import get_pokemon_id
        resultado = await get_pokemon_id(db=mock_db, pokemon_id=1)

    assert resultado["name"] == "bulbasaur"
    mock_set.assert_called_once()  # confirmamos que salvou no cache


@pytest.mark.asyncio
async def test_get_pokemon_id_retorna_none_quando_nao_existe(mock_db):
    """
    Cenário: sem cache, sem banco, PokeAPI retorna 404.
    Esperado: retorna None.
    """
    mock_resultado = MagicMock()
    mock_resultado.scalar_one_or_none.return_value = None  # não tem no banco
    mock_db.execute.return_value = mock_resultado

    with patch("app.services.pokemon.get_cache", new_callable=AsyncMock) as mock_get, \
         patch("app.services.pokemon.buscar_na_PokeAPI", new_callable=AsyncMock) as mock_api:

        mock_get.return_value = None   # sem cache
        mock_api.return_value = None   # PokeAPI retornou 404

        from app.services.pokemon import get_pokemon_id
        resultado = await get_pokemon_id(db=mock_db, pokemon_id=99999)

    assert resultado is None


# ══════════════════════════════════════════════════════
# TESTES DA FUNÇÃO: get_pokemons
# ══════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_get_pokemons_retorna_cache_quando_existe(mock_db):
    """
    Cenário: lista paginada está no Redis.
    Esperado: retorna do cache sem tocar no banco.
    """
    cache_fake = {
        "data": [],
        "total": 1350,
        "limit": 20,
        "offset": 0,
        "next": "http://localhost/api/v1/pokemons?limit=20&offset=20",
        "previous": None
    }

    with patch("app.services.pokemon.get_cache", new_callable=AsyncMock) as mock_cache:
        mock_cache.return_value = cache_fake

        from app.services.pokemon import get_pokemons
        resultado = await get_pokemons(
            db=mock_db, limit=20, offset=0,
            base_url="http://localhost/api/v1/pokemons"
        )

    assert resultado["total"] == 1350
    assert resultado["limit"] == 20
    mock_db.execute.assert_not_called()


@pytest.mark.asyncio
async def test_get_pokemons_pagina_corretamente(mock_db, pokemon_model):
    """
    Cenário: sem cache, banco tem pokémons.
    Esperado: retorna lista paginada com next/previous corretos.
    """
    # scalar retorna o total de pokémons no banco
    mock_db.scalar.return_value = 100

    # execute retorna lista com um pokémon
    mock_resultado = MagicMock()
    mock_resultado.scalars.return_value.all.return_value = [pokemon_model]
    mock_db.execute.return_value = mock_resultado

    with patch("app.services.pokemon.get_cache", new_callable=AsyncMock) as mock_get, \
         patch("app.services.pokemon.set_cache", new_callable=AsyncMock):

        mock_get.return_value = None  # sem cache

        from app.services.pokemon import get_pokemons
        resultado = await get_pokemons(
            db=mock_db, limit=20, offset=0,
            base_url="http://localhost/api/v1/pokemons"
        )

    assert len(resultado["data"]) == 1
    assert resultado["data"][0]["name"] == "bulbasaur"
    assert resultado["next"] is not None    # tem próxima página
    assert resultado["previous"] is None    # não tem página anterior