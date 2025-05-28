import os

class Config:
    # MongoDB Configuration
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://syeddaniyalhashmi123:test123@cluster0.dutvq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "FYP")

    # API Endpoints
    BASE_API_URL = os.getenv("BASE_API_URL", "http://10.0.2.2:8000/api")
    FETCH_CATEGORIES_ENDPOINT = f"{BASE_API_URL}/fetch_categories/"
    FETCH_TOP_PRODUCTS_ENDPOINT = f"{BASE_API_URL}/fetch_top_products/"
    SEARCH_PRODUCTS_ENDPOINT = f"{BASE_API_URL}/products/search/"

    # Debug Mode
    DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"

    # Logging Configuration
    LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "app_debug.log")

# Export the configuration object
config = Config()

class Config:
    # MongoDB Configuration
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://syeddaniyalhashmi123:test123@cluster0.dutvq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "FYP")

    # API Endpoints
    BASE_API_URL = os.getenv("BASE_API_URL", "http://10.0.2.2:8000/api")
    FETCH_CATEGORIES_ENDPOINT = f"{BASE_API_URL}/fetch_categories/"
    FETCH_TOP_PRODUCTS_ENDPOINT = f"{BASE_API_URL}/fetch_top_products/"
    SEARCH_PRODUCTS_ENDPOINT = f"{BASE_API_URL}/products/search/"

    # Debug Mode
    DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"

    # Logging Configuration
    LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "app_debug.log")

# Export the configuration object
config = Config()