from django import template
 
register = template.Library()
 
 
@register.filter(name='censor')  
def censor(value):

    censored_text = ""       
    operate_text = value.split(' ')
    rude_words = ["сука", "блять", "нахуй", "мудак"]

    for word in operate_text:
            
        if word in rude_words:
            censored_text += "МАТ" + " "
        else:
            censored_text += word + " "
    return str(censored_text) 
    