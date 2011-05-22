from django.contrib import admin
from models import Mail, Attachment

class MailAdmin( admin.ModelAdmin ):
    list_display = ( "subject", "sender", "receiver", "date" )
    date_hierarchy = "date"

class AttachmentAdmin( admin.ModelAdmin ):
    pass



admin.site.register( Mail, MailAdmin )
admin.site.register( Attachment, AttachmentAdmin )
