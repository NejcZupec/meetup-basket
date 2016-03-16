Meetup Basket
=============

[![Build Status](https://travis-ci.org/NejcZupec/meetup-basket.svg?branch=master)](https://travis-ci.org/NejcZupec/meetup-basket)
[![Coverage Status](https://coveralls.io/repos/NejcZupec/meetup-basket/badge.svg?branch=master&service=github)](https://coveralls.io/github/NejcZupec/meetup-basket?branch=master)
[![Codacy Badge](https://www.codacy.com/project/badge/f2a0eb5c905a416da4e137ca2bfbed2e)](https://www.codacy.com/public/zupecnejc_3396/meetup-basket_2)


[ ![Codeship Status for NejcZupec/meetup-basket](https://codeship.com/projects/9733edb0-4eee-0132-aaa0-76883f3d5ece/status)](https://codeship.com/projects/47802)


Setup
-----
You have to set three environment variables: SECRET_KEY, MEETUP_API_KEY and DJANGO_SETTINGS_MODULE.

Deploy
------

Run the following command to deploy everything to basket.zupec.net.

```
cd deploy
ansible-playbook deploy.yml
```

Sync development and production databases
-----------------------------------------

If you want to get the production's data, go to the `deploy` folder and run the following commands:

```
ansible production -m fetch -a "src=/opt/db_backups/<year>-<month>-<day>-daily/meetupbasket.custom dest=meetupbasket.custom flat=yes"
dropdb meetupbasket;
createdb meetupbasket;
pg_restore -d meetupbasket meetupbasket.custom
```

The server generates daily database snapshots. You have to specify `year`, `month`and `day` to determine which snapshot do you want to restore to your local database.

