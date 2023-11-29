from django.db import models
from django.contrib.auth.models import AbstractUser
from users.modules.functions2 import get_random_string_of_numbers

from area.settings import CODE_LENGTH

from area.settings import BASE_URL
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator


class MyUser(AbstractUser): 
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] 

    def __str__(self) -> str:
        return self.username


class VerificationPhone(models.Model):
    email = models.TextField(null=True, blank=True)
    code = models.TextField(default="")

    def generate_code(self):        
        code_unique = False
        ran = ""
        while not code_unique:
            ran = get_random_string_of_numbers(CODE_LENGTH)
            if len(VerificationPhone.objects.filter(code=ran))==0:
                code_unique = True
        self.code = ran
        self.save()
    
    def generate_link(self):
        user = self.get_user()
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        link = f"{BASE_URL}/reset_password/{uid}/{token}/"
        return link

    def get_user(self):
        try:
            return MyUser.objects.get(email=self.email)
        except:
            return None

    def __str__(self):
        return self.email + " | " + self.code