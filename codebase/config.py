import os
from pathlib import Path

class Config:
    """Base configuration"""
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    FLASK_APP = 'app.py'
    
    # API settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ASSISTANT_ID = "asst_gpMZde0cPZgU0AOSgUZhVcZz"
    
    # File paths
    BASE_DIR = Path(__file__).parent
    LOG_FILE = BASE_DIR / 'app.log'
    
    # CORS settings
    CORS_HEADERS = 'Content-Type'

class DevelopmentConfig(Config):
    """Development configuration"""
    FLASK_ENV = 'development'
    DEBUG = True
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    
    # Server
    HOST = 'localhost'
    PORT = 5000

class ProductionConfig(Config):
    """Production configuration"""
    FLASK_ENV = 'production'
    DEBUG = False
    
    # Logging
    LOG_LEVEL = 'INFO'
    
    # Server
    HOST = '0.0.0.0'
    PORT = int(os.getenv('PORT', 5000))

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    
    # Use temporary directory for file operations
    import tempfile
    TEMP_DIR = tempfile.gettempdir()

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default']) 