from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class BookNotAvailableException(Exception):
    pass

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=[('Admin', 'Admin'), ('User', 'User')], default='User')

    objects = CustomUserManager()

    def _str_(self):
        return self.email

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13, unique=True)
    published_date = models.DateField()
    total_copies = models.PositiveIntegerField()
    available_copies = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.title} by {self.author}"
    
    def borrow(self):
        if self.available_copies <= 0:
            raise BookNotAvailableException("No available copies to borrow.")
        self.available_copies -= 1
        self.save()

    def return_book(self):
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            self.save()
        else:
            raise ValueError("All copies are already returned.")

class BorrowingHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='borrowing_history')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrowing_history')
    borrow_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    overdue = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"
