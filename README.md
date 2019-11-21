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

## 4. movies - genres ManyToManyField 만들기

먼저 ERD에 명시된대로 DB 모델을 구성한다.

```python
# movies/movdels.py
from django.db import models
from django.conf import settings

class Genre(models.Model):
    name = models.CharField(max_length=20)

class Movie(models.Model):
    title = models.CharField(max_length=30)
    audience = models.IntegerField()
    poster_url = models.CharField(max_length=140)
    description = models.TextField()
    genres = models.ManyToManyField(Genre)
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_movies')
    score_sum = models.IntegerField(default=0)
    score_avg = models.FloatField(default=0)

class Review(models.Model):
    content = models.CharField(max_length=100)
    score = models.IntegerField()
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
```

project08에서 가져온 `movie.json` 파일에서 `"genre_id": 3`을 `"genres": [3]`으로 바꿔준다.

```json
[
  {
      "pk": 1,
      "model": "movies.Movie",
      "fields": {
          "title": "82년생 김지영",
          "audience": 1120468,
          "poster_url": "https://movie-phinf.pstatic.net/20191024_215/1571900079078PNazL_JPEG/movie_image.jpg",
          "description": "1982년 봄에 태어나\n 누군가의 딸이자 아내, 동료이자 엄마로\n 2019년 오늘을 살아가는 ‘지영’(정유미).\n 때론 어딘가 갇힌 듯 답답하기도 하지만\n 남편 ‘대현’(공유)과 사랑스러운 딸\n 그리고 자주 만나지 못해도 항상 든든한 가족들이 ‘지영’에겐 큰 힘이다. \n 하지만 언젠가부터 마치 다른 사람이 된 것처럼 말하는 ‘지영’.\n ‘대현’은 아내가 상처 입을까 두려워 그 사실을 털어놓지 못하고\n ‘지영’은 이런 ‘대현’에게 언제나 “괜찮다”라며 웃어 보이기만 하는데…\n 모두가 알지만 아무도 몰랐던\n 당신과 나의 이야기",
          "genre_id": 3  // 이 부분
           
      }
  },
```

```json
[
  {
      "pk": 1,
      "model": "movies.Movie",
      "fields": {
          "title": "82년생 김지영",
          "audience": 1120468,
          "poster_url": "https://movie-phinf.pstatic.net/20191024_215/1571900079078PNazL_JPEG/movie_image.jpg",
          "description": "1982년 봄에 태어나\n 누군가의 딸이자 아내, 동료이자 엄마로\n 2019년 오늘을 살아가는 ‘지영’(정유미).\n 때론 어딘가 갇힌 듯 답답하기도 하지만\n 남편 ‘대현’(공유)과 사랑스러운 딸\n 그리고 자주 만나지 못해도 항상 든든한 가족들이 ‘지영’에겐 큰 힘이다. \n 하지만 언젠가부터 마치 다른 사람이 된 것처럼 말하는 ‘지영’.\n ‘대현’은 아내가 상처 입을까 두려워 그 사실을 털어놓지 못하고\n ‘지영’은 이런 ‘대현’에게 언제나 “괜찮다”라며 웃어 보이기만 하는데…\n 모두가 알지만 아무도 몰랐던\n 당신과 나의 이야기",
          "genres": [3]  // 리스트로 바꿔준다.
           
      }
  },
```

그리고 `movies/fixtures/`에 `movie.json`과 `genre.json`을 넣고 DB에 반영한다.

```bash
$ python manage.py loaddata genre.json
Installed 11 object(s) from 1 fixture(s)
$ python manage.py loaddata movie.json
Installed 10 object(s) from 1 fixture(s)
```



## 5. 나머지 부분

영화 추천을 제외한 나머지 부분은 이전의 프로젝트와 **내용이 똑같아서** 리드미를 쓰지 않을 것입니다! 대신 결과 스샷만 추가할게요!

### 1. 유저 정보

![user_detail](/images/user_detail.PNG)

### 2. 영화 상세 정보

좋아요 버튼을 누르면 안좋아요 버튼으로 바뀌게 했다. 안좋아요 버튼 옆의 숫자는 좋아요한 유저의 수를 의미한다.

![movie_detail](/images/movie_detail.png)

## 6. 협업 과정에서 느낀점

이번 프로젝트는 지난 프로젝트와 내용이 거의 똑같아서 협업의 어려움을 느끼지 못했다. 다만, 겨레오빠의 변수명은 조금 색달랐다.