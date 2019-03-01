aurweb [Django Port]
--------------------

_The following TravisCI widget is run off of the most recent commit at [https://github.com/kevr/aurweb.v6](https://github.com/kevr/aurweb.v6)._

[![Build Status](https://travis-ci.com/kevr/aurweb.v6.svg?branch=master)](https://travis-ci.com/kevr/aurweb.v6)

This project is intended to be a continued replacement for an
existing PHP-implemented aurweb. This django port contributes
the following improvements to aurweb from a developer perspective:

* Model-based ORM
* Automated REST content serialization
* Easy to integrate HTTP transport middlewares
* Simplified reasoning of codebase from reviewer's perspective
* Structured framework
* Separation between Controller and View

And as for the user-view improvements:

* Standardize v6 API across the board (multiple by predicates)
* POST requests now work across all API requests
* Increased password hashing security OOB

Many additional improvements are to be added as soon as possible.

Dependencies
------------

* Django
* djangorestframework
* passlib (required for compat password hashes)

Optional Dependencies
---------------------

* django-subdomain (required for hosting aurwebdj in a Django project with existing routes)

Authors
-------

of the original aurweb backend python package and PHP-driven aurweb:

[https://git.archlinux.org/aurweb.git](https://git.archlinux.org/aurweb.git).

of distinct contents of this repository, not including `./lib/aurweb`:

Kevin Morris &lt;kevr.gtalk@gmail.com&gt;

License
-------

This project will adopt and act under the GNU General Public
License, Version 2. See `LICENSE` for full GNU GPLv2.

