from django.shortcuts import get_object_or_404, render_to_response
from pymime.django_app.pymime_attachmentservice.models import Mail, Problem_Report
from pymime.django_app.pymime_attachmentservice.forms import ReportForm
from django.template.context import RequestContext
def show_mail(request, uuid):
    m = get_object_or_404(Mail, uuid = uuid)
    return render_to_response("show_mail.html", RequestContext(request, {"mail":m}))

def report_mail(request, uuid):
    m = get_object_or_404(Mail, uuid = uuid)
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data["reason"]
            reporter_mail = form.cleaned_data["reporter_mail"]
            r = Problem_Report()
            r.mail = m
            r.reason = reason
            r.ip = request.META["REMOTE_ADDR"]
            r.headers = str(request.META)
            r.reporter_address = reporter_mail
            r.save()
            return render_to_response("show_mail.html", RequestContext(request, {"mail":m}))
    else:
        form = ReportForm()
    return render_to_response("report_mail.html", RequestContext(request, {"mail":m, "form":form}))
