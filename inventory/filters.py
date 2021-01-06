import django_filters as filters
from .models import Part, Job
from django import forms

# search filters on Parts page
class PartFilter(filters.FilterSet):
    name = filters.CharFilter(label="Name",lookup_expr='icontains')
    quantity_lte = filters.NumberFilter(field_name='quantity',label="Quantity (Max)",lookup_expr='lte')
    quantity_gte = filters.NumberFilter(field_name='quantity',label="Quantity (Min)",lookup_expr='gte')
    unit_price_lte = filters.NumberFilter(field_name='unit_price',label="Unit Price (Max)",lookup_expr='lte')
    unit_price_gte = filters.NumberFilter(field_name='unit_price',label="Unit Price (Min)",lookup_expr='gte')

    class Meta:
        model = Part
        fields = ['name','id','quantity']

# search filters on Jobs page
class JobFilter(filters.FilterSet):
    STATUS_CHOICES = [
        ("NS","Not Started"),
        ("IP","In Progress"),
        ("C","Complete")
    ]

    customer_name = filters.CharFilter(label="Customer",lookup_expr='icontains')
    vehicle = filters.CharFilter(label="Vehicle",lookup_expr='icontains')
    status = filters.ChoiceFilter(choices=STATUS_CHOICES)
    created = filters.DateFromToRangeFilter(label="Date Created")

    class Meta:
        model = Job
        fields = ['id','customer_name','created','vehicle','status']  