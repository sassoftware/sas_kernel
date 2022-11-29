# SAS Kernel for Jupyter

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/sassoftware/sas_kernel/HEAD)

[![Publish Python Package](https://github.com/sassoftware/sas_kernel/actions/workflows/python-publish.yml/badge.svg)](https://github.com/sassoftware/sas_kernel/actions/workflows/python-publish.yml)
## Overview

The SAS Kernel for [Jupyter Notebooks](http://www.jupyter.org) is capable of running SAS programs from within the Jupyter interface.
The SAS kernel allows a user to leverage all of the SAS products they have licensed.

After installing the SAS kernel, you can use a notebook and a SAS installation to write, document, and submit SAS programming statements. The Jupyter notebook interface allows sharing of results through JSON and the SAS kernel is no exception, you can share code and results in a static form through the Jupyter notebook.

## Documentation

Here is the link to the current documentation <https://sassoftware.github.io/sas_kernel/>

## Prerequisites

- Python3 (this is now the default since Python2 went end of life in January 2020)
- Jupyter version 4 or higher
- SAS 9.4 or higher -- This includes [SAS Viya](http://www.sas.com/en_us/software/viya.html). The SAS kernel is compatible with any version of SAS released since July 2013.
- SASPy -- The SAS kernel has a dependency on [SASPy](https://github.com/sassoftware/saspy). The package will be installed automatically but it must be configured to access your available SAS server. **SASPy must be [configured](https://sassoftware.github.io/saspy/install.html#configuration) before the SAS kernel can work successfully**.

## Installation

This will install the SAS Kernel for jupyter as well as the Jupyter lab extensions (jupyterlab v3+ is required) to make you a more productive programmer within Jupyter. [Here are details](https://github.com/jld23/sas_kernel_ext) about the extensions.

```bash
pip install SAS-kernel['jlab_ext']
```

### The common methods to install are

1. `pip` -- PIP is the most common way to install the latest stable version of the code.

   ```bash
   pip install sas_kernel
   ```

1. `conda` -- A conda package is also available if you prefer to use conda as your package manger

   ```bash
   conda install -c anaconda sas_kernel
   ```

1. From source -- If you need to install from the source branch before a new version has been built and pushed you can install from source like this:

   ```bash
   pip install git+https://git@github.com/sassoftware/sas_kernel.git@main
   ```

   Note that the default branch is now `main` to match the GitHub convention. You can modify the about URL if you're installing from a fork or a non-default branch.

### To verify that the sas_kernel is installed

```bash
jupyter kernelspec list
```

You should see output _similar_ to code below:

```bash
Available kernels:
    python3    /home/sas/anaconda3/lib/python3.5/site-packages/ipykernel/resources
    sas        /home/sas/.local/share/jupyter/kernels/sas
```

**NOTE:** You will not be able to execute SAS code through Jupyter until you have [configured SASPy](https://sassoftware.github.io/saspy/install.html#configuration).

## Getting Started

Here is a basic example of programming with SAS and Jupyter Notebook: [Getting Started](https://sassoftware.github.io/sas_kernel/getting-started.html)

### Improving Usability

#### For the Jupyter Lab extensions

There is a seperate repository where the extensions are developed and maintained. See [that repo](https://github.com/jld23/sas_kernel_ext) for details

#### For the Legacy Jupyter Notebook

There are a few NBExtensions that have been created to make working with Jupyter notebooks more productive. These are largely the result of pain points from my use of SAS Kernel for programming tasks. The extensions can be found [here](./sas_kernel/nbextensions). The list includes:

- SAS Log -- which show the SAS log for the last executed cell or the entire log since the last (re)start of the notebook
- themes -- this allows you to change the color scheme for your code to match the traditional SAS color scheme

**NOTE:** These extensions are for Jupyter _Notebook_ they are not compatable with Jupyter _Lab_. Jupyter Lab extensions are in development and will be released shortly.

#### Installing the SAS Extensions

Details for installing the extensions for SAS can be found [here](./sas_kernel/nbextensions/README.md).

#### Jupyter Magics for the sas_kernel

There are magics that have been written specifically for the sas_kernel to get more details see the [README](./sas_kernel/magics/README.md).

### NBGrader

[nbgrader](http://nbgrader.readthedocs.org/en/stable/) is a system for assigning and grading notebooks and extends jupyter. NBgrader is compatible with the SAS kernel. The work was merged in [September 2020](https://github.com/jupyter/nbgrader/pull/1356). It will be widely available with the next release of NBGrader (0.62), until then you can install from source.

## FAQ

- Is there a SAS Magic that I can access from a python kernel?

  Yes! There are actually several cell magics available from SAS.
  They are `%%SAS`, `%%IML`, and `%%OPTMODEL`. To load these magics in your notebook, execute the following command `%load_ext saspy.sas_magic`. You can check that the magics have are successfully activated by looking at the results of `%lsmagic` and looking in the cell magic section.
  If you use multiple SAS Cell magics in the _same_ notebook they will share a SAS session (have the same WORK libname and MACROS). There is currently no sharing of SAS Sessions between different notebooks.

- Do I need to buy SAS to use this kernel?

  The SAS Kernel is simply a gateway for Jupyter notebooks to talk to SAS, as such, if SAS is not installed this kernel won't be helpful. For information on purchasing SAS [click here](http://www.sas.com/en_us/software/how-to-buy.html).

- How does Jupyter communicate with SAS?

  Behind a Jupyter notebook is a python session, that python session submits code to SAS and receives responses through various pathways (depending on the SASPy configuration). Jupyter can communicate with any SAS host (Windows, Linux, Unix, MVS) that has been released since July 2013 to present.

- How can I see my SAS log, I only see the listing output?

  SAS is different from many other programming languages in that it has two useful information streams, the log (which details the technical details of what happened and how long it took) and the lst (which includes the tables and graphics from the analysis). The SAS Kernel attempts to show you what I _think_ you want. Here are the rules:

  | LOG                         | LST | DISPLAYED                                                         | NOTES                                                                   |
  | --------------------------- | --- | ----------------------------------------------------------------- | ----------------------------------------------------------------------- |
  | Yes                         | No  | LOG                                                               | This happens when you run DATA Step or a PROC with the `noprint` option |
  | Yes                         | Yes | LST                                                               | ---                                                                     |
  | Yes (with ERROR message(s)) | Yes | ERROR messages with context from the log, then the listing output | ---                                                                     |
  | Yes (with ERROR message(s)) | No  | LOG                                                               | ---                                                                     |

  If you want to see the log but it was not displayed you can use [SASLog NBExtension](./sas_kernel/nbextensions/README.md) which will show the log for the last executed cell or the entire log since the last (re)start of the notebook.

- Will this leave a bunch of SAS sessions hanging around?

  A SAS session is started for each notebook you have open i.e. 5 notebooks open = 5 SAS sessions. Those sessions will remain active for the life of the notebook. If you shutdown your notebook, the SAS session will also terminate. In JupyterHub, there are configuration options to shutdown inactive sessions and the SAS kernel complies with those directives.

- I restarted my SAS Kernel and now my WORK library is now empty. What happened?

  When you restart the kernel in a notebook you are terminating the current SAS session and starting a new one. All of the temporary artifacts, data sets in the WORK library, assigned libnames, filename, WORK macros, and so on are destroyed.

## Contributing

The [Contributor Agreement](https://github.com/sassoftware/sas_kernel/blob/master/ContributorAgreement.txt) details how contributions can be made.

## Licensing

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at [LICENSE.txt](https://github.com/sassoftware/sas_kernel/blob/master/LICENSE.txt)

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.


Add new section for github actions
