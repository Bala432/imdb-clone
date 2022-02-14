from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.dispatch import receiver
from django.utils.text import slugify

#Specifying the directory path for storing images
def user_directory_path(instance,filename):
    return '{0}/{1}'.format(instance.slug, filename)

# Create your models here.
class StreamPlatform(models.Model):
    name = models.CharField(max_length=30,unique=True)
    about = models.TextField(max_length=200)
    website = models.URLField(max_length=100,unique=True)
    slug = models.SlugField(max_length=50,null=False,unique=True)
    
    def save(self,*args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
class Genre(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(max_length=50,null=False)
    
    def save(self,*args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=100,unique=True)
    storyline = models.TextField(max_length=300)
    created_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)
    platforms = models.ManyToManyField(StreamPlatform,related_name="movies")
    average_rating  = models.FloatField(default=0)
    number_of_ratings = models.PositiveIntegerField(default=0)
    genres = models.ManyToManyField(Genre,related_name='movie_genres')
    slug = models.SlugField(max_length=150,null=False)
    poster = models.ImageField(upload_to=user_directory_path)
    
    def save(self,*args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
class Review(models.Model):
    review_user = models.ForeignKey(User,on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1),MaxValueValidator(10)])
    comment = models.TextField(max_length=500)
    created_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE,related_name='reviews')
    
    def __str__(self):
        return str(self.rating) + " by "+ self.movie.title
    
