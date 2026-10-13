from django.forms import *
from archivio.models import *
from negozio.models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail
import datetime
from django.template import Context, Template
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from dal_select2.widgets import ModelSelect2
from dal_select2.widgets import ModelSelect2Multiple
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
import random
from string import digits, letters

class Email(EmailField):
    def clean(self, value):
        super(Email, self).clean(value)
        try:
            User.objects.get(email=value)
            raise forms.ValidationError("Indirizzo email esistente")
        except User.DoesNotExist:
            return value

class RegistrazioneForm(UserCreationForm):
    email = Email()
    nome = CharField(max_length=255,required=True,label="Nome")
    cognome = CharField(max_length=255,required=True,label="Cognome")

    def save(self, data):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = data["email"]
        user.first_name = data["nome"]
        user.last_name = data["cognome"]
        user.set_password(data["password1"])
        user.is_active = False
        if True:
            user.save()
            cliente = Cliente()
            cliente.user = user
            cliente.chiave_attivazione = data["chiave"]
            cliente.scadenza_chiave = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=2),
                                                                 "%Y-%m-%d %H:%M:%S")
            cliente.save()
        return user

    def inviaEmail(self,data):
        link = "http://test.pulitecna.it/registrazione/conferma/"+data["chiave"]
        c = Context({'link': link})
        f = open(BASE_DIR + "/negozio/templates/email/attivazione_account.html", 'r')
        t = Template(f.read())
        f.close()
        message = t.render(c)
        send_mail("Attivazione account", "", "Cartuccia24.com <attivazioni@cartuccia24.com>", [data["email"]],
                  fail_silently=False, html_message=message)

class CambiaPasswordForm(PasswordChangeForm):
    pass

def _pw(length=6):
    s = ''
    for i in range(length):
        s += random.choice(digits + letters)
    return s

class RecuperaPasswordForm(PasswordResetForm):

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
            Generates a one-use only link for resetting password and sends to the
            user.
            """
        email = self.cleaned_data["email"]
        for user in self.get_users(email):
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override

            new_pass = _pw(8)
            user.set_password(new_pass)
            user.save()
            context = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'user': user,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'password':new_pass,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            if extra_email_context is not None:
                context.update(extra_email_context)
            self.send_mail(subject_template_name, email_template_name,
                           context, from_email, user.email,
                           html_email_template_name=html_email_template_name)

class IndirizzoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(IndirizzoForm, self).__init__(*args, **kwargs)
        self.fields["citta"].queryset = Citta.objects.all().order_by("nome")

    class Meta:
        model = Indirizzo
        exclude = ('has_prodotti',)
        widgets = {
            'citta': ModelSelect2(url='citta-autocomplete'),
            'utente':ModelSelect2(url='cliente-autocomplete'),
        }

class NuovoIndirizzoForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(NuovoIndirizzoForm, self).__init__(*args, **kwargs)
        self.fields["citta"].queryset = Citta.objects.all().order_by("nome")



    class Meta:
        model = Indirizzo
        exclude = ('utente',)
        widgets = {
            'citta': ModelSelect2(url='citta-autocomplete'),
            'utente': ModelSelect2(url='cliente-autocomplete'),
        }

class ModificaInformazioniForm(ModelForm):
    username = CharField(required=False)
    email = EmailField(required=True)
    first_name = CharField(required=True)
    last_name = CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(ModificaInformazioniForm, self).__init__(*args, **kwargs)

        default_field_excludes = [
            'date_joined',
            'groups',
            'is_staff',
            'is_active',
            'is_superuser',
            'last_login',
            'user_permissions',
            'password',
        ]

        for field in default_field_excludes:
            del self.fields[field]

    current_user = User()

    class Meta:
        model = User
        exclude = ('username',)


    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email and User.objects.filter(email=email).exclude(username=self.current_user.username).count():
            raise forms.ValidationError(
                'Email in uso riprova')
        return email

    def save(self, commit=True):
        user = self.current_user
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()

        return user

class RigaOrdineForm(ModelForm):

    class Meta:
        model = RigaOrdine
        exclude = ('',)
        widgets = {
            "prodotto":ModelSelect2(url='prodotto-autocomplete')
        }

class InfoOrdineForm(Form):

    utente = Cliente()
    def __init__(self,*args,**kwargs):
        self.utente = kwargs.pop("utente")
        super(InfoOrdineForm,self).__init__(*args,**kwargs)
        self.fields["indirizzo_spedizione"].queryset = Indirizzo.objects.all().filter(utente=self.utente)
        self.fields["indirizzo_fatturazione"].queryset = Indirizzo.objects.all().filter(utente=self.utente)


    indirizzo_spedizione = ModelChoiceField(queryset=None,required=True,label="Indirizzo dove spedire")
    fattura = BooleanField(label="Fattura ?",required=False)
    indirizzo_fatturazione = ModelChoiceField(queryset=None,required=False,label="Indirizzo dove fatturare")
    pagamento = ModelChoiceField(queryset=Pagamento.objects.all(),required=True,widget=RadioSelect())

class OrdineForm(ModelForm):


    def clean_url_tracciamento(self):
        current_state = str(self.instance.url_tracciamento)
        new_state = str(self.cleaned_data["url_tracciamento"])

        if current_state != new_state:
            self.instance.invia_tracking(url=new_state)
        return self.cleaned_data["url_tracciamento"]

    def clean_stato(self):
        current_state = str(self.instance.stato.nome)
        new_state = str(self.cleaned_data["stato"])

        if current_state != new_state:

            try:
                if new_state == "Spedito":
                    self.instance.invia_email_spedito()

                if new_state == "Pagato":
                    self.instance.invia_email_pagato()

                if new_state == "Pagato con PayPal":
                    self.instance.invia_email_pagato()

                if new_state == "Annullato":
                    self.instance.invia_email_annullato()
            except:
                pass





        return self.cleaned_data["stato"]


    class Meta:
        exclude = ()




class StampantePreferitaForm(ModelForm):

    class Meta:
        model = StampantePreferita
        exclude = ('',)
        widgets = {
            "cliente":ModelSelect2(url='cliente-autocomplete'),
            "stampante":ModelSelect2Multiple(url='stampante-autocomplete')
        }

class ContattaciForm(Form):
    nome = CharField(required=True)
    cognome = CharField(required=True)
    email = EmailField(required=True)
    oggetto = CharField(required=True)
    messaggio = CharField(required=True)

