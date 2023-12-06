from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth.hashers import make_password, check_password
from area.settings import EMAIL_HOST
from users.modules.functions import *
from django.urls import reverse
from django.http import JsonResponse
from users.models import MyUser, VerificationPhone
from rest_framework.response import Response
from django.db.models import Q
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import SetPasswordForm
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import logout
from django.utils.html import strip_tags

class LoginView(View):
    template_name = "login.html"
    def get(self, request, *args, **kwargs):                            
        return render(request, self.template_name, {})
    def post(self, request, *args, **kwargs):
        email = post_parameter(request, "email")
        password = post_parameter(request, "password")
        
        user = None
        try:
            user = MyUser.objects.get(email=email)
        except Exception as e:              
            return render(request, self.template_name, {
                "error": "Неверный логин или пароль!"
            })
        if check_password(password, user.password):  
            old_vers = VerificationPhone.objects.filter(email=email)
            for ver in old_vers:
                ver.delete()

            ver = VerificationPhone.objects.create(email=email)
            ver.generate_code()            
            request.session["verify_user_id"] = user.id

            message = render_to_string('two_factor.html', {
                'code': ver.code,                            
            })
            send_mail(
                "Вход на сайте POKESEARCH",
                message,
                EMAIL_HOST,
                [email]
            )

            return redirect(reverse("polls:check_code"))
        return render(request, self.template_name, {
            "error": "Неверный логин или пароль!"
        })

class RegisterView(View):
    template_name = "register.html"
    def get(self, request, *args, **kwargs):                            
        return render(request, self.template_name, {})
    def post(self, request, *args, **kwargs):
        email = post_parameter(request, "email")
        password = post_parameter(request, "password")
        username = post_parameter(request, "username")
        try:
            MyUser.objects.get(Q(email=email) | Q(username=username)) 
            return JsonResponse({"error": "Пользователь уже существует!"})
        except:
            pass

        request.session["register_email"] = email
        request.session["register_password"] = password
        request.session["register_username"] = username

        old_vers = VerificationPhone.objects.filter(email=email)
        for ver in old_vers:
            ver.delete()

        ver = VerificationPhone.objects.create(email=email)
        ver.generate_code()

        message = render_to_string('two_factor.html', {
            'code': ver.code,                            
        })
        send_mail(
            "Подтверждение почты",
            message,
            EMAIL_HOST,
            [email]
        )
        return redirect(reverse("polls:confirm_email"))
        

class ConfirmEmail(View):
    template_name = "check_code.html"
    def get(self, request, *args, **kwargs):                            
        return render(request, self.template_name, {})
    def post(self, request):
        code = None
        email = session_parameter(request, "register_email")
        password = session_parameter(request, "register_password")
        username = session_parameter(request, "register_username")
        try:
            code = request.POST["code"]            
        except:
            return render(request, self.template_name,{
                "error": "Неправильный код!"
            })
        
        if not email or not password:
            return redirect("polls:register")

        verification_phone = VerificationPhone.objects.filter(email=email, code=code).first()
        if not verification_phone:
            return render(request, self.template_name,{
                "error": "Неправильный код!"
            })
        
        hash_password = make_password(password)
        user = MyUser.objects.create(email=email, password=hash_password, username=username)
        user.save()

        request.session["user"] = user.id
        del request.session["register_email"]
        del request.session["register_password"]
        del request.session["register_username"]
        verification_phone.delete()

        return redirect(reverse("polls:login"))

class LogoutView(View):    
    def get(self, request, *args, **kwargs):                            
        return JsonResponse({"error": "GET method not allowed!"})
    def post(self, request, *args, **kwargs):
        try:
            del request.session["user"]
        except:
            logout(request)
        return redirect(reverse("polls:login"))
    

class RequestPasswordResetView(View):
    template_name = 'request_reset_password.html'

    def get(self, request):
        return render(request, self.template_name, {})

    def post(self, request):
        email = post_parameter(request, "email")
        
        try:
            user = MyUser.objects.get(email=email)
        except (TypeError, ValueError, OverflowError, MyUser.DoesNotExist):
            user = None

        if user:
            verification_phone = VerificationPhone.objects.create(email=email)
            message = render_to_string('restore_password_email.html', {
                'link': verification_phone.generate_link(),                            
            })
            plain_message = strip_tags(message)
            send_mail(
                "Восстановление пароля",
                plain_message,
                EMAIL_HOST,
                [email],
                html_message=message
            )
            return redirect(reverse("polls:password_requested"))              
        else:
            return render(request, self.template_name, {
                "error": "Неверный email!"
            })  

class PasswordRequested(View):
    def get(self, request):
        return render(request, 'success_request_restore_password.html')                               


class PasswordResetConfirmView(View):
    template_name = 'restore_password_confirm.html'

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = MyUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, MyUser.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            context = {'form': SetPasswordForm(user), 'uidb64': uidb64, 'token': token}
            return render(request, self.template_name, context)
        else:
            return render(request, 'invalid_link.html')

    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = MyUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, MyUser.DoesNotExist):
            user = None        
       
        print("User:", user)
        
        if user is not None and default_token_generator.check_token(user, token):
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()              
                return redirect(reverse("polls:login"))  
            else:
                context = {'form': form, 'uidb64': uidb64, 'token': token}
                return render(request, self.template_name, context)
        else:
            return render(request, 'invalid_link.html')  

class CheckCode(View):
    template_name = "check_code.html"

    def get(self, request):
        return render(request, self.template_name,{})
    def post(self, request):
        code = None
        user_id = session_parameter(request, "verify_user_id")
        try:
            code = request.POST["code"]            
        except:
            return render(request, self.template_name,{
                "error": "Неправильный код!"
            })
        
        try:
            user = MyUser.objects.get(id=user_id)
        except:
            user = None
        
        if not user:
            return redirect(reverse("main:login"))

        verification_phone = VerificationPhone.objects.filter(email=user.email, code=code).first()
        if not verification_phone:
            return render(request, self.template_name,{
                "error": "Неправильный код!"
            })
        
        request.session["user"] = user.id
        del request.session["verify_user_id"]
        verification_phone.delete()

        return redirect(reverse("polls:home"))
    

def signup_redirect(request):
    messages.error(request, "Что-то пошло не так! Похоже у вас уже есть аккаунт с этим email!")
    return redirect("homepage")