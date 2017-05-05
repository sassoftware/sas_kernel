SAS Kernel for Jupyter
======================

What is this?
-------------

A SAS Kernel for `Jupyter Notebooks`_

Dependencies
------------

-  Python3.X
-  Jupyter
-  SAS 9.4 or higher – This includes `SAS Viya`_
-  Linux OS

With the latest changes in `saspy`_ it is no longer a requirement that
Jupyter and SAS be installed on the same machine. SAS and Jupyter can
now communicate via passwordless ssh. This is in response to `issue
11`_. The configuration details are located in `sascfg.py`_

Documentation
-------------

Here is the link to the current documentation
https://sassoftware.github.io/sas\_kernel/

Install
-------

To successfully use the SAS Kernel you must have each of the following:
\* `SAS version 9.4 or above`_ \* `Jupyter`_ \* Jupyter has a number of
dependencies. See the subsections for steps on installing Jupyter on
your system. \* `Python 3`_

Install for Anaconda Python (assuming SAS already installed)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. `Download`_ and install Anaconda Python (make sure you get
   Python3.X). If you install Anaconda without super user rights (root
   or sudo) then other users on the system will not be able to access
   the SAS kernel. A couple notes that I’ve observed:

-  The default install location is the users home directory. This is
   fine for a single user install I would put it in a common location
   (``/opt``) if you’re doing a system wide install
-  One of the prompts is to add the path to your environment. I
   recommend you want to answer ‘yes’ to that question so that all the
   installing user has the executables in their path. If you’re doing a
   system wide install (root or sudo) all the other users should add
   that path to their environmental variables

1. Install sas\_kernel. The sas\_kernel has a dependency on saspy which
   is located `here`_. In the command below I’m assuming that ``pip``
   maps to python3 if that is not the case the you might need to use
   ``pip3`` instead. ``pip install sas_kernel``

2. Verify that the sas\_kernel is installed ``jupyter kernelspec list``

   If you installed as a superuser, your output should similar to this:

   ::

       Available kernels:
         python3    /opt/Anaconda3-2.5.0/lib/python3.5/site-packages/ipykernel/resources
         sas        /usr/local/share/jupyter/kernels/sas

   If you installed as a regular user (sas in this case), your output
   should similar to this:

   ::

       Available kernels:
         python3    /home/sas/anaconda3/lib/python3.5/site-packages/ipykernel/resources
         sas        /home/sas/.local/share/jupyter/kernels/sas

3. Verify SAS Executable is correct

   1. find the sascfg.py file – it is currently located in the install
      location (see above) \`[install location]/site-

.. _Jupyter Notebooks: http://www.jupyter.org
.. _SAS Viya: http://www.sas.com/en_us/software/viya.html
.. _saspy: https://github.com/sassoftware/saspy
.. _issue 11: https://github.com/sassoftware/sas_kernel/issues/11
.. _sascfg.py: https://github.com/sassoftware/saspy/blob/master/saspy/sascfg.py
.. _SAS version 9.4 or above: http://www.sas.com
.. _Jupyter: http://jupyter.org
.. _Python 3: http://www.python.org
.. _Download: https://www.continuum.io/downloads
.. _here: https://github.com/sassoftware/saspy