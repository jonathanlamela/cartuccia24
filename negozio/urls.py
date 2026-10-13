from django.conf.urls import url

from negozio import views as negozio_views

from django.contrib.auth.views import password_reset_confirm
from django.conf.urls.static import static
from cartuccia24 import settings
from django.conf.urls import include

urlpatterns = [
    url(r'slides/(\d)/$', negozio_views.slide_element),
    url(r'index/$',negozio_views.home,name='home',),
    url(r'contattaci/$',negozio_views.contattaci),
    url(r'^$', negozio_views.home,name='home',),
    url(r'^s/', negozio_views.get_page,name='pagina',),
    url(r'^st/', negozio_views.get_printer,name='get-stampante'),
    url(r'^pr/', negozio_views.get_product,name='get-prodotto'),
    url(r'^serie/(\d+)/',negozio_views.produttore),
    url(r'^stampante/(\d+)/serie/(\d+)', negozio_views.stampanti_serie),
    url(r'^stampante/(?P<slug>[\w\-]+)', negozio_views.render_printer,name='mostra-stampante',),
    url(r'^prodotto/(?P<slug>[\w\-]+)', negozio_views.render_product,name='mostra-prodotto',),
    url(r'ricerca/$',negozio_views.ricerca),
    url(r'produttore/tutti', negozio_views.produttori),
    url(r'produttore/(\d+)/$', negozio_views.ricerca_produttore),
    url(r'search-engine/$', negozio_views.motore_ricerca),
    url(r'^get-series', negozio_views.serie_ajax.as_view()),
    url(r'^get-printers', negozio_views.printers_ajax),
    url(r'img-printer/(\d+)/$', negozio_views.get_printer_image),
    url(r'img-product/(\d+)/$', negozio_views.get_product_image),
    url(r'^login',negozio_views.login,name='login'),
    url(r'^logout', negozio_views.logout,name='logout'),
    url(r'^registrazione/email/(\d+)/$', negozio_views.reinviaEmail),
    url(r'^registrazione/conferma/(?P<chiave>[\w\-]+)', negozio_views.confermaRegistrazione),
    url(r'^registrazione/',negozio_views.registrazione),
    url(r'^recupera/password/conferma/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        password_reset_confirm, name='password_reset_confirm'),
    url(r'^recupera/password/$', negozio_views.recupera_password),
    url(r'^account/profilo/cambia/password/$', negozio_views.cambia_password),
    url(r'^account/profilo/cambia/indirizzi/modifica/(\d+)/$', negozio_views.modifica_indirizzo),
    url(r'^account/profilo/cambia/indirizzi/elimina/(\d+)/$', negozio_views.elimina_indirizzo),
    url(r'^account/profilo/cambia/indirizzi/crea/$', negozio_views.nuovo_indirizzo),
    url(r'^account/profilo/cambia/indirizzi/$', negozio_views.indirizzi_utente),
    url(r'^account/profilo/cambia/informazioni/$', negozio_views.cambia_informazioni),
    url(r'^account/profilo/$', negozio_views.profilo),
    url(r'^account/stampanti/aggiungi/(\d+)/$', negozio_views.aggiungi_stampante),
    url(r'^account/stampanti/elimina/(\d+)/$', negozio_views.elimina_stampante),
    url(r'^account/stampanti/$', negozio_views.stampanti),
    url(r'^account/ordini/paga/paypal', include('paypal.standard.ipn.urls')),
    url(r'^account/ordini/', negozio_views.ordini),
    url(r'^carrello/aggiungi/(\d+)/$', negozio_views.aggiungi_prodotto_unico),
    url(r'^carrello/rimuovi/(\d+)/$', negozio_views.rimuovi_prodotto),
    url(r'^carrello/diminuisci/(\d+)/$', negozio_views.diminuisci_prodotto),
    url(r'^carrello/incrementa/(\d+)/$', negozio_views.incrementa_prodotto),
    url(r'^carrello/aggiungi/$', negozio_views.aggiungi_prodotto),
    url(r'^carrello/$',negozio_views.carrello),
    url(r'^images/(?P<mpn>[\w\-]+)',negozio_views.immagine_mpn),
    url(r'^citta-autocomplete/$',negozio_views.CittaAutocomplete.as_view(),name='citta-autocomplete'),
    url(r'^cliente-autocomplete/$', negozio_views.ClienteAutocomplete.as_view(), name='cliente-autocomplete'),
    url(r'^prodotto-autocomplete/$', negozio_views.ProdottoAutocomplete.as_view(), name='prodotto-autocomplete'),
    url(r'^stampante-autocomplete/$', negozio_views.StampanteAutocomplete.as_view(), name='stampante-autocomplete'),
    url(r'^ordine/completa/', negozio_views.completa_ordine),
    url(r'^ordine/conferma/(\d+)/$', negozio_views.conferma_ordine),
    url(r'^sitemap/$', negozio_views.sitemap),
    url(r'^sitemap/generate',negozio_views.genera_sitemap),


]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.ASSETS_URL, document_root=settings.ASSETS_ROOT)