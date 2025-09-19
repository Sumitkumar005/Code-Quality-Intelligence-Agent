"""
SQLite database session management
"""
import sqlite3
import structlog

logger = structlog.get_logger(__name__)

async def init_db():
    """Initialize SQLite database"""
    try:
        conn = sqlite3.connect('cqia_tool.db')
        cursor = conn.cursor()
        
        # Create basic tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_reports (
                id TEXT PRIMARY KEY,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # Don't fail startup for database issues
        pass