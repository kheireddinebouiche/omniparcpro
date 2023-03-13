from sqlite3 import Date, datetime
import dateutil
from dateutil.parser import parser
#import dateutils as dateutils
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage, send_mail, BadHeaderError
from django.db import transaction
from django.db.models import Q, Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import csrf_protect
from django.views.generic import ListView, DetailView, View, UpdateView
from django.views.generic.edit import FormMixin
from marketing.forms import EmailSignUpForm
from .forms import CheckoutForm, AddItems, UserForm, ProfileForm,  ContactForm, ItemUpdate, DevisForm, \
    ReservationFrom, Update_commande, AnnonceForm, RespondeAnnonce, SignUpForm_particulier, SignUpForm_entreprise
from .models import Item, OrderItem, Order, BillingAddress, Profile, ShippingAddress, DevisItem, Annonce, \
    Annonce_responde
from .token_generator import account_activation_token
from .filter import ItemFilter

##############################################################
class HomeView(ListView, FormMixin):
    form_class = EmailSignUpForm
    model = Item
    paginate_by = 4
    template_name = "home-page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = ItemFilter(self.request.GET, queryset=self.get_queryset())
        return context

##########################################################################
class PayementOption(View):
    def get(self, *args, **kwargs):
        return render(self.request, "payement.html")


###########################################################################
class OrderSummeryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order,
            }
            return render(self.request, "order_summery.html", context)

        except ObjectDoesNotExist:
            messages.warning(self.request, "Vous n'avez aucune commande actif pour le moment")
            return redirect("/")
#############################################################################

class Commande(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            my_command = OrderItem.objects.filter(user=self.request.user, ordered=True)
            context = {
                'commande': my_command,
            }
            return render(self.request, 'mes_commandes.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "Vous n'avez aucune commande actif pour le moment")
            return redirect("/")

##############################################################################

class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        order_s = Order.objects.get(user=self.request.user, ordered=False)

        context = {
            'form': form,
            'order': order_s,
        }
        return render(self.request, 'checkout-page.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data['street_address']
                appartement_address = form.cleaned_data['appartement_address']
                country = form.cleaned_data['country']
                zip = form.cleaned_data['zip']
                same_shipping_address = form.cleaned_data['same_shipping_address']
                save_info = form.cleaned_data['save_info']
                #payement_option = form.cleaned_data['payement_option']
                billing_address = BillingAddress(

                    user=self.request.user,
                    street_address=street_address,
                    appartement_address=appartement_address,
                    country=country,
                    zip=zip,
                )
                if same_shipping_address == True:
                    shipping = ShippingAddress(
                        user=self.request.user,
                        street_address=street_address,
                        appartement_address=appartement_address,
                        country=country,
                        zip=zip
                    )
                    billing_address.save()
                    shipping.save()
                    order_items = order.items.all()
                    order_items.update(ordered=True)
                    order_items.update(status='ET')
                    order_items.update(addresse_livraison=shipping)
                    for items in order_items:
                        items.save()
                    order.ordered = True


                    order.billing_address = billing_address
                    order.shipping_address = shipping
                    order.save()
                    messages.success(self.request, "Votre commande a été validée")
                    return redirect('omniparc:home')
                else:
                    order.ordered = True
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()
                    messages.success(self.request, "Votre commande a été validée")
                    return redirect('omniparc:home')
            else:
                messages.warning(self.request, "Veuillez vérifier votre formulaire")
                return redirect('omniparc:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "Vous n'avez aucune commande actif pour le moment")
            return redirect("omniparc:order_summery")


###############################################################
class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"

    def get_object(self):
        object = super(ItemDetailView, self).get_object()
        object.view_count += 1
        object.save()
        return object

def ViewCount(request):
    item = Item.objects.filter(user = request.user)
    context = {
        'item' : item,
    }
    return render(request, 'backadminpanel/item_view_count.html', context)

def ZeroVueItem(request, slug):
    item = get_object_or_404(Item, slug = slug)
    item.view_count = 0
    item.save()
    return redirect('omniparc:view-count')

###############################################################
@login_required
def details_commande(request, slug):
    item = get_object_or_404(Item, slug=slug)
    context = {
        'item' : item
    }
    return render(request, 'details_commande.html', context)
###############################################################

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    form = ReservationFrom(request.POST)
    if request.method == 'POST' and form.is_valid():
        duree_location = form.cleaned_data['duree_location']
        avec_operateur = form.cleaned_data['avec_operateur']
        reprise_livraison = form.cleaned_data['reprise_livraison']

        if avec_operateur == True and reprise_livraison== True:
            avec_operateur = "Avec operateur"
            reprise_livraison = "Avec livraison et reprise"
            tot = item.prix_avec_operateur + item.prix_avec_livraison_reprise
        elif avec_operateur== False and reprise_livraison==False:
            avec_operateur = "Sans operateur"
            reprise_livraison = "Sans livraison et reprise"
            tot= 0
        elif avec_operateur == True and reprise_livraison==False:
            avec_operateur = "Avec operateur"
            reprise_livraison = "Sans livraison et reprise"
            tot = item.prix_avec_operateur
        elif avec_operateur == False and reprise_livraison==True:
            avec_operateur = "Sans operateur"
            reprise_livraison = "Avec livraison et reprise"
            tot = item.prix_avec_livraison_reprise

        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user=request.user,
            ordered=False,
            duree_location=duree_location,
            reprise_livraison=reprise_livraison,
            avec_operateur=avec_operateur,
            prix_unitaire=item.price,
            montant_total= (item.price + tot) * duree_location,
            montant_service_adi = tot
        )


        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if order.items.filter(item__slug=item.slug).exists():
                order_item.quantity += 1
                order_item.save()
                messages.info(request, "This item quantity was updated")
                return redirect("omniparc:order_summery")
            else:
                messages.info(request, "Cette article vien d'étre ajouter a votre panier")
                order.items.add(order_item)
                return redirect("omniparc:order_summery")
        else:

            ordered_date = timezone.now()
            order = Order.objects.create(user=request.user, ordered_date=ordered_date, )
            order.items.add(order_item)
            messages.info(request, "Cette article vien d'étre ajouter a votre panier")
                
###############################################################################################
@transaction.atomic
@login_required
def confirm_devis_add_cart(request, slug):
    Devis = get_object_or_404(DevisItem, slug=slug)
    item = Item.objects.filter(slug=Devis.item.slug)
    Devis.is_confirmed = True
    item.update(disponible=False)
    Devis.save()
    order_item, created = OrderItem.objects.get_or_create(
        item=Devis.item,
        user=request.user,
        ordered=False,
        montant_total = Devis.montant_location,
        addresse_livraison = Devis.adreese_chantier,
        reference_devis = Devis.id_devis,
        avec_operateur = Devis.avec_operateur,
        reprise_livraison = Devis.reprise_livraison,
        date_fin_commande= Devis.devis_date_fin,
        date_debut_commande= Devis.devis_date_debut,
        duree_location= Devis.dure_location,
        prix_unitaire = Devis.prix_unitaire,
        montant_service_adi=Devis.montant_service_adi,

    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=Devis.item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated")
            return redirect("omniparc:order_summery")
        else:
            messages.info(request, "Cette article vien d'étre ajouter a votre panier")
            order.items.add(order_item)
            return redirect("omniparc:order_summery")
    else:

        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user,
            ordered_date=ordered_date,

        )
        order.items.add(order_item)
        order_items = order.items.all()
        order_items.update(ordered=True)
        order_items.update(status='ET')

        for items in order_items:
            items.save()
        order.ordered = True
        order.save()
        messages.info(request, "Votre commande a été validée")
        return redirect('omniparc:home')

###################################################################################
@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )

    if order_qs.exists():
        order = order_qs[0]

        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "L'article a bien été  supprimer de votre panier")
            return redirect("omniparc:order_summery")

        else:
            messages.info(request, "This item was not in your cart")
            return redirect("omniparc:products", slug=slug)

    else:
        messages.info(request, "You do not have an active order")
        return redirect("omniparc:products", slug=slug)

#########################################################################################

@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )

    if order_qs.exists():
        order = order_qs[0]

        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False

            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)

            messages.info(request, "This item quantity was updated")
            return redirect("omniparc:order_summery")

        else:
            messages.info(request, "This item was not in your cart")
            return redirect("omniparc:products", slug=slug)



    else:
        messages.info(request, "You do not have an active order")
        return redirect("omniparc:product", slug=slug)


##############################################################################################
#            this section is for the contröle panel of the administrations 					 #
##############################################################################################
def PlanChoice(request):
    return render(request, "plan.html")


##############################################################################################

@login_required(login_url='/accounts/login')
def Administration(request):
    if request.user.profile.is_entreprise == True or request.user.profile.is_offre:
        item = Item.objects.filter(user=request.user)
        nb_devis = DevisItem.objects.filter(user_owner=request.user)
        context = {
            'objects': item,
            'nb_devis': nb_devis,
        }
        return render(request, "backadminpanel/index.html", context)
    else:
        messages.warning(request, 'you are note allowed to view this section')
        return redirect('omniparc:home')


##############################################################################################

class ItemDetailAdministration(DetailView):
    model = Item
    template_name = "backadminpanel/admin_product_detail.html"


##############################################################################################

class Profile_admin(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        return render(self.request, "backadminpanel/pages-profile.html")


##############################################################################################
@login_required(login_url='/accounts/login')
def ListArticle(request):
    if request.user.profile.is_entreprise == True:
        item = Item.objects.filter(user=request.user)
        context = {
            'objects': item
        }
        return render(request, "backadminpanel/liste_article.html", context)
    else:
        messages.warning(request, "Vous n'étes pas autoriser à voir cette partie de l'application")
        return redirect('omniparc:home')


##############################################################################################

class Add_Item(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        form = AddItems()
        context = {
            'object': form
        }
        return render(self.request, "backadminpanel/add_article.html", context)

    def post(self, *args, **kwargs):
        form = AddItems(self.request.POST, self.request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            price = form.cleaned_data['price']
            mode_location = form.cleaned_data['mode_location']
            category = form.cleaned_data['category']
            label = form.cleaned_data['label']
            description = form.cleaned_data['description']
            image = form.cleaned_data['image']
            date_debut = form.cleaned_data['date_debut']
            date_fin = form.cleaned_data['date_fin']
            motorisation = form.cleaned_data['motorisation']
            puissance = form.cleaned_data['puissance']
            ptac = form.cleaned_data['ptac']
            ptra = form.cleaned_data['ptra']
            ptc = form.cleaned_data['ptc']
            prix_avec_operateur = form.cleaned_data['prix_avec_operateur']
            prix_avec_livraison_reprise = form.cleaned_data['prix_avec_livraison_reprise']
            disp = form.cleaned_data['disp']


            item = Item(
                user=self.request.user,
                title=title,
                price=price,
                mode_location=mode_location,
                category=category,
                label=label,
                description=description,
                image=image,
                date_fin= date_fin,
                date_debut=date_debut,
                motorisation = motorisation,
                puissance = puissance,
                ptac = ptac,
                ptra = ptra,
                ptc = ptc,
                prix_avec_operateur = prix_avec_operateur,
                prix_avec_livraison_reprise = prix_avec_livraison_reprise,
                disp = disp,

            )
            item.save()
            messages.success(self.request, "L'article a été bien ajouter")
            return redirect('omniparc:Administration')
        else:
            messages.warning(self.request, "Veuillez verifier les informations renséigner !")
            return redirect('omniparc:add-item')
            

            
################################################################################################
@transaction.atomic
@csrf_protect
def RegisterParticulier(request):
    if request.method == 'POST':
        form = SignUpForm_particulier(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active=False
            user.save()

            user = form.save()
            user.refresh_from_db()
            user.profile.organisation = form.cleaned_data.get('organisation')
            user.profile.adresse_siege = form.cleaned_data.get('adresse_siege')
            user.profile.is_particulier = True
            user.profile.photo_de_profile = 'media.png'
            user.profile.banniere = 'banniere_default.JPG'

            user.save()

            current_site = get_current_site(request)
            email_subject = "Lien d'activation de votre compte offre demandeur"
            message = render_to_string('activate_account.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(email_subject, message, to=[to_email])
            email.send()
            return render(request, 'email_sent.html')

        else:
            messages.error(request, "Veuillez verifier votre fomulaire")
    else:
        form = SignUpForm_particulier()
    return render(request, 'register-particulier.html', {'form': form})

################################################################################################
@transaction.atomic
@csrf_protect
def RegisterEntreprise_offre(request):
    if request.method == 'POST':
        form = SignUpForm_entreprise(request.POST)
        if form.is_valid():
            #permet de ne pas enregistrer l'instance dans la base de donnée
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            #permet d'enregistrer le profile de l'utilisateur
            user = form.save()
            user.refresh_from_db()
            user.profile.organisation = form.cleaned_data.get('organisation')
            user.profile.adresse_siege = form.cleaned_data.get('adresse_siege')
            user.profile.nif = form.cleaned_data.get('nif')
            user.profile.nis = form.cleaned_data.get('nis')
            user.profile.is_offre = True
            user.profile.note = True
            user.profile.photo_de_profile = 'media.png'
            user.profile.banniere = 'banniere_default.JPG'
            user.save()

            current_site = get_current_site(request)
            email_subject = "Lien d'activation de votre compte entreprise"
            message = render_to_string('activate_account.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(email_subject, message, to=[to_email])
            email.send()
            return render(request, 'email_sent.html')

        else:
            messages.error(request, "Veuillez verifier votre fomulaire")
    else:
        form = SignUpForm_entreprise()
    return render(request, 'register_offre.html', {'form': form})
################################################################################################
@transaction.atomic
@csrf_protect
def RegisterEntreprise(request):
    if request.method == 'POST':
        form = SignUpForm_entreprise(request.POST)
        if form.is_valid():
            #permet de ne pas enregistrer l'instance dans la base de donnée
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            #permet d'enregistrer le profile de l'utilisateur
            user = form.save()
            user.refresh_from_db()

            user.profile.organisation = form.cleaned_data.get('organisation')
            user.profile.adresse_siege = form.cleaned_data.get('adresse_siege')
            user.profile.nif = form.cleaned_data.get('nif')
            user.profile.nis = form.cleaned_data.get('nis')
            user.profile.is_entreprise = True
            user.profile.note = True
            user.profile.photo_de_profile = 'media.png'
            user.profile.banniere = 'banniere_default.JPG'
            user.save()

            current_site = get_current_site(request)
            email_subject = "Lien d'activation de votre compte entreprise"
            message = render_to_string('activate_account.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(email_subject, message, to=[to_email])
            email.send()
            return render(request, 'email_sent.html')

        else:
            messages.error(request, "Veuillez verifier votre fomulaire")
    else:
        form = SignUpForm_entreprise()
    return render(request, 'register.html', {'form': form})


def activate_account(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'success_activation.html')
    else:
        return HttpResponse('Activation link is invalid!')

################################################################################################
@login_required
@transaction.atomic
@csrf_protect
def update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, request.FILES, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, ('Votre profile a été mit a jour avec succées'))
            return redirect('omniparc:update-profile')
        else:
            messages.error(request, 'Please correct the error below')

    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'backadminpanel/pages-profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

###################################################################################
@login_required
@transaction.atomic
@csrf_protect
def update_profile_gen(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, request.FILES, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, ('Votre profile a été mit a jour avec succées'))
            return redirect('omniparc:monprofile')
        else:
            messages.error(request, 'Please correct the error below')

    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'profile_particulier.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

###################################################################################
class UpdateItem(UpdateView):
    model = Item
    form_class = ItemUpdate
    #fields = '__all__'
    template_name = 'backadminpanel/item_update_form.html'
    success_url = '/List-Article'

###################################################################################
@login_required(login_url='/accounts/login')
def entreprise_list(request):
    list = Profile.objects.filter(note=True)
    context = {
        'list': list
    }
    return render(request, 'list_des_entreprises.html', context)


###################################################################################
@login_required(login_url='/accounts/login')
def ProfileItem(request):
    return render(request, 'item_profile_list.html')
####################################################################################

def contactView(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            message = from_email + ' à envoyer un email avec le message suivant: \n' + message
            try:
                send_mail(subject, message, from_email, ['django.send2020@gmail.com'])

            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('omniparc:success')
    return render(request, "email.html", {'form': form})

def successView(request):
    messages.success(request,'Votre émail a été bien envoyé.')
    return redirect('omniparc:home')

######################################################################################

def search(request):
    nom = request.GET.get('q1')
    localite = request.GET.get('q')

    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')

    dd = datetime.datetime.strptime(date_min, "%Y-%m-%d").date()
    df = datetime.datetime.strptime(date_max, "%Y-%m-%d").date()

    ddj = dd.day
    ddm = dd.month
    ddy = dd.year

    dfj = df.day
    dfm = df.month
    dfy = df.year

    if ddj < dfj and ddm == dfm and ddy == dfy:
        item_d = Item.objects.filter(Q(date_debut=dd, date_fin=df))
        other_result = Item.objects.filter(Q(date_debut__day__range=[ddj, dfm]) and Q(date_debut__day__lte=dfj, date_fin__month__gte=dfm) and Q(date_fin__gt=dd))
        context = {
            'filter': item_d,
            'other': other_result
        }
        return render(request, 'recherche.html', context)

    if dd < df and ddm < dfm and ddy == dfy:
        item_d = Item.objects.filter(Q(date_debut=dd, date_fin=df))
        other_result = Item.objects.filter(Q(date_debut__month=ddm, date_fin__gt=dd) or Q(date_fin__month=dfm) or Q(date_debut__month=ddm, date_fin__gte=df))
        context = {
            'filter': item_d,
            'other': other_result
        }
        return render(request, 'recherche.html', context)

    elif dd > df:
        messages.warning(request,'La date de fin de location ne peux étre inférieure à celle du début de location')
        return redirect('omniparc:home')

######################################################################################
def list_commande(request):
    commande = OrderItem.objects.filter(item__user=request.user)
    print(commande)
    context = {
        'commande': commande
    }
    return render(request, 'backadminpanel/liste_commande.html', context)

######################################################################################

class Detailcommande(DetailView):
    model = OrderItem
    template_name = 'backadminpanel/detail_commande.html'
######################################################################################
@login_required(login_url='/accounts/login')
def DemandeDevis(request, slug):
    item = get_object_or_404(Item, slug=slug)
    context = {
        'model': item,
    }
    return render(request, 'demande_devis.html', context)

######################################################################################
@transaction.atomic
@login_required(login_url='/accounts/login')
def Devis(request, slug):
    item = get_object_or_404(Item, slug=slug)
    if request.method == 'POST':
        forme = DevisForm(request.POST)
        if forme.is_valid():
            duree_location = forme.cleaned_data['duree_location']
            adresse_livraison = forme.cleaned_data['adresse_livraison']
            avec_operateur = forme.cleaned_data.get('avec_operateur')
            reprise_livraison = forme.cleaned_data.get('reprise_livraison')
            devis_date_debut = forme.cleaned_data.get('devis_date_debut')
            devis_date_fin = forme.cleaned_data.get('devis_date_fin')

            if reprise_livraison == True and avec_operateur == True:
                reprise_livraison = "Avec livraison et reprise"
                avec_operateur = "Avec opérateur"
                tot = item.prix_avec_livraison_reprise + item.prix_avec_operateur

            elif reprise_livraison == True and avec_operateur == False:
                reprise_livraison = "Sans livraison et reprise"
                avec_operateur = "Sans opérateur"
                tot = item.prix_avec_livraison_reprise

            elif reprise_livraison == False and avec_operateur == True:
                reprise_livraison = "Sans livraison et reprise"
                avec_operateur = "Avec opérateur"
                tot = item.prix_avec_operateur

            elif reprise_livraison == False and avec_operateur == False:
                reprise_livraison = "Sans livraison et reprise"
                avec_operateur = "Sans opérateur"
                tot = 0

            if item.mode_location == 'PJ':
                mode_location = 'Jour'
            else:
                mode_location = 'Heure'
            ship = ShippingAddress(
                user= request.user,
                street_address=adresse_livraison,
            )

            ship.save()
            devis = DevisItem(
                user = request.user,
                item=item,
                prix_unitaire = item.price,
                dure_location = duree_location,
                montant_location = (tot + item.price) * duree_location,
                mode_location = mode_location,
                avec_operateur = avec_operateur,
                reprise_livraison = reprise_livraison,
                adreese_chantier = ship,

                entreprise_emetrice = item.user.profile.organisation,
                gerant_emeteur = item.user.last_name,
                user_owner = item.user,
                tel_emeteur = item.user.profile.phone_number,
                email_emeteur = item.user.email,
                adresse_emeteur = item.user.profile.adresse,

                entreprise_reception = request.user.profile.organisation,
                gerant_reception = request.user.last_name,
                tel_reception = request.user.profile.phone_number,
                email_reception = request.user.email,

                montant_service_adi=tot,

                devis_date_debut= devis_date_debut,
                devis_date_fin = devis_date_fin,

                etat_devis='En attente de traitement'
            )
            devis.save()
            messages.success(request,'Votre devis a été générer avec success, veuillez verifier la dérniere ligne du tableau')
            return HttpResponseRedirect(reverse('omniparc:list'))


        else:
            return HttpResponse('erreur dans le formulaire')
    else:

        return redirect('omniparc:home')
######################################################################################
@login_required(login_url='/accounts/login')
def return_devis_user(request):
    list = DevisItem.objects.filter(user=request.user)
    context = {
        'list' : list,
    }
    return render(request, 'liste_des_devis.html', context)

######################################################################################
class ViewDevis(DetailView):
    model = DevisItem
    template_name = 'devis.html'


#######################################################################################
@login_required(login_url='/accounts/login')
def delete_devis(request, slug):
    devis = get_object_or_404(DevisItem, slug=slug)
    devis.delete()
    messages.success(request, 'Le devis a bien été supprimer')
    return redirect('omniparc:list')
#######################################################################################
@login_required(login_url='/accounts/login')
def update_commande(request,slug):
    devis = get_object_or_404(DevisItem, slug=slug)
    form = Update_commande(request.POST or None, instance=devis)
    context = {
        'form': form,
        'devis': devis
    }
    if form.is_valid():
        devis = form.save(commit=False)
        f = form.cleaned_data['prix_unitaire']
        d = form.cleaned_data['dure_location']
        devis.montant_location = (int(f) + devis.montant_service_adi) * int(d)
        devis.save()

        messages.success(request,'Le devis à bien été modifier')
        return redirect('omniparc:lis_des_devis')
    else:
        return render(request, 'backadminpanel/update_devis.html', context)

#######################################################################################

@login_required(login_url='/accounts/login')
def lis_des_devis(request):
    devis = DevisItem.objects.filter(user_owner=request.user)
    context = {
        'devis': devis
    }
    return render(request, 'backadminpanel/liste_de_mes_devis.html', context)
#######################################################################################
@transaction.atomic
def detail_annonce(request, slug):
    ann = get_object_or_404(Annonce, slug=slug)
    item = Item.objects.filter(disponible=True, user=request.user)
    form = RespondeAnnonce()
    if request.method == 'POST':
        forme = RespondeAnnonce(request.POST)
        if forme.is_valid():
            name = forme.cleaned_data['v']
            art = Item.objects.get(slug=name)
            reponse = forme.save(commit=False)
            reponse.auteur = request.user
            reponse.ann = ann
            reponse.item = art
            reponse.slug_annonce = slug
            reponse.save()

            email_subject = "Informations liée a votre annonce de recherche d'engin"
            message = render_to_string('text_email.html')
            to_email = ann.user.email
            email = EmailMessage(email_subject, message, to=[to_email])
            email.send()

            messages.success(request,'votre porposition a été transmise avec succées')
            return redirect('omniparc:home')
        else:
            messages.warning(request,'Il y a une erreur dans votre formulaire')
            form = RespondeAnnonce()

    context = {
        'ann' : ann,
        'form' : form,
        'item' : item,
    }
    return render(request, 'detail_annonce.html', context)

##########################################################################################

def view_annonce(request):
    annonce_last = Annonce.objects.order_by('-created_date')[:3]
    annonce_all = Annonce.objects.all()
    context = {
        'annonce_last' : annonce_last,
        'annonce_all' : annonce_all
    }
    return render(request, 'view_annonce.html', context)


def create_annonce(request):
    form = AnnonceForm()
    if request.method == 'POST':
        forme = AnnonceForm(request.POST)
        if forme.is_valid():
            annonce = forme.save(commit=False)
            annonce.user = request.user
            annonce.save()
            messages.success(request,'Votre annonce à été publier avec succées')
            return redirect('omniparc:home')
        else:
            form = AnnonceForm()
    context = {
        'form': form
    }
    return render(request, 'annonce_creation.html', context)

###########################################################################
def view_annonce_responde_particulier(request):
    annonce = Annonce.objects.filter(user=request.user).order_by('-created_date')[:100]
    context = {
        'annonce' : annonce,

    }
    return render(request,'view_annonce_responde_particulier.html', context)

#############################################################################
def view_responde(request,slug):
    annonce=get_object_or_404(Annonce, slug=slug)
    responde= Annonce_responde.objects.filter(slug_annonce=slug)

    context = {
        'annonce' : annonce,
        'responde' : responde,
    }
    return render(request,'voir_responde_annonce.html', context)


###########################################################################

def how_it_works(request):
    return render(request, 'how_it_works.html')

def charte(request):
    return render(request, 'charte_utilisation.html')

def catalogue_machine(request):
    return render(request, 'catalogue_machine.html')

def about_us(request):
    return render(request, 'about_us.html')

def faq(request):
    return render(request, 'about_us.html')

def View_ets_profile(request, slug):
    profile = get_object_or_404(Profile , slug=slug)
    i = OrderItem.objects.filter(item__user__profile__nif=slug)
    item = Item.objects.filter(user__profile=profile)

    context= {
        'object': profile,
        'i' : i,
        'item' : item,
    }
    return render(request, 'profile_view_entreprise.html', context)



#############################################################################
def filter_camion_nacelle_pi(request):
    result = Item.objects.filter(label='CNP')
    cat = "Travaux en hauteur"
    lab = "Camion nacelle PL"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)

def filter_camion_nacelle_vi(request):
    result = Item.objects.filter(label='CNV')
    cat = "Travaux en hauteur"
    lab = "Camion nacelle VL"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)

def filter_er(request):
    result = Item.objects.filter(label='ER')
    cat = "Travaux en hauteur"
    lab = "Echaffaudage roulant"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)

def filter_na(request):
    result = Item.objects.filter(label='NA')
    cat = "Travaux en hauteur"
    lab = "Nacelle araignée"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)

def filter_nar(request):
    result = Item.objects.filter(label='NAR')
    cat = "Travaux en hauteur"
    lab = "Nacelle Articulé"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)

def filter_nc(request):
    result = Item.objects.filter(label='NC')
    cat = "Travaux en hauteur"
    lab = "Nacelle ciseaux"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)

def filter_nt(request):
    result = Item.objects.filter(label='NT')
    cat = "Travaux en hauteur"
    lab = "Nacelle Télescopique"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)

def filter_ntc(request):
    result = Item.objects.filter(label='NTC')
    cat = "Travaux en hauteur"
    lab = "Nacelle Toucon"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)

def filter_nel(request):
    result = Item.objects.filter(label='NEL')
    cat = "Travaux en hauteur"
    lab = "Nacelle Elavatrice"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)


def filter_b(request):
    result = Item.objects.filter(label='B')
    cat = "Terassement & Extraction"
    lab = "Buldozer"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)

def filter_c(request):
    result = Item.objects.filter(label='C')
    cat = "Terassement & Extraction"
    lab = "Chargeuse"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)

def filter_mc(request):
    result = Item.objects.filter(label='MC')
    cat = "Terassement & Extraction"
    lab = "Mini Chargeuse"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)

def filter_mp(request):
    result = Item.objects.filter(label='MP')
    cat = "Terassement & Extraction"
    lab = "Mini Pelle"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)

def filter_p(request):
    result = Item.objects.filter(label='P')
    cat = "Terassement & Extraction"
    lab = "Pelleteuse"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)


#################################################################################
def filter_ch(request):
    result = Item.objects.filter(label='CH')
    cat = " Levage & Manutention"
    lab = "Chariot Elevateur"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)

def filter_ct(request):
    result = Item.objects.filter(label='CT')
    cat = " Levage & Manutention"
    lab = "Chariot Télescopique"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)

def filter_gt(request):
    result = Item.objects.filter(label='GT')
    cat = " Levage & Manutention"
    lab = "Gerbeur & Transpalette"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)


def filter_gmv(request):
    result = Item.objects.filter(label='GMV')
    cat = " Levage & Manutention"
    lab = "Glas lift : Monte Vitre"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)

def filter_g(request):
    result = Item.objects.filter(label='G')
    cat = " Levage & Manutention"
    lab = "Grue Mobile"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)

def filter_gsr(request):
    result = Item.objects.filter(label='GSR')
    cat = " Levage & Manutention"
    lab = "Grue sur remorque"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)

def filter_mga(request):
    result = Item.objects.filter(label='MGA')
    cat = " Levage & Manutention"
    lab = "Mini Grue Araigné"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)

def filter_mgb(request):
    result = Item.objects.filter(label='MGB')
    cat = " Levage & Manutention"
    lab = "Mini Grue Araigné"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)

def filter_mca(request):
    result = Item.objects.filter(label='MCA')
    cat = " Levage & Manutention"
    lab = "Monte Charge"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)

def filter_be(request):
    result = Item.objects.filter(label='BE')
    cat = " Chargement & transport "
    lab = "Benne"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)

def filter_cb(request):
    result = Item.objects.filter(label='CB')
    cat = " Chargement & transport "
    lab = "Camion Benne"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)

def filter_cbg(request):
    result = Item.objects.filter(label='CBG')
    cat = " Chargement & transport "
    lab = "Camion Bras de grue"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)

def filter_tom(request):
    result = Item.objects.filter(label='TOM')
    cat = " Chargement & transport "
    lab = "Tombereau"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)

def filter_rb(request):
    result = Item.objects.filter(label='RB')
    cat = "Gros oeuvre & démolition "
    lab = "Robot de démolition"

    context = {
        'result': result,
        'cat': cat,
        'lab': lab
    }
    return render(request,'result_filtrage.html', context)







