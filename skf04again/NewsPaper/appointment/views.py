from django.shortcuts import render, reverse, redirect
from django.views import View
from django.core.mail import send_mail
from datetime import datetime
 
from .models import Appointment

from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
 
 
class AppointmentView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'make_appointment.html', {})
 
    def post(self, request, *args, **kwargs):
        appointment = Appointment(
            date=datetime.strptime(request.POST['date'], '%Y-%m-%d'),
            client_name=request.POST['client_name'],
            message=request.POST['message'],
        )
        appointment.save()
 
        # отправляем письмо
        send_mail( 
            subject=f'{appointment.client_name} {appointment.date.strftime("%Y-%M-%d")}',  # имя клиента и дата записи будут в теме для удобства
            message=appointment.message, # сообщение с кратким описанием проблемы
            from_email='destpoch@yandex.ru', # здесь указываете почту, с которой будете отправлять (об этом попозже)
            recipient_list=['destpoch@mail.ru'] # здесь список получателей. Например, секретарь, сам врач и т. д.
        )
 
        return redirect('/news/')

@login_required
def subscribe_me(request):
    user = request.user
    subscribe_needed = Group.objects.get(name='Политика')
    if not request.user.groups.filter(name='Политика').exists():
        subscribe_needed.user_set.add(user)
        print(id)

    return redirect('/news/')