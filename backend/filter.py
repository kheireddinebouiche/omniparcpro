from django.db.models import Q

from .models import Item
import django_filters

DAYS_OF_WEEK = (
    ('DIM', 'Dimanche'),
    ('LUN', 'Lundi'),
    ('MAR', 'Mardi'),
    ('MER', 'Mercredi'),
    ('JEU', 'Jeudi'),
    ('VEN', 'Vendredi'),
    ('SAM', 'Samedi'),
)

CATEGORY_CHOICES = (
    ('TH', 'Travaux en hauteur'),
    ('TE', 'Terrassement & Extraction'),
    ('LM', 'Levage & Manutention'),
    ('CT', 'Chargement & Transport'),
    ('GD', 'Gros Oeuvre & Démolition'),
)

class MultiValueCharFilter(django_filters.filters.Filter):
    def __init__(self, *args, **kwargs):
        self.method_multivalue = kwargs.pop('method_multivalue')
        super(MultiValueCharFilter, self).__init__(*args, **kwargs)
    def filter(self, qs, value):
        q = Q()
        for v in value.split('|'):
            q = q | Q(**{self.method_multivalue: v})
        return qs.filter(q)




class ItemFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label="Titre contenant...")
    price = django_filters.NumberFilter(label="Selon le prix...")
    price__lt = django_filters.NumberFilter(field_name='price', lookup_expr='lt', label="Supérieur à")
    disp = django_filters.CharFilter(field_name='disp')
    category = django_filters.ChoiceFilter(field_name="category", lookup_expr='contains')
    localisation_engin = django_filters.CharFilter(field_name="localisation_engin", lookup_expr='contains')


    class Meta:
        model=Item
        fields=['title', 'price', 'disp', 'category', 'localisation_engin']

    def filter_disp(self, queryset, name, disp):
        return queryset.filter(disp__icontains=disp.split(','))
