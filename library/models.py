from django.conf import settings
from django.db import models
from django.db.models import Q

from core.models import BaseModel


class Book(BaseModel):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    page_count = models.PositiveIntegerField()
    available_copies = models.PositiveIntegerField(default=1)

    @property
    def is_available(self) -> bool:
        return self.available_copies > 0

    def __str__(self) -> str:
        return f'{self.title} by {self.author}'


class Loan(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loans')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans')
    borrowed_at = models.DateTimeField(auto_now_add=True)
    returned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'book'],
                condition=Q(returned_at__isnull=True),
                name='unique_active_loan',
            )
        ]
        ordering = ['-borrowed_at']

    def __str__(self) -> str:
        status = 'Returned' if self.returned_at else 'Borrowed'
        return f'{self.book} -> {self.user} ({status})'


