import logging
 
from django.conf import settings
 
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution


from news.models import Post, Author, Category, PostCategory, Comment, User, CategorySubscribers
from datetime import datetime, timedelta
from django.shortcuts import render, reverse, redirect
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives # импортируем класс для создание объекта письма с html
from django.template.loader import render_to_string
from django.conf import settings

 
logger = logging.getLogger(__name__)
 
 
# наша задача по выводу текста на экран
def my_job():
    #  Your job processing logic here... 
    print("Выполняем задачу")
    allUsers = User.objects.all()  #получаем список юзеров
    for curUser in allUsers:   # перебираю юзеров
        if curUser.email:       #если емаил существует


            send_user = curUser.username  #получаем юзера
            send_user_Email = curUser.email

            today_day = datetime.now()   # получаем дату сегодня
            result_date = today_day - timedelta(days = 7) # получаем дату минус 7 дней
            sortPost = Post.objects.filter(post_datetime__gte = result_date, post_datetime__lte = today_day)  #получаем список новостей за неделю 
            usCat = Category.objects.filter(subscribers= User.objects.get(username=str(send_user)))  #получаем список категорий на которые подписан юзер
                

            email_subscribers_week_result = []  #тут будем хранить Ай ди новостей которые отправим
            for cat in usCat: #тут у нас категории юзера

                for sortedCat in sortPost:  # тут у нас все категории данного поста
                    postCat = Post.objects.get(pk=sortedCat.id).post_category.all()   
                    for allPostCategory in postCat: #и вот наконец сравниваем юзера и все категории новости
                        #print("tut", allPostCategory, 'user', cat)
                        if allPostCategory == cat:
                            email_subscribers_week_result.append(sortedCat.id)  #если совпало то записываем айди чтобы потом выслать юзеру 
            print(email_subscribers_week_result)        
                # теперь займемся отправкой новостей

            html_content = render_to_string( 
            'subscribe_weekly.html',
            {
            'user': curUser.username, 'cat': cat, 'art_id':email_subscribers_week_result,
            }

            )

            msg = EmailMultiAlternatives(
            subject=f'{send_user_Email} ',    #кому
                
            body=f'Недельная подписка категорию', 
            from_email='destpoch22@mail.ru',
            to=[f'{send_user_Email}', ]  
            )

            msg.attach_alternative(html_content, "text/html")
            msg.send() # отсылаем
            print("Закончили задачу")
    

 
 
# функция которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)
 
 
class Command(BaseCommand):
    help = "Runs apscheduler."
 
    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")
        
        # добавляем работу нашему задачнику
        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day_of_week="sun"),  # Тоже самое что и интервал, но задача тригера таким образом более понятна django
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")
 
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )
 
        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
            