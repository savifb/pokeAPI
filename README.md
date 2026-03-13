# pokeAPI

# 🎮 Pokémon API

![CI](https://github.com/savifb/pokeAPI/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.135-green)
![Docker](https://img.shields.io/badge/docker-ready-blue)

API REST que consome dados da [PokéAPI](https://pokeapi.co) e os disponibiliza de forma paginada, com cache local via Redis e persistência em PostgreSQL.

🚀 **Deploy:** https://pokeapi-1641.onrender.com/docs

---

## 📋 Funcionalidades

- 📋 Listagem paginada de pokémons
- 🔍 Busca de pokémon individual por ID
- ⚡ Cache Redis para respostas rápidas
- 🗄️ Persistência local com PostgreSQL
- 🐳 Dockerizado com docker-compose
- ✅ Testes unitários com pytest
- 🔄 CI/CD com GitHub Actions

---

## 🔄 Fluxo de cache

```
Requisição → Redis → PostgreSQL → PokéAPI
```

1. Verifica se o dado está no **Redis** (cache rápido)
2. Se não tiver, busca no **PostgreSQL** (banco local)
3. Se não tiver no banco, busca na **PokéAPI** e salva localmente

---

## 🛠️ Stack

| Tecnologia | Uso |
|---|---|
| FastAPI | Framework da API |
| SQLAlchemy | ORM |
| PostgreSQL | Banco de dados |
| Redis | Cache |
| Pydantic | Validação dos dados |
| Docker | Containerização |
| pytest | Testes unitários |
| GitHub Actions | CI/CD |
| Render | Deploy |

---

## 📡 Endpoints

### `GET /api/v1/pokemons`
Retorna lista paginada de pokémons.

**Query params:**
| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| limit | int | 20 | Pokémons por página (máx: 100) |
| offset | int | 0 | Posição inicial |

**Exemplo de resposta:**
```json
{
  "data": [
    {
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
  ],
  "total": 1302,
  "limit": 20,
  "offset": 0,
  "next": "/api/v1/pokemons?limit=20&offset=20",
  "previous": null
}
```

---

### `GET /api/v1/pokemons/{id}`
Retorna um pokémon específico pelo ID.

**Exemplo:**
```
GET /api/v1/pokemons/1
```

**Resposta:**
```json
{
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
```

**Status codes:**
| Código | Descrição |
|---|---|
| 200 | Pokémon encontrado |
| 404 | Pokémon não encontrado |
| 422 | ID inválido |

---

### `GET /health`
Verifica se a API está no ar.

```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

## 🚀 Como rodar localmente

### Pré-requisitos
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### 1. Clone o repositório
```bash
git clone https://github.com/savifb/pokeAPI.git
cd pokeAPI
```

### 2. Configure as variáveis de ambiente
```bash
cp .env.example .env
```

Edite o `.env` com suas configurações:
```env
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=pokemon_db
DATABASE_USER=postgres
DATABASE_PASSWORD=sua_senha

REDIS_URL=redis://localhost:6379
```

### 3. Suba os containers
```bash
docker-compose up --build
```

### 4. Acesse a API
```
http://localhost:8000/docs        → Swagger UI
http://localhost:8000/api/v1/pokemons → Endpoint principal
```

---

## 🧪 Testes

### Rodar os testes
```bash
docker-compose exec api pytest tests/ -v
```

### Rodar com relatório de cobertura
```bash
docker-compose exec api pytest tests/ -v --cov=app --cov-report=term
```

---

## 📁 Estrutura do projeto

```
pokeAPI/
├── app/
│   ├── main.py           # Ponto de entrada da aplicação
│   ├── database.py       # Configuração do PostgreSQL
│   ├── redis_client.py   # Configuração do Redis
│   ├── models/
│   │   └── pokemon.py    # Model do banco de dados
│   ├── schemas/
│   │   └── pokemon.py    # Schemas Pydantic
│   ├── router/
│   │   └── pokemon.py    # Endpoints da API
│   └── services/
│       └── pokemon.py    # Lógica de negócio e cache
├── tests/
│   ├── conftest.py       # Fixtures compartilhadas
│   ├── test_services.py  # Testes dos services
│   └── test_router.py    # Testes dos endpoints
├── .github/
│   └── workflows/
│       └── ci.yml        # Pipeline CI/CD
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## 🔄 CI/CD

A cada push na branch `main` o GitHub Actions automaticamente:

1. Sobe PostgreSQL e Redis em containers
2. Instala as dependências
3. Roda os testes com relatório de cobertura
4. Se tudo passar, o Render faz o deploy automático

---

