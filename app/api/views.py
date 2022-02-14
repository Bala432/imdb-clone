from app.models import StreamPlatform, Genre, Movie, Review
from app.api.serializers import StreamPlatformSerializer, GenreSerializer, UserSerializer, MovieSerializer, ReviewSerializer
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView
from app.api.permissions import AdminOrReadOnly, ReviewUserOrReadOnly
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

# API for Registering User
class RegisterView(APIView):
    
    def post(self, request):
        
        serializer = UserSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            account = serializer.save()
            data['response'] = 'Registration Succesfull'
            data['username'] = account.username
            refresh_token = RefreshToken.for_user(account)
            data['token'] = {
                'access_token': str(refresh_token.access_token),
                'refresh_token' : str(refresh_token)
            }
            
        else:
            data = serializer.errors
        return Response(data)

# API for Authenticating Users
class LoginView(APIView):
    
    def post(self,request):
        username = request.data['username']
        password = request.data['password']
        
        user = authenticate(username=username, password=password)
        if user is None:
            raise ValidationError({'Error':'Invalid User'})
        
        account = User.objects.get(username=username)
        data = {}
        data['Response'] = "Login is Successful"
        refresh_token = RefreshToken.for_user(account)
        data['tokens'] = {
            'access_token': str(refresh_token.access_token),
            'refresh_token': str(refresh_token)
        }
        return Response(data)

# API for Creating and Listing Streaming Platforms
class ListCreateStreamPlatformView(ListCreateAPIView):
    permission_classes = [AdminOrReadOnly]              # Restricting Creation of Stream Platforms operation to Admin User
    serializer_class = StreamPlatformSerializer
    queryset = StreamPlatform.objects.all()

# API for accessing Individual Stream Platform
class StreamPlatformDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = StreamPlatformSerializer
    lookup_field = 'slug'
    permission_classes = [ AdminOrReadOnly ]           # Restricting Update and Delete operations of Stream Platform to Admin User
    queryset = StreamPlatform.objects.all()
    
# API for Creating and Listing Genres
class ListCreateGenreView(ListCreateAPIView):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    permission_classes = [ AdminOrReadOnly ]           # Restricting Creation of Genre operation to Admin User
    
# API for Retrieving, Updating and Destroying a Particular Genre 
class GenreDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    lookup_field = 'slug'                               # Customizing lookup_field to identify slug rather than pk (default lookup_field = pk) 
    permission_classes = [ AdminOrReadOnly ]            # Restricting Update and Delete operations of Genre to Admin User
    
# API for Creating a Movie Instance
class CreateMovieView(CreateAPIView):
    serializer_class = MovieSerializer
    queryset = Movie.objects.all()
    permission_classes = [IsAdminUser]                  # Assigning Creation of Movie operation to only Admin User

    def create(self,request,*args,**kwargs):
        data = request.data
        title = data['title']
        storyline = data['storyline']
        poster = data['poster']
        movie = Movie.objects.create(title=title,storyline=storyline,poster=poster)
        platforms = data['platforms'].split(",")
        
        for platform in platforms:
            platform_object = StreamPlatform.objects.get(slug=platform)
            movie.platforms.add(platform_object)
            
        genres = data['genres'].split(",")
        for genre in genres:
            genres_object = Genre.objects.get(slug=genre)
            movie.genres.add(genres_object)
        serializer = MovieSerializer(movie)
        return Response(serializer.data)
    
# API for Listing Movie Instances
class MoviesListView(ListAPIView):
    serializer_class = MovieSerializer
    queryset = Movie.objects.all()
    filter_backends = [filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['platforms__name']         # Listing Movies in accordance with Streaming Platforms 
    ordering_fields = ['average_rating']        # Movies will be listed in order of their average rating
    
# API for Retrieving, Updating and Deleting Movie Instance
class MovieDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = MovieSerializer
    lookup_field = 'slug'
    permission_classes = [ AdminOrReadOnly ]     # Restricting Update and Delete operations on Movie to Admin User
    queryset = Movie.objects.all()
    
# API for Creating a Review for a Movie
class CreateReviewView(CreateAPIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = [ IsAuthenticated ]    # Only Authenticated Users can write a review
    
    def create(self,request,*args,**kwargs):
        data = request.data
        movie_slug = self.kwargs['slug']
        movie = Movie.objects.get(slug=movie_slug)
        user = request.user
        
        if user.is_staff:
            raise ValidationError("Admin cannot rate the movie")
        
        if Review.objects.filter(movie=movie,review_user=user).exists():
            raise ValidationError("You have already reviewed this movie")

        movie.number_of_ratings = movie.number_of_ratings + 1
        if movie.number_of_ratings == 1:
            movie.average_rating = data['rating']
        else:
            reviews_list = Review.objects.filter(movie=movie)
            ratings_sum = reviews_list.aggregate(Sum('rating'))     # Using Django's db aggregate method Sum for calculating sum of ratings
            total_rating = ratings_sum['rating__sum'] + int(data['rating'])
            movie.average_rating = total_rating / movie.number_of_ratings
            
        movie.save()
        review = Review.objects.create(review_user=user, rating=data['rating'],comment=data['comment'],movie=movie)
        serializer = ReviewSerializer(review)
        return Response(serializer.data)
    
# API for Listing Reviews
class ReviewsListView(ListAPIView):
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['rating']                          # Filter List of Movies by their rating
    
    def get_queryset(self):
        slug = self.kwargs['slug']
        movie = Movie.objects.get(slug=slug)
        return Review.objects.filter(movie=movie)
    
# API for Retrieving, Updating and Destroying Review Instance
class ReviewDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = [ ReviewUserOrReadOnly ]          # Restricting Update access to only Reviewed User
    
    def patch(self, request, *args, **kwargs):
        data = request.data
        pk = self.kwargs['pk']
        slug = self.kwargs['slug']
        review = Review.objects.get(pk=pk)
        serializer = ReviewSerializer(review,data=data,partial=True)
        
        if serializer.is_valid():
            serializer.save()
            
        movie = Movie.objects.get(slug=slug)
        if 'rating' in data:
            updated_rating = int(data['rating'])
            movie.rating = updated_rating
            reviews_list = Review.objects.filter(movie=movie)
            ratings_sum = reviews_list.aggregate(Sum('rating'))   # Using Djano's aggregate method Sum for calculating sum of ratings            
            movie.average_rating = ratings_sum['rating__sum'] / movie.number_of_ratings
            movie.save()
            review.movie = movie
            review.save()
        return Response(serializer.data)
    