from django.db import models
import os
import uuid

class Mail(models.Model):
    subject = models.CharField( max_length = 255, verbose_name="subject" )
    sender = models.CharField( max_length = 255, verbose_name = "sender" )
    receiver = models.CharField( max_length = 255, verbose_name = "sent to" )
    date = models.DateTimeField(auto_now_add=True)
    max_age = models.IntegerField(default=30)
    def __unicode__(self):
        return "{0} from {1} to {2} on {3}".format(self.subject,self.sender,self.receiver,self.date)
    class Meta:
        verbose_name = "mail"
        verbose_name_plural = "mails"

def _attachment_upload_to(instance, filename):
    instance.filename_orig = filename
    if len(filename)>100:
        ext=filename.rpartition(".")[2]
        if ext==filename:
            filename=filename[0:99]
        else:
            filename="{0}.{1}".format(filename[0:99-(len(ext)+1)],ext)
    return os.path.join(str(uuid.uuid4()),filename)

class Attachment( models.Model ):
    mail = models.ForeignKey(Mail, related_name="attachments")
    content_type = models.CharField( max_length = 255, verbose_name = "content-type" )
    file = models.FileField(max_length=255, upload_to=_attachment_upload_to)
    filename_orig = models.CharField(max_length=255, verbose_name="original filename")
    def __unicode__( self ):
        return self.filename_orig
    class Meta:
        verbose_name = "attachment"
        verbose_name_plural = "attachments"