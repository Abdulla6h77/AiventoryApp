from django.urls import path
from .views import (
    signup, login, list_product_ids, search_products,
    fetch_categories, fetch_top_products,
    google_signup, google_login,compare_products # 👈 Added new import
)

urlpatterns = [
    # Auth URLs
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),

    # Google Sign-Up URL ← Newly added
    path('google-signup/', google_signup, name='google_signup'),
    path('google-login/', google_login, name='google_login'),

    # Product & Store URLs
    path('products/list-ids/', list_product_ids, name='list_product_ids'),
    path('products/search/', search_products, name='search_products'),
    path('products/compare/', compare_products, name='compare_products'),
    # Compare Product URL ← Newly added
    # path('products/search-second/', search_second_product, name='search_second_product'),

    # Category & Top Products URLs
    path('fetch_categories/', fetch_categories, name='fetch_categories'),
    path('fetch_top_products/', fetch_top_products, name='fetch_top_products'),
]