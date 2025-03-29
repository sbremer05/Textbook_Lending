from django.urls import path
from . import views

urlpatterns = [
    path("add-item/", views.add_item, name="add_item"),
    path("view-items/", views.view_items, name='view_items'),

    path("add-collection/", views.add_collection, name="add_collection"),
    path("view-collections/", views.view_collections, name="view_collections"),

    path('collections/<int:pk>/', views.collection_detail, name='collection_detail'),
    path('items/<int:pk>/', views.item_detail, name='item_detail'),

    path("search/", views.search_home, name="search_home"),
    path("search-items/", views.search_items, name="search_items"),
    path("search-collections/", views.search_collections, name="search_collections"),
]
