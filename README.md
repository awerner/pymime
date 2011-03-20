pymime - A MIME formatter in python
===================================

Installation & Configuration
----------------------------

* Simply run `python setup.py install` to install the necessary files.
* Look at the default configuration files in /etc/pymime/,
  copy them from *\*.conf.default* to *\*.conf* and change them to your liking.
* Make sure that the server (`pymimed`) has write access to the logfile.
* Run the server: `pymimed`.
* The client by default accepts mails from STDIN and writes them to STDOUT:
  `cat test.eml | pymimec > parsed.eml`

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
