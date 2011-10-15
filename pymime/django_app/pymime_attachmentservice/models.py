from django.db import models
import os
import uuid
from django.core.files.storage import FileSystemStorage
from datetime import timedelta, datetime
from django.core import urlresolvers

class Mail(models.Model):
    uuid = models.CharField(max_length = 36, verbose_name = "UUID", default = lambda:uuid.uuid4(), editable = False)
    subject = models.CharField(max_length = 255, verbose_name = "subject")
    sender = models.CharField(max_length = 255, verbose_name = "sender")
    receiver = models.CharField(max_length = 255, verbose_name = "sent to")
    date = models.DateTimeField(auto_now_add = True)
    max_age = models.IntegerField(default = 30, help_text = "Maximum age of the mail and its attachment in days.")
    archive_url = models.URLField(verify_exists = False, blank = True, max_length = 255)
    def max_age_date (self):
        if self.max_age > 0:
            return self.date + timedelta(days = self.max_age)
        else:
            return "indefinite"
    def get_admin_url(self):
        return urlresolvers.reverse('admin:pymime_attachmentservice_mail_change', args = (self.id,))
    @models.permalink
    def get_absolute_url(self):
        return ('pymime.django_app.pymime_attachmentservice.views.show_mail', [str(self.uuid)])
    def expire(self):
        if self.max_age > 0:
            valid_until = self.date + timedelta(days = self.max_age)
            if valid_until < datetime.now():
                self.delete()
                return True
        return False
    def delete(self, *args, **kwargs):
        for a in self.attachments.all():
            a.delete()
        super(Mail, self).delete(*args, **kwargs)
    def __unicode__(self):
        return u"{0} from {1} to {2} on {3}".format(self.subject, self.sender, self.receiver, self.date)
    class Meta:
        verbose_name = "mail"
        verbose_name_plural = "mails"

def _attachment_upload_to(instance, filename):
    instance.filename_orig = filename
    filename = filename.encode("ascii", "replace")
    if len(filename) > 100:
        ext = filename.rpartition(".")[2]
        if ext == filename:
            filename = filename[0:99]
        else:
            filename = "{0}.{1}".format(filename[0:99 - (len(ext) + 1)], ext)
    return os.path.join(str(uuid.uuid4()), filename)

class AttachmentStorage(FileSystemStorage):
    def delete(self, name):
        super(AttachmentStorage, self).delete(name)
        dir = os.path.dirname(name)
        if dir:
            cwd = os.getcwd()
            os.chdir(self.location)
            try:
                os.removedirs(dir)
            except OSError:
                # Leaf directory not empty
                pass
            os.chdir(cwd)

class Attachment(models.Model):
    mail = models.ForeignKey(Mail, related_name = "attachments")
    content_type = models.CharField(max_length = 255, verbose_name = "content-type")
    file = models.FileField(max_length = 255, upload_to = _attachment_upload_to, storage = AttachmentStorage())
    filename_orig = models.CharField(max_length = 255, verbose_name = "original filename")
    def printsize(self):
        if self.file.size > 1024 ** 3:
            size = "{0:.3}".format(self.file.size / float(1024 ** 3))
            ext = "GiB"
        elif self.file.size > 1024 ** 2:
            size = "{0:.3}".format(self.file.size / float(1024 ** 2))
            ext = "MiB"
        elif self.file.size > 1024:
            size = "{0:.3}".format(self.file.size / float(1024))
            ext = "KiB"
        else:
            size = self.file.size
            ext = "B"
        return "{0} {1}".format(size, ext)
    def delete(self, *args, **kwargs):
        self.file.delete()
        super(Attachment, self).delete(*args, **kwargs)
    def __unicode__(self):
        return self.filename_orig
    class Meta:
        verbose_name = "attachment"
        verbose_name_plural = "attachments"

class Dropped_Attachment(models.Model):
    mail = models.ForeignKey(Mail, related_name = "dropped_attachments")
    content_type = models.CharField(max_length = 255, verbose_name = "content-type")
    filename = models.CharField(max_length = 255, verbose_name = "filename")
    reason = models.CharField(max_length = 255, verbose_name = "reason", blank = True, default = "Extension or Content-Type not allowed.")
    def __unicode__(self):
        return self.filename
    class Meta:
        verbose_name = "dropped attachment"
        verbose_name_plural = "dropped attachments"

class Problem_Report(models.Model):
    mail = models.ForeignKey(Mail, related_name= "problem report")
    reason = models.TextField(max_length = 1000, verbose_name = "reason", blank = True)
    ip = models.IPAddressField(verbose_name="reporter ip", blank = True)
    headers = models.TextField(verbose_name = "header", blank = True)
    reporter_address = models.EmailField(verbose_name = "reporter address", blank=True)
    def __unicode__(self):
        return "{0} sent from {1}".format(str(self.mail),str(self.reporter_address))
    class Meta:
        verbose_name = "problem report"
        verbose_name_plural = "problem reports"
