import django_tables2 as tables
from .models import Part, Job, JobPart, Service

# for monetary values - prepends $ to column entries
class MoneyColumn(tables.Column):
    def render(self,value):
        return "$" + str(value)

class PartTable(tables.Table):
    actions = tables.TemplateColumn(
                    "<button type='button' title='Edit Part' class='edit btn btn-sm btn-primary' data-id='{% url 'edit_part' record.id %}'><span class='fa fa-pencil'></button> <button type='button' title='Delete Part' class='delete btn btn-sm btn-danger' data-id='{% url 'delete_part' record.id %}'><span class='fa fa-trash'></button> <button type='button' title='Jobs with Part' class='edit btn btn-sm btn-info' data-id='{% url 'view_jobparts' record.id %}'><span class='fas fa-briefcase'></button>",
                    verbose_name='',orderable=False)
    unit_price = MoneyColumn()
    class Meta:
        model = Part
        template_name = "django_tables2/bootstrap4.html"
        order_by = ('-id',)
        exclude = ('ignore',)
        attrs = {"class": "table table-responsive-sm"} # appending responsive class allows horizontal table scrolling on small screens

class JobTable(tables.Table):
    actions = tables.TemplateColumn(
                    "<a href='{% url 'job_details' record.id %}'><button type='button' title='Job Details' class='details btn btn-primary'><i class='far fa-eye'></i></button></a> <button type='button' title='Delete Job' class='delete-job btn btn-danger' data-id='{% url 'delete_job' record.id %}'><span class='fa fa-trash'></button>",
                    verbose_name='',orderable=False)
    class Meta:
        model = Job
        template_name = "django_tables2/bootstrap4.html"
        fields = ('id','created','customer_name','vehicle','status')
        order_by = ('-id',)
        attrs = {"class": "table table-responsive-sm"}

class JobPartTable(tables.Table):
    actions = tables.TemplateColumn(
                    "<button type='button' title='Edit Part' class='edit-jobpart btn btn-sm btn-primary' data-id='{% url 'edit_jobpart' record.id %}'><span class='fa fa-pencil'></button> <button type='button' title='Delete Part' class='delete-jobpart btn btn-sm btn-danger' data-id='{% url 'delete_jobpart' record.id %}'><span class='fa fa-trash'></button>",
                    verbose_name='',orderable=False)
    unit_price = MoneyColumn()
    class Meta:
        model = JobPart
        template_name = "django_tables2/bootstrap4.html"
        exclude = ('id','job','tax')
        order_by = ('-id',)
        attrs = {"class": "table table-responsive-sm"}

class ServiceTable(tables.Table):
    actions = tables.TemplateColumn(
                    "<button type='button' title='Edit Service' class='edit-service btn btn-sm btn-primary' data-id='{% url 'edit_service' record.id %}'><span class='fa fa-pencil'></button> <button type='button' title='Delete Service' class='delete-service btn btn-sm btn-danger' data-id='{% url 'delete_service' record.id %}'><span class='fa fa-trash'></button>",
                    verbose_name='',orderable=False)
    price = MoneyColumn()
    class Meta:
        model = Service
        template_name = "django_tables2/bootstrap4.html"
        exclude = ('id','job','tax')
        order_by = ('-id',)
        attrs = {"class": "table table-responsive-sm"}