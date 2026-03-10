import redis.asyncio as redis
import os 
from dotenv import load_dotenv
import json 

load_dotenv()

REDIS_URL = os.getenv('REDIS_URL')
CACHE_TTL = 3600

redis_client = redis.from_url(REDIS_URL, decode_responses=True)


# funções para pegar os dados do cache redis

async def get_cache(key: str):
    '''busca valor no cache
    retorn none se não encontrar'''
    valor = await redis_client.get(key)
    
    if valor is None:
        return None
    
    return json.loads(valor)

#funções para salvar os dados no cache redis 

async def set_cache(key:str, valor: dict, ttl: int = CACHE_TTL):
    
    await redis_client.set(key, json.dumps(valor), ex=ttl) #expiração, redis só guarda string
    #por isso se deve converter o valor em string com  json.dumps
    # como é um json - é tratado com chave-valor - por isso precisa da key.



#funções para deletar os dados no cache redis

async def delete_cache(key: str):
    
    await redis_client.delete(key)

# função para verificar conexão redis

async def check_connection():
    try:
        await redis_client.ping()  # ✅
        return True
    except Exception:
        return False


'''
1. Conectar ao Redis
2. Fornecer funções para salvar dados
3. Fornecer funções para buscar dados
4. Fornecer funções para apagar dados
5. Definir o TTL padrão
'''