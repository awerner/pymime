from django.contrib import admin
from models import Mail, Attachment
from django.utils.translation import ugettext_lazy, ugettext as _

admin.site.disable_action('delete_selected')
def iterate_delete(modeladmin, request, queryset):
    for obj in queryset:
        obj.delete()
    modeladmin.message_user(request, _("Deletion successful."))
iterate_delete.short_description = ugettext_lazy("Delete selected %(verbose_name_plural)s")

admin.site.add_action(iterate_delete, 'iterate_delete')


class AttachmentInline(admin.StackedInline):
    model = Attachment
    extra = 0

class MailAdmin(admin.ModelAdmin):
    list_display = ("subject", "sender", "receiver", "date")
    list_filter = ("receiver",)
    search_fields = ("subject", "sender", "receiver", "attachments__filename_orig", "attachments__content_type")
    date_hierarchy = "date"
    inlines = (AttachmentInline,)


class AttachmentAdmin(admin.ModelAdmin):
    pass


admin.site.register(Mail, MailAdmin)
admin.site.register(Attachment, AttachmentAdmin)
