# your_app/forms.py

from django import forms
from django.contrib.auth import get_user_model
from .models import Collection, Item

User = get_user_model()

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
    allowed_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Users",
    )

    items = forms.ModelMultipleChoiceField(
        queryset=Item.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Books",
    )

    class Meta:
        model = Collection
        fields = [
            'title',
            'description',
            'is_public',
            'allowed_users',
            'items',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # build each label as "username (email@example.com)"
        self.fields['allowed_users'].label_from_instance = (
            lambda u: f"{u.username} ({u.email})"
        )


class ItemForm(forms.ModelForm):
    collections = forms.ModelMultipleChoiceField(
        # queryset=Collection.objects.filter(is_public=True),
        queryset=Collection.objects.all(),
        widget=forms.CheckboxSelectMultiple,
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



# from django import forms
# from.models import Collection, Item, User
#
#
# class UpdateItemCollectionForm(forms.ModelForm):
#     class Meta:
#         model = Item
#         fields = ['collections']
#
#     def clean_collections(self):
#         collections = self.cleaned_data.get('collections')
#         if not collections:
#             return collections
#
#         has_private = any(not c.is_public for c in collections)
#         if has_private and len(collections) > 1:
#             raise forms.ValidationError(
#                 "If assigned to a private collection, the item cannot belong to more than one collection."
#             )
#
#         return collections
#
# class CollectionForm(forms.ModelForm):
#     allowed_users = forms.ModelMultipleChoiceField(
#         queryset=User.objects.all(),
#         widget=forms.CheckboxSelectMultiple,
#         required=False,
#         label="Users",
#     )
#
#     class Meta:
#         model = Collection
#         fields = [
#             'title',
#             'description',
#             'is_public',
#             'allowed_users',
#         ]
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # build each label as "username (email@example.com)"
#         self.fields['allowed_users'].label_from_instance = (
#             lambda u: f"{u.username} ({u.email})"
#         )
#
# class ItemForm(forms.ModelForm):
#     collections = forms.ModelMultipleChoiceField(
#         queryset=Collection.objects.all(),
#         widget=forms.CheckboxSelectMultiple,
#         required=False,
#         label="Collections",
#     )
#
#     class Meta:
#         model = Item
#         fields = [
#             'title',
#             'author',
#             'location',
#             'description',
#             'collections',
#             'image',
#         ]
#
#     def clean_collections(self):
#         collections = self.cleaned_data.get('collections')
#         if not collections:
#             return collections
#         has_private = any(not c.is_public for c in collections)
#         if has_private and len(collections) > 1:
#             raise forms.ValidationError(
#                 "If assigned to a private collection, the item cannot belong to more than one collection."
#             )
#         return collections