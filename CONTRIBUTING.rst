.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/ratt-ru/smops/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

smops could always use more documentation, whether as part of the
official smops docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/ratt-ru/smops/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `smops` for local development.

1. Fork the `smops` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/smops.git

3. Install your local copy, with the test dependencies, into a virtual
   environment::

    $ cd smops/
    $ python -m venv .venv
    $ source .venv/bin/activate
    $ pip install -e ".[test]"

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the
   tests, including testing other Python versions with tox::

    $ flake8 smops tests
    $ pytest
    $ tox

   To get flake8 and tox, just pip install them into your virtualenv.

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for all supported Python versions (see
   ``requires-python`` in pyproject.toml). GitHub Actions runs the tests on
   each of them for every pull request; check that they pass.

Tips
----

To run a subset of tests::

$ pytest tests/test_spectral.py


Deploying
---------

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed, the version in
``smops/__init__.py`` has been bumped, and HISTORY.rst has an entry for the
release. Then publish a release on GitHub, tagged with the version (e.g.
``v0.2.0``). The publish workflow builds the package and uploads it to PyPI.
