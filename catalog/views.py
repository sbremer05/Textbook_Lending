from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden
from .models import Item, Collection, BorrowRequest, Review, CollectionAccessRequest
from .forms import ItemForm, CollectionForm, UpdateItemCollectionForm
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
# =====================
# Item Views
# =====================

@login_required
def submit_review(request, pk):
    item = get_object_or_404(Item, pk=pk)

    has_borrowed = BorrowRequest.objects.filter(
    item=item, patron=request.user, status='approved'
    ).exists()

    if not has_borrowed:
        messages.error(request, "You can only review items you've borrowed.")
        return redirect("item_detail", pk=pk)

    review = item.reviews.filter(user=request.user).first()

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if rating:
            rating = int(rating)
            if 1 <= rating <= 5:
                if review:
                    review.rating = rating
                    review.comment = comment
                    review.save()
                    messages.success(request, "✅ Review updated successfully!")
                else:
                    item.reviews.create(user=request.user, rating=rating, comment=comment)
                    messages.success(request, "✅ Review submitted successfully!")
            else:
                messages.error(request, "Rating must be between 1 and 5.")
        else:
            messages.error(request, "Rating is required.")

        return redirect("item_detail", pk=pk)

    return render(request, "catalog/submit_review.html", {
        "item": item,
        "review": review,
        "has_borrowed": has_borrowed
    })
def add_item(request):
    if not request.user.is_authenticated:
        return render(request, "catalog/add_item.html", {
            "form": None,
            "error_message": "You must be logged in to add an item."
        })
    if request.user.profile.role != 'librarian':
        return redirect('home')

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

def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    collections = item.collections.all()

    has_access = False
    for collection in collections:
        if (collection.is_public or 
            request.user == collection.created_by or 
            request.user in collection.allowed_users.all()):
            has_access = True
            break

    if not has_access and collections.exists():
        return redirect("view_items")

    already_requested = False
    is_borrowed = BorrowRequest.objects.filter(item=item, status='approved').exists()
    is_borrowed_by_user = False
    borrow_due_date = None
    if request.user.is_authenticated:
        already_requested = BorrowRequest.objects.filter(
            item=item, patron=request.user, status='pending'
        ).exists()
        try:
            current_borrow = BorrowRequest.objects.get(
                item=item, patron=request.user, status='approved'
            )
            is_borrowed_by_user = True
            borrow_due_date = current_borrow.due_date
        except BorrowRequest.DoesNotExist:
            pass

    reviews = item.reviews.all().order_by('-created_at')

    context = {
        'item': item,
        'collections': collections,
        'already_requested': already_requested,
        'is_borrowed': is_borrowed,
        'reviews': reviews,
        'is_borrowed_by_user': is_borrowed_by_user,
        'borrow_due_date': borrow_due_date,
    }
    return render(request, 'catalog/item_detail.html', context)



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

# =====================
# Collection Views
# =====================

def view_collection_access_requests(request, pk):
    if request.user.profile.role != 'librarian':
        return redirect('home')

    collection = get_object_or_404(Collection, pk=pk)
    
    requests = CollectionAccessRequest.objects.filter(collection=collection) \
                   .select_related('collection', 'user').order_by('-requested_at')
    
    return render(request, 'catalog/view_collection_access_requests.html', {'requests': requests})

def approve_collection_access(request, request_id):
    if request.user.profile.role != 'librarian':
        return redirect('home')
    access_request = get_object_or_404(CollectionAccessRequest, pk=request_id)
    if access_request.status == 'pending':
        access_request.status = 'approved'
        access_request.collection.allowed_users.add(access_request.user)
        access_request.save()
        messages.success(request, f"✅ Access request for '{access_request.collection.title}' approved.")
    return redirect('view_collection_access_requests', pk=access_request.collection.pk)

def deny_collection_access(request, request_id):
    if request.user.profile.role != 'librarian':
        return redirect('home')
    access_request = get_object_or_404(CollectionAccessRequest, pk=request_id)
    if access_request.status == 'pending':
        access_request.status = 'denied'
        access_request.save()
        messages.info(request, f"❌ Access request for '{access_request.collection.title}' denied.")
    return redirect('view_collection_access_requests', pk=access_request.collection.pk)


def add_collection(request):
    if not request.user.is_authenticated:
        return render(request, "catalog/add_collection.html", {
            "form": None,
            "error_message": "You must be logged in to add a collection."
        })

    User = get_user_model()
    if request.user.profile.role in ['patron', 'pending']:
        if request.method == 'POST':
            form = CollectionForm(request.POST)
            if form.is_valid():
                collection = form.save(commit=False)
                collection.created_by = request.user
                collection.is_public = True
                collection.save()
                form.save_m2m()
                librarians = User.objects.filter(profile__role='librarian')
                collection.allowed_users.add(*librarians)

                return redirect('view_collections')
        else:
            form = CollectionForm()
            form.fields['is_public'].initial = True
            form.fields['is_public'].disabled = True

    elif request.user.profile.role == 'librarian':
        if request.method == 'POST':
            form = CollectionForm(request.POST)
            if form.is_valid():
                collection = form.save(commit=False)
                collection.created_by = request.user
                collection.save()
                form.save_m2m()

                librarians = User.objects.filter(profile__role='librarian')
                collection.allowed_users.add(*librarians)

                return redirect('view_collections')
        else:
            form = CollectionForm()

    else:
        return redirect('search_home')

    return render(request, "catalog/add_collection.html", {"form": form})


def request_collection_access(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    if request.user.is_authenticated:
        if collection.is_public:
            messages.info(request, "This collection is public. No request needed.")
            return redirect('collection_detail', pk=pk)
        elif request.user == collection.created_by or request.user in collection.allowed_users.all():
            messages.info(request, "You already have access to this collection.")
            return redirect('collection_detail', pk=pk)

        elif CollectionAccessRequest.objects.filter(collection=collection, user=request.user).exists():
            messages.info(request, "You have already requested access to this collection.")
            return redirect('collection_detail', pk=pk)
        
        existing_request = CollectionAccessRequest.objects.filter(collection=collection, user=request.user, status='pending').first()
        if existing_request:
            messages.info(request, "You have already requested access to this collection.")
            return redirect('collection_detail', pk=pk)
        
        if request.method == 'POST':
            access_request = CollectionAccessRequest.objects.create(
                collection=collection,
                user=request.user
            )
            messages.success(request, "Access request submitted successfully!")
            return redirect('collection_detail', pk=pk)
    else:
        messages.error(request, "You must be logged in to request access to a collection.")
        return redirect('login')
    return render(request, "catalog/request_collection_access.html", {
        "collection": collection,
        "request": request
    })


def view_collections(request):
    user = request.user
    if user.is_authenticated and hasattr(user, "profile"):
        collections = Collection.objects.all()
        # profile = user.profile
        # if profile.role == "librarian":
        #     collections = Collection.objects.all()
        # elif profile.role == "patron":
        #     collections = Collection.objects.filter(is_public=True) | Collection.objects.filter(allowed_users=user)
        # else:
        #     collections = Collection.objects.filter(is_public=True)
    else:
        collections = Collection.objects.filter(is_public=True)

    return render(request, "catalog/view_collections.html", {"collections": collections.distinct()})

def update_item_collections(request, pk):
    if not request.user.is_authenticated or request.user.profile.role != 'librarian':
        return render(request, "catalog/update_item_collections.html", {
            "form": None,
            "error_message": "You do not have permission to access this page."
        })
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = UpdateItemCollectionForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Item collections updated successfully!")
            return redirect('item_detail', pk=item.pk)
        else:
            messages.error(request, "Error updating item collections.")
    else:
        form = UpdateItemCollectionForm(instance=item)
    return render(request, 'catalog/update_item_collections.html', {'form': form, 'item': item})

def collection_detail(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    if not collection.is_public and request.user.profile.role != 'librarian' and request.user not in collection.allowed_users.all():
        messages.error(request, "❌ You do not have permission to view this collection.")
        return redirect('view_collections')
    
    query = request.GET.get("query", "")

    if query:
        items = collection.items.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    else:
        items = collection.items.all()
    return render(request, "catalog/collection_detail.html", 
                  {"collection": collection, "items": items, "query": query})

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

# =====================
# Search Views
# =====================

def search_home(request):
    return render(request, "catalog/search.html")

def search_items(request):
    query = request.GET.get("q", "")
    results = Item.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    )
    return render(request, "catalog/search_results.html", {"results": results, "query": query})

def search_collections(request):
    query = request.GET.get("q", "")
    results = Collection.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    )
    return render(request, "catalog/collection_results.html", {"results": results, "query": query})

# =====================
# Borrowing Views
# =====================
@login_required
def request_borrow(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if BorrowRequest.objects.filter(item=item, patron=request.user, status='pending').exists():
        messages.info(request, "You have already requested to borrow this item.")
    elif BorrowRequest.objects.filter(item=item, status='approved').exists():
        messages.warning(request, "This item is currently borrowed by someone else.")
    else:
        BorrowRequest.objects.create(item=item, patron=request.user)
        messages.success(request, "Borrow request submitted successfully.")
    return redirect("item_detail", pk=pk)

@login_required
def view_borrow_requests(request):
    if request.user.profile.role != 'librarian':
        return redirect('home')
    requests = BorrowRequest.objects.select_related('item', 'patron').order_by('-requested_at')
    return render(request, 'catalog/borrow_requests.html', {'requests': requests})

@login_required
def approve_borrow_request(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest, pk=request_id)
    if request.user.profile.role != 'librarian':
        return redirect('home')

    # Mark any other approved requests for this item as returned.
    BorrowRequest.objects.filter(item=borrow_request.item, status='approved').update(status='returned')
    
    # Approve this borrow request and set the due date.
    borrow_request.status = 'approved'
    lending_period = timedelta(days=14)  # Change this if you need a different lending period.
    borrow_request.due_date = timezone.now() + lending_period
    borrow_request.save()

    # Update the item's status from 'available' to 'checked_out'.
    item = borrow_request.item
    if item.status != 'checked_out':  # Safety check if it's already checked out.
        item.status = 'checked_out'
        item.save()

    messages.success(
        request,
        f"✅ Borrow request for '{borrow_request.item.title}' approved. Due date is set to {(borrow_request.due_date).strftime('%Y-%m-%d')}."
    )
    return redirect('view_borrow_requests')

@login_required
def deny_borrow_request(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest, pk=request_id)
    if request.user.profile.role != 'librarian':
        return redirect('home')

    borrow_request.status = 'denied'
    borrow_request.save()
    messages.info(request, f"❌ Borrow request for '{borrow_request.item.title}' denied.")
    return redirect('view_borrow_requests')

@login_required
def return_borrowed_item(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest, pk=request_id, patron=request.user)
    borrow_request.status = 'returned'
    borrow_request.save()
    messages.success(request, f"📦 You have returned '{borrow_request.item.title}'.")
    return redirect('my_borrowed_items')

@login_required
def my_borrowed_items(request):
    borrowed = BorrowRequest.objects.filter(
        patron=request.user,
        status='approved'
    ).select_related('item')

    user_reviews = Review.objects.filter(user=request.user)
    
    reviews_by_item = {review.item_id: review for review in user_reviews}

    return render(request, 'catalog/my_borrowed_items.html', {
        'borrowed_items': borrowed,
        'reviews_by_item': reviews_by_item
    })

# =====================
# S3 Cleanup
# =====================
from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=Item)
def delete_item_image(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)
