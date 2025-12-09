from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from library.models import Book, Loan

User = get_user_model()


class BookViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="charlie", password="pass123")
        self.admin = User.objects.create_user(username="admin", password="pass123", is_staff=True)
        self.book = Book.objects.create(
            title="View Book",
            author="Author",
            isbn="2222222222222",
            page_count=200,
            available_copies=2,
        )

    def test_list_books_paginated(self):
        url = "/api/books/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("results", resp.data)
        self.assertGreaterEqual(resp.data["count"], 1)

    def test_borrow_requires_auth(self):
        url = f"/api/books/{self.book.id}/borrow/"
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_borrow_and_return_flow(self):
        self.client.force_authenticate(user=self.user)
        borrow_url = f"/api/books/{self.book.id}/borrow/"
        resp = self.client.post(borrow_url)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 1)
        loan_id = resp.data["id"]
        self.assertTrue(Loan.objects.filter(id=loan_id, returned_at__isnull=True).exists())

        return_url = f"/api/books/{self.book.id}/return_book/"
        resp = self.client.post(return_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 2)
        self.assertTrue(Loan.objects.filter(id=loan_id, returned_at__isnull=False).exists())

    def test_admin_can_create_book(self):
        self.client.force_authenticate(user=self.admin)
        url = "/api/books/"
        resp = self.client.post(
            url,
            {
                "title": "New Book",
                "author": "New Author",
                "isbn": "3333333333333",
                "page_count": 150,
                "available_copies": 1,
            },
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


class AccountsViewTests(APITestCase):
    def test_register_user(self):
        url = "/api/auth/register/"
        resp = self.client.post(
            url,
            {"username": "newuser", "password": "strongpass123", "email": "user@example.com"},
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

