from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Part, Job, JobPart, Service
from .forms import PartForm, JobForm, ServiceForm, JobPartForm, JobPartEditForm, ReturnPartForm
from .tables import PartTable, JobTable, ServiceTable, JobPartTable
from .filters import PartFilter, JobFilter
from django.urls import reverse_lazy
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView, BSModalReadView
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin, MultiTableMixin
from django.views.generic.base import TemplateView
from .utils import calculate_prices
import json
import datetime
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.template.loader import render_to_string

class ViewJobParts(BSModalReadView):
    template_name = 'inventory/view_jobparts.html'
    model = Part

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal_title'] = "Jobs with Part"
        part = get_object_or_404(Part, pk=self.kwargs['pk'])
        context['jobparts'] = JobPart.objects.filter(part=part)
        return context

# Create your views here.
@login_required
def email_invoice(request,job_pk):
    job = Job.objects.filter(pk=job_pk).first()
    if not job:
        status = 404
    else:
        if not job.customer_email:
            status = 400
        else:
            prices = calculate_prices(job,invoice=True)
            context = {'job':job, 'prices':prices, 'now': datetime.datetime.now()}
            subject = "TNR Motorcycle & ATV - Invoice for " + job.customer_name
            html_message = render_to_string('inventory/email_invoice.html', context)
            plaintext_message = render_to_string('inventory/invoice_plaintext', context)
            try:
                send_mail(subject,plaintext_message,None,[job.customer_email],html_message=html_message)
                status = 200
            except Exception as e:
                status = 500   
    return HttpResponse(status=status)

@login_required
def view_invoice(request,job_pk):
    job = get_object_or_404(Job, pk=job_pk)
    prices = calculate_prices(job,invoice=True)
    context = {'job':job, 'prices':prices, 'now': datetime.datetime.now()}
    return render(request,"inventory/view_invoice.html",context=context)

@login_required
def get_part_data(request, pk):
    part_dict = {}
    if Part.objects.filter(pk=pk).exists():
        part = Part.objects.get(pk=pk)
        part_dict['id'] = pk
        part_dict['quantity'] = part.quantity
        part_dict['unit_price'] = str(part.unit_price)
    return HttpResponse(json.dumps(part_dict))

class JobDetails(MultiTableMixin,TemplateView):
    template_name = "inventory/job_details.html"
    table_pagination = {
        "per_page": 25
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Job Details"
        context['job'] = Job.objects.get(pk=self.kwargs['pk'])
        context['prices'] = calculate_prices(context['job'])
        return context
    
    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        if not Job.objects.filter(pk=pk).exists():
            return HttpResponse(status=404)
        else:
            self.tables = [
                ServiceTable(Service.objects.filter(job=pk)),
                JobPartTable(JobPart.objects.filter(job=pk))
            ]
        return super().dispatch(request, *args, **kwargs)

class EditJob(BSModalUpdateView):
    model = Job
    template_name = 'inventory/form_modal.html'
    form_class = JobForm
    success_message = 'Job has been updated.'
    success_url = reverse_lazy('job_details')

    def get_success_url(self):
        return reverse_lazy('job_details', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal_title'] = "Edit Job"
        return context

    def dispatch(self, request, *args, **kwargs):
        if not Job.objects.filter(pk=kwargs['pk']).exists():
            return HttpResponse(status=404)
        return super().dispatch(request, *args, **kwargs)

class DeleteJob(BSModalDeleteView):
    model = Job
    template_name = 'inventory/modal_delete.html'
    success_message = 'Job was deleted.'
    success_url = reverse_lazy('jobs')

    def post(self, request, *args, **kwargs):
        if request.POST.get("return_parts") == 'on':
            job = Job.objects.get(pk=kwargs['pk'])
            jobparts = JobPart.objects.filter(job=job)
            for jp in jobparts:
                part = jp.part
                part.quantity += jp.quantity
                part.save()
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal_title'] = "Delete Job"
        context['descriptor'] = " - ".join([context['job'].customer_name,context['job'].vehicle])
        context['form'] = ReturnPartForm('Job')
        return context

    def dispatch(self, request, *args, **kwargs):
        if not Job.objects.filter(pk=kwargs['pk']).exists():
            return HttpResponse(status=404)
        return super().dispatch(request, *args, **kwargs)

class NewService(BSModalCreateView):
    template_name = 'inventory/form_modal.html'
    form_class = ServiceForm
    success_message = 'Service added.'

    def get_success_url(self):
        return reverse_lazy('job_details', kwargs={'pk': self.kwargs['job_pk']})

    def form_valid(self, form):
        form.instance.job = Job.objects.get(pk=self.kwargs['job_pk'])
        return super(NewService, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal_title'] = "New Service"
        return context

class EditService(BSModalUpdateView):
    model = Service
    template_name = 'inventory/form_modal.html'
    form_class = ServiceForm
    success_message = 'Service has been updated.'

    def get_success_url(self):
        job_pk = Service.objects.get(pk=self.kwargs['pk']).job.pk
        return reverse_lazy('job_details', kwargs={'pk': job_pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal_title'] = "Edit Service"
        return context

    def dispatch(self, request, *args, **kwargs):
        if not Service.objects.filter(pk=kwargs['pk']).exists():
            return HttpResponse(status=404)
        return super().dispatch(request, *args, **kwargs)

class DeleteService(BSModalDeleteView):
    model = Service
    template_name = 'inventory/modal_delete.html'
    success_message = 'Service was deleted.'

    def get_success_url(self):
        job_pk = Service.objects.get(pk=self.kwargs['pk']).job.pk
        return reverse_lazy('job_details', kwargs={'pk': job_pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal_title'] = "Delete Service"
        context['descriptor'] = context['service'].description
        return context

    def dispatch(self, request, *args, **kwargs):
        if not Service.objects.filter(pk=kwargs['pk']).exists():
            return HttpResponse(status=404)
        return super().dispatch(request, *args, **kwargs)

class NewJobPart(BSModalCreateView):
    template_name = 'inventory/form_modal.html'
    form_class = JobPartForm
    success_message = 'Part added to job.'

    def get_success_url(self):
        return reverse_lazy('job_details', kwargs={'pk': self.kwargs['job_pk']})

    def form_valid(self, form):
        form.instance.job = Job.objects.get(pk=self.kwargs['job_pk'])
        if not self.request.is_ajax():
            part = form.instance.part
            part.quantity -= form.instance.quantity
            part.save()
        return super(NewJobPart,self).form_valid(form)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal_title'] = "Add Part"
        return context

class EditJobPart(BSModalUpdateView):
    model = JobPart
    template_name = 'inventory/form_modal.html'
    form_class = JobPartEditForm
    success_message = 'Part has been updated.'

    def form_valid(self, form):
        if not self.request.is_ajax() and 'quantity' in form.changed_data:
            old_quantity = JobPart.objects.get(pk=form.instance.pk).quantity
            new_quantity = form.instance.quantity
            part = form.instance.part
            if new_quantity < old_quantity:
                part.quantity += (old_quantity - new_quantity)
                part.save()
            elif old_quantity < new_quantity:
                part.quantity -= (new_quantity - old_quantity)
                part.save()
        return super(EditJobPart,self).form_valid(form)

    def get_success_url(self):
        job_pk = JobPart.objects.get(pk=self.kwargs['pk']).job.pk
        return reverse_lazy('job_details', kwargs={'pk': job_pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal_title'] = "Edit Part"
        return context

    def dispatch(self, request, *args, **kwargs):
        if not JobPart.objects.filter(pk=kwargs['pk']).exists():
            return HttpResponse(status=404)
        return super().dispatch(request, *args, **kwargs)

class DeleteJobPart(BSModalDeleteView):
    model = JobPart
    template_name = 'inventory/modal_delete.html'
    success_message = 'Part was removed from job.'

    def post(self, request, *args, **kwargs):
        if request.POST.get("return_parts") == 'on':
            jobpart = JobPart.objects.get(pk=kwargs['pk'])
            part = jobpart.part
            part.quantity += jobpart.quantity
            part.save()
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        job_pk = JobPart.objects.get(pk=self.kwargs['pk']).job.pk
        return reverse_lazy('job_details', kwargs={'pk': job_pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal_title'] = "Remove Part"
        context['descriptor'] = context['jobpart'].part.name + " (Quantity: " + str(context['jobpart'].quantity) + ")"
        context['form'] = ReturnPartForm('JobPart')
        return context

    def dispatch(self, request, *args, **kwargs):
        if not JobPart.objects.filter(pk=kwargs['pk']).exists():
            return HttpResponse(status=404)
        return super().dispatch(request, *args, **kwargs)

class JobsView(SingleTableMixin, FilterView):
    table_class = JobTable
    model = Job
    template_name = "inventory/jobs.html"
    filterset_class = JobFilter
    table_pagination = {
        "per_page": 25
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Jobs"
        return context

class NewJob(BSModalCreateView):
    template_name = 'inventory/form_modal.html'
    form_class = JobForm
    success_message = 'Job has been created.'
    success_url = reverse_lazy('jobs')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal_title'] = "New Job"
        return context

class PartsView(SingleTableMixin, FilterView):
    table_class = PartTable
    model = Part
    template_name = "inventory/parts.html"
    filterset_class = PartFilter
    table_pagination = {
        "per_page": 25
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Parts"
        return context

    def dispatch(self, request, *args, **kwargs):
        zeroes = Part.objects.filter(quantity=0,ignore=False)
        if zeroes:
            zeroes_msg = "You've run out of the following parts:<ul>"
            for z in zeroes:
                zeroes_msg += "<li>"+z.name+" (ID: " + str(z.id) + ")</li>"
            zeroes_msg += "</ul>"
            messages.warning(request,zeroes_msg,extra_tags='safe')
        return super().dispatch(request, *args, **kwargs)

class NewPart(BSModalCreateView):
    template_name = 'inventory/form_modal.html'
    form_class = PartForm
    success_message = 'Part has been added to the inventory.'
    success_url = reverse_lazy('parts')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal_title'] = "New Part"
        return context

class EditPart(BSModalUpdateView):
    model = Part
    template_name = 'inventory/form_modal.html'
    form_class = PartForm
    success_message = 'Part has been updated.'
    success_url = reverse_lazy('parts')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal_title'] = "Edit Part"
        return context

    def dispatch(self, request, *args, **kwargs):
        if not Part.objects.filter(pk=kwargs['pk']).exists():
            return HttpResponse(status=404)
        return super().dispatch(request, *args, **kwargs)

class DeletePart(BSModalDeleteView):
    model = Part
    template_name = 'inventory/modal_delete.html'
    success_message = 'Part was deleted.'
    success_url = reverse_lazy('parts')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modal_title'] = "Delete Part"
        context['descriptor'] = context['part'].name
        context['msg'] = " Doing so will remove any instances of this part from jobs."
        return context

    def dispatch(self, request, *args, **kwargs):
        if not Part.objects.filter(pk=kwargs['pk']).exists():
            return HttpResponse(status=404)
        return super().dispatch(request, *args, **kwargs)

def login(request):
    if request.user.is_authenticated:
        return redirect('parts')
    elif request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            auth_login(request,user)
            nxt = request.POST.get('next')
            dest = nxt if nxt else "parts"
            return redirect(dest)
        else:
            messages.error(request,'Invalid username/password combination.')
    return render(request,"inventory/login.html",{'title':"Login"})