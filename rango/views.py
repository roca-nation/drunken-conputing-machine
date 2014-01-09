from django.shortcuts import render

from django.http import HttpResponse

from django.template import RequestContext
from django.shortcuts import render, render_to_response, get_object_or_404

from rango.models import Category, Page

from rango.forms import CategoryForm, PageForm
from django.utils import timezone

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from rango.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime

from rango.bing_search import run_query

from django.contrib.auth.models import User#, UserProfile
from rango.models import UserProfile
from django.shortcuts import redirect

#from django.http import Http404



def get_cat_list():
    cat = Category.objects.all()
    for category in cat:
        category.url = category.name.replace(' ', '_')
    return cat





def index(request): 
    #request.session.set_test_cookie()#just a test
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    

    for category in category_list:
        category.url = category.name.replace(' ', '_')
    context_dict = {'categories': category_list, 'pages': page_list}

    if request.session.get('last_visit_date'):
        last_visit_date = request.session.get('last_visit_date')
        num_of_visits = request.session.get('num_of_visits', 0)

        if (datetime.now() - datetime.strptime(last_visit_date[:-7], "%Y-%m-%d %H:%M:%S")).days > 0:
            request.session['num_of_visits'] = num_of_visits + 1
            request.session['last_visit_date'] = str(datetime.now())
    else:
        request.session['num_of_visits'] = 1
        request.session['last_visit_date'] = str(datetime.now())
    cat_list = get_cat_list()        
    context_dict['cat_list'] = cat_list
    return render(request, 'rango/index.html', context_dict)
    




def about(request):
    context_dict = {'visits': 0}
    if request.session.get('num_of_visits'):
        context_dict['visits'] = request.session['num_of_visits']    
    cat_list = get_cat_list()        
    context_dict['cat_list'] = cat_list
    return render(request, 'rango/about.html', context_dict)

def category(request, category_name_url):
    context = RequestContext(request)
    category_name = category_name_url.replace('_', ' ')
    context_dict = {'category_name':category_name}


    try:
        category = Category.objects.get(name=category_name)
        
    #category = get_object_or_404(Category, name=category_name)        

        pages = Page.objects.filter(category=category).order_by('-views')

        context_dict['pages'] = pages
        context_dict['category'] = category
        context_dict['category_name_url'] = category_name_url
    
    except Category.DoesNotExist:

        pass
        #raise Http404
    cat_list = get_cat_list()        
    context_dict['cat_list'] = cat_list
    return render_to_response('rango/category.html', context_dict, context)    
        

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)#What's commit?
            #return index(request)
            return HttpResponseRedirect(reverse('rango:index'))
        else:
            print form.errors
    else:
        form = CategoryForm()
    context_dict = {'form': form}
    cat_list = get_cat_list()        
    context_dict['cat_list'] = cat_list
    return render(request, 'rango/add_category.html', context_dict)


def encode_url(url):
    return url.replace(' ', '_')

def decode_url(url):
    return url.replace('_', ' ')

@login_required
def add_page(request, category_name_url):
    category_name = decode_url(category_name_url)
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid(): 
            page = form.save(commit=False)
            cat = Category.objects.get(name=category_name)
            page.category = cat
            page.views = 0
            page.pub_date = timezone.now()
            page.save()
            #return category(request, category_name_url)
            return HttpResponseRedirect(reverse('rango:category', args=(category_name_url,)))
        else:
            print form.errors
            #print form 
    else:
        form = PageForm()
    
    context_dict = {'category_name_url':category_name_url, 'category_name':category_name, 'form':form}
    #DONT EVER FORGET RETURN!!!!!!!!!!!!!
    cat_list = get_cat_list()        
    context_dict['cat_list'] = cat_list
    return render(request, 'rango/add_page.html', context_dict)




def register(request):
    #if request.session.test_cookie_worked():
        #print '>>>> TEST COOKIE WORKED!'
        #request.session.delete_test_cookie()
            #just a test^
    registered = False
    
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            
            user = user_form.save()
            #user = user_form
            
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)#This is unnecessary as well since pic/url is not required
            profile.user = user#Do we need this??
            #I guess yes, because this 'user' is new one, and needs to referenced to newly created profile...
           

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            
            profile.save()
            registered = True

        else:
            print user_form.errors, profile_form.errors
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    context_dict = {'user_form': user_form}
    context_dict['profile_form'] = profile_form
    context_dict['registered'] = registered
    cat_list = get_cat_list()        
    context_dict['cat_list'] = cat_list
    return render(request, 'rango/register.html', context_dict)


def user_login(request):
    disabled_account = False
    error_message= False
    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

            # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.

        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('rango:index'))

            else:
                disabled_account = True
        
        else:
            print 'Invalid login details: {0}, {1}'.format(username, password)#<- print out in the TERMINAL!!!
            #return HttpResponse('Invalid login details supplied.')
            error_message = True
    #else:
    context_dict = {'error_message':error_message}
    context_dict['disabled_account'] = disabled_account
    cat_list = get_cat_list()        
    context_dict['cat_list'] = cat_list
    return render(request, 'rango/login.html', context_dict) 




@login_required
def restricted(request):
    context_dict = dict()
    cat_list = get_cat_list()        
    context_dict['cat_list'] = cat_list
    return render(request, 'rango/restricted.html', context_dict) 

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('rango:index'))
    


def search(request):
    result_list =[]
    search_query = ''
    if request.method =='POST':
        print 'Hello'+request.POST['query']+'World'
        query = request.POST['query'].strip()

        if query:
            print 'query!'
            result_list = run_query(query)
            search_query = query
    context_dict = {'result_list':result_list}
    context_dict['search_query'] = search_query
    cat_list = get_cat_list()        
    context_dict['cat_list'] = cat_list
    return render(request, 'rango/search.html', context_dict)




@login_required
def profile(request):
    context_dict = {}
    cat_list = get_cat_list()        
    context_dict['cat_list'] = cat_list
    u = User.objects.get(username=request.user)
    try:
        up = UserProfile.objects.get(user=u)
    except:
        up = None
    context_dict['user'] = u
    context_dict['userprofile'] = up
    return render(request, 'rango/profile.html', context_dict)


def track_url(request):
    #context_dict = {}
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views += 1
                page.save()
                url = page.url
            except:
                pass
    return redirect(url)


@login_required
def like_category(request):
    #context = RequestContext(request)
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']

    likes = 0
    
    if cat_id:
        category = Category.objects.get(id=int(cat_id))
        if category:
            likes = category.likes + 1
            category.likes = likes
            category.save()

    return HttpResponse(likes+1)    




def get_category_list(max_results=0, starts_with=''):
   
    cat_list = []

    if starts_with:
        cat_list = Category.objects.filter(name__startswith=starts_with)
    else:
        cat_list = Category.objects.all()
        
    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]

    for cat in cat_list:
        cat.url = encode_url(cat.name)
    return cat_list



def suggest_category(request):
    cat_list = []
    starts_with = ''    
    if request.method =='GET':
        starts_with = request.GET['suggestion']
    else:
        starts_with = request.POST['suggestion']

    cat_list = get_category_list(8, starts_with)
    context_dict = { 'cat_list': cat_list }    
    return render(request, 'rango/category_list.html', context_dict)



@login_required
def auto_add_page(request):
    cat_id = None
    url = None
    title = None
    context_dict = {}
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']
        print 'cat_id = ', cat_id
        print 'url = ', url
        print 'title = ', title
        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            p = Page.objects.get_or_create(category=category, title=title, url=url)
            pages = Page.objects.filter(category=category).order_by('-views')

            context_dict['pages'] = pages
    return render(request, 'rango/page_list.html', context_dict)









