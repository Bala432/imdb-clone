from app.models import Movie, StreamPlatform, Genre, Review
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError

# API for Serializing StreamPlatform Model Fields
class StreamPlatformSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = StreamPlatform
        fields = ['name','about','website']
        
# API for Serializing Genre Model Fields
class GenreSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Genre
        fields = ['name']

# Class for Serializing Review Model Fields
class ReviewSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Review
        fields = ['rating','comment']
        
    def to_representation(self,instance):
        rating = instance.rating
        comment = instance.comment
        review_user = instance.review_user.username
        
        data = {
            'rating': rating,
            'comment': comment,
            'review_user' : review_user
        }
        
        return data
    
# Class for Serializing Movie Model Fields
class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = [ 'title', 'storyline', 'poster', 'platforms', 'genres' ]
        
    def to_representation(self, instance):
        print("instance is",instance)
        data = {}
        data['title'] = instance.title
        data['storyline'] = instance.storyline
        data['poster'] = instance.poster.url
        platforms = instance.platforms.all()
        genres = instance.genres.all()
        platforms_list = []
        for platform in platforms:
            platforms_list.append(platform.name)
        data['platforms'] = platforms_list
        reviews_list = []
        reviews_queryset = Review.objects.filter(movie=instance)
        print("review queryset is ",reviews_queryset)
        print("Before iteration")
        for review in reviews_queryset:
            print("review is ",review)
            reviews_list.append(review)
        print("reviews_list is ",reviews_list)
        genres_list = []
        for genre in genres:
            genres_list.append(genre.name)
        data['genres'] = genres_list
        
        if instance.number_of_ratings == 0 :
           data['ratings'] = "There are no ratings for this movie"
        else:
            data['ratings'] = instance.number_of_ratings
            data['average_rating'] = instance.average_rating 
        print("Before reviews assign")
        reviews_list = [ {'rating': review.rating, 'comment': review.comment, 'review_user' : review.review_user.username} for review in reviews_list]
        print("reviews_list is ",reviews_list)
        data['reviews'] = reviews_list

        return data
        
class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True,style={'input_type':'password'})
    
    class Meta:
        model = User
        fields = ['username','email','password','password2']
        extra_kwargs = {'password':{
            'write_only':True
        }}
        
    def create(self,validated_data):
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']
        password2 = validated_data['password2']
        if password != password2:
            raise ValidationError({'Error':'Invalid password'})
        
        if User.objects.filter(username=username).exists():
            raise ValidationError({'Error':'Username already exists'})
        
        if User.objects.filter(email=email).exists():
            raise ValidationError({'Error':'Email already exists'})
        
        user = User.objects.create(username=username,email=email)
        user.set_password(password)
        user.save()
        return user
    
# Class for Serializing Review Model Fields
class ReviewSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Review
        fields = ['rating','comment']
        
    def to_representation(self,instance):
        rating = instance.rating
        comment = instance.comment
        review_user = instance.review_user.username
        
        data = {
            'rating': rating,
            'comment': comment,
            'review_user' : review_user
        }
        
        return data
        
        