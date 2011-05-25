from django.shortcuts import get_object_or_404, render_to_response
from pymime.django_app.pymime_attachmentservice.models import Mail
from django.template.context import RequestContext
def show_mail(request, uuid):
    m = get_object_or_404(Mail, uuid = uuid)
    return render_to_response("show_mail.html", RequestContext(request, {"mail":m}))
