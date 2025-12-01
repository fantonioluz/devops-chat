from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import os
from dotenv import load_dotenv

load_dotenv()

# Usar SQLite para testes, PostgreSQL para produção
if os.getenv("TEST_MODE") == "true":
    DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://devops_user:devops_password@db:5432/devops_chat"
    )
    
    # Tentar criar o database se não existir
    try:
        engine = create_engine(DATABASE_URL)
        # Testa a conexão
        with engine.connect() as conn:
            pass
    except OperationalError as e:
        if "database" in str(e) and "does not exist" in str(e):
            # Conecta no database postgres para criar o devops_chat
            from sqlalchemy.engine.url import make_url
            url = make_url(DATABASE_URL)
            default_db_url = url.set(database="postgres")
            default_engine = create_engine(default_db_url, isolation_level="AUTOCOMMIT")
            
            with default_engine.connect() as conn:
                conn.execute(text(f"CREATE DATABASE {url.database}"))
            
            default_engine.dispose()
            # Agora cria a engine para o database criado
            engine = create_engine(DATABASE_URL)
        else:
            raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
