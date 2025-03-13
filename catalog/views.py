from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Item
from .forms import ItemForm

@login_required
def add_item(request):
    if request.user.profile.role != 'librarian':
        return redirect('patron_dashboard')  # Only librarians can upload

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('librarian_dashboard')

    form = ItemForm()
    return render(request, "catalog/add_item.html", {"form": form})

@login_required
def view_items(request):
    items = Item.objects.all()
    return render(request, "catalog/view_items.html", {"items": items})