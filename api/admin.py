from django.contrib import admin
from .models import CustomUser, Book, BorrowingHistory

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Book)
admin.site.register(BorrowingHistory)