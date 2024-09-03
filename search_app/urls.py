from django.urls import path
from .views import search_products, home  # Импортирай от текущия модул

urlpatterns = [
    path('', home, name='home'),
    path('search/', search_products, name='search_products'),
]