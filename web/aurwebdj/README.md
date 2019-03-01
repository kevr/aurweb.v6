<span id="top">aurwebdj</span>
------------------------------

_The following TravisCI widget is run off of the most recent commit
at [https://github.com/kevr/aurweb.v6](https://github.com/kevr/aurweb.v6)._

[![Build Status](https://travis-ci.com/kevr/aurweb.v6.svg?branch=master)](https://travis-ci.com/kevr/aurweb.v6)

This project is currently in its porting stage of the process. This
project's development contains a four step process, each of which
contain subtasks:

1. Port `aurweb[php]` to a Django-driven website `aurwebdj`
	* Migrate database records from `aurweb[php]` to Django ORM [Done]
	* Port `$project_root/lib/aurweb` package to Django ORM
	* Implement HTML components of `aurweb[php]`
	* Implement API components of `aurweb[php]`
2. Convert `aurwebdj` to a Django extension
3. Fix outstanding bugs on the Trello board
4. Setup `aur.git` in our repository
5. [Potentially implement new features from the Trello board]

When these steps are completed, with the fifth being optional, the project
will be submitted to [aur-dev@archlinux.org](mailto:aur-dev@archlinux.org)
accompanied with a proposal.

<span id="setup">Setup</span>
-----------------------------

`aurwebdj` requires some setup before it can run properly. This will
require the following steps:

1. [Virtualenv](#virtualenv)
2. [Configuring /etc/aurweb/config](#config_config)
3. [Configuring /etc/aurweb/my.cnf](#my_config)
4. [Database model migration](#model_migrate)

### <span id="#virtualenv">Virtualenv</span>

Setup a virtualenv inside of $project_root/web/aurwebdj and run:

	(venv) shell$ pip install -r requirements.txt

Whenever you are working with Django or aurweb scripts related
to this project, you should be under the virtualenv above.

### <span id="config_config">Configuring /etc/aurweb/config</span>

See [git.archlinux.org/aurweb.git](https://git.archlinux.org/aurweb.git/)
for information about bootstrapping `/etc/aurweb/config`.

### <span id="my_config">Configuring /etc/aurweb/my.cnf</span>

Login to MySQL as root and create the aurweb database that
Django will use:

	shell$ mysql -u root
	mysql[NONE]> CREATE USER 'aur'@'localhost' IDENTIFIED BY 'aur_password';
	...
	mysql[NONE]> CREATE DATABASE aurweb CHARACTER SET utf8;
	...
	mysql[aurweb]> GRANT ALL ON aurweb.* TO 'aur'@'localhost'; 
	...
	mysql[aurweb]> COMMIT;

Then, configure MySQL database information for Django:

	# /etc/aurweb/my.cnf
	[client]
	database = aurweb
	user = aur
	password = aur_password
	default-character-set = utf8

### <span id="model_migrate">Database model migration</span>

If you are migrating from another legacy aurweb database, you should
skip this section and continue on to [Migration](#migrate).

After running the steps in [Setup](#setup), you can run the following
to setup the production database:

	(venv) shell$ ./manage.py migrate

If all goes well, you can continue to serving aurwebdj to the web
via nginx + uwsgi, or by `./manage.py runserver` for DEBUG mode.

<span id="migrate">Migration</span>
-----------------------------------

<small>Migrations from aurweb[php]</small>

This migration requires [Setup](#setup) to be completed, if you have
not done so, please revisit the section.

If you currently host *aurweb[php]*, you will need to run the local
migration script at `$project_root/lib/aurweb/scripts/migrate.py`.

`migrate.py` expects that the Django database be completely clear
of records. However, it will bypass records which already exist
when running the script.

	./lib/aurweb/scripts/migrate.py [--setup]
		--setup | Run Django `makemigrations` and `migrate` commands


Authors of aurwebdj
-------------------

* Kevin Morris &lt;kevr.gtalk@gmail.com&gt;

Authors of aurweb
-----------------

See [../../doc/AUTHORS](../../doc/AUTHORS) for original aurweb authors.

