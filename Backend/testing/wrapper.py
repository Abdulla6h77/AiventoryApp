import requests
from config import config
from debugger import logger, log_function_call

class APIWrapper:
    @staticmethod
    @log_function_call
    def get(url, params=None, headers=None):
        try:
            response = requests.get(url, params=params, headers=headers or {"Content-Type": "application/json"})
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    @staticmethod
    @log_function_call
    def post(url, data=None, headers=None):
        try:
            response = requests.post(url, json=data, headers=headers or {"Content-Type": "application/json"})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

class DatabaseWrapper:
    def __init__(self, uri, db_name):
        from pymongo import MongoClient
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    @log_function_call
    def find(self, collection, query=None):
        try:
            return list(self.db[collection].find(query or {}))
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise

    @log_function_call
    def aggregate(self, collection, pipeline):
        try:
            return list(self.db[collection].aggregate(pipeline))
        except Exception as e:
            logger.error(f"Database aggregation failed: {e}")
            raise

    @log_function_call
    def get(url, params=None, headers=None):
        try:
            response = requests.get(url, params=params, headers=headers or {"Content-Type": "application/json"})
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    @staticmethod
    @log_function_call
    def post(url, data=None, headers=None):
        try:
            response = requests.post(url, json=data, headers=headers or {"Content-Type": "application/json"})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

class DatabaseWrapper:
    def __init__(self, uri, db_name):
        from pymongo import MongoClient
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    @log_function_call
    def find(self, collection, query=None):
        try:
            return list(self.db[collection].find(query or {}))
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise

    @log_function_call
    def aggregate(self, collection, pipeline):
        try:
            return list(self.db[collection].aggregate(pipeline))
        except Exception as e:
            logger.error(f"Database aggregation failed: {e}")
            raise    