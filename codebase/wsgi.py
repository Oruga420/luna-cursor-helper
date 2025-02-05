from app import app

if __name__ == "__main__":
    # Get configuration
    from config import get_config
    config = get_config()
    
    # Run the application
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    ) 