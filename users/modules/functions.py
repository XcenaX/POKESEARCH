from users.models import MyUser
import string
import random

def get_parameter(request, name):
    try:
        return request.GET[name]
    except:
        return None 

def post_parameter(request, name):
    try:
        return request.POST[name]
    except:
        return None 

def post_file(request, name):
    try:
        return request.FILES.getlist(name)
    except:
        return None

def session_parameter(request, name):
    try:
        return request.session[name]
    except:
        return None

def get_current_user(request):
    try:
        return MyUser.objects.get(id=int(request.session["user"]))
    except: 
        if request.user.is_authenticated:
            return request.user
        return None
        