from django.urls import path
from . import views

urlpatterns = [
    path("add-item/", views.add_item, name="add_item"),
    path("view-items/", views.view_items, name='view_items'),

    path("add-collection/", views.add_collection, name="add_collection"),
    path("view-collections/", views.view_collections, name="view_collections"),

    path('collections/<int:pk>/', views.collection_detail, name='collection_detail'),
    path('items/<int:pk>/', views.item_detail, name='item_detail'),
    path('items/<int:pk>/update_collection/', views.update_item_collections, name='update_item_collections'),

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
    path("collections/<int:pk>/request_access/", views.request_collection_access, name='request_collection_access'),

    path("collections_access_requests/<int:request_id>/approve_access/", views.approve_collection_access, name='approve_collection_access'),
    path("collections_access_requests/<int:request_id>/deny_access/", views.deny_collection_access, name='deny_collection_access'),
    path("collections/<int:pk>/pending_requests/", views.view_collection_access_requests, name='view_collection_access_requests'),
]
