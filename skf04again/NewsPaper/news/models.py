from django.db import models
from django.contrib.auth.models import User
from django.conf import settings



class Author(models.Model):
    rating_user = models.FloatField(default = 0.0)
    author_user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def update_rating(self):

        posts_author = Post.objects.filter(author_post = self.id) 
        rating_article = sum([r.rating_article * 3 for r in posts_author]) 
        print(rating_article)
        rating_comment = sum([r.rating_comment for r in Comment.objects.filter(comment_user = self.author_user)])
        print(rating_comment)
        
      
        likes_author_comment_sum = sum([r.rating_comment for r in Comment.objects.filter(post_comment__in = posts_author)])
        print(likes_author_comment_sum)
        self.rating_user =  rating_article + rating_comment + likes_author_comment_sum
        print(self.rating_user)
        self.save()

    
    def __str__(self):
        return self.author_user.username


class Category(models.Model):
    title_category = models.CharField(max_length = 64, unique = True)
    subscribers = models.ManyToManyField(settings.AUTH_USER_MODEL, through='CategorySubscribers', verbose_name='Подписчики')

    
    
    def __str__(self):
        return self.title_category

class CategorySubscribers(models.Model):
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    user= models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)




    def __str__(self):
        return f'{self.user, self.category}'


class Post(models.Model):
    post_datetime = models.DateTimeField(auto_now_add = True)
    post_title = models.CharField(max_length = 64, default = "Default value")
    article_text = models.TextField()
    rating_article = models.FloatField(default = 0.0)

    article = 'AR'
    news = 'NE'

    POSITIONS = [
    (article, 'Статья'),
    (news, 'Новость'),
]
    position = models.CharField(max_length = 2, choices = POSITIONS, default = news)
    author_post = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_category = models.ManyToManyField(Category, through = 'PostCategory')

    def __str__(self):
        return self.post_title

    def get_absolute_url(self): # добавим абсолютный путь чтобы после создания нас перебрасывало на страницу с товаром
        return f'/news/{self.id}' 

    def post_like(self):
        self.rating_article += 1
        self.save()

    def post_dislike(self):
        self.rating_article -= 1
        self.save()

    def preview(self):
        text_preview = self.article_text[:124]+'...'
        return text_preview

    def typeNews(self):
        choice = self.position
        if choice == 'AR':
            pos = 'Статья'
        else:
            pos = 'Новость'
        return pos


    

class PostCategory(models.Model):
    category_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category_category = models.ForeignKey(Category, on_delete=models.CASCADE) 

    def __str__(self):
        return f'{self.category_post}'   

class Comment(models.Model):
    comment_text = models.CharField(max_length = 255, default = "Your comment")
    comment_datetime = models.DateTimeField(auto_now_add = True)
    rating_comment = models.FloatField(default = 0.0)
    post_comment = models.ForeignKey(Post, on_delete=models.CASCADE) 
    comment_user = models.ForeignKey(User, on_delete=models.CASCADE) 

    def comment_like(self):
        self.rating_comment += 1
        self.save()

    def comment_dislike(self):
        self.rating_comment -= 1
        self.save()

