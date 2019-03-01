<span id="top">aurwebdj</span>
------------------------------

_The following TravisCI widget is run off of the most recent commit at [https://github.com/kevr/aurweb.v6](https://github.com/kevr/aurweb.v6)._

[![Build Status](https://travis-ci.com/kevr/aurweb.v6.svg?branch=master)](https://travis-ci.com/kevr/aurweb.v6)

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

<small>If you are migrating from another legacy aurweb database, you should
skip this section and continue on to [Migration](#migrate).</small>

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

