from django import forms
from .models import Part, Job, Service, JobPart
from bootstrap_modal_forms.forms import BSModalModelForm
from django.core.exceptions import ValidationError

# for creating / managing a Part
class PartForm(BSModalModelForm):
    class Meta:
        model = Part
        fields = ('name','quantity','unit_price','ignore')
        widgets = {
            'name': forms.TextInput(attrs={'size':50})
        }

# for creating / managing a Job
class JobForm(BSModalModelForm):
    class Meta:
        model = Job
        exclude = ('created',)
        widgets = {
            'notes': forms.Textarea(attrs={"rows":5, "cols":10})
        }

# for creating / managing a Service
class ServiceForm(BSModalModelForm):
    class Meta:
        model = Service
        fields = ('description','price','tax')

# for attaching a Part to a Job
class JobPartForm(BSModalModelForm):
    QUANTITY_CHOICES = [(i,i) for i in range(1,1000)] # placeholder initial values for quantity selection (overridden with actual quantities upon part selection via JS)
    quantity = forms.ChoiceField(choices=QUANTITY_CHOICES)
    part = forms.ModelChoiceField(queryset=Part.objects.filter(quantity__gt=0).order_by('name')) # only selectable parts have stock in inventory

    class Meta:
        model = JobPart
        fields = ('part','quantity','unit_price','tax')
    
    def clean_quantity(self):
        part = self.cleaned_data.get("part")
        quantity = int(self.cleaned_data.get("quantity"))
        in_inventory = part.quantity
        if quantity > in_inventory: # check that jobpart quantity doesn't exceed stock
            error_msg = 'Quantity must be less than or equal to ' + str(in_inventory) + "."
            raise ValidationError(error_msg)
        return quantity

# for editing a JobPart
class JobPartEditForm(BSModalModelForm):
    QUANTITY_CHOICES = [(0,0)]
    quantity = forms.ChoiceField(choices=QUANTITY_CHOICES)

    def __init__(self,*args,**kwargs):
        super(JobPartEditForm,self).__init__(*args,**kwargs) # populates the post
        part = Part.objects.filter(pk=self.instance.part.pk)
        self.fields['part'].queryset = part
        self.fields['part'].disabled = True # part selection disabled for editing
        quantity = [(i,i) for i in range(1,part.first().quantity + self.instance.quantity + 1)] # only allowable quantities range from quantity already established to the remaining quantity in inventory
        self.fields['quantity'].choices = quantity

    class Meta:
        model = JobPart
        fields = ('part','quantity','unit_price','tax')

    def clean_part(self):
        return Part.objects.get(pk=self.initial["part"]) # part can't be changed, will always default to inital value (the initially selected part)

# this form provides users with a choice to return any deleted JobParts to the inventory
class ReturnPartForm(forms.Form):
    return_parts = forms.BooleanField(required=False)

    def __init__(self,to_delete,*args,**kwargs):
        super(ReturnPartForm,self).__init__(*args,**kwargs)
        if to_delete == 'Job': # if deleting a job, prompt to return all attached parts to inventory (unchecked by default)
            self.fields['return_parts'].initial = False
            self.fields['return_parts'].label = "Return parts to inventory?"
            self.fields['return_parts'].help_text = "If checked, all quantities of parts attached to this job will be returned to the inventory."
        else: # deleting a jobpart - prompt to return all attached parts to inventory (unchecked by default)
            self.fields['return_parts'].initial = True
            self.fields['return_parts'].label = "Return part to inventory?"
            self.fields['return_parts'].help_text = "If checked, all quantities of this part (pertaining to this job) will be returned to the inventory."
