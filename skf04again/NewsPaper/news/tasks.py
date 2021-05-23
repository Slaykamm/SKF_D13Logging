from celery import shared_task


from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives # импортируем класс для создание объекта письма с html
from django.template.loader import render_to_string
from .models import Post, Author, Category, PostCategory, Comment, User, CategorySubscribers
from datetime import datetime, timedelta
from .filters import NewsFilter # импортируем недавно написанный фильтр






@shared_task
def creationNotice(newsId):
  
    id = newsId   # получаем ID побуликованной новости

    postCat = Post.objects.get(pk=id).post_category.all()  # получаем к каой категории она отностися
    for cat in postCat:   # пошли по категориям, к которым относится опубликованная новость
        #получаем емаил подписчиков. 
        emails_list = []  
        subscribers = User.objects.filter(category = cat)  #получили список подписчков.
        for subscriber_name in subscribers:  #итерируемся по списку - получаем имена
            subscriber_email = User.objects.get(username=str(subscriber_name)).email #из имен получаем емаил
            emails_list.append(subscriber_email)  #добавляем в список емаилов
            emailarticle = Post.objects.get(pk=id).article_text


        html_content = render_to_string( 
        'subscribe_created.html',
        {
        'title': cat, 'text':emailarticle,  'art_id':id,  #
        }

        )

        msg = EmailMultiAlternatives(
        subject=f'Создана новая новость ',   
                
        body=f'В категории, на которую Вы подписались появилась новое сообщение', 
        from_email= 'destpoch44@mail.ru', #'destpoch33@mail.ru',  #'destpoch22@mail.ru'
        to=emails_list  
        )

        msg.attach_alternative(html_content, "text/html")
        print("печатаем что отправили:", 'title', cat, 'text', emailarticle,  'art_id',id)
        #msg.send() # отсылаем

@shared_task
def weeklyCategoryUpdates():
    freshNews = Post.objects.values_list('id', flat=True).exclude(post_datetime__lt = datetime.now()-timedelta(days=7))   #получаем все новости за неделю
    newsAll = Post.objects.values_list('id')

    weeklyNewsIds = []
    for idk in freshNews:
        weeklyNewsIds.append(idk)  # тут получил список айти новостей за неделю


#1  Берем пользователя и вычленияем его емаил 
    userList = User.objects.all()  #получили bимена всех подписчков.
#    emails_list = []
    for userName in userList:   # перебираем по именно и получаем емаил к каждому имени
        userEmail = User.objects.get(username=str(userName)).email
        if userEmail: #если емаил есть то добавляем его в список емаилов.
#            emails_list.append(userEmail) 
#2      Получением список категорий, членом которых он является
            usCat = Category.objects.filter(subscribers= User.objects.get(username=str(userName)))
            if usCat:

    
    #3          Делаем общий по пользователю список ID для отправки
                user_id_list_for_sending = []
            #дальше начинаем перебирать категории пользователя и сравнивать с категорией новости. Если оно совпадает - добавляем ID в лист
                for newsId in weeklyNewsIds:  #список новостей
                    postCat = Post.objects.get(pk=newsId).post_category.all()  # получаем к каой категории она отностися
                    for categ in usCat: 
                        if categ in postCat:
                            user_id_list_for_sending.append(newsId)  

                print("User", userName, "IDs", user_id_list_for_sending) 
                
                html_content = render_to_string( 
                'subscribe_weekly.html',
                {
                'user': userName, 'art_id':user_id_list_for_sending,
                }

                )
                msg = EmailMultiAlternatives(
                subject=f'{userName} ',    #кому
                
                body=f'недельные обновления в категориях ', 
                from_email='destpoch44@mail.ru',
                to=[f'{userEmail}', ]  
                )

                msg.attach_alternative(html_content, "text/html")
                print("Вместо отправки еженедельной подписки печатаем", 'user', userName, 'art_id',user_id_list_for_sending)
#                msg.send() # отсылаем
