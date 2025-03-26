from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Item, Collection
from .forms import ItemForm, CollectionForm

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Item, Collection
from .forms import ItemForm, CollectionForm

# Librarians can add items
@login_required
def add_item(request):
    if request.user.profile.role != 'librarian':
        return redirect('patron_dashboard')  # Only librarians can upload

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
@login_required
def view_items(request):
    user = request.user
    if user.profile.role == 'librarian':
        items = Item.objects.all()
    else:
        # Patrons: Show items not in any collection + public collection items
        public_collections = Collection.objects.filter(is_public=True)
        items = Item.objects.filter(
            collections__in=public_collections
        ) | Item.objects.filter(collections=None)

    return render(request, "catalog/view_items.html", {"items": items.distinct()})

# Librarians can add collections
@login_required
def add_collection(request):
    if request.user.profile.role != 'librarian':
        return redirect('patron_dashboard')

    if request.method == 'POST':
        form = CollectionForm(request.POST)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.created_by = request.user
            collection.save()
            form.save_m2m()
            return redirect('view_collections')

    form = CollectionForm()
    return render(request, "catalog/add_collection.html", {"form": form})

# All users can view collections (with role-based filtering)
@login_required
def view_collections(request):
    user = request.user
    profile = user.profile

    if profile.role == 'librarian':
        collections = Collection.objects.all()
    elif profile.role == 'patron':
        collections = Collection.objects.filter(is_public=True) | Collection.objects.filter(private_users=user)
    else:
        collections = Collection.objects.filter(is_public=True)

    return render(request, "catalog/collection_list.html", {"collections": collections.distinct()})

@login_required
def collection_detail(request, pk):
    collection = get_object_or_404(Collection, pk=pk)

    if not collection.is_public and request.user != collection.created_by and request.user not in collection.private_users.all():
        return redirect('view_collections')

    items = collection.item_set.all()
    return render(request, "catalog/collection_detail.html", {"collection": collection, "items": items})

@login_required
def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)

    # Check collection privacy if item is in a private collection
    if item.collection:
        if not item.collection.is_public and request.user != item.collection.created_by and request.user not in item.collection.private_users.all():
            return redirect('view_items')

    return render(request, "catalog/item_detail.html", {"item": item})
