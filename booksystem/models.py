from django.db import models
from decimal import Decimal
from django.utils.text import slugify


from Accounts.models import MemberProfile

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Category" ## to dispaly this name in the admin panel
        verbose_name_plural = "Categories" ## //

    ## * take all arguments and put them togther in a tuple
    ## and ** collect  the key args and put them together in a dictionary
    def save(self, *args, **kwargs):  
        if not self.slug:
            self.slug = slugify(self.name) ## to make  the entered name to a book-name-data 
        super().save(*args, **kwargs) ## override normal save method to add the slug field automatically when saving a category

    def __str__(self):
        return self.name

class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    biography = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Book(models.Model):
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    author = models.ForeignKey(Author, on_delete=models.PROTECT, related_name="books") ## cant delete author if he has books

    ## related_name to access books from category it is used to access objects from the other side category.books.all()
    categories = models.ManyToManyField(Category, related_name="books", blank=True) 

    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    published_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title


class BorrowTransaction(models.Model):
    class Status(models.TextChoices):## creating a fixed set of choices as status
        ACTIVE = "ACTIVE", "Active" ## the actual value stored in db is ACTIVE and the other for human readable
        RETURNED = "RETURNED", "Returned"
        OVERDUE = "OVERDUE", "Overdue"

    ## cant delete book if borrowed
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name="transactions")

    ## if member is deleted then delete all his borrowed books
    member = models.ForeignKey(MemberProfile, on_delete=models.CASCADE, related_name="transactions")
    borrow_date = models.DateField(auto_now_add=True) ## add date when borrowed
    due_date = models.DateField()
    returned_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        ordering = ["-borrow_date"]

    def __str__(self):
        return f"{self.member.user.username} → {self.book.title}"



