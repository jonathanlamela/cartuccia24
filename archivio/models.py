from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
from cartuccia24.settings import BASE_DIR

import os

# Create your models here.
class Colore(models.Model):
    nome = models.CharField(max_length=255)
    codice_html = models.CharField(max_length=200)

    def __str__(self):
        return self.nome.encode('utf8')

    class Meta:
        verbose_name_plural = "Colori"

class Produttore(models.Model):
    icecat_id = models.CharField(max_length=15,blank=True)
    nome = models.CharField(max_length=255)
    image = models.ImageField(upload_to=BASE_DIR+"/assets/manufacturer/",blank=True)
    slug = models.SlugField(max_length=255, blank=True, verbose_name="SEO Name")


    @property
    def image_name(self):
        file_name = ""
        try:
            file_name = os.path.basename(self.image.file.name)
        except:
            pass
        return file_name

    def __str__(self):
        return self.nome.encode('utf8')

    class Meta:
        verbose_name_plural = "Marche"
        verbose_name = "Marca"

class Categoria(models.Model):
    nome = models.CharField(max_length=255)
    parent = models.ForeignKey("self",blank=True,null=True,verbose_name="categoria padre")
    icecat_id = models.CharField(max_length=255,blank=True)
    level = models.IntegerField(verbose_name="Livello",blank=True,editable=False,default=1)
    slug = models.SlugField(max_length=255, blank=True, verbose_name="SEO Name")

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.parent is not None:
            self.level = self.parent.level + 1
        else:
            self.level = 1
        super(Categoria, self).save()

    def __str__(self):
        nome = ""
        parent = self.parent

        if parent is None:
            nome = "Root"
        else:
            while parent is not None:
                nome = parent.nome + " > " + nome
                parent = parent.parent
                if parent is None:
                    nome += self.nome
        return nome

    class Meta:
        verbose_name_plural = "Categorie"

class Serie(models.Model):
    nome = models.CharField(max_length=255)
    marca = models.ForeignKey(Produttore,blank=True)

    def __str__(self):
        return self.nome.encode('utf8')

    class Meta:
        verbose_name_plural = "Serie"

class Stampante(models.Model):
    nome = models.CharField(max_length=255)
    descrizione_breve = models.TextField(verbose_name="Descrizione breve", default='',blank=True,)
    descrizione_lunga = models.TextField(verbose_name="Descrizione lunga", default='',blank=True,)
    mpn = models.CharField(max_length=50, blank=False, verbose_name="MPN (codice Marca)", )
    ean = models.CharField(max_length=13,verbose_name="EAN13 (codice a barre)",blank=True,default='')
    url_image = models.URLField(verbose_name="URL Immagine",blank=True)
    marca = models.ForeignKey(Produttore)
    categoria = models.ForeignKey(Categoria)
    icecat_id = models.CharField(max_length=255, blank=True, verbose_name="Codice View Icecat")
    slug = models.SlugField(max_length=255, blank=True, verbose_name="SEO Name")
    attivo = models.BooleanField(blank=False, default=True)
    date_add = models.DateTimeField(verbose_name="Data creazione", default=timezone.now,)
    date_upd = models.DateTimeField(verbose_name="Data modifica", default=timezone.now,blank=True)
    prodotti_associati = models.ManyToManyField("Prodotto",blank=True)
    serie = models.ForeignKey(Serie)

    def get_absolute_url(self):
        return "/stampante/{slug}.html".format(slug=self.slug)


    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.date_upd = timezone.now()
        super(Stampante, self).save()

    def __str__(self):
        if self.slug != self.pk+" "+str(self.pk):
            self.slug = slugify(self.pk+" "+str(self.pk))
            self.save()
        return self.nome.encode('utf8')

    def __unicode__(self):
        return self.nome.encode('ascii')

    class Meta:
        verbose_name_plural = "Stampanti"

class Prodotto(models.Model):
    nome = models.CharField(max_length=255)
    descrizione_breve = models.TextField(verbose_name="Descrizione breve",default='',blank=True)
    descrizione_lunga = models.TextField(verbose_name="Descrizione lunga",default='',blank=True)
    mpn = models.CharField(max_length=50, blank=False, verbose_name="MPN (codice Marca)",)
    ean = models.CharField(max_length=13,verbose_name="EAN13 (codice a barre)", blank=True, default='')
    url_image = models.URLField(verbose_name="URL Immagine",blank=True)
    marca = models.ForeignKey(Produttore)
    categoria = models.ForeignKey(Categoria)
    icecat_id = models.CharField(max_length=255, blank=True, verbose_name="Codice View Icecat")
    slug = models.SlugField(max_length=255, blank=True, verbose_name="SEO Name")
    attivo = models.BooleanField(blank=False, default=True)
    date_add = models.DateTimeField(verbose_name="Data creazione", default=timezone.now,blank=True)
    date_upd = models.DateTimeField(verbose_name="Data modifica", default=timezone.now,blank=True)
    colore = models.ForeignKey(Colore)
    from negozio.models import Offerte
    offerte = models.ManyToManyField(Offerte,blank=True)

    def get_absolute_url(self):
        return "/prodotto/{slug}.html".format(slug=self.slug)

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "nome__icontains","mpn__icontains","ean__icontains")

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.date_upd = timezone.now()
        super(Prodotto, self).save()


    def __str__(self):
        if self.slug != self.pk + " " + str(self.pk):
            self.slug = slugify(self.pk + " " + str(self.pk))
            self.save()
        return self.nome.encode('utf8')

    def __unicode__(self):
        return self.nome.encode('utf8')

    class Meta:
        verbose_name_plural = "Prodotti"


class IcecatPrinters(models.Model):
    view_id = models.IntegerField()











