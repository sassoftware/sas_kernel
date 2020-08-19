#!/usr/bin/env python3
#
# Copyright SAS Institute
#
#  Licensed under the Apache License, Version 2.0 (the License);
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages
from distutils.command.install import install

import os
import sys
from sas_kernel.version import __version__

svem_flag = '--single-version-externally-managed'
if svem_flag in sys.argv:
    sys.argv.remove(svem_flag)


class InstallWithKernelspec(install):
    def run(self):
        # Regular installation
        install.run(self)

        # Kernel installation
        if "NO_KERNEL_INSTALL" in os.environ:
            # If the NO_KERNEL_INSTALL env variable is set then skip the kernel installation.
            return
        else:
            from sas_kernel import install as kernel_install
            kernel_install.main(argv=sys.argv)


setup(name='SAS_kernel',
      version=__version__,
      description='A SAS kernel for Jupyter',
      long_description=open('README.rst', 'rb').read().decode('utf-8'),
      author='Jared Dean',
      license='Apache Software License',
      author_email='jared.dean@sas.com',
      url='https://github.com/sassoftware/sas_kernel',
      packages=find_packages(),
      cmdclass={'install': InstallWithKernelspec},
      package_data={'': ['*.js', '*.md', '*.yaml', '*.css'], 'sas_kernel': ['data/*.json', 'data/*.png']},
      install_requires=['saspy>=3', "metakernel>=0.24.0", "jupyter_client >=4.4.0",
                        "ipython>=5.0.0"
                        ],
      classifiers=['Framework :: IPython',
                   'License :: OSI Approved :: Apache Software License',
                   "Programming Language :: Python :: 3.4",
                   "Programming Language :: Python :: 3.5",
                   "Programming Language :: Python :: 3.6",
                   "Programming Language :: Python :: 3.7",
                   "Programming Language :: Python :: 3.8",
                   "Topic :: System :: Shells"]
      )
