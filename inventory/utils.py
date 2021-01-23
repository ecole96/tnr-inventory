from decimal import Decimal
from .models import Service, JobPart, JobPart_SingleUse
from django.db.models import Sum

# used to calculate pricing data for Job Details page and invoices
def calculate_prices(job,invoice=False):
    prices = {}
    tax_rate = Decimal('0.06') # Kentucky tax rate

    services = Service.objects.filter(job=job)
    prices['labor_price'] = services.aggregate(Sum('price'))['price__sum'] or Decimal('0.00') # total labor price

    inventory_parts = JobPart.objects.filter(job=job)
    singleuse_parts = JobPart_SingleUse.objects.filter(job=job)
    inventory_parts_price = sum([j.quantity * j.unit_price for j in inventory_parts]) or Decimal('0.00') # total price of parts from inventory
    singleuse_parts_price = sum([j.quantity * j.unit_price for j in singleuse_parts]) or Decimal('0.00') # total of single-use parts
    prices['parts_price'] = sum([inventory_parts_price,singleuse_parts_price])

    taxed_services = Service.objects.filter(job=job,tax=True)
    service_taxes = taxed_services.aggregate(Sum('price'))['price__sum'] or Decimal('0.00') # total of taxed services
    inventory_part_taxes = sum([j.quantity * j.unit_price for j in JobPart.objects.filter(job=job,tax=True)]) or Decimal('0.00') # total of taxed parts from inventory
    singleuse_part_taxes = sum([j.quantity * j.unit_price for j in JobPart_SingleUse.objects.filter(job=job,tax=True)]) or Decimal('0.00') # total of taxed single-use parts
    prices['tax'] = round(sum([service_taxes,inventory_part_taxes,singleuse_part_taxes]) * tax_rate,2) # calculate final tax

    if invoice: # calculating for invoice - more itemizing necessary
        services = Service.objects.filter(job=job)
        prices['labor'] = []
        for s in services:
            service_dict = {'desc':s.description, 'price':s.price}
            prices['labor'].append(service_dict) # appending detailed service pricing
        prices['parts'] = []
        for ip in inventory_parts:
            part_dict = {'name':ip.part.name,'unit_price':ip.unit_price,'quantity':ip.quantity, 'total':ip.unit_price * Decimal(ip.quantity)}
            prices['parts'].append(part_dict) # appending detailed parts pricing
        for sp in singleuse_parts:
            part_dict = {'name':sp.name,'unit_price':sp.unit_price,'quantity':sp.quantity, 'total':sp.unit_price * Decimal(sp.quantity)}
            prices['parts'].append(part_dict) # appending detailed parts pricing
        prices['subtotal'] = prices['labor_price'] + prices['parts_price']

    prices['total'] = sum([prices['labor_price'],prices['parts_price'],prices['tax']])
    return prices