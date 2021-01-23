from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from decimal import Decimal

# represents parts in the inventory (can be added to jobs as a JobPart)
class Part(models.Model):
    name = models.CharField(max_length=250,help_text = "250 characters max.")
    quantity = models.PositiveIntegerField(help_text="This is the number of parts currently in stock (but not allocated to any jobs).")
    unit_price = models.DecimalField(max_digits=11,decimal_places=2,verbose_name="Unit Price ($)",help_text="This can be overridden when adding a part to a job.",validators=[MinValueValidator(Decimal('0.00'))])
    archived = models.BooleanField(default=False,blank=True,verbose_name="Archive?",help_text="Check this to ignore any zero-quantities of this part, and to disable any further attachments to jobs (it will not affect jobs with the part already attached).")

    def __str__(self):
        return self.name

# self-explanatory - represents repair jobs. Customer data is rolled in with individual Jobs, as normalizing with a Customers table would be overkill for current purposes
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
    status = models.CharField(max_length=2,choices=STATUS_CHOICES,default="NS") # current state of repair progress
    notes = models.CharField(max_length=1000,blank=True,help_text="Enter any repair notes here.") # these will appear on the invoice
    created = models.DateTimeField(auto_now_add=True,verbose_name="Date/Time Created")

    def __str__(self): # String representation is in "Customer - Vehicle" format
        v_str = self.vehicle if self.vehicle else "N/A"
        return "#%s / %s" % (self.pk, " - ".join([self.customer_name, v_str]))

# represents a Part being attached to a Job (what part, how many, and how much to charge per part)
class JobPart(models.Model):
    job = models.ForeignKey(Job,on_delete=models.CASCADE)
    part = models.ForeignKey(Part,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(help_text="How many instances of this part do you want to apply to this job?")
    unit_price = models.DecimalField(max_digits=11,decimal_places=2,verbose_name="Unit Price ($)",validators=[MinValueValidator(Decimal('0.00'))]) # default is selected part's unit price, but can be overridden via form
    tax = models.BooleanField(default=True,blank=True,verbose_name="Tax?",help_text="Check this to charge tax for all quantities of this part (for this job).") # can decide whether to charge tax or not

# like JobPart, but doesn't interact with the inventory - for adding parts not regularly kept in stock to a job. 
# Usually only needed for single jobs - keeps inventory from being filled with unnecessary parts; user can just directly create the part when adding to job
class JobPart_SingleUse(models.Model):
    job = models.ForeignKey(Job,on_delete=models.CASCADE)
    name = models.CharField(max_length=250,help_text = "250 characters max.",verbose_name="Part")
    quantity = models.PositiveIntegerField(help_text="How many instances of this part do you want to apply to this job?")
    unit_price = models.DecimalField(max_digits=11,decimal_places=2,verbose_name="Unit Price ($)",validators=[MinValueValidator(Decimal('0.00'))]) # default is selected part's unit price, but can be overridden via form
    tax = models.BooleanField(default=True,blank=True,verbose_name="Tax?",help_text="Check this to charge tax for all quantities of this part (for this job).") # can decide whether to charge tax or not

# represents services performed for Jobs (description of service and how much to charge for it)
class Service(models.Model):
    job = models.ForeignKey(Job,on_delete=models.CASCADE)
    description = models.CharField(max_length=250,verbose_name="Description")
    price = models.DecimalField(max_digits=11,decimal_places=2,verbose_name="Service Price ($)",validators=[MinValueValidator(Decimal('0.00'))])
    tax = models.BooleanField(default=False,blank=True,verbose_name="Tax?",help_text="Check this to charge tax on this service.")