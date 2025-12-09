from django.contrib.auth import get_user_model
from django.test import TestCase

from library.models import Book, Loan
from library.serializers import BookSerializer, LoanSerializer


class SerializerTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="bob", password="pass123")
        self.book = Book.objects.create(
            title="Serial Book",
            author="Author",
            isbn="1111111111111",
            page_count=120,
            available_copies=3,
        )

    def test_book_serializer_fields(self):
        data = BookSerializer(self.book).data
        self.assertEqual(data["title"], self.book.title)
        self.assertIn("is_available", data)
        self.assertTrue(data["is_available"])

    def test_loan_serializer_nested_book(self):
        loan = Loan.objects.create(user=self.user, book=self.book)
        data = LoanSerializer(loan).data
        self.assertEqual(data["book"]["title"], self.book.title)
        self.assertEqual(data["user"], str(self.user))

