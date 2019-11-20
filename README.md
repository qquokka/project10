---
typora-root-url: ./
---

# Project 10

## 1. 영화 평균 평점 계산

평균평점이 가장 높은 영화를 추천하기 위해 Movie model에 다음 두 칼럼을 추가했다.

```python
# movies/models.py
class Movie(models.Model):
    ...
    score_sum = models.IntegerField(default=0)
    score_avg = models.FloatField(default=0)
```

`score_sum`은 모든 사용자들이 준 점수를 총합한 것이고, `score_avg`는 리뷰를 작성하거나 삭제할 때마다 `score_sum / { review의 개수 }`로 계산하여 소수점 두자리까지의 값을 저장해줄 것이다. **리뷰 개수가 0개일 땐 ZeroDivisionError가 발생하므로 max 함수로 1로 나누어준다. 리뷰가 0개일 땐 어차피 score_sum도 0점이기 때문에 score_avg는 그대로 0점이다.**

```python
# movies/views.py
@login_required
def review_create(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.movie = movie
            comment.save()
            
            movie.score_sum += comment.score  # score_sum에 리뷰에 작성한 점수를 더해주고
            # 리뷰 개수로 나누어준다. ZeroDivisionError를 피하기 위해 max 함수를 사용했다.
            movie.score_avg = round(movie.score_sum / max(movie.review_set.count(), 1), 2)
            movie.save()
            
            return redirect('movies:detail', movie_pk)
        else:
            return redirect('movies.detail', movie_pk)


def review_delete(request, movie_pk, review_pk):
    review = Review.objects.get(pk=review_pk)
    if request.user == review.user: 
        movie = Movie.objects.get(pk=movie_pk)
        
        movie.score_sum -= review.score  # review를 삭제하기 전에 먼저 score_sum에서 빼주고
        review.delete()
        # 리뷰 개수로 나누어준다. 여기도 ZeroDivisionError를 피하기 위해 max 함수를 사용했다.
        movie.score_avg = round(movie.score_sum / max(movie.review_set.count(), 1), 2)
        movie.save()
        
    return redirect('movies:detail', movie_pk)
```

## 2. 영화 평균 평점 화면

처음엔 0점

![score0](/images/score0.PNG)

5점을 준 후

![score5](/images/score5.PNG)

8점을 준 후

![score13](/images/score13.PNG)

평점이 6.5로 바뀐 것을 볼 수 있다.

## 3. 최고 평점 영화 추천

`score_avg`로 내림차순 정렬 후 첫번째 오브젝트를 `movie_recom`으로 넘겨주었다.

```python
# movies/views.py
def index(request):
    context = {
        'movies': Movie.objects.all(),
        'movie_recom': Movie.objects.order_by('-score_avg')[0]
    }
    return render(request, 'movies/index.html', context)
```

![movie_recommendation](/images/movie_recommendation.PNG)

영화 목록 상단에 해당 영화 포스터를 추가하였고, 포스터를 누르면 영화 상세 정보로 이동하도록 했다.

## 4. 나머지 부분

영화 추천을 제외한 나머지 부분은 이전의 프로젝트와 **내용이 똑같아서** 리드미를 쓰지 않을 것입니다! 대신 결과 스샷만 추가할게요!

### 1. 유저 정보

![user_detail](/images/user_detail.PNG)

### 2. 영화 상세 정보

좋아요 버튼을 누르면 안좋아요 버튼으로 바뀌게 했다. 안좋아요 버튼 옆의 숫자는 좋아요한 유저의 수를 의미한다.

![movie_detail](/images/movie_detail.png)

## 5. 협업 과정에서 느낀점

이번 프로젝트는 지난 프로젝트와 내용이 거의 똑같아서 협업의 어려움을 느끼지 못했다. 다만, 겨레오빠의 변수명은 조금 색달랐다.