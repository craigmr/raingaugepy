RainGuagePy
============

Python script that gets rainfall inches from wunderground.com stations and emails you when
it is time to water the garden.  I use this script as a cron job on my home server to collect yesterday's
rainfall at 8 am.  If the rainfall for the last three days is less than one inch then an
email is sent to water my garden. (This was the recommendation from my gardener).

This is one of my first python scripts I made will getting my feet wet learning the language. Any constructive
feedback would be appericated!

Requirements
------------
RainGaugePy uses the following external python libraries:

* BeautifulSoup
* lxml

Other requirements
*Know station id from wunderground.com
*STMP enabled email server (currently setup for gmail.com)

Usage
-----
	$ python rainguage.py -c 'app.cfg'
	
Current State
-------------
* There is sqlite database setup so the data base needs to have the table Rainfall and EmailSent
already formatted when the script is run for the first time.

Next Steps
----------
* Add support for db-sql initailization so tables do not have to be pre-built.
* Document code.
* Review if I am writing python correctly.
* Learn about getting some sort of dependency manager.
* Learn about unit tests!
