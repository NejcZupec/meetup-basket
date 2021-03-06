Meetup Basket
=============

[![Build Status](https://travis-ci.org/NejcZupec/meetup-basket.svg?branch=master)](https://travis-ci.org/NejcZupec/meetup-basket)
[![Coverage Status](https://coveralls.io/repos/NejcZupec/meetup-basket/badge.svg?branch=master&service=github)](https://coveralls.io/github/NejcZupec/meetup-basket?branch=master)
[![Codacy Badge](https://www.codacy.com/project/badge/f2a0eb5c905a416da4e137ca2bfbed2e)](https://www.codacy.com/public/zupecnejc_3396/meetup-basket_2)

Development environment
-----------------------
The following prerequisities are required:
 * Python 2.7
 * Virtualenv
 * Pip
 * Git

*Note: we are asuming you are running an UNIX-like operating system.*

Create a new virtual environment and activate it:

    virtualenv meetup_basket_env
    source meetup_basket_env/bin/activate

Clone the repository from Github:

    git clone git@github.com:NejcZupec/meetup-basket.git

Install all development requirements:

    pip install -r requirements/development.txt

You have to set the following environment variables: SECRET_KEY, MEETUP_API_KEY and DJANGO_SETTINGS_MODULE.

    export SECRET_KEY='<random_string>'
    export MEETUP_API_KEY='<get it from https://secure.meetup.com/meetup_api/key/>'
    export DJANGO_SETTINGS_MODULE='meetup_basket.settings.development'

Migrate database:

    python manage.py migrate

Create superuser:

    python manage.py createsuperuser

Now you are ready to run application:

    python manage.py runserver
    
Go to the control panel (http://127.0.0.1:8000/admin), login with the account you've just created and add a new season `2015/2016` with a slug `#15/16`. Now you can open the root of application at http://127.0.0.1:8000

That's it, you have successfully set the environment for *meetup-basket* app :)

Deploy
------

Run the following command to deploy everything to basket.zupec.net.

```
cd deploy
ansible-playbook site.yml --tags deploy
```

Sync development and production databases
-----------------------------------------

If you want to get the production's data, go to the `deploy` folder and run the following commands:

```
ansible production -m fetch -a "src=/opt/db_backups/<year>-<month>-<day>-daily/meetupbasket.custom dest=meetupbasket.custom flat=yes"
dropdb meetupbasket; createdb meetupbasket
pg_restore -d meetupbasket meetupbasket.custom
```

The server generates daily database snapshots. You have to specify `year`, `month`and `day` to determine which snapshot do you want to restore to your local database.

