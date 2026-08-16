from django.contrib import admin
from .models import MemberProfile
from .models import Author, Book, BorrowTransaction, Category


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "phone_number", "max_books_allowed", "active_status"]
    list_filter = ["active_status"]
    search_fields = ["user__username", "user__email", "phone_number"]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name"]


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name"]
    search_fields = ["first_name", "last_name"]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "isbn", "total_copies", "available_copies"]
    list_filter = ["categories"]
    search_fields = ["title", "isbn"]
    filter_horizontal = ["categories"]


@admin.register(BorrowTransaction)
class BorrowTransactionAdmin(admin.ModelAdmin):
    list_display = ["book", "member", "borrow_date", "due_date",
                    "returned_date", "status", "fine_amount"]
    list_filter = ["status"]
    autocomplete_fields = ["book", "member"]