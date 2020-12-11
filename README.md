# Problem - Coding Clinic Booking System

Refer to the Miro board for the project overview and specifications.

## Project Structure

This repository contains the following files already:


* `booking` - this directory contains code required to make a calendar booking
* `cancel_booking` - this directory contains code required to cancel a booking
* `cancel_volunteering` - this directory contains code required to cancel volunteering slots
* `config` - this directory contains the configuration settings required to initialize the project
* `deving` - this directory contains practice code completed during the project
* `tests/` - this directory contains LMS acceptance tests, which will be run against your code when you submit.
* `view_calendar` - this directory contains code to view the calendar slots
* `volunteer` - this directory contains code required to make a volunteering slot
* `secrets/credentials.json` - this file needs to be used with the Google Python module in order to authenticate with the Google API
* `clinic.py` - empty placeholder python file to get you going with the clinic setup and bookings
* `calendar-sync.py` - empty placeholder python file to get started with the tool to sync calendars
* `requirements.txt` - file to use with `PIP` to install the required modules

### To Test

* To run all the acceptance tests: `python3 -m unittest tests/test_main.py`
* _Note_: at the minimum, these (*unedited*) tests must succeed before you may submit the solution for review.
