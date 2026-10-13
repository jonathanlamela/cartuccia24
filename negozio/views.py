from dal_select2.views import Select2QuerySetView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import mimetypes
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from StringIO import StringIO
import cartuccia24.settings
import requests
from django.shortcuts import render_to_response
from django.db.models import Q
from django.template import RequestContext
import ho.pisa,cStringIO
from django.contrib.auth import authenticate
from django.contrib.auth import login as effettua_accesso
from django.contrib.auth import logout as chiudi_accesso
from negozio.forms import *
import hashlib
import random
import datetime
from django.core.mail import send_mail
from django.template import Context, Template
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from cart.cart import Cart
from paypal.standard.forms import PayPalPaymentsForm
from django.db.models.functions import Length

# Create your views here.
def slide_element(request, id):
    obj = get_object_or_404(SliderChildren, pk=id)
    image = StringIO(file(obj.image_file.path, "rb").read())
    mimetype = mimetypes.guess_type(os.path.basename(obj.image_file.name))[0]

    return HttpResponse(image.read(), content_type=mimetype)


def view_404(request):
    return render_to_response('../templates/404.html', {},
                              context_instance=RequestContext(request), status=404)

def home(request):

    ultime_offerte = Prodotto.objects.all().filter(url_image__contains="http",offerte__isnull=False).order_by("?")[:48]

    marche_maggiori = Produttore.objects.raw("SELECT *,(select count(*) from archivio_stampante where marca_id=archivio_produttore.id) as Conteggio FROM archivio_produttore where image!='' ORDER BY Conteggio desc")
    marche_maggiori = marche_maggiori[:8]

    marche_objs = Stampante.objects.all().order_by("marca__nome").values_list('marca', flat=True).distinct()
    marche = list()
    for marca_id in marche_objs:
        marca = Produttore.objects.get(pk=marca_id)
        test = Stampante.objects.all().filter(marca=marca).exclude(prodotti_associati=False)

        if test > 0:
            marche.append(marca)
    return render_to_response('../templates/index.html',
                              {
                                  "settings" : cartuccia24.settings,
                                  "pages":getPages(),
                                  "marche":marche,
                                  "slider":Slider.objects.get(pk=1).slides.all(),
                                  "modelli":ultimiModelli(),
                                  "marche":Produttore.objects.all().exclude(image="").order_by("nome"),
                                  "msg_login":getLoginErrors(request),
                                  "carrello": get_current_cart(request),
                                  "ultime_offerte":ultime_offerte,
                                  "marche_maggiori":marche_maggiori

                              },
                              context_instance=RequestContext(request))


def getLoginErrors(request):
    error = None
    if "msg_login" in request.session:
        error = request.session["msg_login"]
        del request.session["msg_login"]
    return error


def ultimiModelli():
    modelli = Stampante.objects.all().exclude(Q(slug="") | Q(url_image="")).order_by("-id")[:24]
    return modelli

def ultimiProdotti():
    prodotti = Prodotto.objects.all().exclude(Q(slug="") | Q(url_image="")).order_by("-id")[:24]
    return prodotti

def getPages():
    pages = Pagina.objects.filter(parent_page__isnull=True).order_by("posizione")
    return pages

def get_page(request):
    path = request.path[3:]
    page = get_object_or_404(Pagina,url=path)
    return render_to_response('../templates/page.html', {
        "settings": cartuccia24.settings,
        "page" : page,
        "pages" : getPages(),
        "msg_login": getLoginErrors(request),
        "carrello": get_current_cart(request)
    },
                              context_instance=RequestContext(request))

def ricerca(request):

    if "keyword" in request.GET:
        keyword = request.GET["keyword"]

        printer_list = Stampante.objects.all().filter(Q(mpn__contains=keyword) | Q(ean=keyword) | Q(nome__contains=keyword) | Q(serie__nome__contains=keyword))
        product_list = Prodotto.objects.all().filter(Q(mpn__contains=keyword) | Q(ean=keyword) | Q(nome__contains=keyword))

        if "active_tab" in request.GET:
            active = request.GET["active_tab"]
        else:
            if printer_list.count() == 0:
                active = "prodotti"
            else:
                active = "stampanti"

        return render_to_response('../templates/risultati_ricerca.html', {
            "settings": cartuccia24.settings,
            "printer": printer_list,
            "product": product_list,
            "pages": getPages(),
            "active_tab":active,
            "keyword":keyword,
            "msg_login": getLoginErrors(request),
            "carrello": get_current_cart(request)

        }, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/")


def ricerca_produttore(request,produttore):

    printer_list = Stampante.objects.all().filter(marca_id=produttore)
    product_list = Prodotto.objects.all().filter(marca_id=produttore)

    if "active_tab" in request.GET:
        active = request.GET["active_tab"]
    else:
        if printer_list.count() == 0:
            active = "prodotti"
        else:
            active = "stampanti"

    return render_to_response('../templates/risultati_ricerca_produttore.html', {
        "settings": cartuccia24.settings,
        "printer": printer_list,
        "product": product_list,
        "pages": getPages(),
        "produttore":Produttore.objects.get(id=produttore),
        "active_tab":active,
        "msg_login": getLoginErrors(request),
        "carrello": get_current_cart(request)

    }, context_instance=RequestContext(request))




def motore_ricerca(request):
    pass

def render_printer(request,slug):
    printer = Stampante.objects.filter(slug=slug)[0]

    return render_to_response('../templates/stampante.html', {
        "settings": cartuccia24.settings,
        "printer": printer,
        "pages": getPages(),
        "msg_login": getLoginErrors(request),
        "carrello": get_current_cart(request)

    },context_instance=RequestContext(request))

def render_product(request,slug):
    product = Prodotto.objects.filter(slug=slug)[0]

    modelli = Stampante.objects.all().filter(prodotti_associati__in=Prodotto.objects.filter(slug=slug).all())

    return render_to_response('../templates/prodotto.html', {
        "settings": cartuccia24.settings,
        "product": product,
        "pages": getPages(),
        "msg_login": getLoginErrors(request),
        "modelli":modelli,
        "carrello": get_current_cart(request)

    },context_instance=RequestContext(request))

def get_printer_image(request,id):
    obj = get_object_or_404(Stampante, pk=id)
    url = "http://www.bmhc.gov.bt/wp-content/themes/BmhcTheme/images/no.jpg"
    if (obj.url_image is not None) & (len(obj.url_image) > 0):
        url = obj.url_image

    resp = requests.get(url)
    return HttpResponse(resp)

def get_product_image(request,id):
    obj = get_object_or_404(Prodotto, pk=id)
    url = "http://www.bmhc.gov.bt/wp-content/themes/BmhcTheme/images/no.jpg"
    if (obj.url_image is not None) & (len(obj.url_image) > 0):
        url = obj.url_image

    resp = requests.get(url)
    return HttpResponse(resp)

def get_printer(request):
    printer = get_object_or_404(Stampante, id=request.POST["modello"])

    return HttpResponseRedirect(redirect_to='/stampante/{slug}.html'.format(slug=printer.slug))

def get_product(request):
    printer = get_object_or_404(Stampante, id=request.POST["modello"])
    return HttpResponseRedirect(redirect_to='/prodotto/{slug}.html'.format(slug=printer.slug))

class serie_ajax(Select2QuerySetView):
    def get_queryset(self):
        serie = Serie.objects.all().filter(marca_id=self.q)
        return serie

def printers_ajax(request):

    response_data = {}

    if ("serie" in request.GET) & (request.GET["serie"] != "0"):
        modelli = Stampante.objects.filter(serie_id=request.GET["serie"],marca_id=request.GET["marca"]).exclude(prodotti_associati=False).order_by("nome")
    else:
        modelli = Stampante.objects.filter(marca_id=request.GET["marca"]).exclude(prodotti_associati=False).order_by("nome")

    elenco = list()
    for modello in modelli:
        elenco.append({"id":modello.id,"nome":modello.nome})

    return JsonResponse(elenco,safe=False)

def export_printer(request,id):
    obj = Stampante.objects.get(id=id)
    response = render_to_response("pdf/stampante.html",RequestContext(request,{
        'stampante':obj
    }))
    file_pdf = cStringIO.StringIO()
    pdf = ho.pisa.CreatePDF(StringIO(response.content.encode("utf8")),dest=file_pdf)
    if pdf.err:
        print(pdf.err)
    return HttpResponse(file_pdf.getvalue(),content_type='application/pdf')

def login(request):

    if ("HTTP_REFERER" in request.META) & ("email" in request.POST):
        email = request.POST["email"]
        password = request.POST["password"]
        usr = User.objects.filter(Q(email=email) | Q(username=email))
        str = request.META.get("HTTP_REFERER")

        if usr.count() > 0:
            auth = authenticate(username=usr[0].username,password=password)
            if auth is not None:
                if auth.is_active:
                    effettua_accesso(request,auth)
                    msg = {"type": "success", "msg": "Bentornato {utente}".format(utente=usr[0].first_name+" "+usr[0].last_name)}
                else:
                    msg = {"type": "danger", "msg": "Account disabilitato per motivi amministrativi"}
            else:
                msg = {"type":"danger","msg":"Nessun account con queste credenziali"}
            request.session["msg_login"] = msg
    return HttpResponseRedirect(str)

def logout(request):
    if ("HTTP_REFERER" in request.META):
        chiudi_accesso(request)
        request.session["msg_login"] = {"type":"success","msg":"Logout completato"}
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

def registrazione(request):
    if request.user.is_authenticated()==False:
        if request.method == 'POST':
            form = RegistrazioneForm(request.POST)
            if form.is_valid():

                usernamesalt = form.cleaned_data["username"]
                salt = hashlib.sha1(str(random.random())).hexdigest()[:5]

                data = {}
                data["email"] = form.cleaned_data["email"]
                data["chiave"] = hashlib.sha1(salt+usernamesalt).hexdigest()
                data["nome"] = form.cleaned_data["nome"]
                data["cognome"] = form.cleaned_data["cognome"]
                data["password1"] = form.cleaned_data["password1"]

                form.inviaEmail(data)
                new_user = form.save(data)

                return render_to_response("conferma_registrazione.html", {
                    'id': new_user.id,
                    'email':new_user.email,
                    "pages": getPages(),
                    "settings": cartuccia24.settings,
                    "carrello": get_current_cart(request)

                }, context_instance=RequestContext(request))
        else:
            form = RegistrazioneForm()
        return render_to_response("registrazione.html",{
            'form': form,
            "pages": getPages(),
            "settings":cartuccia24.settings,
            "carrello": get_current_cart(request)

        },context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/")

def reinviaEmail(request,id):

    user = User.objects.get(id=id)
    cliente = Cliente.objects.get(user=user)

    if cliente is not None:
        if user.is_active :
            return HttpResponseRedirect("/")
        else:
            data = {}
            data["username"] = user.username
            data["email"] = user.email


            usernamesalt = user.username
            salt = hashlib.sha1(str(random.random())).hexdigest()[:5]

            data["chiave"] = hashlib.sha1(salt + usernamesalt).hexdigest()

            cliente.chiave_attivazione = data["chiave"]
            cliente.scadenza_chiave = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=2),
                                                                 "%Y-%m-%d %H:%M:%S")
            cliente.save()

            link = "http://test.pulitecna.it/registrazione/conferma/" + data["chiave"]

            c = Context({'link': link})
            f = open(BASE_DIR + "/negozio/templates/email/attivazione_account.html", 'r')
            t = Template(f.read())
            f.close()
            message = t.render(c)
            send_mail("Attivazione account", "", "Cartuccia24.com <attivazioni@cartuccia24.com>", [data["email"]],
                      fail_silently=False, html_message=message)

            return render_to_response("conferma_registrazione.html", {
                'id': user.id,
                'email': user.email,
                "pages": getPages(),
                "settings": cartuccia24.settings,
                "carrello": get_current_cart(request)

            }, context_instance=RequestContext(request))




def confermaRegistrazione(request,chiave):

    cliente = Cliente.objects.get(chiave_attivazione=chiave)

    if cliente is not None:
        user = cliente.user

        chiave = cliente.chiave_attivazione
        scadenza = cliente.scadenza_chiave

        data_oggi = timezone.now()

        if scadenza >= data_oggi:
            status = "OK"
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            user.is_active = 1
            user.save()
            effettua_accesso(request,user)
        else:
            status = "ChiaveScaduta"

        return render_to_response("attivazione_completata.html", {
            "status":status,
            'id': user.id,
            'email': user.email,
            "pages": getPages(),
            "settings": cartuccia24.settings,
            "carrello": get_current_cart(request)

        }, context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect("/")


def profilo(request):

    if request.user.is_authenticated() == False:
        return HttpResponseRedirect("/")

    return render_to_response("account/profilo.html", {

        "pages": getPages(),
        "settings": cartuccia24.settings,
        "carrello": get_current_cart(request)

    }, context_instance=RequestContext(request))

def cambia_password(request):

    if request.user.is_authenticated() == False:
        return HttpResponseRedirect("/")

    cambia_password = CambiaPasswordForm(request.user)

    message = None

    if request.method == "POST":
        cambia_password = CambiaPasswordForm(request.user)
        cambia_password.data = {}

        data = {}

        data["old_password"] = request.POST["old_password"]
        data["new_password1"] = request.POST["new_password1"]
        data["new_password2"] = request.POST["new_password2"]
        cambia_password.data = data
        cambia_password.is_bound = True

        if cambia_password.is_valid():
            user = cambia_password.save(True)
            if user is not None:
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                effettua_accesso(request,user)
            message = "Password cambiata con successo"

    return render_to_response("account/cambia_password.html", {
        "form_password":cambia_password,
        "pages": getPages(),
        "settings": cartuccia24.settings,
        "message":message,
        "carrello": get_current_cart(request)

    }, context_instance=RequestContext(request))

def stampanti(request):

    return render_to_response("account/stampanti.html", {
        "pages": getPages(),
        "settings": cartuccia24.settings,
        "carrello": get_current_cart(request),
        "stampanti":StampantePreferita.objects.filter(cliente__user=request.user)[0].stampante.all()

    }, context_instance=RequestContext(request))

def ordini(request):
    return render_to_response("account/ordini.html", {
        "pages": getPages(),
        "settings": cartuccia24.settings,
        "carrello": get_current_cart(request),
        "ordini":Ordine.objects.all().filter(cliente__user=request.user).order_by("-data")
    }, context_instance=RequestContext(request))

def recupera_password(request):
    if request.user.is_authenticated() == True:
        return HttpResponseRedirect("/account/profilo/")

    form = RecuperaPasswordForm()

    message = None

    if request.method == "POST":
        form = RecuperaPasswordForm(request.POST)
        if form.is_valid():
            form.save(request=request,html_email_template_name="account/password_reset_email.html",from_email="attivazioni@cartuccia24.com")
            message = "Ho inviato una mail all'indirizzo da te indicato con il codice temporaneo per recuperare la password"
    return render_to_response("account/recupera_password.html", {
        "form":form,
        "pages": getPages(),
        "settings": cartuccia24.settings,
        "message":message,
        "carrello": get_current_cart(request)

    }, context_instance=RequestContext(request))

def carrello(request):

    return render_to_response("carrello.html", {
        "pages": getPages(),
        "settings": cartuccia24.settings,
        "carrello":get_current_cart(request),
    }, context_instance=RequestContext(request))

def get_current_cart(request):
    carrello = Cart(request=request)
    return carrello

def aggiungi_prodotto(request):

    if "prodotto" in request.POST:

        carrello = Cart(request=request)
        prodotto = Prodotto.objects.get(pk=request.POST["prodotto"])
        qta = int(request.POST["qta"])
        prezzo = Offerte.objects.get(prodotto=prodotto).prezzo_ivato
        if qta > 0:
            carrello.add(product=prodotto,quantity=qta,unit_price=prezzo)

    return HttpResponseRedirect(request.META["HTTP_REFERER"])

def aggiungi_prodotto_unico(request,id):

    carrello = Cart(request=request)
    prodotto = Prodotto.objects.get(pk=id)
    qta = 1
    prezzo = Offerte.objects.get(prodotto=prodotto).prezzo_ivato
    carrello.add(product=prodotto,quantity=qta,unit_price=prezzo)

    return HttpResponseRedirect(request.META["HTTP_REFERER"])

def rimuovi_prodotto(request,id):

    carrello = Cart(request=request)
    prodotto = Prodotto.objects.get(pk=id)
    carrello.remove(prodotto)

    return HttpResponseRedirect(request.META["HTTP_REFERER"])

def diminuisci_prodotto(request,id):

    carrello = Cart(request=request)
    prodotto = Prodotto.objects.get(pk=id)
    prezzo = Offerte.objects.get(prodotto=prodotto).prezzo_ivato

    curr_quantity = 1
    for item in carrello:
        if item.product == prodotto:
            curr_quantity = item.quantity
    if curr_quantity > 1:
        carrello.update(prodotto,curr_quantity-1,prezzo)

    return HttpResponseRedirect("/carrello/")

def incrementa_prodotto(request,id):

    carrello = Cart(request=request)
    prodotto = Prodotto.objects.get(pk=id)
    prezzo = Offerte.objects.get(prodotto=prodotto).prezzo_ivato
    qta_disponibile = Offerte.objects.get(prodotto=prodotto).qta

    curr_quantity = 1
    for item in carrello:
        if item.product == prodotto:
            curr_quantity = item.quantity
    if curr_quantity+1 <= qta_disponibile:
        carrello.update(prodotto, curr_quantity + 1, prezzo)

    return HttpResponseRedirect("/carrello/")

from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received

def show_me_the_money(sender, **kwargs):
    ipn_obj = sender

    if ipn_obj.payment_status == ST_PP_COMPLETED:
        codice_transazione = ipn_obj.txn_id
        codice_ordine = ipn_obj.custom

        ord = Ordine.objects.get(codice=codice_ordine)
        ord.stato_id = 3
        ord.codice_transazione = codice_transazione
        ord.save()
    else:
        pass


valid_ipn_received.connect(show_me_the_money)

def immagine_mpn(request,mpn):
    try:
        image = StringIO(file(BASE_DIR + "/assets/prodotto/{mpn}.jpg".format(mpn=mpn), "rb").read())
        mimetype = mimetypes.guess_type(os.path.basename(BASE_DIR + "/assets/img/prodotto/{mpn}.jpg".format(mpn=mpn)))[0]
    except:
        image = StringIO(file(BASE_DIR + "/assets/img/no-image.gif", "rb").read())
        mimetype = mimetypes.guess_type(os.path.basename(BASE_DIR + "/assets/img/no-image.gif"))[0]


    return HttpResponse(image.read(), content_type=mimetype)

from dal_select2.views import Select2QuerySetView
class CittaAutocomplete(Select2QuerySetView):
    def get_queryset(self):

        qs = Citta.objects.all()

        if self.q.encode("utf8"):
            qs = qs.filter(Q(nome__icontains=self.q.encode("utf8")) | Q(cap__contains=self.q.encode("utf8")))

        return qs.order_by("nome")

class ClienteAutocomplete(Select2QuerySetView):
    def get_queryset(self):

        qs = Cliente.objects.all()

        if self.q.encode("utf8"):
            qs = qs.filter(Q(user__first_name__icontains=self.q.encode("utf8")) | Q(user__lastname__icontains=self.q.encode("utf8")) | Q(user__username__icontains=self.q.encode("utf8")))

        return qs

class ProdottoAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        qs = Prodotto.objects.all()

        if self.q.encode("utf8"):
            qs = qs.filter(Q(nome__icontains=self.q.encode("utf8")) | Q(mpn__contains=self.q.encode("utf8")))

        return qs.order_by("nome")

class StampanteAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        qs = Stampante.objects.all()

        if self.q.encode("utf8"):
            qs = qs.filter(Q(nome__icontains=self.q.encode("utf8")) | Q(mpn__contains=self.q.encode("utf8")))

        return qs.order_by("nome")


def indirizzi_utente(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/")

    indirizzi = Indirizzo.objects.all().filter(utente__user=request.user)

    return render_to_response("account/indirizzi.html", {
        "pages": getPages(),
        "settings": cartuccia24.settings,
        "carrello":get_current_cart(request),
        "indirizzi":indirizzi
    }, context_instance=RequestContext(request))


def modifica_indirizzo(request,id):

    if request.user.is_authenticated() == False:
        return HttpResponseRedirect("/")

    utente = Cliente.objects.get(user=request.user)

    form = NuovoIndirizzoForm(instance=Indirizzo.objects.get(id=id))

    if request.method == "POST":
        form = NuovoIndirizzoForm(request.POST)

        if form.is_valid():
            indirizzo = form.save(False)
            indirizzo.id = id
            indirizzo.utente = utente
            indirizzo.save()
            return HttpResponseRedirect("/account/profilo/cambia/indirizzi/")

    return render_to_response("account/modifica_indirizzo.html", {
        "pages": getPages(),
        "settings": cartuccia24.settings,
        "carrello": get_current_cart(request),
        "form": form,
        "id":id,
    }, context_instance=RequestContext(request))


def elimina_indirizzo(request,id):

    Indirizzo.objects.get(id=id).delete()

    return HttpResponseRedirect("/account/profilo/cambia/indirizzi/")

def nuovo_indirizzo(request):

    if request.user.is_authenticated() == False:
        return HttpResponseRedirect("/")

    utente = Cliente.objects.get(user=request.user)

    form = NuovoIndirizzoForm()

    if request.method == "POST":
        form = NuovoIndirizzoForm(request.POST)

        if form.is_valid():
            indirizzo = form.save(False)
            indirizzo.utente = utente
            indirizzo.save()
            return HttpResponseRedirect("/account/profilo/cambia/indirizzi/")


    return render_to_response("account/nuovo_indirizzo.html", {
        "pages": getPages(),
        "settings": cartuccia24.settings,
        "carrello": get_current_cart(request),
        "form":form
    }, context_instance=RequestContext(request))

def cambia_informazioni(request):

    if request.user.is_authenticated() == False:
        return HttpResponseRedirect("/")

    form = ModificaInformazioniForm(instance=request.user)

    msg = None

    if request.method == "POST":
        form = ModificaInformazioniForm(request.POST,instance=request.user)
        form.current_user = request.user
        form.instance = request.user

        if form.is_valid():
            form.save(True)
            msg = "Informazioni salvate con successo"
        else:
            print(form.errors)

    return render_to_response("account/modifica_informazioni.html", {
        "pages": getPages(),
        "settings": cartuccia24.settings,
        "carrello": get_current_cart(request),
        "form":form,
        "msg":msg
    }, context_instance=RequestContext(request))

def get_shipping_options(price):

    fasce = FasciaCorriere.objects.raw("SELECT * FROM negozio_fasciacorriere where prezzo_minimo <= {minimo} and prezzo_massimo >= {massimo} order by prezzo_minimo".format(minimo=price,massimo=price))

    rs = list()
    for f in fasce:
        corriere = Corriere.objects.filter(fasce_prezzo=f,attivo=True)[0]
        rs.append({"corriere":corriere,"costo":f.costo})
    return rs

def completa_ordine(request):
    if request.user.is_authenticated() == False:
        return HttpResponseRedirect("/")

    cliente = Cliente.objects.get(user=request.user)

    form = InfoOrdineForm(utente=cliente)

    if request.method == "POST":
        form = InfoOrdineForm(request.POST,utente=cliente)

        if form.is_valid():
            cart = get_current_cart(request)
            shipping = get_shipping_options(cart.summary())
            ordine = Ordine()
            ordine.data = datetime.datetime.now()

            anno = "{:%Y}".format(datetime.datetime.now())

            ricerca_codice = Ordine.objects.filter(codice__contains=anno).order_by("-id")

            numero = 1
            if len(ricerca_codice) > 0:
                str = ricerca_codice[0].codice.split("/")[1]
                numero = int(str)
                numero = numero+1

            codice = anno + "/" + numero.__str__()

            ordine.codice = codice
            ordine.cliente = cliente
            ordine.corriere = Corriere.objects.get(id=request.POST["corriere"])
            ordine.indirizzo_spedizione = Indirizzo.objects.get(id=request.POST["indirizzo_spedizione"])
            if "fattura" in request.POST:
                if request.POST["fattura"] == "on":
                    ordine.fattura = True
                    ordine.indirizzo_fatturazione = Indirizzo.objects.get(id=request.POST["indirizzo_fatturazione"])
                else:
                    ordine.fattura = False
                    ordine.indirizzo_fatturazione = Indirizzo.objects.get(id=request.POST["indirizzo_spedizione"])
            else:
                ordine.fattura = False
                ordine.indirizzo_fatturazione = Indirizzo.objects.get(id=request.POST["indirizzo_spedizione"])

            ordine.tipo_pagamento = Pagamento.objects.get(id=request.POST["pagamento"])
            ordine.stato = StatoOrdine.objects.get(id=2)
            ordine.totale_prodotti = cart.summary()

            for corriere in shipping:

                if corriere["corriere"] == ordine.corriere:
                    ordine.spese_spedizione = corriere["costo"]

            ordine.totale_da_pagare = ordine.totale_prodotti + ordine.spese_spedizione

            ordine.save()

            if ordine:
                for oggetto in cart:
                    riga_ordine = RigaOrdine()
                    riga_ordine.ordine = ordine
                    riga_ordine.prodotto = oggetto.product
                    riga_ordine.prezzo_unitario = oggetto.unit_price
                    riga_ordine.qta = oggetto.quantity
                    offerta = Offerte.objects.get(prodotto=oggetto.product)
                    offerta.qta = offerta.qta - oggetto.quantity
                    offerta.save()
                    riga_ordine.save()
            cart.clear()
            try:
                ordine.invia_email_conferma()

            except:
                pass
            return HttpResponseRedirect("/ordine/conferma/{id}".format(id=ordine.id))
        else:
            print(form.errors)

    return render_to_response("ordine/info_ordine.html", {
        "pages": getPages(),
        "settings": cartuccia24.settings,
        "carrello": get_current_cart(request),
        "form": form,
        "corrieri": get_shipping_options(Decimal(get_current_cart(request).summary()))
    }, context_instance=RequestContext(request))

def conferma_ordine(request,ordine):

    if request.user.is_authenticated() == False:
        return HttpResponseRedirect("/")



    from django.core.urlresolvers import reverse
    ord = Ordine.objects.get(id=ordine)

    if ord.cliente.user != request.user:
        return HttpResponseRedirect("/")

    ord.invia_email_conferma_admin()


    config = Configurazione.objects.get(nome="PAYPAL_ADDRESS")

    paypal_dict = {
        "cmd": "_cart",
        "business": config.valore,
        "invoice": ord.codice,
        "notify_url": "http://test.pulitecna.it" + reverse('paypal-ipn'),
        "return_url": "http://test.pulitecna.it/ordine/conferma/{id}/".format(id=ord.id),
        "custom": ord.codice,  # Custom command to correlate to some function later (optional)
        "currency_code": "EUR",
        "upload": 1,
        "shipping":ord.spese_spedizione
    }

    option_num = 1

    for riga in ord.righe_ordine:
        paypal_dict["item_name_" + str(option_num)] = riga.prodotto.nome
        paypal_dict["amount_" + str(option_num)] = riga.prezzo_unitario
        paypal_dict["quantity_" + str(option_num)] = riga.qta

        option_num = option_num + 1

    paypal_dict["item_name_" + str(option_num)] = "Spedizione"
    paypal_dict["amount_" + str(option_num)] = ord.spese_spedizione
    paypal_dict["quantity_" + str(option_num)] = 1

    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict, button_type="cart")

    return render_to_response("ordine/conferma.html", {
        "pages": getPages(),
        "settings": cartuccia24.settings,
        "carrello": get_current_cart(request),
        "ordine":Ordine.objects.get(id=ordine),
        "form_paypal":form
    }, context_instance=RequestContext(request))

def aggiungi_stampante(request,id):
    if request.user.is_authenticated() == False:
        return HttpResponseRedirect("/")

    stampante = Stampante.objects.get(id=id)
    cliente  = Cliente.objects.get(user=request.user)

    cerca_scheda = StampantePreferita.objects.filter(cliente=cliente)

    st_preferita = StampantePreferita()
    if cerca_scheda > 0:
        st_preferita = cerca_scheda[0]
        st_preferita.stampante.add(stampante)
    else:
        st_preferita.cliente = cliente
        st_preferita.stampante.add(stampante)
    st_preferita.save()

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

def elimina_stampante(request,id):
    if request.user.is_authenticated() == False:
        return HttpResponseRedirect("/")

    stampante = Stampante.objects.get(id=id)
    cliente  = Cliente.objects.get(user=request.user)

    cerca_scheda = StampantePreferita.objects.filter(cliente=cliente)

    st_preferita = StampantePreferita()
    if cerca_scheda > 0:
        st_preferita = cerca_scheda[0]
        st_preferita.stampante.remove(stampante)

    st_preferita.save()

    return HttpResponseRedirect("/account/stampanti/")
def indent(elem, level=0):
  i = "\n" + level*"  "
  if len(elem):
    if not elem.text or not elem.text.strip():
      elem.text = i + "  "
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
    for elem in elem:
      indent(elem, level+1)
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
  else:
    if level and (not elem.tail or not elem.tail.strip()):
      elem.tail = i

def genera_sitemap(request):
    import xml.etree.cElementTree as ET
    root = ET.Element("urlset")
    root.attrib["xmls"] = "http://www.sitemaps.org/schemas/sitemap/0.9"

    pagine = Pagina.objects.all()

    url = ET.SubElement(root, "url")
    ET.SubElement(url, "loc").text = "http://www.cartuccia24.com/"

    for pagina in pagine:
        url = ET.SubElement(root, "url")
        ET.SubElement(url, "loc").text = "http://www.cartuccia24.com/s/{slug}/".format(slug=pagina.slug)

    indent(root)
    tree = ET.ElementTree(root)
    tree.write(BASE_DIR + "/assets/sitemap_pagine.xml")

    root = ET.Element("urlset")
    root.attrib["xmls"] = "http://www.sitemaps.org/schemas/sitemap/0.9"

    stampanti = Stampante.objects.all().filter(attivo=True)
    for stampante in stampanti:
        url = ET.SubElement(root, "url")
        ET.SubElement(url, "loc").text = "http://www.cartuccia24.com/stampante/{slug}.html".format(slug=stampante.slug)

    indent(root)
    tree = ET.ElementTree(root)
    tree.write(BASE_DIR + "/assets/sitemap_stampanti.xml")

    root = ET.Element("urlset")
    root.attrib["xmls"] = "http://www.sitemaps.org/schemas/sitemap/0.9"

    prodotti = Prodotto.objects.all().filter(attivo=True)
    for prodotto in prodotti:
        url = ET.SubElement(root, "url")
        ET.SubElement(url, "loc").text = "http://www.cartuccia24.com/prodotto/{slug}.html".format(slug=prodotto.slug)

    indent(root)
    tree = ET.ElementTree(root)
    tree.write(BASE_DIR+"/assets/sitemap_prodotti.xml")

    root = ET.Element("urlset")
    root.attrib["xmls"] = "http://www.sitemaps.org/schemas/sitemap/0.9"

    url = ET.SubElement(root, "sitemap")
    ET.SubElement(url, "loc").text = "http://www.cartuccia24.com/sitemap/?q=sitemap_prodotti.xml"

    url = ET.SubElement(root, "sitemap")
    ET.SubElement(url, "loc").text = "http://www.cartuccia24.com/sitemap/?q=sitemap_stampanti.xml"

    url = ET.SubElement(root, "sitemap")
    ET.SubElement(url, "loc").text = "http://www.cartuccia24.com/sitemap/?q=sitemap_pagine.xml"

    indent(root)
    tree = ET.ElementTree(root)
    tree.write(BASE_DIR + "/assets/sitemap.xml")

    return HttpResponse("Sitemap generata")


def sitemap(request):

    if "q" in request.GET:
        file = open(BASE_DIR+"/assets/{file}.xml".format(file=request.GET["q"]))
        return HttpResponse(file.read())
    else:
        file = open(BASE_DIR + "/assets/sitemap.xml")
        return HttpResponse(file.read())

def produttori(request):
    marche = Produttore.objects.all().exclude(image="").order_by("nome")

    return render_to_response('../templates/marche.html',
                              {
                                  "settings": cartuccia24.settings,
                                  "pages": getPages(),
                                  "marche": marche,
                                  "msg_login": getLoginErrors(request),
                                  "carrello": get_current_cart(request),

                              },
                              context_instance=RequestContext(request))
def produttore(request,id):

    produttore = Produttore.objects.get(id=id)

    serie = Serie.objects.all().filter(marca=produttore).order_by("nome")

    return render_to_response('../templates/marca.html',
                              {
                                  "settings": cartuccia24.settings,
                                  "pages": getPages(),
                                  "produttore":produttore,
                                  "series":serie,
                                  "msg_login": getLoginErrors(request),
                                  "carrello": get_current_cart(request),

                              },
                              context_instance=RequestContext(request))

def stampanti_serie(request,marca,id):

    serie = None
    if id == "0":
        printer_list = Stampante.objects.all().filter(marca_id=marca).order_by("nome")
    else:
        printer_list = Stampante.objects.all().filter(serie_id=id,marca_id=marca).order_by("nome")
        serie = Serie.objects.get(id=id)


    return render_to_response('../templates/risultati_ricerca_serie.html', {
        "settings": cartuccia24.settings,
        "printer": printer_list,
        "pages": getPages(),
        "produttore": Produttore.objects.get(id=marca),
        "serie":serie,
        "msg_login": getLoginErrors(request),
        "carrello": get_current_cart(request)

    }, context_instance=RequestContext(request))

def contattaci(request):

    form = ContattaciForm()

    msg = None

    if request.method == "POST":
        form = ContattaciForm(request.POST)

        if form.is_valid():
            c = Context({
                'nome': form.cleaned_data["nome"],
                'cognome':form.cleaned_data["cognome"],
                'email':form.cleaned_data["email"],
                'oggetto':form.cleaned_data["oggetto"],
                'messaggio':form.cleaned_data["messaggio"]
            })
            f = open(BASE_DIR + "/negozio/templates/email/messaggio_contattaci.html", 'r')
            t = Template(f.read())
            f.close()
            message = t.render(c)
            conf = Configurazione.objects.get(nome="ORDERS_EMAIL")
            emails = conf.valore.split(",")
            send_mail("Messaggio da {email}".format(email=form.cleaned_data["email"]), "", "Cartuccia24.com <attivazioni@cartuccia24.com>", recipient_list=emails,
                      fail_silently=False, html_message=message)
            msg = "Messaggio inviato con successo"



    return render_to_response('../templates/contattaci.html', {
        "settings": cartuccia24.settings,
        "pages": getPages(),
        "msg_login": getLoginErrors(request),
        "msg":msg,
        "carrello": get_current_cart(request),
        "form":form

    }, context_instance=RequestContext(request))


