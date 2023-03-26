from django.urls import path,include

from .views import *

app_name = 'omniparc'

urlpatterns = [

    path('', HomeView.as_view(), name='home'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('products/<slug>/', ItemDetailView.as_view(), name='products'),
    path('products/signale/<slug>/', Signale_Item, name="signale_items"),
    path('products/detail_commande/<slug>', details_commande , name='detail_commande'),
    path('products/Demande-Devis/<slug>', DemandeDevis, name='Demande-devis'),
    path('products/Demande-Devis/Devis/<slug>', Devis, name='devis'),
    path('add_to_cart/<slug>/', add_to_cart, name="add_to_cart"),
    path('remove_from_cart/<slug>/', remove_from_cart, name="remove_from_cart"),
    path('remove_single_item_from_cart/<slug>/', remove_single_item_from_cart, name="remove_single_item_from_cart"),
    path('order_summery', OrderSummeryView.as_view(), name="order_summery"),
    path('payement/<payement_option>/', PayementOption.as_view(), name="payment"),
    path('Administrations/add-item/', Add_Item.as_view(), name="add-item"),
    path('Administration/', Administration, name="Administration"),
    path('Profile-admin/', Profile_admin.as_view(), name="Profile_admin"),
    path('List-Article/', ListArticle, name="List-article"),
    path('Administration/update-profile/', update_profile, name="update-profile"),
    path('plan-choice/', PlanChoice, name="plan-choice"),
    path('Item-Detail-Administration/<slug>/', ItemDetailAdministration.as_view(), name="Item-Detail-Administration"),
    path('update-item/<slug>', UpdateItem.as_view(), name="update-item"),
    path('liste_entreprises', entreprise_list, name="entreprise-list"),
    path('item-profile-list/', ProfileItem, name="item-profile-list"),
    path('register-entreprise/', RegisterEntreprise, name="register-entreprise"),
    path('register-particulier/', RegisterParticulier, name="register-particulier"),
    path('register-offre/', RegisterEntreprise_offre, name="register-offre"),
    path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$' ,activate_account, name='activate'),
    path('contact/', contactView, name='contact'),
    path('success/', successView, name='success'),
    path('search/', search, name='search'),
    path('mes-commandes/', Commande.as_view(), name='commandes'),
    path('Administration/liste-commandes/', list_commande, name='list-commande'),
    path('Administration/liste-commandes/detail-commande/<slug>/', Detailcommande.as_view(), name='detail-commande'),
    path('liste_de_mes_devis/', return_devis_user, name='list'),
    path('Devis/<slug>/', ViewDevis.as_view(), name='Devis'),
    path('delete_devis/<slug>/', delete_devis, name='delete_devis'),
    path('update_commande/<slug>/', update_commande, name='update_commande'),
    path('lis_des_devis/', lis_des_devis, name='lis_des_devis'),
    path('depot-annonce/', create_annonce, name='depot-annonce'),
    path('annonces/', view_annonce, name="annonce"),
    path('annonces/details_de/<slug>', detail_annonce, name="details_de"),
    path('comment_ca_marche/', how_it_works, name="how_it_works"),
    path('charte/', charte, name="charte"),
    path('catalogue/',catalogue_machine,name='catalogue'),
    path('mon_profile/',update_profile_gen,name='monprofile'),
    path('mes_annonces/',view_annonce_responde_particulier,name='mes_annonces'),
    path('mes_annonces/annonces_responses/<slug>',view_responde,name='annonce_responses'),
    path('annonces/details-reponse/<int:pk>/', details_responde, name="details_reponse"),
    path('annonces/update_annonce/<slug>/', update_annonce, name="update_annonce"),
    path('annonces/delete-annonce/<slug>/', delete_annonce, name="delete_annonce"),
    path('view-count/', ViewCount, name="view-count"),
    path('reenitialiser-vue/<slug>/', ZeroVueItem, name="zero-vue"),

    path('filter_camion_nacelle_pi/',filter_camion_nacelle_pi,name='filter_camion_nacelle_pi'),
    path('filter_camion_nacelle_vi/',filter_camion_nacelle_vi,name='filter_camion_nacelle_vi'),
    path('filter_er/',filter_er,name='filter_er'),
    path('filter_na/',filter_na,name='filter_na'),
    path('filter_nar/',filter_nar,name='filter_nar'),
    path('filter_nc/',filter_nc,name='filter_nc'),
    path('filter_nt/',filter_nt,name='filter_nt'),
    path('filter_ntc/',filter_ntc,name='filter_ntc'),
    path('filter_nel/',filter_nel,name='filter_nel'),

    path('filter_b/',filter_b,name='filter_b'),
    path('filter_c/',filter_c,name='filter_c'),
    path('filter_mc/',filter_mc,name='filter_mc'),
    path('filter_mp/',filter_mp,name='filter_mp'),
    path('filter_p/',filter_p,name='filter_p'),

    path('filter_ch/',filter_ch,name='filter_ch'),
    path('filter_ct/',filter_ct,name='filter_ct'),
    path('filter_gt/',filter_gt,name='filter_gt'),
    path('filter_gmv/',filter_gmv,name='filter_gmv'),
    path('filter_g/',filter_g,name='filter_g'),
    path('filter_gsr/',filter_gsr,name='filter_gsr'),
    path('filter_mga/',filter_mga,name='filter_mga'),
    path('filter_mgb/',filter_mgb,name='filter_mgb'),
    path('filter_mca/',filter_mca,name='filter_mca'),


    path('filter_be/',filter_be,name='filter_be'),
    path('filter_cb/',filter_cb,name='filter_cb'),
    path('filter_cbg/',filter_cbg,name='filter_cbg'),
    path('filter_tom/',filter_tom,name='filter_tom'),

    path('filter_rb/',filter_rb,name='filter_rb'),



    path('faq?/',faq,name='faq'),
    path('about_us/',about_us,name='about_us'),
    path('conditions-generals-d-utilisation/', cgu, name="cgu"),
    path('conditions-general-de-vente/',cgv , name="cgv"),
    path('liste_entreprises/entreprise_details/<slug>/',View_ets_profile,name='entreprise_details'),
    path('Search/',search,name='Search'),
    path('confirm_devis_add_cart/<slug>/',confirm_devis_add_cart,name='confirm_devis_add_cart'),











]

