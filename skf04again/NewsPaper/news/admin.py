from django.contrib import admin
from .models import Author, Category, Post, PostCategory, Comment, CategorySubscribers

# Register your models here.

# тут действия в админке дописываем

def add_rating(modeladmin, request, queryset): # все аргументы уже должны быть вам знакомы, самые нужные из них это request — объект хранящий информацию о запросе и queryset — грубо говоря набор объектов, которых мы выделили галочками.
    for changes in queryset:
        changes.post_like()
add_rating.short_description = 'Добавляем 1 рейтинга выбранным статьям' # описание для более понятного представления в админ панеле задаётся, как будто это объект



def minus_rating(modeladmin, request, queryset): # все аргументы уже должны быть вам знакомы, самые нужные из них это request — объект хранящий информацию о запросе и queryset — грубо говоря набор объектов, которых мы выделили галочками.
    for changes in queryset:
        changes.post_dislike()
minus_rating.short_description = 'Уменьшаем 1 рейтинга выбранным статьям' # описание для более понятного представления в админ панеле задаётся, как будто это объект




class PostAdmin(admin.ModelAdmin):
    # list_display — это список или кортеж со всеми полями, которые вы хотите видеть в таблице с товарами
    list_display = ('post_datetime', 'post_title', 'position','rating_article') # генерируем список имён всех полей для более красивого отображения
    list_filter = ('post_datetime',  'position','rating_article') #add filters for items
    search_fields = ('position', 'post_title', 'rating_article')   #add searched items
    actions = [add_rating, minus_rating] # добавляем действия в список


admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Post, PostAdmin)
admin.site.register(PostCategory)
admin.site.register(Comment)
admin.site.register(CategorySubscribers)

