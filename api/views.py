from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, BookSerializer, BorrowingHistorySerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import CustomUser, Book, BorrowingHistory
from django.utils import timezone

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_data = UserSerializer(user).data
            return Response({'message': 'User registered successfully', 'user': user_data}, status=status.HTTP_201_CREATED)
        
        first_error = next(iter(serializer.errors.values()))[0] if serializer.errors else "An error occurred"
        return Response({
            'message': first_error 
        }, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)
            print(user)

            if user:
                if not user.is_active:
                    return Response({'error': 'User account is deactivated'}, status=status.HTTP_403_FORBIDDEN)

                # Generate tokens
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                # Return user details and tokens
                user_data = UserSerializer(user).data
                return Response({
                    'user': user_data,
                    'accessToken': access_token,
                    'refreshToken': refresh_token,
                }, status=status.HTTP_200_OK)

            return Response({'message': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        
        first_error = next(iter(serializer.errors.values()))[0] if serializer.errors else "An error occurred"
        return Response({
            'message': first_error 
        }, status=status.HTTP_400_BAD_REQUEST)
    
class GetUserDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_data = UserSerializer(user).data
        return Response(user_data, status=status.HTTP_200_OK)
    
class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        data = request.data

        serializer = UserSerializer(instance=user, data=data, partial=True)
        if serializer.is_valid():
            updated_user = serializer.save()
            user_data = UserSerializer(updated_user).data
            return Response({'message': 'User details updated successfully', 'user': user_data}, status=status.HTTP_200_OK)
        
        first_error = next(iter(serializer.errors.values()))[0] if serializer.errors else "An error occurred"
        return Response({
            'message': first_error 
        }, status=status.HTTP_400_BAD_REQUEST)
    
class GetUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.role == 'Admin':
            return Response(
                {"message": "You do not have permission to view all users."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        try:
            if not request.user.role == 'Admin':
                return Response(
                    {"message": "You do not have permission to delete a user."},
                    status=status.HTTP_403_FORBIDDEN
                )
            user = CustomUser.objects.get(id=user_id)
            user.delete()
            return Response({'message': 'User deleted successfully'}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
class AddBookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'Admin':
            return Response({'message': 'Only admins can add books'}, status=status.HTTP_403_FORBIDDEN)
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class BookListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
    
class BorrowBookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, book_id):
        try:
            book = Book.objects.get(id=book_id)
            if book.available_copies <= 0:
                return Response({'message': 'No copies available'}, status=status.HTTP_400_BAD_REQUEST)

            BorrowingHistory.objects.create(user=request.user, book=book)
            book.borrow()

            return Response({'message': 'Book borrowed successfully'}, status=status.HTTP_200_OK)
        except Book.DoesNotExist:
            return Response({'message': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class ReturnBookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, book_id):
        try:
            borrowing = BorrowingHistory.objects.get(user=request.user, book_id=book_id, return_date__isnull=True)
            borrowing.return_date = timezone.now()
            borrowing.save()

            borrowing.book.return_book()
            return Response({'message': 'Book returned successfully'}, status=status.HTTP_200_OK)
        except BorrowingHistory.DoesNotExist:
            return Response({'message': 'No active borrowing record found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class DeleteBookView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, book_id):
        try:
            if not request.user.role == 'Admin':
                return Response(
                    {"message": "You do not have permission to delete a book."},
                    status=status.HTTP_403_FORBIDDEN)
            book = Book.objects.get(id=book_id)
            book.delete()
            return Response({'message': 'Book deleted successfully'}, status=status.HTTP_200_OK)
        except Book.DoesNotExist:
            return Response({'message': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        
class UpdateBookView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, book_id):
        try:
            if not request.user.role == 'Admin':
                return Response(
                    {"message": "You do not have permission to update a book."},
                    status=status.HTTP_403_FORBIDDEN)
            book = Book.objects.get(id=book_id)
            serializer = BookSerializer(book, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Book.DoesNotExist:
            return Response({'message': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

class UserBorrowingHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        borrowing_history = BorrowingHistory.objects.filter(user=request.user, return_date__isnull=True)
        serializer = BorrowingHistorySerializer(borrowing_history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AdminBorrowingHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.role == 'Admin':
            return Response(
                {"message": "You do not have permission to view borrowing history."},
                status=status.HTTP_403_FORBIDDEN)
        borrowing_history = BorrowingHistory.objects.filter(return_date__isnull=True)
        serializer = BorrowingHistorySerializer(borrowing_history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)