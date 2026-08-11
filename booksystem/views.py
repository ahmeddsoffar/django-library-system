from django.db import transaction
from rest_framework.throttling import ScopedRateThrottle

from .models import Author, Book, Category , BorrowTransaction
from .permissions import IsStaffOrReadOnly ,IsOwnerOrStaff
from .serializers import AuthorSerializer, BookReadSerializer, BookWriteSerializer, CategorySerializer ,BorrowCreateSerializer, BorrowReadSerializer
from rest_framework import viewsets

from django.conf import settings
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import timedelta
from decimal import Decimal


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsStaffOrReadOnly]

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsStaffOrReadOnly]
    search_fields = ['first_name', 'last_name']

class BookViewSet(viewsets.ModelViewSet):

    queryset = Book.objects.all()
    permission_classes = [IsStaffOrReadOnly]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return BookWriteSerializer

        return BookReadSerializer

    
class BorrowViewSet(viewsets.ModelViewSet): ## modelviewset is too muh here later will use mixins to limit the actions

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "user"

    permission_classes = [IsAuthenticated, IsOwnerOrStaff]

    def get_queryset(self): ## what data can the user see
        if self.request.user.is_staff:
            return BorrowTransaction.objects.all()

        user=self.request.user
        member = user.member_profile
        return BorrowTransaction.objects.filter(
            member=member
        )

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowCreateSerializer

        return BorrowReadSerializer

    def perform_create(self, serializer): ## creation of a new book borrow  serialzer here is passed from get_serializer_class
        with transaction.atomic(): ## treat all transction as single work either it all works or all failll
             ## pervent race condtion as get this book id and lock 
            book = Book.objects.select_for_update().get(pk=serializer.validated_data["book"].pk)

            if book.available_copies <= 0:
                raise ValidationError(
                    "No copies of this book are available."
                )

            book.available_copies -= 1
            book.save()

            serializer.save(
                member=self.request.user.member_profile,
                due_date=timezone.localdate()
                + timedelta(days=settings.LOAN_PERIOD_DAYS)
            )

    @action(detail=True, methods=["post"]) ## detail means i am working with a single object and only post allowed
    def return_book(self, request, pk=None):

        transaction = self.get_object()

        if transaction.status != BorrowTransaction.Status.ACTIVE:
            raise ValidationError(
                "This book has already been returned."
            )

        today = timezone.localdate()

        if today > transaction.due_date:
            days_late = (today - transaction.due_date).days
            fine = Decimal(settings.FINE_PER_DAY) * days_late
        else:
            fine = Decimal("0")

        transaction.status = BorrowTransaction.Status.RETURNED
        transaction.returned_date = today
        transaction.fine_amount = fine
        transaction.save()

        transaction.book.available_copies += 1
        transaction.book.save()

        return Response(
            BorrowReadSerializer(transaction).data,
            status=status.HTTP_200_OK
        )