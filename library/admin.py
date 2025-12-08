from django.contrib import admin

from .models import Book, Loan


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'available_copies')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('author',)


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'borrowed_at', 'returned_at')
    list_filter = ('borrowed_at', 'returned_at')
    search_fields = ('book__title', 'user__username')


