from django.db import models
from datetime import date
import datetime

  

class New(models.Model):
    title = models.CharField(max_length=201)    
    pub_date = models.CharField(default=str(datetime.datetime.today), max_length=300)    
    content = models.CharField(max_length=200)    
    img_url = models.CharField(max_length=200)    
    url_name = models.CharField(max_length=200, default="")  
    views = models.IntegerField(default=0)  

class User(models.Model):
    login = models.CharField(max_length=100, default="") 
    password = models.CharField(max_length=100, default="") 
    FIO = models.CharField(max_length=100, default="")