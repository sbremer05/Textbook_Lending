from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from catalog.models import Item, Collection, BorrowRequest, CollectionAccessRequest
from login.models import Profile, Notification
from datetime import timedelta
from django.utils import timezone

class CatalogTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.librarian = User.objects.create_user(username='librarian', password='pass')
        self.librarian.profile.role = 'librarian'
        self.librarian.profile.save()

        self.patron = User.objects.create_user(username='patron', password='pass')
        self.patron.profile.role = 'patron'
        self.patron.profile.save()

        self.item = Item.objects.create(
            title='Test Book',
            author='Test Author',         
            location='Shelf A',
            description='Test Description',
            created_by=self.librarian,
            status='available'
        )

        self.collection = Collection.objects.create(
            title='Public Collection',
            description='A public collection.',  
            created_by=self.librarian,
            is_public=True
        )
        self.collection.items.add(self.item)

    def test_view_items_as_librarian(self):
        self.client.login(username='librarian', password='pass')
        response = self.client.get(reverse('view_items'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Book')

    def test_view_items_as_patron(self):
        self.client.login(username='patron', password='pass')
        response = self.client.get(reverse('view_items'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Book')

    def test_request_borrow(self):
        self.client.login(username='patron', password='pass')
        response = self.client.post(reverse('request_borrow', args=[self.item.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(BorrowRequest.objects.filter(item=self.item, patron=self.patron).exists())

    def test_approve_borrow_request(self):
        borrow_request = BorrowRequest.objects.create(item=self.item, patron=self.patron)
        self.client.login(username='librarian', password='pass')
        response = self.client.post(reverse('approve_borrow_request', args=[borrow_request.pk]))
        borrow_request.refresh_from_db()
        self.assertEqual(borrow_request.status, 'approved')
        self.assertEqual(response.status_code, 302)

    def test_deny_borrow_request(self):
        borrow_request = BorrowRequest.objects.create(item=self.item, patron=self.patron)
        self.client.login(username='librarian', password='pass')
        response = self.client.post(reverse('deny_borrow_request', args=[borrow_request.pk]))
        borrow_request.refresh_from_db()
        self.assertEqual(borrow_request.status, 'denied')

    def test_return_borrowed_item(self):
        borrow_request = BorrowRequest.objects.create(
            item=self.item,
            patron=self.patron,
            status='approved',
            due_date=timezone.now() + timedelta(days=14)
        )
        self.client.login(username='patron', password='pass')
        response = self.client.post(reverse('return_borrowed_item', args=[borrow_request.pk]))
        borrow_request.refresh_from_db()
        self.assertEqual(borrow_request.status, 'returned')
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, 'available')

    def test_request_collection_access(self):
        private_collection = Collection.objects.create(
            title='Private Collection',
            description='A private collection.', 
            created_by=self.librarian,
            is_public=False
        )
        self.client.login(username='patron', password='pass')
        response = self.client.post(reverse('request_collection_access', args=[private_collection.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CollectionAccessRequest.objects.filter(collection=private_collection, user=self.patron).exists())

    def test_approve_collection_access(self):
        private_collection = Collection.objects.create(
            title='Private Collection',
            description='A private collection.',
            created_by=self.librarian,
            is_public=False
        )
        access_request = CollectionAccessRequest.objects.create(collection=private_collection, user=self.patron)
        self.client.login(username='librarian', password='pass')
        response = self.client.post(reverse('approve_collection_access', args=[access_request.pk]))
        access_request.refresh_from_db()
        self.assertEqual(access_request.status, 'approved')

    def test_deny_collection_access(self):
        private_collection = Collection.objects.create(
            title='Private Collection',
            description='A private collection.',
            created_by=self.librarian,
            is_public=False
        )
        access_request = CollectionAccessRequest.objects.create(collection=private_collection, user=self.patron)
        self.client.login(username='librarian', password='pass')
        response = self.client.post(reverse('deny_collection_access', args=[access_request.pk]))
        access_request.refresh_from_db()
        self.assertEqual(access_request.status, 'denied')

    def test_submit_review(self):
        BorrowRequest.objects.create(item=self.item, patron=self.patron, status='approved')
        self.client.login(username='patron', password='pass')
        response = self.client.post(reverse('submit_review', args=[self.item.pk]), {
            'rating': 5,
            'comment': 'Great book!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.item.reviews.first().rating, 5)
