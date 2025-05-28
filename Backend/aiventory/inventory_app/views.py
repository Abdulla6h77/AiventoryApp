from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.response import Response
from pymongo.errors import PyMongoError
from django.http import JsonResponse
from pymongo import MongoClient
import bcrypt
import logging
import re 
import pymongo
from bson import ObjectId
import traceback 
# Set up logging



# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from pymongo import DESCENDING


# MongoDB Atlas connection
MONGO_CLIENT = pymongo.MongoClient(
    "mongodb+srv://syeddaniyalhashmi123:test123@cluster0.dutvq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
     serverSelectionTimeoutMS=60000  # increase timeout
)
db = MONGO_CLIENT["FYP"]  # Your database

# YOUR GOOGLE CLIENT ID FROM GOOGLE CLOUD CONSOLE
GOOGLE_CLIENT_ID = "http://27195329264-b2pfndu60f211lrug5cslic4qpou0apl.apps.googleusercontent.com"

@csrf_exempt
@api_view(['POST'])
def signup(request):
    try:
        data = request.data
        
        # Validate required fields
        required_fields = ['name', 'email', 'password']
        if not all(field in data for field in required_fields):
            return JsonResponse(
                {"error": "All fields are required"},
                status=400,
                content_type="application/json"
            )
            
        # Validate email
        if not re.match(r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$', data['email'], re.IGNORECASE):
            return JsonResponse(
                {"error": "Invalid email"},
                status=400,
                content_type="application/json"
            )
            
        # Check existing user
        if db.userPhone.find_one({"email": data['email']}):
            return JsonResponse(
                {"error": "This email is already registered"},
                status=409,
                content_type="application/json"
            )
            
        # Hash password
        hashed = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt())
        
        # Insert user
        result = db.userPhone.insert_one({
            "name": data['name'],
            "email": data['email'],
            "password": hashed.decode()
        })
        
        return JsonResponse(
            {"success": True, "user_id": str(result.inserted_id)},
            status=201,
            content_type="application/json"
        )
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        traceback.print_exc()
        return JsonResponse(
            {"error": "An unexpected error occurred"},
            status=500,
            content_type="application/json"
        )

#google signup 
@csrf_exempt  
@api_view(['POST'])
def google_signup(request):
    try:
        token = request.data.get("token")
        if not token:
            return JsonResponse({"error": "Token is required"}, status=400)

        # Verify the Google ID token
        id_info = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)

        # Check that the token is valid and issued by Google
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com ']:
            return JsonResponse({"error": "Invalid issuer"}, status=400)

        email = id_info['email']
        name = id_info.get('name', '')

        # Check if user exists
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            return JsonResponse({"error": "Email already registered"}, status=409)

        # Create new user
        hashed_password = bcrypt.hashpw(email.encode() + b"_google_oauth", bcrypt.gensalt())
        result = users_collection.insert_one({
            "name": name,
            "email": email,
            "password": hashed_password.decode(),
            "google_id": id_info['sub'],  # Save Google user ID if needed
            "is_google_user": True
        })

        return JsonResponse({
            "success": True,
            "user_id": str(result.inserted_id),
            "message": "Google user signed up successfully"
        }, status=201)

    except ValueError as ve:
        logger.error(f"Token verification failed: {ve}")
        return JsonResponse({"error": "Invalid token"}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error during Google signup: {str(e)}")
        return JsonResponse({"error": "Internal server error"}, status=500) 

@csrf_exempt
@api_view(['POST'])
def login(request):
    try:
        data = request.data

        # Check required fields
        if 'email' not in data or 'password' not in data:
            return JsonResponse({"error": "Email and password are required"}, status=400)

        email = data.get('email')
        password = data.get('password')

        # Validate email format (basic validation)
        if not email or '@' not in email:
            return JsonResponse({"error": "Invalid email format"}, status=400)

        # Query the database for the user
        user = db.userPhone.find_one({"email": email})

        # Handle case where user is not found
        if not user:
            return JsonResponse({"error": "Invalid email or password"}, status=401)

        # Validate password
        stored_password = user.get('password')  # Ensure 'password' exists in the user object
        if not stored_password or not isinstance(stored_password, str):
            logger.error(f"Password field is missing or invalid for user with email: {email}")
            return JsonResponse({"error": "Server error: Password not found in database"}, status=500)

        if not bcrypt.checkpw(password.encode(), stored_password.encode()):
            return JsonResponse({"error": "Invalid email or password"}, status=401)

        # Return basic user data
        return JsonResponse({
            "success": True,
            "user": {
                "id": str(user["_id"]),  # Convert MongoDB ObjectID to string
                "name": user.get("name", "Unknown"),  # Default to "Unknown" if name is missing
                "email": user["email"]
            }
        }, status=200)

    except KeyError as e:
        # Handle missing keys in the database response
        logger.error(f"Missing field in database: {str(e)}")
        return JsonResponse({"error": f"Missing field in database: {str(e)}"}, status=500)

    except ValueError as e:
        # Handle invalid data types or encoding issues
        logger.error(f"Data validation error: {str(e)}")
        return JsonResponse({"error": f"Data validation error: {str(e)}"}, status=500)

    except PyMongoError as e:
        # Handle MongoDB-specific errors
        logger.error(f"MongoDB error: {str(e)}")
        return JsonResponse({"error": "Database error. Please try again later."}, status=500)

    except Exception as e:
        # Log the full traceback for debugging purposes
        traceback.print_exc()
        logger.error(f"Unexpected error: {str(e)}")
        return JsonResponse({"error": "An unexpected error occurred"}, status=500)
    
#google login
@csrf_exempt
@api_view(['POST'])
def google_login(request):
    try:
        token = request.data.get("token")
        if not token:
            return JsonResponse({"error": "Token is required"}, status=400)

        # Verify the Google ID token
        id_info = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)

        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com ']:
            return JsonResponse({"error": "Invalid issuer"}, status=400)

        email = id_info['email']
        name = id_info.get('name', '')

        # Check if user exists
        user = users_collection.find_one({"email": email})
        if not user:
            # Create user if they don't exist
            hashed_password = bcrypt.hashpw(email.encode() + b"_google_oauth", bcrypt.gensalt())
            result = users_collection.insert_one({
                "name": name,
                "email": email,
                "password": hashed_password.decode(),
                "google_id": id_info['sub'],
                "is_google_user": True
            })
            user = users_collection.find_one({"_id": result.inserted_id})

        # Return basic user info
        return JsonResponse({
            "success": True,
            "user": {
                "id": str(user["_id"]),
                "name": user.get("name", "Unknown"),
                "email": user["email"],
            }
        })

    except ValueError as ve:
        logger.error(f"Token verification failed: {ve}")
        return JsonResponse({"error": "Invalid token"}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error during Google login: {str(e)}")
        return JsonResponse({"error": "Internal server error"}, status=500)    

from bson import ObjectId  # Make sure to import this at the top

@csrf_exempt
@api_view(['GET'])
def list_product_ids(request):
    try:
        datasets = db.datasets.find({}, {"product_id": 1, "user_id": 1})

        shops = []

        for dataset in datasets:
            product_id = dataset.get("product_id")
            user_id = dataset.get("user_id")

            if not user_id or not product_id:
                continue

            user = db.users.find_one({"_id": user_id})
            if user:
                shopname = user.get("shopname")
                if shopname:
                    shops.append({
                        "product_id": str(product_id),   # Convert ObjectId to string
                        "shopname": shopname
                    })

        return JsonResponse(
            {"success": True, "shops": shops},
            status=200,
            safe=False  # Important when returning a list
        )

    except PyMongoError as e:
        logger.error(f"MongoDB error: {str(e)}")
        return JsonResponse(
            {"error": "Database error", "details": str(e)},
            status=500
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JsonResponse(
            {"error": "An unexpected error occurred", "details": str(e)},
            status=500
        )


from bson import ObjectId
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.http import JsonResponse

@csrf_exempt
@api_view(['GET'])
def search_products(request):
    try:
        # Extract query parameters
        productId = request.GET.get('productId')
        category = request.GET.get('category')
        productname = request.GET.get('productname')

        if not productId:
            return JsonResponse({"error": "Product ID is required"}, status=400)

        try:
            obj_id = ObjectId(productId)
        except Exception:
            return JsonResponse({"error": "Invalid product ID"}, status=400)

        match_filters = {}
        if category:
            match_filters["products.category"] = {"$regex": category, "$options": "i"}
        if productname:
            match_filters["products.productname"] = {"$regex": productname, "$options": "i"}

        pipeline = [
            {"$match": {"_id": obj_id}},
            {"$unwind": "$products"},
            {"$match": match_filters} if match_filters else {"$match": {}},
            {"$replaceRoot": {"newRoot": "$products"}},
        ]

        matched_products = list(db.products.aggregate(pipeline))

        if not matched_products:
            return JsonResponse({
                "success": True,
                "product": None,
                "count": 0,
                "benchmark": []
            }, status=200)

        selected_product = matched_products[0]
        category_value = selected_product.get("category", "")

        # Benchmark pipeline
        benchmark_pipeline = [
            {"$match": {"_id": obj_id}},
            {"$unwind": "$products"},
            {"$match": {"products.category": category_value}},
            {"$replaceRoot": {"newRoot": "$products"}},
            {"$sort": {"monthly_sales": -1}},
            {"$limit": 3}
        ]
        benchmark_products = list(db.products.aggregate(benchmark_pipeline))

        # Serialize ObjectIds
        def serialize(obj):
            if isinstance(obj, list):
                return [serialize(o) for o in obj]
            elif isinstance(obj, dict):
                return {k: serialize(v) for k, v in obj.items()}
            elif isinstance(obj, ObjectId):
                return str(obj)
            return obj

        return JsonResponse({
            "success": True,
            "product": serialize(selected_product),
            "count": len(matched_products),
            "benchmark": serialize(benchmark_products)
        }, status=200)

    except Exception as e:
        print("Exception:", e)
        return JsonResponse({"error": str(e)}, status=500)



@csrf_exempt
@api_view(['GET'])
def fetch_categories(request):
    try:
        # Step 1: Extract productId from query parameters
        product_id = request.GET.get('productId')
        if not product_id:
            return JsonResponse({"error": "Product ID (user ID) is required"}, status=400)

        try:
            user_id = ObjectId(product_id)  # Convert to ObjectId
        except Exception:
            return JsonResponse({"error": "Invalid Product ID (user ID)"}, status=400)

        # Step 2: Aggregation pipeline to fetch unique categories
        pipeline = [
            {"$match": {"_id": user_id}},  # Match documents for the specific user
            {"$unwind": "$products"},      # Unwind the products array
            {"$group": {"_id": "$products.category"}},  # Group by product category
            {"$project": {"category": "$_id", "_id": 0}}  # Project only the category field
        ]

        # Execute the aggregation pipeline
        result = list(db["products"].aggregate(pipeline))

        # Extract categories from the result
        categories = [doc["category"] for doc in result if doc.get("category")]
        print(categories)
        # Step 3: Return the categories as a JSON response
        return JsonResponse({"success": True, "categories": categories}, status=200)

    except Exception as e:
        # Log the error and return a generic error response
        logger.error(f"Error fetching categories: {e}")
        return JsonResponse({"success": False, "error": "An error occurred while fetching categories"}, status=500)
  
from bson import ObjectId
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from pymongo.errors import PyMongoError

@csrf_exempt
@api_view(['GET'])
def fetch_top_products(request):
    try:
        # Step 1: Extract query parameters
        productId = request.GET.get('productId')
        category = request.GET.get('category')
        print("Incoming product_id:", productId)
        print("Incoming category:", category)
        if not productId:
            return JsonResponse({"error": "Product ID is required"}, status=400)

        try:
            obj_id = ObjectId(productId)
        except Exception:
            return JsonResponse({"error": "Invalid product ID"}, status=400)
        
        if not category:
            return JsonResponse({"error": "Category is required"}, status=400)
        # Validate and convert product_id to ObjectId
        print("User ID (ObjectId):", obj_id)
        print("Looking for category:", category)
        print("All documents for user:")
        for doc in db["products"].find({"user_id": obj_id}):
            print(doc)

      

        # ✅ Now it's safe to use
        print("User ID (ObjectId):", obj_id)
        print("Looking for category:", category)
        print("All documents for user:")
        for doc in db["products"].find({"user_id": obj_id}):
            print(doc)
        # Step 2: Aggregation pipeline to fetch top products
        pipeline = [
            {"$match": {"_id": obj_id}},  # Match documents for the specific user
            {"$unwind": "$products"},          # Unwind the products array
            {"$match": {"products.category": category}},  # Filter by category
            {
                "$group": {
                    "_id": "$products.Barcode",  # Group by Barcode to avoid duplicates
                    "product": {"$first": "$products"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "productname": "$product.productname",
                    "category": "$product.category",
                    "stockquantity": "$product.stockquantity",
                    "sellingprice": "$product.sellingprice",
                    "Barcode": "$product.Barcode",
                    "expirydate": "$product.expirydate",
                    "reorderthreshold": "$product.reorderthreshold",
                    "costprice": "$product.costprice",
                    "monthly_sales": "$product.monthly_sales",
                    "timespan": "$product.timespan",
                    "sale_date": "$product.sale_date",
                    "productSize": "$product.productSize",
                    "id": {"$toString": "$product._id"},
                    "vendor_id": "$product.vendor_id"
                }
            }
        ]

        # Execute the aggregation pipeline
        result = list(db["products"].aggregate(pipeline))
        if not result:
            return JsonResponse({"error": "No products found matching the criteria"}, status=404)

        

        # Step 3: Return the products as a JSON response
        return JsonResponse({"success": True, "products": result}, status=200)
    except PyMongoError as e:
        # Log MongoDB-specific errors
        logger.error(f"Database error: {e}")
        return JsonResponse({"success": False, "error": "A database error occurred"}, status=500)
    except Exception as e:
        # Log generic errors
        logger.error(f"Unexpected error: {e}")
        return JsonResponse({"success": False, "error": "An unexpected error occurred"}, status=500)




@csrf_exempt
@api_view(['GET'])
def compare_products(request):
    try:
        id1 = request.GET.get("id1")
        id2 = request.GET.get("id2")
        print(id1)
        print(id2)
        if not id1 or not id2:
            return JsonResponse({"error": "Both product IDs are required"}, status=400)

        # Query both products by ID or Name
        product1 = db.products.find_one({"_id": ObjectId(id1)})
        product2 = db.products.find_one({"_id": ObjectId(id2)})

        if not product1 or not product2:
            return JsonResponse({"error": "One or both products not found"}, status=404)
        

        # Return only the necessary fields
        return JsonResponse({
            "success": True,
            "products": [
                {
                    "_id": str(product1["_id"]),
                    "productname": product1.get("productname", "Unknown"),
                    "sellingprice": product1.get("sellingprice", 0),
                    "monthly_sales": product1.get("monthly_sales", 0),
                    "category": product1.get("category", "")
                },
                {
                    "_id": str(product2["_id"]),
                    "productname": product2.get("productname", "Unknown"),
                    "sellingprice": product2.get("sellingprice", 0),
                    "monthly_sales": product2.get("monthly_sales", 0),
                    "category": product2.get("category", "")
                }
            ]
        })

    except Exception as e:
        logger.error(f"Error comparing products: {str(e)}")
        return JsonResponse({"error": "An unexpected error occurred"}, status=500)
# def search_second_product(request):
#     try:
#         # Extract query parameters
#         productId = request.GET.get('productId')
#         categoryName = request.GET.get('category')
#         productName = request.GET.get('productname')

#         print("🔍 [DEBUG] Received Request for Second Product Search")
#         print("Product ID:", productId)
#         print("Category:", categoryName)
#         print("Product Name:", productName)

#         if not productId:
#             return JsonResponse({"error": "Product ID is required"}, status=400)

#         try:
#             obj_id = ObjectId(productId)
#         except Exception as e:
#             print("❌ [DEBUG] Invalid Product ID:", str(e))
#             return JsonResponse({"error": "Invalid product ID"}, status=400)

#         match_filters = {}
#         if categoryName:
#             match_filters["products.category"] = {"$regex": categoryName, "$options": "i"}
#         if productName:
#             match_filters["products.productname"] = {"$regex": productName, "$options": "i"}

#         pipeline = [
#             {"$match": {"_id": obj_id}},
#             {"$unwind": "$products"},
#             {"$match": match_filters} if match_filters else {"$match": {}},
#             {"$replaceRoot": {"newRoot": "$products"}},
#         ]

#         matched_products = list(db.products.aggregate(pipeline))

#         if not matched_products:
#             print("⚠️ [DEBUG] No products found matching:", {
#                 "category": categoryName,
#                 "productname": productName
#             })
#             return JsonResponse({
#                 "success": True,
#                 "product": None,
#                 "message": "No matching product found."
#             }, status=200)

#         selected_product = matched_products[0]

#         print("✅ [DEBUG] Fetched Second Product:", serialize(selected_product))

#         return JsonResponse({
#             "success": True,
#             "product": serialize(selected_product),
#             "message": "Second product successfully fetched."
#         }, status=200)

#     except Exception as e:
#         print("🚨 [DEBUG] Exception occurred:", str(e))
#         traceback.print_exc()
#         return JsonResponse({"error": str(e)}, status=500)


def serialize(obj):
    if isinstance(obj, list):
        return [serialize(o) for o in obj]
    elif isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    elif isinstance(obj, ObjectId):
        return str(obj)
    return obj


