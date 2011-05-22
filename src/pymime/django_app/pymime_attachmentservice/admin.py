from django.contrib import admin
from models import Mail, Attachment

class AttachmentInline( admin.StackedInline ):
    model = Attachment
    extra = 0


class MailAdmin( admin.ModelAdmin ):
    list_display = ( "subject", "sender", "receiver", "date" )
    list_filter=("receiver",)
    search_fields=("subject", "sender", "receiver", "attachments__filename_orig", "attachmetns__content_type")
    date_hierarchy = "date"
    inlines=(AttachmentInline,)


class AttachmentAdmin( admin.ModelAdmin ):
    pass


admin.site.register( Mail, MailAdmin )
admin.site.register( Attachment, AttachmentAdmin )
