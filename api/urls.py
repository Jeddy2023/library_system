from django.urls import path
from .views import (
    RegisterView, LoginView, GetUserDetailsView, UpdateProfileView, GetUsersView, 
    AddBookView, BookListView, BorrowBookView, ReturnBookView,
    DeleteUserView, DeleteBookView, UpdateBookView, UserBorrowingHistoryView, AdminBorrowingHistoryView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', GetUserDetailsView.as_view(), name='get_user_details'),
    path('update-profile/', UpdateProfileView.as_view(), name='update_profile'),
    path('users/', GetUsersView.as_view(), name='get_users'),
    path('books/', BookListView.as_view(), name='book_list'),
    path('add-book/', AddBookView.as_view(), name='add_book'),
    path('borrow-book/<int:book_id>/', BorrowBookView.as_view(), name='borrow_book'),
    path('return-book/<int:book_id>/', ReturnBookView.as_view(), name='return_book'),
    path('delete-user/<int:user_id>/', DeleteUserView.as_view(), name='delete_user'),
    path('delete-book/<int:book_id>/', DeleteBookView.as_view(), name='delete_book'),
    path('update-book/<int:book_id>/', UpdateBookView.as_view(), name='update_book'),
    path('user-borrowing-history/', UserBorrowingHistoryView.as_view(), name='user_borrowing_history'),
    path('admin-borrowing-history/', AdminBorrowingHistoryView.as_view(), name='admin_borrowing_history'),
]