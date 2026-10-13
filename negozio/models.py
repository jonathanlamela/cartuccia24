from django.db import models
from cartuccia24.settings import BASE_DIR
import os
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template import Context, Template
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from paypal.standard.forms import PayPalPaymentsForm
from archivio.models import Stampante


# Create your models here.
class Configurazione(models.Model):
    nome = models.CharField(max_length=255,blank=False)
    valore = models.TextField(blank=False,default='')

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = "Configurazioni"
        verbose_name = "Configurazione"

class SliderChildren(models.Model):
    image_file = models.ImageField(blank=True,upload_to=BASE_DIR+'/assets/slides/')
    titolo = models.CharField(max_length=255,default='',blank=False)
    url = models.URLField(default='#',blank=True,verbose_name='Reindirizza a')

    def get_absolute_url(self):
        return "/slides/{id}/".format(id=self.pk)

    def __str__(self):
        return self.titolo

    def delete(self, using=None, keep_parents=False):
        try:
            os.remove(self.image_file.path)
        except:
            pass
        super(SliderChildren, self).delete(using,keep_parents)


class Slider(models.Model):
    nome = models.CharField(max_length=255,default='',blank=False)
    slides = models.ManyToManyField(SliderChildren)
    attivo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = "Slider"

class PaginaManager(models.Manager):

    def get_all(self):
        return Pagina.objects.filter(parent_page=self)

class Pagina(models.Model):
    titolo = models.CharField(max_length=255)
    slug = models.SlugField(blank=False,verbose_name="SEO URL")
    url = models.TextField(blank=True,null=True)
    content = models.TextField(blank=False)
    parent_page = models.ForeignKey("Pagina",verbose_name="Pagina padre",blank=True,null=True)
    pubblicata = models.BooleanField(default=True)
    posizione = models.IntegerField(default=0)

    def get_childrens(self):
        return Pagina.objects.filter(parent_page=self)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        url = ""
        if self.parent_page is not None:
            url = self.parent_page.url + self.slug + "/"
        else:
            url = self.slug + "/"
        self.url = url
        super(Pagina, self).save()

    def __str__(self):
        return self.titolo

    class Meta:
        verbose_name_plural = "Pagine"





class Offerte(models.Model):
    import django.utils.timezone


    data_creazione = models.DateField(blank=False,default=django.utils.timezone.now)
    mpn = models.CharField(max_length=200,default='',blank=True)
    ean = models.CharField(max_length=13, default='', blank=True)
    qta = models.IntegerField(verbose_name="Qty", default=0, blank=True)
    prezzo = models.DecimalField(max_digits=8, decimal_places=2)
    prezzo_ivato = models.DecimalField(max_digits=8, decimal_places=2,blank=True)
    attiva = models.BooleanField(default=True)
    aggiornata = models.BooleanField(default=True)
    fornitore = models.CharField(max_length=255,default='',blank=True)

    @property
    def product_image(self):
        from archivio.models import Prodotto
        return Prodotto.objects.get(mpn=self.mpn).url_image

    @property
    def product(self):
        from archivio.models import Prodotto
        return Prodotto.objects.get(mpn=self.mpn)

    def get_absolute_url(self):
        from archivio.models import Prodotto

        obj = Prodotto.objects.filter(offerte__in=Offerte.objects.filter(pk=self.pk).all())[0]
        return "/prodotto/{slug}.html".format(slug=obj.slug)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(Offerte, self).save(force_insert,force_update,using,update_fields)
        self.prezzo_ivato = Decimal(float(self.prezzo) + float(self.prezzo)*0.22)
        super(Offerte, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return "({mpn}) Prezzo : {prezzo} Qta : {qta}".format(mpn=self.mpn,prezzo=self.prezzo,qta=self.qta)

    class Meta:
        verbose_name_plural = "Offerte"
        verbose_name = "Offerta"

class Listino(models.Model):
    file_listino = models.FileField(upload_to=BASE_DIR+"/offers_files/")
    data_upload = models.DateTimeField(auto_now_add=True, blank=True)
    righe_lette = models.IntegerField(default=0)
    righe_elaborate = models.IntegerField(default=0)
    offerte_aggiunte = models.IntegerField(default=0)
    offerte_eliminate = models.IntegerField(default=0)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(Listino, self).save(force_insert, force_update, using, update_fields)
        f = open(self.file_listino.name)
        self.righe_lette = len(f.readlines())
        super(Listino, self).save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        super(Listino, self).delete(using, keep_parents)
        try:
            os.remove(self.file_listino.path)
        except:
            pass


    def __str__(self):
        return "Listino {nome}".format(nome=os.path.basename(self.file_listino.name))

    class Meta:
        verbose_name = "Listino"
        verbose_name_plural = "Listini"

class FasciaCorriere(models.Model):
    prezzo_minimo = models.DecimalField(max_digits=8, decimal_places=2)
    prezzo_massimo = models.DecimalField(max_digits=8, decimal_places=2)
    costo = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return "{minimo} a {massimo} - Costo {costo}".format(minimo=self.prezzo_minimo,massimo=self.prezzo_massimo,costo=self.costo)

    class Meta:
        verbose_name = "Fascia prezzo"
        verbose_name_plural = "Fasce prezzo"

class Corriere(models.Model):
    nome = models.CharField(max_length=255,blank=False)
    logo = models.ImageField(blank=False,upload_to=BASE_DIR+"/assets/carrier/")
    url_tracking = models.URLField(blank=True)
    fasce_prezzo = models.ManyToManyField(FasciaCorriere,blank=True)
    costo_oggetto = models.DecimalField(max_digits=8, decimal_places=2,verbose_name="Costo per oggetto aggiuntivo")
    attivo = models.BooleanField(default=True)
    delay = models.CharField(max_length=255,blank=False)

    def __str__(self):
        return " {nome}".format(nome=self.nome)

    class Meta:
        verbose_name = "Corriere"
        verbose_name_plural = "Corrieri"

class Cliente(models.Model):
    user = models.OneToOneField(User,related_name='cliente')
    chiave_attivazione = models.CharField(max_length=40)
    scadenza_chiave = models.DateTimeField()

    @property
    def nome(self):
        return self.user.first_name

    def cognome(self):
        return self.user.last_name

    def username(self):
        return self.user.username

    def __str__(self):
        return "{username} - {email}".format(username=self.user.username,email=self.user.email)

    class Meta:
        verbose_name_plural = "Clienti"

class Citta(models.Model):
    nome = models.CharField(max_length=200)
    cap = models.CharField(max_length=200)
    provincia = models.CharField(max_length=200)

    def __str__(self):
        return "{citta} ({pr}) - {cap}".format(citta=self.nome,pr=self.provincia,cap=self.cap)

class Indirizzo(models.Model):
    utente = models.ForeignKey(Cliente,blank=False)
    alias = models.CharField(max_length=255,blank=False,default="Indirizzo")
    azienda  = models.CharField(max_length=255,blank=True)
    nome = models.CharField(max_length=255,blank=False)
    cognome = models.CharField(max_length=255,blank=False)
    via = models.CharField(max_length=255,blank=False)
    n_civico = models.CharField(max_length=20, blank=False)
    citta = models.ForeignKey(Citta)
    codice_fiscale = models.CharField(max_length=50, blank=True)
    p_iva = models.CharField(max_length=50, blank=True)
    n_telefono = models.CharField(max_length=50, blank=True)
    n_cellulare = models.CharField(max_length=50, blank=True)
    cap = models.CharField(max_length=50,blank=False)

    def __str__(self):
        return "({alias}) Indirizzo di {nome} {cognome} - Utente {utente}".format(alias=self.alias,nome=self.nome,cognome=self.cognome,utente=self.utente.user.username)

    class Meta:
        verbose_name_plural = "Indirizzi"
        verbose_name = "Indirizzo"

class StatoOrdine(models.Model):
    nome = models.CharField(max_length=255)
    pagato = models.BooleanField(blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Stato ordine"
        verbose_name_plural = "Stati ordine"


class RigaOrdine(models.Model):
    prodotto = models.ForeignKey("archivio.Prodotto")
    ordine = models.ForeignKey("Ordine")
    qta = models.IntegerField(blank=False,default=1)
    prezzo_unitario = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return "{prodotto} - Qta {qta} Prezzo {prezzo}".format(prodotto=self.prodotto.mpn,qta=self.qta,prezzo=self.prezzo_unitario)

    class Meta:
        verbose_name_plural = "Dettagli ordini"
        verbose_name = "Dettagli ordine"

class Pagamento(models.Model):
    nome = models.CharField(max_length=255,blank=False)
    istruzioni = models.TextField(blank=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = "Pagamenti"

class Ordine(models.Model):
    data = models.DateTimeField()
    codice = models.CharField(max_length=255)
    stato = models.ForeignKey(StatoOrdine,default=2)
    cliente = models.ForeignKey(Cliente)
    corriere = models.ForeignKey(Corriere)
    spese_spedizione = models.DecimalField(max_digits=8, decimal_places=2)
    totale_prodotti = models.DecimalField(max_digits=8, decimal_places=2)
    totale_da_pagare = models.DecimalField(max_digits=8, decimal_places=2)
    indirizzo_spedizione = models.ForeignKey(Indirizzo,related_name='indirizzo_spedizione',blank=False)
    fattura = models.BooleanField(blank=True)
    indirizzo_fatturazione = models.ForeignKey(Indirizzo,related_name='indirizzo_fatturazione',blank=True)
    tipo_pagamento = models.ForeignKey(Pagamento)
    codice_transazione = models.TextField(blank=True)
    url_tracciamento = models.URLField(blank=True)

    def __str__(self):
        return "Ordine {ordine}".format(ordine=self.codice)

    class Meta:
        verbose_name_plural = "Ordini"

    @property
    def righe_ordine(self):
        return RigaOrdine.objects.all().filter(ordine=self)


    def invia_tracking(self,url):


        # Create the instance.

        c = Context({'ordine': self,'url':url})
        f = open(BASE_DIR + "/negozio/templates/email/ordine_tracking.html", 'r')
        t = Template(f.read())
        f.close()
        message = t.render(c)
        send_mail("Tracking per l'ordine {codice}".format(codice=self.codice), "", "Cartuccia24.com <attivazioni@cartuccia24.com>",
                  [self.cliente.user.email],
                  fail_silently=False, html_message=message)

    @property
    def invia_email_conferma(self):

        ord = Ordine.objects.get(id=self.id)

        # Create the instance.

        c = Context({'ordine': self})
        f = open(BASE_DIR + "/negozio/templates/email/ordine_conferma.html", 'r')
        t = Template(f.read())
        f.close()
        message = t.render(c)
        send_mail("Ordine {codice}".format(codice=self.codice), "", "Cartuccia24.com <attivazioni@cartuccia24.com>", [self.cliente.user.email],
                  fail_silently=False, html_message=message)

        ord.invia_email_conferma_admin()

    @property
    def invia_email_conferma_admin(self):
        ord = Ordine.objects.get(id=self.id)

        # Create the instance.

        conf = Configurazione.objects.get(nome="ORDERS_EMAIL")
        emails = conf.valore.split(",")


        c = Context({'ordine': self})
        f = open(BASE_DIR + "/negozio/templates/email/ordine_conferma_admin.html", 'r')
        t = Template(f.read())
        f.close()
        message = t.render(c)
        send_mail("Nuovo ordine con codice {codice}".format(codice=self.codice), "", "Cartuccia24.com <attivazioni@cartuccia24.com>",
                  recipient_list=emails,
                  fail_silently=False, html_message=message)

    @property
    def invia_email_pagato(self):
        ord = Ordine.objects.get(id=self.id)

        # Create the instance.

        c = Context({'ordine': self})
        f = open(BASE_DIR + "/negozio/templates/email/ordine_pagato.html", 'r')
        t = Template(f.read())
        f.close()
        message = t.render(c)
        send_mail("Ordine {codice} pagato".format(codice=self.codice), "", "Cartuccia24.com <attivazioni@cartuccia24.com>",
                  [self.cliente.user.email],
                  fail_silently=False, html_message=message)

    @property
    def invia_email_spedito(self):

        c = Context({'ordine': self})
        f = open(BASE_DIR + "/negozio/templates/email/ordine_spedito.html", 'r')
        t = Template(f.read())
        f.close()
        message = t.render(c)
        send_mail("Ordine {codice} spedito".format(codice=self.codice), "",
                  "Cartuccia24.com <attivazioni@cartuccia24.com>",
                  [self.cliente.user.email],
                  fail_silently=False, html_message=message)

    @property
    def invia_email_annullato(self):
        ord = Ordine.objects.get(id=self.id)

        # Create the instance.

        c = Context({'ordine': self})
        f = open(BASE_DIR + "/negozio/templates/email/ordine_annullato.html", 'r')
        t = Template(f.read())
        f.close()
        message = t.render(c)
        send_mail("Ordine {codice} annullato".format(codice=self.codice), "",
                  "Cartuccia24.com <attivazioni@cartuccia24.com>",
                  [self.cliente.user.email],
                  fail_silently=False, html_message=message)

    @property
    def invia_email_rimborsato(self):
        ord = Ordine.objects.get(id=self.id)

        # Create the instance.

        c = Context({'ordine': self})
        f = open(BASE_DIR + "/negozio/templates/email/ordine_rimborsato.html", 'r')
        t = Template(f.read())
        f.close()
        message = t.render(c)
        send_mail("Ordine {codice} rimborsato".format(codice=self.codice), "",
                  "Cartuccia24.com <attivazioni@cartuccia24.com>",
                  [self.cliente.user.email],
                  fail_silently=False, html_message=message)

class StampantePreferita(models.Model):
    cliente = models.ForeignKey(Cliente)
    stampante = models.ManyToManyField(Stampante)

    def __str__(self):
        return "Stampanti preferite del cliente {nome} {cognome}".format(nome=self.cliente.user.first_name,cognome=self.cliente.user.last_name)

    class Meta:
        verbose_name_plural = "Stampanti preferite"



