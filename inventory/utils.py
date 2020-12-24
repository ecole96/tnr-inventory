from decimal import Decimal
from .models import Service, JobPart
from django.db.models import Sum

def calculate_prices(job,invoice=False):
    prices = {}
    tax_rate = Decimal('0.06')

    prices['labor_price'] = Service.objects.filter(job=job).aggregate(Sum('price'))['price__sum'] if Service.objects.filter(job=job).count() > 0 else Decimal('0.00')
    prices['parts_price'] = sum([Decimal(j.quantity) * j.unit_price for j in JobPart.objects.filter(job=job)]) if JobPart.objects.filter(job=job).count() > 0 else Decimal('0.00')
    prices['tax'] = round(sum([prices['labor_price'],prices['parts_price']]) * tax_rate,2)
    if invoice:
        jobparts = JobPart.objects.filter(job=job)
        services = Service.objects.filter(job=job)
        prices['labor'] = []
        for s in services:
            service_dict = {'desc':s.description, 'price':s.price}
            prices['labor'].append(service_dict)
        prices['parts'] = []
        for jp in jobparts:
            part_dict = {'name':jp.part.name,'unit_price':jp.unit_price,'quantity':jp.quantity, 'total':jp.unit_price * Decimal(jp.quantity)}
            prices['parts'].append(part_dict)
        prices['subtotal'] = prices['labor_price'] + prices['parts_price']
    prices['total'] = sum([prices['labor_price'],prices['parts_price'],prices['tax']])
    return prices