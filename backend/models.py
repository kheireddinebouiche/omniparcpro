from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django.utils import timezone
from django.utils.datetime_safe import datetime
from django_countries.fields import CountryField
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from multiselectfield import MultiSelectField


CATEGORY_CHOICES = (
    ('TH', 'Travaux en hauteur'),
    ('TE', 'Terrassement & Extraction'),
    ('LM', 'Levage & Manutention'),
    ('CT', 'Chargement & Transport'),
    ('GD', 'Gros Oeuvre & Démolition'),
)

CH = {
    ('o', 'Oui'),
    ('n', 'Non'),

}

PUISSANCE = {
    ('ess', 'Essence'),
    ('die', 'Diesel'),
    ('ele', 'Electrique'),
}

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

ORDER_STATUS = (
    ('ET', 'En cours de traitement'),
    ('CV', 'Commande valider'),
    ('CET', 'Commande on cours de livraison'),
    ('CA', 'Commande annuler'),
    ('CL', 'Commande livrée'),
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

class Profile(models.Model):
    user = models.OneToOneField(User, unique=True, on_delete=models.CASCADE)
    organisation = models.CharField(max_length=50, blank=True, null=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    adresse = models.CharField(max_length=300,null=True,blank=True)
    photo_de_profile = models.ImageField(null=True, blank=True)
    is_entreprise = models.BooleanField(default=False)
    is_particulier = models.BooleanField(default=False)
    is_offre = models.BooleanField(default=False)
    raison_social = models.CharField(max_length=33,null=True, blank=True)
    adresse_siege = models.CharField(max_length=400, null=True, blank=True)
    nif = models.CharField(max_length=30, null=True, blank=True)
    nis = models.CharField(max_length=30, null=True, blank=True)
    banniere = models.ImageField(null=True, blank=True)
    slug = models.SlugField(max_length=100, null=True, blank=True)
    note = models.BooleanField(default=False)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nif)
        super(Profile, self).save(*args, **kwargs)

    def get_profile_details(self):
        return reverse("omniparc:entreprise_details", kwargs={
            'slug': self.slug
        })

    def __str__(self):
        return self.user.username

class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=100, unique=True)
    reference = models.CharField(max_length=1000, null=True, blank=True)
    price = models.FloatField(null=True)
    prix_avec_operateur = models.FloatField(null=True, blank=True)
    prix_avec_livraison_reprise = models.FloatField(null=True, blank=True)
    mode_location = models.CharField(choices=MODE_LOCATION, null=True, blank=True, max_length=2)
    reprise_livraison = models.CharField(max_length=33, null=True, blank=True)
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=4, null=True, blank=True)
    label = models.CharField(choices=LABEL_CHOICES, max_length=4, null=True, blank=True)
    slug = models.SlugField(unique=True)
    image = models.ImageField(null=True)
    date_debut = models.DateField(null=True, blank=True, default=None)
    date_fin = models.DateField(null=True, blank=True, default=None)
    disp = MultiSelectField(choices=DAYS_OF_WEEK ,null=True, max_length=20, max_choices=7, min_choices=1)
    description = models.TextField()
    localisation_engin = models.CharField(max_length=200, null=True, blank=True)

    motorisation = models.CharField(max_length=300, null=True, blank=True)
    puissance = models.CharField(max_length=3, choices=PUISSANCE, blank=True, null=True )

    ptac = models.CharField(max_length=3000, blank=True, null=True)
    ptra = models.CharField(max_length=100,blank=True, null=True)
    ptc = models.CharField(max_length=200,blank=True, null=True)

    disponible = models.BooleanField(default=True)
    view_count = models.IntegerField(default=0,null=True,blank=True)


    is_approuved = models.BooleanField(default=False, blank=True, null=True)
    commentaire = models.CharField(max_length=10000,blank=True, null=True)

    class Meta:
        ordering = ["title"]
        verbose_name_plural = "Items"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Item, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("omniparc:products", kwargs={
            'slug': self.slug
        })
    def get_detail_info_comm(self):
        return reverse("omniparc:detail_commande", kwargs={
            'slug' : self.slug
        })
    def get_demande_devis(self):
        return reverse('omniparc:Demande-devis', kwargs={
            'slug' : self.slug
        })
    def get_devis(self):
        return reverse('omniparc:devis', kwargs={
           'slug': self.slug
        })
    def get_url_admin(self):
        return reverse("omniparc:Item-Detail-Administration", kwargs={
            'slug': self.slug
        })
    def update(self):
        return reverse("omniparc:update-item", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("omniparc:add_to_cart", kwargs={
            'slug': self.slug
        })
    
    def zero_vue(self):
        return reverse("omniparc:zero-vue", kwargs={
            'slug' : self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("omniparc:remove_from_cart", kwargs={
            'slug': self.slug
        })
    
    def signalement_item(self):
        return reverse('omniparc:signale_items', kwargs={
            'slug' : self.slug
        })

class SignaledItems(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True)

    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    motifs = models.CharField(max_length=1000,blank=True, null=True)


    class Meta:
        verbose_name="Signalement de l'article"
        verbose_name_plural = "Signalements des articles"

    def __str__(self):
        return self.user.username

class Annonce(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    article = models.CharField(max_length=200)
    localisation = models.CharField(max_length=300, null=True, blank=True)
    date = models.DateField(null=True,blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(null=True, blank=True, unique=True)

    duree_location = models.IntegerField(null=True, blank=True)
    date_de_debut = models.DateField(null=True, blank=True)
    date_de_fin = models.DateField(null=True, blank=True)

    avec_operateur = models.BooleanField(null=True, blank=True, default=False)
    reprise_livraison = models.BooleanField(null=True, blank=True, default=False)

    is_approuved = models.BooleanField(blank=True, null=True, default=False)
    is_rejected = models.BooleanField(blank=True, null=True)
    commentaire = models.CharField(max_length=100000, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.created_date)
        super(Annonce, self).save(*args, **kwargs)

    def delete_annonce(self):
        return reverse('omniparc:delete_annonce', kwargs={
            'slug' : self.slug
        })

    def update_annonce(self):
        return reverse('omniparc:update_annonce', kwargs={
            'slug': self.slug
        })

    def get_absolute_url(self):
        return reverse("omniparc:details_de", kwargs={
            'slug': self.slug
        })
    def get_response(self):
        return reverse("omniparc:annonce_responses", kwargs={
            'slug':self.slug
        })

    def __str__(self):
        return self.slug

class Annonce_responde(models.Model):
    ann = models.ForeignKey(Annonce, on_delete=models.CASCADE, null=True)
    slug_annonce = models.CharField(max_length=400, null=True, blank=True)
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    created_date = models.DateTimeField(default=timezone.now)
    approuved_proposition = models.BooleanField(default=False)

    item = models.ForeignKey(Item,on_delete=models.CASCADE)
    prix = models.CharField(max_length=300,null=True, blank=True)

    duree_location = models.IntegerField(null=True, blank=True)
    date_debut_commande = models.DateField(null=True, blank=True)
    date_fin_commande = models.DateField(null=True, blank=True)

    avec_operateur = models.BooleanField(default=False, null=True, blank=True)
    livraison_reprise = models.BooleanField(default=False, null=True, blank=True)

    montant_global = models.FloatField(max_length=30, null=True, blank=True)


    is_approuved = models.BooleanField(default=False)
    is_choosed = models.BooleanField(default=False)

    commentaire = models.CharField(max_length=10000, null=True, blank=True)

    def approuve(self):
        self.approuved_proposition = True
        self.save()

    def __str__(self):
        return self.slug_annonce

def increment_order_id_number():
        dernier_nomber = OrderItem.objects.all().order_by('id').last()
        if not dernier_nomber:
            return 'I-OMN/' + '1'

        item_order_id = dernier_nomber.item_order_id
        item_order_nb = int(item_order_id.split('I-OMN/')[-1])
        n_item_order_nb = item_order_nb + 1
        n_item_order_id = 'I-OMN/' + str(n_item_order_nb)
        return n_item_order_id

def increment_devis_id_number():
    dernier_nomber = DevisItem.objects.all().order_by('id').last()
    if not dernier_nomber:
        return 'I-OMN/DEVIS' + '1'
    id_devis = dernier_nomber.id_devis
    item_order_nb = int(id_devis.split('I-OMN/DEVIS')[-1])
    n_item_order_nb = item_order_nb + 1
    n_item_order_id = 'I-OMN/DEVIS' + str(n_item_order_nb)
    return n_item_order_id

class DevisItem(models.Model):
    id_devis = models.CharField(max_length=1000, default=increment_devis_id_number, null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item,on_delete=models.CASCADE)
    prix_unitaire = models.FloatField(null=True, blank=True)
    mode_location = models.CharField(max_length=100)
    dure_location = models.IntegerField(default=1)
    montant_location = models.FloatField(null=True)
    avec_operateur = models.CharField(max_length=33)
    reprise_livraison = models.CharField(max_length=33, blank=True, null=True)
    adreese_chantier = models.ForeignKey('ShippingAddress', null=True, blank=True,max_length=300, on_delete=models.SET_NULL)

    entreprise_emetrice = models.CharField(max_length=200, null=True, blank=True)
    gerant_emeteur = models.CharField(max_length=100, null=True, blank=True)
    user_owner = models.CharField(max_length=100, null=True, blank=True)
    tel_emeteur = models.CharField(max_length=14, null=True, blank=True)
    email_emeteur = models.CharField(max_length=100, null=True, blank=True)
    adresse_emeteur = models.CharField(max_length=100, null=True, blank=True)

    entreprise_reception = models.CharField(max_length=200, null=True, blank=True)
    gerant_reception = models.CharField(max_length=100, null=True, blank=True)
    tel_reception = models.CharField(max_length=14, null=True, blank=True)
    email_reception = models.CharField(max_length=100, null=True, blank=True)

    etat_devis = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    montant_service_adi = models.FloatField(max_length=30, null=True, blank=True)

    is_confirmed = models.BooleanField(default=False, null=True, blank=True)

    devis_date_debut = models.DateField(null=True, blank=True)
    devis_date_fin = models.DateField(null=True, blank=True)


    def __str__(self):
        return self.id_devis

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id_devis)
        super(DevisItem, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("omniparc:Devis", kwargs={
            'slug': self.slug
        })

    def get_udpate_devis(self):
        return reverse('omniparc:update_commande', kwargs={
            'slug' : self.slug
        })

    def get_remove_devis(self):
        return reverse("omniparc:delete_devis", kwargs={
            'slug': self.slug
        })

    def get_add_item_cart(self):
        return reverse("omniparc:confirm_devis_add_cart", kwargs={
            'slug' : self.slug
        })

class OrderItem(models.Model):
    item_order_id = models.CharField(max_length=1000, default=increment_order_id_number, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    status = models.CharField(max_length=3, choices=ORDER_STATUS, blank=True, null=True)
    date_de_demande = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    addresse_livraison = models.ForeignKey('ShippingAddress', on_delete=models.SET_NULL, blank=True, null=True)
    avec_operateur = models.CharField(max_length=33, null=True, blank=True)
    reprise_livraison = models.CharField(max_length=33, null=True, blank=True)
    duree_location = models.IntegerField(null=True, blank=True)

    prix_unitaire = models.FloatField(max_length=30, null=True, blank=True)
    montant_total = models.FloatField(max_length=30,null=True,blank=True)

    montant_service_adi = models.FloatField(max_length=30, null=True, blank=True)

    reference_devis = models.CharField(null=True, blank=True, max_length=300)

    date_debut_commande = models.DateField(null=True, blank=True)
    date_fin_commande= models.DateField(null=True, blank=True)


    def __str__(self):
        return self.item_order_id

    def save(self, *args, **kwargs):
        self.slug = slugify(self.item_order_id)
        super(OrderItem, self).save(*args, **kwargs)

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_final_price(self):
        return self.get_total_item_price()

    def get_final(self):
        return (self.prix_unitaire + self.montant_service_adi) * self.duree_location

    def det_tot(self):
        return self.get_final()

    def get_absolute_url(self):
        return reverse("omniparc:detail-commande", kwargs={
            'slug': self.slug
        })

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('BillingAddress', on_delete=models.SET_NULL, blank=True, null=True)
    shipping_address = models.ForeignKey('ShippingAddress', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.det_tot()
        return total

class BillingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    appartement_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    appartement_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username





