from rest_framework import serializers
from .models import Author, Book, BorrowTransaction, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']
        read_only_fields = ['slug']

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name', 'biography']

class BookReadSerializer(serializers.ModelSerializer): ## serlizer for getting book data with author and category
    author = AuthorSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'isbn', 'author', 
                  'categories', 'total_copies', 'available_copies', 'published_date']

class BookWriteSerializer(serializers.ModelSerializer): ## serializer for creating and updating book
    class Meta:
        model = Book
        fields = ['id', 'title', 'isbn', 'author', 
                  'categories', 'total_copies', 'available_copies', 'published_date']

    def validate_isbn(self, value): ## auto called when entring ISBN
        cleaned = value.strip() ## remove whitespace 
        if not cleaned.isdigit() or len(cleaned) not in (10, 13):
            raise serializers.ValidationError("ISBN must be 10 or 13 digits.")
        return cleaned
    
    def validate_number_of_copies(self, attrs):
        total = attrs.get("total_copies", getattr(self.instance, "total_copies", 0)) ## to be support partial updates used getattr
        available = attrs.get("available_copies", getattr(self.instance, "available_copies", 0))

        if available > total:
            raise serializers.ValidationError("Available copies cannot exceed total copies.")
        return attrs


class BorrowCreateSerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all()) ## get book ID

    class Meta:
        model = BorrowTransaction
        fields = ["id", "book"]

    def validate(self, attrs):
        request = self.context["request"] ## as the user doesnt send his id we get it from the request context
        user=request.user
        member = getattr(user, "member_profile", None) # Get the member profile, or None if it doesn't exist

        if member is None:
            raise serializers.ValidationError("Your account has no member profile yet.")

        if not member.active_status:
            raise serializers.ValidationError("Your membership is currently inactive.")

        active_loans = member.transactions.filter(status=BorrowTransaction.Status.ACTIVE)
        if active_loans.count() >= member.max_books_allowed:
            raise serializers.ValidationError(
                f"Borrow limit of {member.max_books_allowed} books reached."
            )

        book = attrs["book"] ## get book object
        already_borrowed = active_loans.filter(book=book).exists()
        if already_borrowed:
            raise serializers.ValidationError("You already have this title checked out.")
        return attrs


class BorrowReadSerializer(serializers.ModelSerializer):
    book = BookReadSerializer(read_only=True)

    class Meta:
        model = BorrowTransaction
        fields = ["id", "book", "borrow_date", "due_date", "returned_date", "status"]