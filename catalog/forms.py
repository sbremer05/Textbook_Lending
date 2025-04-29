from django import forms
from.models import Collection, Item


class UpdateItemCollectionForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['collections']

    def clean_collections(self):
        collections = self.cleaned_data.get('collections')
        if not collections:
            return collections

        has_private = any(not c.is_public for c in collections)
        if has_private and len(collections) > 1:
            raise forms.ValidationError(
                "If assigned to a private collection, the item cannot belong to more than one collection."
            )

        return collections

class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['title', 'description', 'is_public', 'allowed_users']

class ItemForm(forms.ModelForm):
    collections = forms.ModelMultipleChoiceField(
        queryset=Collection.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Change to CheckboxSelectMultiple
        required=False,
        label="Collections",
    )

    class Meta:
        model = Item
        fields = [
            'title',
            'author',
            'location',
            'description',
            'collections',
            'image',
        ]

    def clean_collections(self):
        collections = self.cleaned_data.get('collections')
        if not collections:
            return collections
        has_private = any(not c.is_public for c in collections)
        if has_private and len(collections) > 1:
            raise forms.ValidationError(
                "If assigned to a private collection, the item cannot belong to more than one collection."
            )
        return collections