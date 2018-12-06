# SAS Kernel for Jupyter

# Overview

A SAS Kernel for [Jupyter Notebooks](http://www.jupyter.org) Jupyter Notebooks are capable of running programs in a variety of programming languages and it is the kernel that enables this ability. The SAS kernel enables Jupyter Notebook to provide the following programming experience:
- syntax highlighting for SAS programming statements
- store the input and output from an interactive SAS session

After installing the SAS kernel, you can use a notebook and a SAS installation to write, document, and submit SAS programming statements.
## Documentation
Here is the link to the current documentation https://sassoftware.github.io/sas_kernel/

# Prerequisites
* Python3.X
* Jupyter version 4 or higher
* SAS 9.4 or higher  -- This includes [SAS Viya](http://www.sas.com/en_us/software/viya.html)

With the latest changes in [saspy](https://github.com/sassoftware/saspy) it is no longer a requirement that Jupyter and SAS be installed on the same machine. SAS and Jupyter can now communicate via passwordless ssh or IOM. This is in response to [issue 11](https://github.com/sassoftware/sas_kernel/issues/11). The configuration details are located in [sascfg.py](https://github.com/sassoftware/saspy/blob/master/saspy/sascfg.py) and documentation for configuration is [here](https://sassoftware.github.io/saspy/install.html#configuration)



# Installation
To successfully use the SAS Kernel you must have each of the following:
* [SAS version 9.4 or above](http://www.sas.com)
* [Jupyter](http://jupyter.org)
    * Jupyter has a number of dependencies. See the subsections for steps on installing Jupyter on your system.
* [Python 3](http://www.python.org)

## Install for Anaconda Python (assuming SAS already installed)
1. [Download](https://www.continuum.io/downloads) and install Anaconda Python (make sure you get Python3.X). If you install Anaconda without super user rights (root or sudo) then other users on the system will not be able to access the SAS kernel.
   A couple notes that I've observed:
   * The default install location is the users home directory. This is fine for a single user install I would put it in a common location (`/opt`) if you're doing a system wide install
   * One of the prompts is to add the path to your environment. I recommend you want to answer 'yes' to that question so that all the installing user has the executables in their path. If you're doing a system wide install (root or sudo) all the other users should add that path to their environmental variables  
1. Install sas_kernel. The sas_kernel has a dependency on saspy which is located [here](https://github.com/sassoftware/saspy).
   In the command below I'm assuming that `pip` maps to python3 if that is not the case the you might need to use `pip3` instead. 
   ```
   pip install sas_kernel
   ```
 
1. Verify that the sas_kernel is installed
`jupyter kernelspec list`

    If you installed as a superuser, your output should similar to this:
    ```
    Available kernels:
      python3    /opt/Anaconda3-2.5.0/lib/python3.5/site-packages/ipykernel/resources
      sas        /usr/local/share/jupyter/kernels/sas
    ```

    If you installed as a regular user (sas in this case), your output should similar to this:
    ```
    Available kernels:
      python3    /home/sas/anaconda3/lib/python3.5/site-packages/ipykernel/resources
      sas        /home/sas/.local/share/jupyter/kernels/sas
    ```
1. Verify SAS Executable is correct
    1. find the sascfg.py file -- it is currently located in the install location (see above) `[install location]/site-packages/saspy/sascfg.py`. To query `pip` for the location of the file, type `pip show saspy` (or `pip3 show saspy` if `pip3` was used to install it). Failing that, this command will search the OS for the file location: `find / -name sascfg.py`
    1. edit the file with the correct path the SAS executable and include any options you wish it include in the SAS invocation. See examples in the [file](https://github.com/sassoftware/saspy/blob/master/saspy/sascfg.py)


## Install for Centos 6 (assuming SAS already installed)
These instructions assume you'll be installed system wide for all users using a superuser account (root or sudo)

1. yum packages
   ```
   sudo yum install https://centos6.iuscommunity.org/ius-release.rpm
   sudo yum install python35u gcc-c++ python35u-devel python35u-pip python35u-tools
   ```
 
1. pip
   ```
   wget https://bootstrap.pypa.io/get-pip.py
   python3.5 get-pip.py
   pip3 --version
   ```
 
1. jupyter and sas_kernel. The sas_kernel has a dependency on saspy which is located [here](https://github.com/sassoftware/saspy).
   ```
   pip3.5 install jupyter
   pip3.5 install sas_kernel
   ```
 
1. Verify that the sas_kernel is installed
`jupyter kernelspec list`

    This should produce output similar to this:
    ```
    Available kernels:
      python3    /usr/lib/python3.5/site-packages/ipykernel/resources
      sas        /usr/local/share/jupyter/kernels/sas
    ```

 
1. Verify SAS Executable is correct
    1. find the sascfg.py file -- it is currently located in the site-packages area of python install. To query `pip` for the location of the file, type `pip show saspy` (or `pip3 show saspy` if `pip3` was used to install it). Failing that, this command will search the OS for the file location: ` find / -name sascfg.py`
    1. edit the file with the correct path the SAS executable and include any options you wish it include in the SAS invocation. See examples in the file
    
# Getting Started
Here is a basic example of programming with SAS and Jupyter Notebook: [Getting Started](https://sassoftware.github.io/sas_kernel/getting-started.html)
## Improving Usability
There are a few NBExtensions that have been created to make working with Jupyter notebooks more productive. These are largely the result of pain points from my use of SAS Kernel for programming tasks. The extensions can be found [here](./sas_kernel/nbextensions). The list includes:
* SAS Log -- which show the SAS log for the last executed cell or the entire log since the last (re)start of the notebook
* themes -- this allows you to change the color scheme for your code to match the traditional SAS color scheme

### Installing the SAS Extensions
Details for installing the extensions for SAS can be found [here](./sas_kernel/nbextensions/README.md)
**The install experience was improved with version 1.2**

### Jupyter Magics for the sas_kernel
There are magics that have been written specifically for the sas_kernel to get more details see the [README](./sas_kernel/magics/README.md) 

## Jupyterhub
The SAS kernel can be used with JupyterHub for more information look [here](https://jupyterhub.readthedocs.org/en/latest/) 

## NBGrader
[nbgrader](http://nbgrader.readthedocs.org/en/stable/) is a system for assigning and grading notebooks and extends jupyter. I have a number of contributions that I'm currently working on in conjunction with teaching SAS programming in a classroom setting. You can see my forked repo [here](https://github.com/jld23/nbgrader)

# FAQ
* Is there a SAS Magic that I can access from a python kernel?

    Yes! There are actually several cell magics available from SAS. 
    They are `%%SAS`, `%%IML`, and `%%OPTMODEL`. To load these magics in your notebook, execute the following command `%load_ext saspy.sas_magic`. You can check that the magics have are successfully activated by looking at the results of `%lsmagic` and looking in the cell magic section.
    If you use multiple SAS Cell magics in the *same* notebook they will share a SAS session (have the same WORK libname and MACROS). There is currently no sharing of SAS Sessions between different notebooks.

* Do I need to buy SAS to use this kernel?

   The SAS Kernel is simply a gateway for Jupyter notebooks to talk to SAS, as such, if SAS is not installed this kernel won't be that helpful. For information on purchasing SAS [click here](http://www.sas.com/en_us/software/how-to-buy.html)

* How does Jupyter communicate with SAS?

    Behind a Jupyter notebook is a python session, that python session submits code to SAS and receives responses through socket i/o (leveraging stdin , stdout, and stderr) which has been supported in SAS for a long time

* If stdin, stdout, and stderr have been supported for so long why do I need to have SAS 9.4 or newer?

    First, SAS 9.4 was released in July 2013 so it isn't exactly a bleeding edge requirement. The reason for a prerequisite for SAS 9.4 is because that was the first release that supported the creation of HTML5 documents and that is the returned output so that we can render attractive tables and graphs automagically

* How can I see my SAS log, I only see the listing output?

    SAS is different from many other programming languages in that it has two useful information streams, the log (which details the technical details of what happened and how long it took) and the lst (which includes the tables and graphics from the analysis).  The SAS Kernel attempts to show you I *think* you want.  Here are the rules:
        
    LOG|LST|DISPLAYED| NOTES
    ---|---|---|---
    Yes|No|LOG|This happens when you run DATA Step or a PROC with the `noprint` option
    Yes|Yes|LST|---
    Yes (with ERROR message(s))|Yes|ERROR messages with context from the log, then the listing output|---
    Yes (with ERROR message(s))|No|LOG|---


    If you want to see the log but it was not displayed you can use [SASLog NBExtension](./sas_kernel/nbextensions/README.md) which will show the log for the last executed cell or the entire log since the last (re)start of the notebook

* Will this leave a bunch of SAS sessions hanging around?

    A SAS session is started for each notebook you have open i.e. 5 notebooks open = 5 SAS sessions. Those sessions will remain active for the life of the notebook. If you shutdown your notebook, the SAS session will also terminate. In Jupyterhub, there are configuration options to shutdown inactive sessions and the SAS kernel complies with those directives.

* I restarted my SAS Kernel and now my WORK library is now empty. What happened?

    When you restart the kernel in a notebook you are terminating the current SAS session and starting a new one. All of the temporary artifacts, data sets in the WORK library, assigned libnames, filename, WORK macros, and so on are destroyed.

## Contributing
The [Contributor Agreement](https://github.com/sassoftware/sas_kernel/blob/master/ContributorAgreement.txt) details how contributions can be made.

## Licensing
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at [LICENSE.txt](https://github.com/sassoftware/sas_kernel/blob/master/LICENSE.txt) 

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.




Copyright SAS Institute.
