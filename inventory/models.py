from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from decimal import Decimal

# Create your models here.
class Part(models.Model):
    name = models.CharField(max_length=250,help_text = "250 characters max.")
    quantity = models.PositiveIntegerField(help_text="This is the number of parts currently in stock (but not allocated to any jobs).")
    unit_price = models.DecimalField(max_digits=11,decimal_places=2,verbose_name="Unit Price ($)",help_text="This can be overridden when adding a part to a job.",validators=[MinValueValidator(Decimal('0.00'))])
    ignore = models.BooleanField(default=False,blank=True,verbose_name="Ignore Empty Stock?",help_text="Check this if you want this part to be exempted from the zero-quantity notification.")

    def __str__(self):
        return self.name

class Job(models.Model):
    STATUS_CHOICES = [
        ("NS","Not Started"),
        ("IP","In Progress"),
        ("C","Complete")
    ]
    phone_regex = RegexValidator(regex=r'^\d{10}$', message="Invalid phone number.")
    customer_name = models.CharField(max_length=75,verbose_name="Customer Name")
    customer_phone = models.CharField(validators=[phone_regex],max_length=10,blank=True,help_text="No dashes, parentheses, or country code.",verbose_name="Customer Phone")
    customer_email = models.EmailField(blank=True,verbose_name="Customer Email")
    vehicle = models.CharField(max_length=250,blank=True,help_text="What's being repaired?")
    status = models.CharField(max_length=2,choices=STATUS_CHOICES,default="NS")
    notes = models.CharField(max_length=1000,blank=True,help_text="Enter any repair notes here.")
    created = models.DateTimeField(auto_now_add=True,verbose_name="Date/Time Created")

    def __str__(self):
        v_str = self.vehicle if self.vehicle else "N/A"
        return " - ".join([self.customer_name, v_str])

class JobPart(models.Model):
    job = models.ForeignKey(Job,on_delete=models.CASCADE)
    part = models.ForeignKey(Part,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(help_text="How many instances of this part do you want to apply to this job?")
    unit_price = models.DecimalField(max_digits=11,decimal_places=2,verbose_name="Unit Price ($)",validators=[MinValueValidator(Decimal('0.00'))])

class Service(models.Model):
    job = models.ForeignKey(Job,on_delete=models.CASCADE)
    description = models.CharField(max_length=250,verbose_name="Description")
    price = models.DecimalField(max_digits=11,decimal_places=2,verbose_name="Service Price ($)",validators=[MinValueValidator(Decimal('0.00'))])