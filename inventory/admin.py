from django.contrib import admin
from django.contrib.auth.models import Group
from .models import Part, Job, JobPart, Service

admin.site.unregister(Group)

# Register your models here.
class PartAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'quantity','unit_price')
    search_fields = ('id','name')

class JobAdmin(admin.ModelAdmin):
    list_display = ('id','customer_name','vehicle','status','created')
    search_fields = ('id','customer_name','vehicle')

class JobPartAdmin(admin.ModelAdmin):
    list_display = ('id','job','part','quantity','unit_price')
    search_fields = ('id',)

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id','job','description','price')
    search_fields = ('id','description')

admin.site.register(Part,PartAdmin)
admin.site.register(Job,JobAdmin)
admin.site.register(JobPart,JobPartAdmin)
admin.site.register(Service,ServiceAdmin)