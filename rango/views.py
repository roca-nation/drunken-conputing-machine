from django.shortcuts import render

from django.http import HttpResponse

from django.template import RequestContext
from django.shortcuts import render, render_to_response, get_object_or_404

from rango.models import Category, Page

#from django.http import Http404

def index(request): 
    #context = RequestContext(request)
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}

    for category in category_list:
        category.url = category.name.replace(' ', '_')

    return render(request, 'rango/index.html', context_dict)

def about(request):
    #context = RequestContext(request)
    return render_to_response('rango/about.html')

def category(request, category_name_url):
    context = RequestContext(request)
    category_name = category_name_url.replace('_', ' ')
    context_dict = {'category_name':category_name}


    #try:
        #category = Category.objects.get(name=category_name)
        
    category = get_object_or_404(Category, name=category_name)        

    pages = Page.objects.filter(category=category)

    context_dict['pages'] = pages
    context_dict['category'] = category
    
    #except Category.DoesNotExist:

        #pass
        #raise Http404

    return render_to_response('rango/category.html', context_dict, context)    
        











