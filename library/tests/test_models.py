from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from library.models import Book, Loan

User = get_user_model()


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pass123")

    def test_book_is_available_property(self):
        book = Book.objects.create(
            title="Test Book",
            author="Author",
            isbn="1234567890123",
            page_count=100,
            available_copies=1,
        )
        self.assertTrue(book.is_available)
        book.available_copies = 0
        book.save()
        self.assertFalse(book.is_available)

    def test_loan_unique_active_constraint(self):
        book = Book.objects.create(
            title="Unique Loan",
            author="Author",
            isbn="9999999999999",
            page_count=100,
            available_copies=2,
        )
        Loan.objects.create(user=self.user, book=book)
        with self.assertRaises(IntegrityError):
            Loan.objects.create(user=self.user, book=book)

