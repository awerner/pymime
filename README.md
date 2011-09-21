pymime - A MIME formatter in python
===================================

Installation & Configuration
----------------------------

* Simply run `python setup.py install` to install the necessary files.
* Look at the default configuration files in /etc/pymime/,
  copy them from *\*.conf.default* to *\*.conf* and change them to your liking.
* Make sure that the server (`pymimed`) has write access to the logfile and the pidfile.
* Run the server: `pymimed start[|stop|restart]`.
* The client by default accepts mails from STDIN and writes them to STDOUT:
  `cat test.eml | pymimec > parsed.eml`

Configuring the Webinterface
----------------------------

* Copy the integration/django_attachmentstore directory to a destination of your liking.
* `cd destination/django_attachmentstore`
* Edit the file settings.py: `nano settings.py`
* Insert your name and email in the ADMINS-tuple
* Enter your database settings in DATABASES["default"]
* Change the SECRET_KEY.
* Install the database: `python manage.py syncdb`
* Run the development server: `python manage.py runserver <PORT>`
* Configure the attachmentservice to use the django backend:
* Use the default configuration as starting point:
  `cd /etc/pymime; cp plugin_attachmentservice.conf.default plugin_attachmentservice.default`
* Edit the configuration: `nano plugin_attachmentservice.default`
* Set `store-function=pymime.integration.django_store`
* Set `store-function-options={"project-path": "<path to django_attachmentstore>"}`
* Set `action=store` in your policies.
* To deploy the Webinterface for production, set `DEBUG=False` in settings.py, and
  read https://docs.djangoproject.com/en/dev/howto/deployment/

Usage
-----

	Usage: pymimec [options]
	
	Options:
	  -h, --help            show this help message and exit
	  -i INPUT, --input=INPUT
	                        Where to read the mail from. Defaults to STDIN
	  -o OUTPUT, --output=OUTPUT
	                        Where to write the transformed mail. Defaults to
	                        STDOUT

License
-------

GPLv3
