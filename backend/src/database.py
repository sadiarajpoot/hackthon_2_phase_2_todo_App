from sqlmodel import create_engine, Session
from .config import settings
import urllib.parse

# Safely encode the database URL to handle special characters
database_url_encoded = settings.database_url
if '%' in settings.database_url:
    database_url_encoded = urllib.parse.unquote(settings.database_url)

# Create the database engine with additional connection pooling options
engine = create_engine(
    database_url_encoded,
    echo=settings.db_echo,  # Set to True to see SQL queries in logs
    pool_pre_ping=True,     # Verify connections before use
    pool_recycle=300,       # Recycle connections every 5 minutes
)

def get_session():
    with Session(engine) as session:
        yield session