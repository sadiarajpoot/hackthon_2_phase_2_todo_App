from sqlmodel import create_engine, Session
from .config import settings

# Create the database engine
engine = create_engine(
    settings.database_url,
    echo=settings.db_echo,  # Set to True to see SQL queries in logs
)

def get_session():
    with Session(engine) as session:
        yield session