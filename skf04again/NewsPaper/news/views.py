from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView # импортируем класс, который говорит нам о том, что в этом представлении мы будем выводить список объектов из БД
from .models import Post, Author, Category, PostCategory, Comment, User, CategorySubscribers
from datetime import datetime, timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin

from django.shortcuts import render
from django.views import View # импортируем простую вьюшку
from django.core.paginator import Paginator
from .filters import NewsFilter # импортируем недавно написанный фильтр
from .forms import PostForm
from django.views.generic import TemplateView
from django.shortcuts import render, reverse, redirect
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives # импортируем класс для создание объекта письма с html
from django.template.loader import render_to_string
from django.db.models.signals import m2m_changed




 
class PostList(ListView):
    model = Post  # указываем модель, объекты которой мы будем выводить
    template_name = 'news.html'  # указываем имя шаблона, в котором будет лежать html, в котором будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    context_object_name = 'posts'  # это имя списка, в котором будут лежать все объекты, его надо указать, чтобы обратиться к самому списку объектов через html-шаблон
    queryset = Post.objects.order_by('-post_datetime')  #сортируем по уменьшению
    paginate_by = 10
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id = self.kwargs.get('pk')
        context['time_now'] = datetime.now()   
        context['logged_user'] = self.request.user.username  # это, чтобы в шаблоне показывать вместо логина имя залогиненного




        return context

class PostDetailView(LoginRequiredMixin, DetailView):
#
    template_name = 'news_detail.html'  # указываем имя шаблона, в котором будет лежать html, в котором будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    queryset = Post.objects.all()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        id = self.kwargs.get('pk')
        user = self.request.user.username
        context['logged_user'] = self.request.user.username   # это, чтобы в шаблоне показывать вместо логина имя залогиненного

        postCat = Post.objects.get(pk=id).post_category.all()   # получаем к каой категории относится пост
        usCat = Category.objects.filter(subscribers= User.objects.get(username=str(user))) # к какой категории относится юзер 

        context['is_not_subscriber'] = False  # делаем переменную фолс по умолчанию если юзер никуда не подписан. в зависимости от этого кнопка подписка или отписка

        if usCat.exists():   #проверяем, что пользователь хоть куда то подписан, иначе сразу предлагаем подписаться.
            for check in usCat:  # в каждом юзере проверяем каждую категорию
                for check2 in postCat:
                           
                    if check == check2:
                        context['is_not_subscriber'] = True #  если есть соответсвие значени пеменную делаем тру и передаем в шаблон

                        
        else:
            context['is_not_subscriber'] = False

        context['form'] = PostForm()  # added
        return context

class SubscribeView(DetailView):
#
    template_name = 'news_detail.html'  # указываем имя шаблона, в котором будет лежать html, в котором будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    queryset = Post.objects.all()
    success_url = '/news/'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id = self.kwargs.get('pk')
        posts = Post.objects.get(pk=id)
        user = self.request.user.username  #  тут получаем данные для передачи в емаил, который отправим юзерам
        userEmail = self.request.user.email
        context['logged_user'] = self.request.user.username


        #получаем тут текст статьи
        emailarticle = Post.objects.get(pk=id).article_text
        emailtitle = Post.objects.get(pk=id).post_title



        postCat = Post.objects.get(pk=id).post_category.all()
        usCat = Category.objects.filter(subscribers= User.objects.get(username=str(user)))


        for cat in postCat:
            if not CategorySubscribers.objects.filter(category = cat, user = self.request.user).exists():   # делаем если подпиччика нет
                CategorySubscribers.objects.create(category = cat, user = self.request.user )
                forEmailCat = cat #получаем категорию, чтобы отправить юзеру по емаил
                context['is_not_subscriber'] = False

                html_content = render_to_string( 
                'subscribe_created.html',
                {
                'user': user, 'cat': cat, 'title': emailtitle, 'text':emailarticle, 'art_id':id,
                }

                )
                print ('asdas', id)
                msg = EmailMultiAlternatives(
                subject=f'{self.request.user} ',    #кому
                
                body=f'Вы подписались на категорию {forEmailCat}', 
                from_email='destpoch44@mail.ru',
                to=[f'{userEmail}', ]  
                )

                msg.attach_alternative(html_content, "text/html")
                msg.send() # отсылаем

        context['form'] = PostForm()  # added
        return context
     
class UnsubscribeView(DetailView):
#
    template_name = 'news_detail.html'  # указываем имя шаблона, в котором будет лежать html, в котором будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    queryset = Post.objects.all()
    success_url = '/news/'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id = self.kwargs.get('pk')
        user = self.request.user.username
        userEmail = self.request.user.email
        context['logged_user'] = self.request.user.username


        usCat = Category.objects.filter(subscribers= User.objects.get(username=str(user)))
        categ = Post.objects.get(pk=id).post_category.all()

        
        for cat in categ:
            CategorySubscribers.objects.filter(category = cat, user = self.request.user).delete()  # проверяем что подпичсчик есть
            context['is_not_subscriber'] = True
            forEmailCat = cat #получаем категорию, чтобы отправить юзеру по емаил


            send_mail(
            subject=f'{self.request.user} ',    #кому
                
            message=f'Вы отписались от категории {forEmailCat}', 
            from_email='destpoch44@mail.ru',
            recipient_list=[f'{userEmail}', ]  
            )
            
            

        context['form'] = PostForm()  # added
        return context


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


class PostCreateView(CreateView):

    template_name = 'add.html'
    form_class = PostForm

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['logged_user'] = self.request.user.username
        #id = self.pk 
        print("IDL", context)




        return context


class PostSearch(ListView):
    model = Post  # указываем модель, объекты которой мы будем выводить
    template_name = 'news_search.html'  # указываем имя шаблона, в котором будет лежать html, в котором будут все инструкции о том, как именно пользователю должны вывестись наши объекты
    context_object_name = 'post_search'  # это имя списка, в котором будут лежать все объекты, его надо указать, чтобы обратиться к самому списку объектов через html-шаблон
    form_class = PostForm #добавил тут  добавляем форм класс, чтобы получать доступ к форме через метод POST

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = NewsFilter(self.request.GET, queryset=self.get_queryset()) # вписываем наш фильтр в контекст
        context['categories'] = Category.objects.all()
        context['form'] = PostForm()  # added
        context['logged_user'] = self.request.user.username
        return context
        #added below

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST) # создаём новую форму, забиваем в неё данные из POST запроса 
 
        if form.is_valid(): # если пользователь ввёл всё правильно и нигде не накосячил то сохраняем новый товар
            form.save()
 
        return super().get(request, *args, **kwargs)

class PostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):

    #model = Post
    template_name = 'add.html'
    form_class = PostForm
    permission_required = ('news.add_post',)

    # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте который мы собираемся редактировать
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name = 'authors').exists()
        context['logged_user'] = self.request.user.username

        return context

 
# дженерик для удаления товара
class PostDeleteView(DeleteView):
    template_name = 'news_delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'




      
        #tеще один способ получения голых данных из queryset
#        person = Post.objects.filter(id = id).values('post_category')
#        list1 = list(person)
#        i = 0
#        my_list1 = [0]*len(list1)
#        for i in range(0, len(list1)):
#            my_listX=list1[i]
#            my_list1[i] = my_listX['post_category']

#        print("LIST OF CATEGORIES:", my_list1 )

