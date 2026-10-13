"""cartuccia24 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from archivio import admin_views
from archivio import views

from django.contrib import admin
from django.conf.urls.static import static

from salmonella.views import label_view
from archivio import admin_views
from archivio import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^admin/salmonella/(?P<app_name>[\w-]+)/(?P<model_name>[\w-]+)/multiple/$',
        label_view,
        {
            'multi': True,
            'template_object_name': 'objects',
            'template_name': 'salmonella/multi_label.html'
        },
        name="salmonella_multi_label"),
    url(r'^admin/salmonella/(?P<app_name>[\w-]+)/(?P<model_name>[\w-]+)/$',
        label_view,
        {
            'template_name': 'salmonella/label.html'
        },
        name="salmonella_label"),
    url(r'^prodotto-autocomplete/$',admin_views.ProdottoAutocomplete.as_view(),name='prodotto-autocomplete'),
    url(r'^serie-autocomplete/$', admin_views.SerieAutocomplete.as_view(), name='serie-autocomplete'),
    url(r'^produttore-autocomplete/$', admin_views.ProduttoreAutocomplete.as_view(), name='produttore-autocomplete'),
    url(r'^categoria-autocomplete/$', admin_views.CategoriaAutocomplete.as_view(), name='categoria-autocomplete'),
    url(r'^icecat/process/$',views.runProcess),
    url(r'^archivio/generate/slug/$', views.generateSlug),
]



