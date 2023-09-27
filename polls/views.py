from .models import New
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger        
from datetime import datetime, timezone
COUNT_BLOCKS_ON_PAGE = 10
import pokebase as pb
import re

def item(request, title): 

    current_new = New.objects.filter(url_name=title).first()
    current_new.views += 1
    print(current_new.pub_date)
    current_new.save()

    return render(request, 'page.html', {
        "current_new": current_new,
    })  

def about(request):     
    return render(request, 'about.html', {        
    })  
    
def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

def main(request):      
    pub_date = request.GET.get('pub_date')              
    title = request.GET.get('title')
        
    pokemons = pb.APIResourceList('pokemon')
    q_pokemons = []
    
    if title:    
        for pokemon in pokemons:
            if re.search(title, pokemon["name"], re.IGNORECASE):
                                
                q_pokemons.append(pokemon)
        pokemons = q_pokemons
    else:
        title = ""
        for pokemon in pokemons:
            q_pokemons.append(pokemon)
        pokemons = q_pokemons

    paginator = Paginator(pokemons, COUNT_BLOCKS_ON_PAGE)     
    page = request.GET.get('page')        
    try:
        page = int(page)
    except:
        page = 1
    a = ""
    snews = ""
    pages=[]
    if page:
        try:
            snews = paginator.page(page)
        except EmptyPage:
            snews = paginator.page(paginator.num_pages)
            page = paginator.num_pages

        for i in range(page-2, page+3):
            try:
                a = paginator.page(i)
                pages.append(i)
            except:
                continue        
        if pages[-1] != paginator.num_pages:
            pages.append(paginator.num_pages)

        if pages[0] != 1:
            pages.insert(0, 1)
    else:
        pages = [1,2,3,4,5,paginator.num_pages]
        snews = paginator.page(1)
    

    return render(request, 'news.html', {
        'snews': snews,
        "title": title,     
        "pages": pages,
    })  

def popular(request):      
    pub_date = request.GET.get('pub_date')              
    title = request.GET.get('title')
        
    snews = New.objects.order_by("-views")  
    if pub_date:
        snews = snews.filter(pub_date__icontains=pub_date)
    else:
        pub_date = ""
    if title:    
        snews = snews.filter(title__icontains=title)
    else:
        title = ""
    paginator = Paginator(snews, COUNT_BLOCKS_ON_PAGE)     
    page = request.GET.get('page')        
    try:
        page = int(page)
    except:
        page = 1
    a = ""
    snews = ""
    pages=[]
    if page:
        try:
            snews = paginator.page(page)
        except EmptyPage:
            snews = paginator.page(paginator.num_pages)
            page = paginator.num_pages

        for i in range(page-2, page+3):
            try:
                a = paginator.page(i)
                pages.append(i)
            except:
                continue        
        if pages[-1] != paginator.num_pages:
            pages.append(paginator.num_pages)

        if pages[0] != 1:
            pages.insert(0, 1)
    else:
        pages = [1,2,3,4,5,paginator.num_pages]
        snews = paginator.page(1)
    
    popular = New.objects.order_by("-views")[:5]

    return render(request, 'popular.html', {
        'snews': snews,
        'pub_date': pub_date,  
        "title": title,     
        "pages": pages,
        "popular": popular,
    })  
      

