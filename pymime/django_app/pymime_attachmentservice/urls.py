from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('pymime.django_app.pymime_attachmentservice.views',
    (r'^mail/(?P<uuid>[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12})/$', 'show_mail')
)
