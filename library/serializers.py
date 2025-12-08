from rest_framework import serializers

from .models import Book, Loan


class BookSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Book
        fields = (
            'id',
            'title',
            'author',
            'isbn',
            'page_count',
            'available_copies',
            'is_available',
            'created_at',
            'updated_at',
        )


class LoanSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    book = BookSerializer(read_only=True)

    class Meta:
        model = Loan
        fields = ('id', 'user', 'book', 'borrowed_at', 'returned_at')


