from django.core.management.base import NoArgsCommand
from pymime.django_app.pymime_attachmentservice.models import Mail

class Command(NoArgsCommand):
    help = 'Removes all mails that are older than their max_age'

    def handle_noargs(self, *args, **options):
        counter = 0
        for m in Mail.objects.all():
            id = m.id
            if m.expire():
                counter+=1
                self.stdout.write('Mail ID {0} expired.\n'.format(id))
        self.stdout.write('Removed {0} old mails.\n'.format(counter))