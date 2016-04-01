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
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from distutils.command.install import install
from distutils import log
import json
import os
import sys

try:
    from jupyter_client.kernelspec import install_kernel_spec
except ImportError:
    from IPython.kernel.kernelspec import install_kernel_spec
from IPython.utils.tempdir import TemporaryDirectory

kernel_json = {
    "argv": [sys.executable,
             "-m", "sas_kernel", "-f", "{connection_file}"],
    "display_name": "SAS",
    "codemirror_mode": "sas",
    "language": "sas"
}


class InstallWithKernelspec(install):
    def run(self):
        # Regular installation
        install.run(self)

        # Now write the kernelspec
        with TemporaryDirectory() as td:
            os.chmod(td, 0o755)  # Starts off as 700, not user readable
            with open(os.path.join(td, 'kernel.json'), 'w') as f:
                json.dump(kernel_json, f, sort_keys=True)
            log.info('Installing IPython kernel spec')
            try:
                install_kernel_spec(td, 'SAS', user=self.user, replace=True)
            except:
                print("Could not install SAS Kernel as %s user" % self.user)

setup(name='SAS_kernel',
      version='1.0',
      description='A SAS kernel for IPython',
      long_description=open('README.rst', 'rb').read().decode('utf-8'),
      author='Jared Dean',
      author_email='jared.dean@sas.com',
      url='https://github.com/sassoftware/sas_kernel',
      packages=['sas_kernel'],
      cmdclass={'install': InstallWithKernelspec},
      package_data={'sas_kernel': ['data/*.json']},
      install_requires=['pexpect>=3.3', 'metakernel', 'saspy', 'ipykernel', 'pygments', 'jupyter_client'],
      classifiers=[
          'Framework :: IPython',
          'Programming Language :: Python :: 3',
          'License :: OSI Approved :: Apache Software License',
      ]
      )
