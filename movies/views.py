from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Movie, Genre, Review
from .forms import ReviewForm


# Create your views here.
def index(request):
    return render(request, 'movies/index.html', {'movies': Movie.objects.all()})


def detail(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    form = ReviewForm()
    reviews = movie.review_set.all()
    return render(request, 'movies/detail.html', {'movie': movie, 'form': form, 'reviews': reviews,})


@login_required
def review_create(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user_id = request.user
            comment.movie_id = movie
            comment.save()
            return redirect('movies:detail', movie_pk)
        else:
            return redirect('movies.detail', movie_pk)


def review_delete(request, movie_pk, review_pk):
    review = Review.objects.get(pk=review_pk)
    if request.user == review.user_id: 
        review.delete()
    return redirect('movies:detail', movie_pk)


@login_required
def like(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    if request.user in movie.user_id.all():
        movie.user_id.remove(request.user)
    else:
        movie.user_id.add(request.user)
    return redirect('movies:detail', movie_pk)
