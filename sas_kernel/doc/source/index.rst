:tocdepth: 4

**********
SAS Kernel
**********

.. module:: sas_kernel

**Date**: |today| **Version**: |version|

**Binary Installers:** `<http://github.com/sassoftware/sas_kernel/releases>`_

**Source Repository:** `<http://github.com/sassoftware/sas_kernel>`_

**Issues & Ideas:** `<https://github.com/sassoftware/sas_kernel/issues>`_

The SAS Kernel project defines a kernel for `Jupyter Notebooks <http://www.jupyter.org>`__.
Making it possible to use Jupyter for writing and maintaining SAS coding projects.



.. toctree::

   install
   getting-started
   api
   license



SAS Kernel for Jupyter
======================

What is this?
-------------

A SAS Kernel for `Jupyter Notebooks <http://www.jupyter.org>`__

Dependencies
------------

-  Python3.X
-  Jupyter
-  SAS 9.4 or higher -- This includes `SAS
   Viya <http://www.sas.com/en_us/software/viya.html>`__

Improving Usability
-------------------

There are a few NBExtensions that have been created to make working with
Jupyter notebooks more productive. These are largely the result of pain
points from my use of SAS Kernel for programming tasks. The extensions
can be found `here <https://github.com/sassoftware/sas_kernel/tree/master/sas_kernel/nbextensions>`__.
The list includes: \* SAS Log
-- which show the SAS log for the last executed cell or the entire log
since the last (re)start of the notebook \* themes -- this allows you to
change the color scheme for your code to match the traditional SAS color
scheme

Jupyter Magics for the sas\_kernel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are magics that have been written specifically for the sas\_kernel
to get more details see the `README <./sas_kernel/magics/README.md>`__

Jupyterhub
----------

The SAS kernel can be used with JupyterHub for more information look
`here <https://jupyterhub.readthedocs.org/en/latest/>`__

NBGrader
--------

`nbgrader <http://nbgrader.readthedocs.org/en/stable/>`__ is a system
for assigning and grading notebooks and extends jupyter. I have a number
of contributions that I'm currently working on in conjunction with
teaching SAS programming in a classroom setting. You can see my forked
repo `here <https://github.com/jld23/nbgrader>`__

FAQ
---

-  Is there a SAS Magic that I can access from a python kernel?

   Yes! There are actually several cell magics available from SAS. They
   are ``%%SAS``, ``%%IML``, and ``%%OPTMODEL``. To load these magics in
   your notebook, execute the following command
   ``%load_ext saspy.sas_magic``. You can check that the magics have are
   successfully activated by looking at the results of ``%lsmagic`` and
   looking in the cell magic section. If you use multiple SAS Cell
   magics in the *same* notebook they will share a SAS session (have the
   same WORK libname and MACROS). There is currently no sharing of SAS
   Sessions between different notebooks.

-  Do I need to buy SAS to use this kernel?

The SAS Kernel is simply a gateway for Jupyter notebooks to talk to SAS,
as such, if SAS is not installed this kernel won't be that helpful. For
information on purchasing SAS `click
here <http://www.sas.com/en_us/software/how-to-buy.html>`__

-  How does Jupyter communicate with SAS?

   Behind a Jupyter notebook is a python session, that python session
   submits code to SAS and receives responses through socket i/o
   (leveraging stdin , stdout, and stderr) which has been supported in
   SAS for a long time

-  If stdin, stdout, and stderr have been supported for so long why do I
   need to have SAS 9.4 or newer?

   First, SAS 9.4 was released in July 2013 so it isn't exactly a
   bleeding edge requirement. The reason for a prerequisite for SAS 9.4
   is because that was the first release that supported the creation of
   HTML5 documents and that is the returned output so that we can render
   attractive tables and graphs automagically

-  How can I see my SAS log, I only see the listing output?

   SAS is different from many other programming languages in that it has
   two useful information streams, the log (which details the technical
   details of what happened and how long it took) and the lst (which
   includes the tables and graphics from the analysis). The SAS Kernel
   attempts to show you I *think* you want. Here are the rules:

   +-------------------------------+-------+---------------------------------------------------------------------+-----------------------------------------------------------------------------+
   | LOG                           | LST   | DISPLAYED                                                           | NOTES                                                                       |
   +===============================+=======+=====================================================================+=============================================================================+
   | Yes                           | No    | LOG                                                                 | This happens when you run DATA Step or a PROC with the ``noprint`` option   |
   +-------------------------------+-------+---------------------------------------------------------------------+-----------------------------------------------------------------------------+
   | Yes                           | Yes   | LST                                                                 | ---                                                                         |
   +-------------------------------+-------+---------------------------------------------------------------------+-----------------------------------------------------------------------------+
   | Yes (with ERROR message(s))   | Yes   | ERROR messages with context from the log, then the listing output   | ---                                                                         |
   +-------------------------------+-------+---------------------------------------------------------------------+-----------------------------------------------------------------------------+
   | Yes (with ERROR message(s))   | No    | LOG                                                                 | ---                                                                         |
   +-------------------------------+-------+---------------------------------------------------------------------+-----------------------------------------------------------------------------+

   If you want to see the log but it was not displayed you can use
   `SASLog NBExtension <./sas_kernel/nbextensions/README.md>`__ which
   will show the log for the last executed cell or the entire log since
   the last (re)start of the notebook

-  Will this leave a bunch of SAS sessions hanging around?

   A SAS session is started for each notebook you have open i.e. 5
   notebooks open = 5 SAS sessions. Those sessions will remain active
   for the life of the notebook. If you shutdown your notebook, the SAS
   session will also terminate. In Jupyterhub, there are configuration
   options to shutdown inactive sessions and the SAS kernel complies
   with those directives.

-  I restarted my SAS Kernel and now my WORK library is now empty. What
   happened?

   When you restart the kernel in a notebook you are terminating the
   current SAS session and starting a new one. All of the temporary
   artifacts, data sets in the WORK library, assigned libnames,
   filename, WORK macros, and so on are destroyed.

