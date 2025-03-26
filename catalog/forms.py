from django import forms
from .models import Collection, Item

class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['title', 'description', 'is_public', 'allowed_users']

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'identifier', 'status', 'location', 'description', 'collections']
