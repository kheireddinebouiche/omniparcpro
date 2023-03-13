from collections import OrderedDict
#from contact_form.forms import ContactForm
from django import forms
from django.forms import ModelForm, DateInput
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
#from allauth.account.forms import SignupForm
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Item, DevisItem, Annonce, Annonce_responde
from django.contrib.auth.models import User

PAYMENT_CHOICES = (
    ('S', 'Strip'),
    ('p', 'Paypal'),

)

CATEGORY_CHOICES = (
    ('TH', 'Travaux en hauteur'),
    ('TE', 'Terrassement & Extraction'),
    ('LM', 'Levage & Manutention'),
    ('CT', 'Chargement & Transport'),
    ('GD', 'Gros Oeuvre & Démolition'),
)

LABEL_CHOICES = (
    ('CNP', 'Camion Nacelle PT'),
    ('CNV', 'Camion Nacelle VI'),
    ('ER', 'Echaffaudage Roulant'),
    ('NA', 'Nacelle Araignée'),
    ('NAR', 'Nacelle Articulée'),
    ('NC', 'Nacelle Ciseaux'),
    ('NT', 'Nacelle Telescopique'),
    ('NTC', 'Nacelle Toucon'),
    ('NEL', 'Nacelle Elevatrice'),

    ('B', 'Buldozer'),
    ('C', 'Chargeuse'),
    ('MC', 'Mini Chargeuse'),
    ('MP', 'Mini Pelle'),
    ('P', 'Pelleteuse'),

    ('CH', 'Chariot Elevateur'),
    ('CT', 'Chariot Telescopique'),
    ('GT', 'Gerbeur & Transpalette'),
    ('GMV', 'Glaslift: Monte vitre'),
    ('G', 'Grue Mobile'),
    ('GSR', 'Grue sur remorque'),
    ('MGA', 'Mini Grue araignée'),
    ('MGB', 'Mini Grue mobile'),
    ('MCA', 'Monte Charge'),

    ('BE', 'Benne'),
    ('CB', 'Camion Benne'),
    ('CBG', 'Camion Bras de grue'),
    ('TOM', 'Tombereau'),

    ('RB', 'Rebot de démolition'),
)

DAYS_OF_WEEK = (
    ('DIM', 'Dimanche'),
    ('LUN', 'Lundi'),
    ('MAR', 'Mardi'),
    ('MER', 'Mercredi'),
    ('JEU', 'Jeudi'),
    ('VEN', 'Vendredi'),
    ('SAM', 'Samedi'),
    ('AUC', 'Aucune disponibilité'),
)

MODE_LOCATION = {
    ('PH', 'Heure'),
    ('PJ', 'Jour'),
}

CH = {
    ('o', 'Oui'),
    ('n', 'Non'),

}

ETAT_DEVIS = {
    ('En attente de traitement', 'En attente de traitement'),
    ('Devis confirmer', 'Devis confirmer'),
}

class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': '1234 Main St',
        'class': 'form-control',

    }))
    appartement_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Apartment or Building',
        'class': 'form-control',

    }))
    country = CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(attrs={
        'class': 'custom-select d-block w-100'
    }))
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'zip'
    }))
    same_shipping_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    #payement_option = forms.ChoiceField(widget=forms.RadioSelect(), choices=PAYMENT_CHOICES)


class AddItems(forms.ModelForm):
    class Meta:
        model = Item
        fields = (
            'title',
            'price',
            'prix_avec_operateur',
            'prix_avec_livraison_reprise',
            'mode_location',
            'category',
            'label',
            'image',
            'date_debut',
            'date_fin',
            'description',
            'motorisation',
            'puissance',
            'ptac',
            'ptra',
            'ptc',
            'disp',
        )
        widgets = {
            'date_debut': forms.TextInput(attrs={'type': 'date', 'style': 'width : 18%;'}),
            'title': forms.TextInput(attrs={'type': 'text', 'style': 'width : 50%;', 'placeholder':'kkkk'}),
            'date_fin': forms.TextInput(attrs={'type': 'date', 'style': 'width : 18%;'}),
            'category': forms.Select(attrs={'style': 'width : 20%;'}),
            'disp' : forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


class SignUpForm_entreprise(UserCreationForm):
    email = forms.EmailField(max_length=100)
    organisation = forms.CharField(max_length=100,  label="Renseignez le nom de votre organisation")
    adresse_siege = forms.CharField(max_length=400, label="L'adresse de votre siége social")
    nis = forms.CharField(max_length=100,  label="N° Identification Fiscal")
    nif = forms.CharField(max_length=100,  label="N° Identification Social")

    class Meta:
        model = User
        fields = ('organisation','adresse_siege','nis','nif', 'username', 'first_name', 'last_name','email')


class SignUpForm_particulier(UserCreationForm):
    email = forms.EmailField(max_length=100, help_text='Required')
    organisation = forms.CharField(max_length=100)
    adresse_siege =  forms.CharField(max_length=400)
    class Meta:
        model = User
        fields = ('organisation', 'adresse_siege','username', 'first_name', 'last_name', 'email')

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('photo_de_profile','banniere', 'organisation', 'phone_number','adresse_siege','nif','nis')
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'phone'})
        }

class ItemUpdate(ModelForm):

    class Meta:
        model = Item
        fields = ('title', 'price', 'mode_location' ,'category', 'label', 'image', 'date_debut', 'date_fin', 'description', 'disp', 'prix_avec_operateur', 'prix_avec_livraison_reprise')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'label':'Titre de l''article'}),
            'date_debut': forms.TextInput(attrs={'type': 'date', 'style': 'width : 100%;'}),
            'date_fin': forms.TextInput(attrs={'type': 'date', 'style': 'width : 100%;'}),
            'price': forms.NumberInput(attrs={'type' : 'number', 'step':'0.01'}),
            'category': forms.Select(attrs={'style': 'width : 100%;'}),
            'disp' : forms.SelectMultiple(attrs={'class' :'form-control'}),
        }

class ContactForm(forms.Form):
    from_email = forms.EmailField(required=True, label='Votre adresse Email')
    subject = forms.CharField(required=True, label='Le suject de votre message')
    message = forms.CharField(widget=forms.Textarea, required=True, label='Votre message')

class DevisForm(forms.Form):
    duree_location = forms.IntegerField(required=True, label='Veuiller définir la durée de location')
    adresse_livraison = forms.CharField(max_length=100)
    avec_operateur = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'input'}), required=False, label='Avec opérateur ?')
    reprise_livraison  = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'input'}), required=False)
    devis_date_debut = forms.DateField(widget=forms.DateInput(attrs={'class' : 'input'}), required=False)
    devis_date_fin = forms.DateField(widget=forms.DateInput(attrs={'class' : 'input'}), required=False)

class ReservationFrom(forms.Form):
    duree_location = forms.IntegerField(required=True, label='Veuiller définir la durée de location')
    avec_operateur = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'input'}), required=False,label='Avec opérateur ?')
    reprise_livraison = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'input'}), required=False)

class Update_commande(forms.ModelForm):
    etat_devis = forms.ChoiceField(widget=forms.Select, choices=ETAT_DEVIS)
    class Meta:
        model = DevisItem
        fields=['prix_unitaire', 'dure_location', 'etat_devis']


class AnnonceForm(forms.ModelForm):
    article = forms.CharField(required=True, label='Saisir la designation de votre engin rechercher')
    localisation = forms.CharField(required=True, label='Renseigner la localisation de votre chantier')
    date_de_debut = forms.DateField(widget=forms.DateInput)
    date_de_fin = forms.DateField(widget=forms.TextInput(attrs={'class': 'datepicker'}))
    avec_operateur = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'input'}), required=False,label='Avec opérateur ?')
    reprise_livraison = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'input'}), required=False)
    class Meta:
        model = Annonce
        fields = ['article','localisation','duree_location','date_de_debut','date_de_fin','avec_operateur','reprise_livraison']

class RespondeAnnonce(forms.ModelForm):

    prix = forms.CharField(required=True, label='Saisir la designation de votre engin rechercher')
    v = forms.CharField(required=True, label='Saisir la designation de votre engin rechercher')
    duree_location = forms.IntegerField()
    date_debut_commande = forms.DateField(widget=forms.DateInput)
    date_fin_commande = forms.DateField(widget=forms.TextInput(attrs={'class': 'datepicker'}))
    avec_operateur = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'input'}), required=False,label='Avec opérateur ?')
    livraison_reprise = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': 'input'}), required=False)

    class Meta:
        model = Annonce_responde
        fields = ['prix','duree_location','date_debut_commande','date_fin_commande','avec_operateur','livraison_reprise']








