A simple IPython kernel for SAS

This requires IPython 3.

To use it, install with ``pip install sas_kernel``, and then run one of:

.. code:: shell

    ipython notebook
    # In the notebook interface, select SAS from the 'New' menu
    ipython qtconsole --kernel sas
    ipython console --kernel sas

For details of how this works, see IPython's docs on `wrapper kernels
<http://ipython.org/ipython-doc/dev/development/wrapperkernels.html>`_, and
Pexpect's docs on the `replwrap module
<http://pexpect.readthedocs.org/en/latest/api/replwrap.html>`_
