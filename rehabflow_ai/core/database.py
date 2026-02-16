"""
Database management using SQLAlchemy for RehabFlow AI.
Handles all database operations with thread-safe connections.
"""
from sqlalchemy import create_engine, event, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator
from utils.config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

# Create base class for models
Base = declarative_base()

# Metadata instance
metadata = MetaData()


class Database:
    """Database connection and session management."""
    
    def __init__(self):
        """Initialize database engine and session factory."""
        self.engine = None
        self.session_factory = None
        self.Session = None
        self._initialize_engine()
    
    def _initialize_engine(self) -> None:
        """Create SQLAlchemy engine with appropriate configuration."""
        logger.info(f"Initializing database: {Config.DATABASE_URL}")
        
        # SQLite-specific configuration for thread safety
        if Config.DATABASE_URL.startswith("sqlite"):
            self.engine = create_engine(
                Config.DATABASE_URL,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False
            )
            # Enable WAL mode for better concurrency
            @event.listens_for(self.engine, "connect")
            def set_sqlite_pragma(dbapi_conn, connection_record):
                cursor = dbapi_conn.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.close()
        else:
            self.engine = create_engine(Config.DATABASE_URL, echo=False)
        
        # Create scoped session factory for thread safety
        session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.Session = scoped_session(session_factory)
        
        logger.info("Database engine initialized successfully")
    
    def create_tables(self) -> None:
        """Create all tables in the database."""
        logger.info("Creating database tables...")
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created successfully")
    
    def drop_tables(self) -> None:
        """Drop all tables in the database."""
        logger.warning("Dropping all database tables...")
        Base.metadata.drop_all(self.engine)
        logger.info("Database tables dropped successfully")
    
    @contextmanager
    def get_session(self) -> Generator:
        """
        Provide a transactional scope for database operations.
        
        Yields:
            SQLAlchemy session
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def close(self) -> None:
        """Close database connections."""
        if self.Session:
            self.Session.remove()
        if self.engine:
            self.engine.dispose()
        logger.info("Database connections closed")


# Global database instance
db = Database()


def get_db_session():
    """
    Dependency function to get database session.
    
    Yields:
        SQLAlchemy session
    """
    with db.get_session() as session:
        yield session
