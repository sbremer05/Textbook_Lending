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

    path("items/<int:pk>/edit/", views.edit_item, name="edit_item"),
    path("items/<int:pk>/delete/", views.delete_item, name="delete_item"),
    path("collections/<int:pk>/edit/", views.edit_collection, name="edit_collection"),
    path("collections/<int:pk>/delete/", views.delete_collection, name="delete_collection"),

    path("items/<int:pk>/borrow/", views.request_borrow, name="request_borrow"),
    path("borrow/requests/", views.view_borrow_requests, name="view_borrow_requests"),
    path("borrow/approve/<int:request_id>/", views.approve_borrow_request, name="approve_borrow_request"),
    path("borrow/deny/<int:request_id>/", views.deny_borrow_request, name="deny_borrow_request"),
    path("borrow/return/<int:request_id>/", views.return_borrowed_item, name="return_borrowed_item"),
    path("borrow/my-items/", views.my_borrowed_items, name="my_borrowed_items"),

    path('items/<int:pk>/review/', views.submit_review, name='submit_review'),
]
