import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_django_project.settings')
from rango.models import Category, Page
from django.utils import timezone


def populate():
    python_cat = add_cat(name='Python', views=128, likes=64)

    add_page(cat=python_cat,
        title='Official Python Tutorial',
        url='http://docs.python.org/2/tutorial/')

    add_page(cat=python_cat,
        title='Think Pyhon',
        url='http://www.greenteapress.com/thinkpython/')


    django_cat = add_cat(name='Django', views=64, likes=32)

    add_page(cat=django_cat,
        title='Official Django Tutorial',
        url='https://doc.djangoproject.com/en/1.6/intro/tutorial01/')

    add_page(cat=django_cat,
        title='How to Tango with Django',
        url='http://www.tangowithdjango.com/')

    frame_cat = add_cat(name='Other Frameworks', views=32, likes=16)

    add_page(cat=frame_cat,
        title='Flask',
        url='http://flask.pocoo.org')

#additional goodies

    add_page(cat=python_cat,
        title="Learn Python in 10 Minutes",
        url="http://www.korokithakis.net/tutorials/python/")

    add_page(cat=django_cat,
        title="Django Rocks",
        url="http://www.djangorocks.com/")

    add_page(cat=frame_cat,
        title="Bottle",
        url="http://bottlepy.org/docs/dev/")



    for c in Category.objects.all():
        print c
        for p in Page.objects.filter(category=c):
            print '- {0} - {1}'.format(str(c), str(p))



    
def add_page(cat, title, url, views=0):
    p = Page.objects.get_or_create(category=cat, title=title, url=url, views=views, pub_date=timezone.now())[0]#Returns a tuple of (object, created<-boolean)
    return p

def add_cat(name, views=0, likes=0):
    c = Category.objects.get_or_create(name=name, views=views, likes=likes)[0]
    return c


if __name__ == '__main__':
    print 'Starting Rango population script...'
    #os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_django_project.settings')
    #from rango.models import Category, Page
    #it was originally here!!
    populate()


