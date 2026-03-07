# Configuração do banco de dados do postgreSQL
from dotenv import load_dotenv
import os 
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

# banco de dados do ppostgreSQL - se conecta com o bd a partir da url
# que endereça até ele no servidor,
# para se conectar ele precisa das credenciais que são essas aqui embaixo: 
# que devem ser armazenadas no ambiente seguro que não é vai para o github.
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_PORT = os.getenv('DATABASE_PORT')
DATABASE_NAME = os.getenv('DATABASE_NAME')
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_URL = f'postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'

#CRIAR O MOTOR DE CONEXÃO COM O BANCO DE DADOS - ASSÍNCRONO - o que é esse motor?
# resposta:  O motor é responsável por gerenciar as conexões com o banco de dados, 
# ele é criado a partir da URL de conexão e pode ser configurado para mostrar as queries no console
# (echo=True). Ele é usado para criar sessões de banco de dados, que são usadas
# para executar operações no banco.
engine = create_async_engine(DATABASE_URL, echo=True) 

# criando uma sessão local para ser acessada. - ASSÍNCRONA 
# o que é uma sessão? resposta: A sessão é uma interface para interagir com o banco de dados,
# ela é criada a partir do motor de conexão e é usada para executar operações no banco de dados,
# qual a diferença do engine - resposta: O engine é responsável por gerenciar as 
# conexões com o banco de dados, enquanto a sessão é uma interface para interagir com o 
# banco de dados, ela é criada a partir do motor de conexão e é usada para executar 
# operações no banco de dados. A sessão é usada para criar, ler, atualizar e deletar 
# registros no banco de dados,
# enquanto o engine é usado para criar sessões e gerenciar as conexões com o banco de dados.
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False) 


# a função get_db é uma função assíncrona que é usada para obter a sessão do banco de dados,
async def get_db():
    async with SessionLocal() as db: # aqui crio a variável db que carrega uma sessão 
        try:
            yield db # crio um gerador 
            await db.commit() # commito o que foi o comando da sessão CRUD
        except Exception:
            await db.rollback() # rollback serve para reverter as alterações feitas no banco.
            raise
        finally:
            await db.close() # após as operações, fecho a sessão do banco de dados.


# com essa classe base, podemos criar modelos do SQLAlchemy, 
# assim pode-se criar tabelas no banco de dados a partir desses modelos, 
# e o SQLAlchemy irá mapear esses modelos para as tabelas do banco de dados.
# é como se fosse uma classe para permitir a interação entre o SQLAlchemy e o banco de dados,
class Base(DeclarativeBase):
    pass
# função para criar tabelas dentro do banco - a partir dos modelos criados,
async def create_tables():
    async with engine.begin() as conn: # aqui cria-se uma variável com o engine 
        #que é a conexão com o banco de dados,
        #e o begin é usado para iniciar uma transação, CRUD - CREATE, READ, UPDATE, DELETE
        await conn.run_sync(Base.metadata.create_all) # aqui é onde as tabelas 
        #são criadas no banco de dados, a partir dos modelos criados 
        # que usaram o Base como classe base. 
        # O run_sync é usado para executar a função de criação de tabelas de forma síncrona,

''' Aqui criei e armazenei conexões e sessão com o banco de dados, tal como criei função para criação de tabelas a partir dos modelso'''

    


