from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Book, Loan
from .permissions import IsAdminOrReadOnly
from .serializers import BookSerializer, LoanSerializer


class BookViewSet(viewsets.ModelViewSet):
    """
    Browse, search, and manage books. Anonymous users can read, admins can write.
    """

    serializer_class = BookSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = Book.objects.all().order_by('title')
        query = self.request.query_params.get('q')
        author = self.request.query_params.get('author')
        available = self.request.query_params.get('available')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(author__icontains=query) | Q(isbn__icontains=query)
            )
        if author:
            queryset = queryset.filter(author__icontains=author)
        if available is not None:
            if available.lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(available_copies__gt=0)
            elif available.lower() in ['false', '0', 'no']:
                queryset = queryset.filter(available_copies__lte=0)
        return queryset

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def borrow(self, request, pk=None):
        book = self.get_object()
        if not book.is_available:
            return Response({'detail': 'Book is not available.'}, status=status.HTTP_400_BAD_REQUEST)

        existing = Loan.objects.filter(user=request.user, book=book, returned_at__isnull=True).first()
        if existing:
            return Response({'detail': 'You already borrowed this book.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            loan = Loan.objects.create(user=request.user, book=book)
            book.available_copies = max(book.available_copies - 1, 0)
            book.save(update_fields=['available_copies'])

        serializer = LoanSerializer(loan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def return_book(self, request, pk=None):
        book = self.get_object()
        loan = Loan.objects.filter(user=request.user, book=book, returned_at__isnull=True).first()
        if not loan:
            return Response({'detail': 'No active loan found for this book.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            loan.returned_at = timezone.now()
            loan.save(update_fields=['returned_at'])
            book.available_copies = book.available_copies + 1
            book.save(update_fields=['available_copies'])

        serializer = LoanSerializer(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LoanViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    View active and past loans. Regular users see their own, admins see all.
    """

    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        base_qs = Loan.objects.select_related('book', 'user')
        if getattr(self.request.user, 'is_admin', False):
            return base_qs
        return base_qs.filter(user=self.request.user)


