from django.urls import path
from .views import PostList, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView, PostSearch, SubscribeView, UnsubscribeView # импортируем наше представление


 
 
urlpatterns = [
#    path — означает путь. В данном случае путь ко всем товарам у нас останется пустым, позже станет ясно почему 
    path('', PostList.as_view()), # т.к. сам по себе это класс, то нам надо представить этот класс в виде view. Для этого вызываем метод as_view
    path('<int:pk>/', PostDetailView.as_view(), name='news_detail'),
    path('add/', PostCreateView.as_view(), name='post_create'),
    path('<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('<int:pk>/update/', PostUpdateView.as_view(), name='post_update'),
    path('search/', PostSearch.as_view(), name='post_search'),
    path('<int:pk>/subscribe', SubscribeView.as_view(), name='subscribe'),
    path('<int:pk>/unsubscribe', UnsubscribeView.as_view(), name='unsubscribe'),
   
]

