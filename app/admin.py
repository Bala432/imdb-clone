from django.contrib import admin
from app.models import Movie, StreamPlatform, Genre, Review
# Register your models here.

admin.site.register(Movie)
admin.site.register(StreamPlatform)
admin.site.register(Genre)
admin.site.register(Review)