from django.urls import path
from app.api.views import ( ListCreateStreamPlatformView, StreamPlatformDetailView, ListCreateGenreView, GenreDetailView, 
                           LoginView, RegisterView, 
                           CreateMovieView, MoviesListView, MovieDetailView,
                           CreateReviewView, ReviewsListView, ReviewDetailView,)

urlpatterns = [
    path('create-stream-platform/',ListCreateStreamPlatformView.as_view()),
    path('login/',LoginView.as_view()),
    path('register/',RegisterView.as_view()),
    path('stream-platform-detail/<slug:slug>/',StreamPlatformDetailView.as_view()),
    path('create-genre/',ListCreateGenreView.as_view()),
    path('genre-detail/<slug:slug>/',GenreDetailView.as_view()),
    path('create-movie/',CreateMovieView.as_view()),
    path('movies-list/',MoviesListView.as_view()),
    path('movie-detail/<slug:slug>/',MovieDetailView.as_view()),
    path('title/<slug:slug>/create-review/',CreateReviewView.as_view()),
    path('title/<slug:slug>/reviews-list/',ReviewsListView.as_view()),
    path('title/<slug:slug>/review/<int:pk>/',ReviewDetailView.as_view()),
]