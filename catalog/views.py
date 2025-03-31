from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Item, Collection
from .forms import ItemForm, CollectionForm
from django.contrib import messages
from django.contrib.messages import get_messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Item, Collection
from .forms import ItemForm, CollectionForm

from django.db.models import Q
from django.http import HttpResponseForbidden


# Librarians can add items
# @login_required
def add_item(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to add an item.")
        return render(request, "catalog/add_item.html", {
            "form": None,
            "error_message": "You must be logged in to add a item. Please log in first."
        })
    if request.user.profile.role != 'librarian':
        return redirect('home')  # Only librarians can upload

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()
            form.save_m2m()
            return redirect('view_items')

    form = ItemForm()
    return render(request, "catalog/add_item.html", {"form": form})

# All users can view items (with filtering logic)
# @login_required
def view_items(request):
    user = request.user
    if user.is_authenticated and hasattr(user, "profile") and user.profile.role == "librarian":
        items = Item.objects.all()
    else:
        public_collections = Collection.objects.filter(is_public=True)
        items = Item.objects.filter(
            collections__in=public_collections
        ) | Item.objects.filter(collections=None)

    return render(request, "catalog/view_items.html", {"items": items.distinct()})

# Librarians can add collections
# @login_required
def add_collection(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to add a collection.")
        return render(request, "catalog/add_collection.html", {
            "form": None,
            "error_message": "You must be logged in to add a collection. Please log in first."
        })
    
    if request.user.profile.role in ['patron', 'pending']:
        # Patrons can only create public collections
        if request.method == 'POST':
            form = CollectionForm(request.POST)
            if form.is_valid():
                collection = form.save(commit=False)
                collection.created_by = request.user
                collection.is_public = True  # Force public
                collection.save()
                form.save_m2m()
                return redirect('view_collections')
        else:
            form = CollectionForm()
            form.fields['is_public'].initial = True
            form.fields['is_public'].disabled = True  # Lock the field
    elif request.user.profile.role == 'librarian':
        # Librarians: full collection form
        if request.method == 'POST':
            form = CollectionForm(request.POST)
            if form.is_valid():
                collection = form.save(commit=False)
                collection.created_by = request.user
                collection.save()
                form.save_m2m()
                return redirect('view_collections')
        else:
            form = CollectionForm()
    else:
        return redirect('search_home')

    return render(request, "catalog/add_collection.html", {"form": form})


# All users can view collections (with role-based filtering)
# @login_required
def view_collections(request):
    user = request.user

    if user.is_authenticated and hasattr(user, "profile"):
        profile = user.profile

        if profile.role == "librarian":
            collections = Collection.objects.all()
        elif profile.role == "patron":
            collections = Collection.objects.filter(is_public=True) | Collection.objects.filter(allowed_users=user)
        else:
            collections = Collection.objects.filter(is_public=True)
    else:
        collections = Collection.objects.filter(is_public=True)  # Unauthenticated users see only public collections

    return render(request, "catalog/view_collections.html", {"collections": collections.distinct()})

# @login_required
def collection_detail(request, pk):
    collection = get_object_or_404(Collection, pk=pk)

    if not collection.is_public and request.user != collection.created_by and request.user not in collection.allowed_users.all():
        return redirect('view_collections')

    items = collection.items.all()
    return render(request, "catalog/collection_detail.html", {"collection": collection, "items": items})

# @login_required
def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    collections = item.collections.all()

    # Allow access if at least one collection is public or user has rights
    has_access = False
    for collection in collections:
        if collection.is_public or request.user == collection.created_by or request.user in collection.allowed_users.all():
            has_access = True
            break

    if not has_access and collections.exists():
        return redirect("view_items")  # or show an error page

    return render(request, 'catalog/item_detail.html', {
        'item': item,
        'collections': collections
    })


# @login_required
def search_home(request):
    return render(request, "catalog/search.html")

# @login_required
def search_items(request):
    query = request.GET.get("q", "")
    results = Item.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query)
    )
    return render(request, "catalog/search_results.html", {"results": results, "query": query})

# @login_required
def search_collections(request):
    query = request.GET.get("q", "")
    results = Collection.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query)
    )
    return render(request, "catalog/collection_results.html", {"results": results, "query": query})

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Item
from .forms import ItemForm

# @login_required
def edit_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    
    if request.user != item.created_by:
        messages.error(request, "❌ You do not have permission to edit this item.")
        return redirect("view_items")  

    form = ItemForm(request.POST or None, request.FILES or None, instance=item)
    if form.is_valid():
        form.save()
        messages.success(request, "✅ Item updated successfully!")
        return redirect("view_items")  

    return render(request, "catalog/edit_item.html", {"form": form, "item": item})


# @login_required
def delete_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    
    if request.user != item.created_by:
        messages.error(request, "❌ You do not have permission to delete this item.")
        return redirect("view_items")

    if request.method == "POST":
        item.delete()
        messages.success(request, "🗑️ Item deleted successfully!")
        return redirect("view_items")  

    return render(request, "catalog/confirm_delete.html", {"object": item, "type": "Item"})

# @login_required
def edit_collection(request, pk):
    collection = get_object_or_404(Collection, pk=pk)

    if request.user != collection.created_by:
        messages.error(request, "❌ You do not have permission to edit this collection.")
        return redirect("view_collections")

    if request.method == 'POST':
        form = CollectionForm(request.POST, instance=collection)
        if form.is_valid():
            form.save()
            messages.success(request, "Collection updated successfully!")
            return redirect('collection_detail', pk=collection.pk)
    else:
        form = CollectionForm(instance=collection)

    return render(request, 'catalog/edit_collection.html', {'form': form, 'collection': collection})


# @login_required
def delete_collection(request, pk):
    collection = get_object_or_404(Collection, pk=pk)

    if request.user != collection.created_by:
        messages.error(request, "❌ You do not have permission to delete this collection.")
        return redirect("view_collections")

    if request.method == 'POST':
        collection.delete()
        messages.success(request, "Collection deleted successfully!")
        return redirect('view_collections')

    return render(request, 'catalog/delete_collection.html', {'collection': collection})