from django import forms
from .models import Part, Job, Service, JobPart
from bootstrap_modal_forms.forms import BSModalModelForm
from django.core.exceptions import ValidationError

class PartForm(BSModalModelForm):
    class Meta:
        model = Part
        fields = ('name','quantity','unit_price','ignore')
        widgets = {
            'name': forms.TextInput(attrs={'size':50})
        }

class JobForm(BSModalModelForm):
    class Meta:
        model = Job
        exclude = ('created',)
        widgets = {
            'notes': forms.Textarea(attrs={"rows":5, "cols":10})
        }

class ServiceForm(BSModalModelForm):
    class Meta:
        model = Service
        fields = ('description','price')

class JobPartForm(BSModalModelForm):
    QUANTITY_CHOICES = [(i,i) for i in range(1,1000)]
    quantity = forms.ChoiceField(choices=QUANTITY_CHOICES)
    part = forms.ModelChoiceField(queryset=Part.objects.filter(quantity__gt=0).order_by('name'))

    class Meta:
        model = JobPart
        fields = ('part','quantity','unit_price')
    
    def clean_quantity(self):
        part = self.cleaned_data.get("part")
        quantity = int(self.cleaned_data.get("quantity"))
        in_inventory = part.quantity
        if quantity > in_inventory:
            error_msg = 'Quantity must be less than or equal to ' + str(in_inventory) + "."
            raise ValidationError(error_msg)
        return quantity

class JobPartEditForm(BSModalModelForm):
    QUANTITY_CHOICES = [(0,0)]
    quantity = forms.ChoiceField(choices=QUANTITY_CHOICES)

    def __init__(self,*args,**kwargs):
        super(JobPartEditForm,self).__init__(*args,**kwargs) # populates the post
        part = Part.objects.filter(pk=self.instance.part.pk)
        self.fields['part'].queryset = part
        self.fields['part'].disabled = True
        quantity = [(i,i) for i in range(1,part.first().quantity + self.instance.quantity + 1)]
        self.fields['quantity'].choices = quantity

    class Meta:
        model = JobPart
        fields = ('part','quantity','unit_price')

    def clean_part(self):
        return Part.objects.get(pk=self.initial["part"])


class ReturnPartForm(forms.Form):
    return_parts = forms.BooleanField(required=False)

    def __init__(self,to_delete,*args,**kwargs):
        super(ReturnPartForm,self).__init__(*args,**kwargs)
        if to_delete == 'Job':
            self.fields['return_parts'].initial = False
            self.fields['return_parts'].label = "Return parts to inventory?"
            self.fields['return_parts'].help_text = "If checked, all quantities of parts attached to this job will be returned to the inventory."
        else:
            self.fields['return_parts'].initial = True
            self.fields['return_parts'].label = "Return part to inventory?"
            self.fields['return_parts'].help_text = "If checked, all quantities of this part (pertaining to this job) will be returned to the inventory."
