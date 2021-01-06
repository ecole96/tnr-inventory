from decimal import Decimal
from .models import Service, JobPart
from django.db.models import Sum

# used to calculate pricing data for Job Details page and invoices
def calculate_prices(job,invoice=False):
    prices = {}
    tax_rate = Decimal('0.06') # Kentucky tax rate

    services = Service.objects.filter(job=job)
    prices['labor_price'] = services.aggregate(Sum('price'))['price__sum'] or Decimal('0.00') # total labor price

    parts = JobPart.objects.filter(job=job)
    prices['parts_price'] = sum([j.quantity * j.unit_price for j in parts]) or Decimal('0.00') # total part price

    taxed_services = Service.objects.filter(job=job,tax=True)
    service_taxes = taxed_services.aggregate(Sum('price'))['price__sum'] or Decimal('0.00') # total of taxed services
    part_taxes = sum([j.quantity * j.unit_price for j in JobPart.objects.filter(job=job,tax=True)]) or Decimal('0.00') # total of taxed parts
    prices['tax'] = round(sum([service_taxes,part_taxes]) * tax_rate,2) # calculate final tax

    if invoice: # calculating for invoice - more itemizing necessary
        jobparts = JobPart.objects.filter(job=job)
        services = Service.objects.filter(job=job)
        prices['labor'] = []
        for s in services:
            service_dict = {'desc':s.description, 'price':s.price}
            prices['labor'].append(service_dict) # appending detailed service pricing
        prices['parts'] = []
        for jp in jobparts:
            part_dict = {'name':jp.part.name,'unit_price':jp.unit_price,'quantity':jp.quantity, 'total':jp.unit_price * Decimal(jp.quantity)}
            prices['parts'].append(part_dict) # appending detailed parts pricing
        prices['subtotal'] = prices['labor_price'] + prices['parts_price']
        
    prices['total'] = sum([prices['labor_price'],prices['parts_price'],prices['tax']])
    return prices