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
try:
    from jupyter_client.kernelspec import install_kernel_spec
except ImportError:
    from IPython.kernel.kernelspec import install_kernel_spec

from distutils.command.install import install
from distutils import log
from IPython.utils.tempdir import TemporaryDirectory
import json
import os
import sys


kernel_json = {
    "argv": [sys.executable,
             "-m", "sas_kernel", "-f", "{connection_file}"],
    "display_name": "SAS",
    "codemirror_mode": "sas",
    "language": "sas"
}
# Create temp directory for install of kernel.json and logo files
tempdir = TemporaryDirectory()
temppath = str(tempdir).split('\'')[1]

svem_flag = '--single-version-externally-managed'
if svem_flag in sys.argv:
    sys.argv.remove(svem_flag)


class InstallWithKernelspec(install):
    def run(self):
        # Regular installation
        install.run(self)

        # Now write the kernelspec
        with tempdir:
            os.chmod(temppath, 0o755)  # Starts off as 700, not user readable
            log.info('Installing IPython kernel spec')
            with open(os.path.join(temppath, 'kernel.json'), 'w') as f:
                json.dump(kernel_json, f, sort_keys=True)
            log.info('files copied to kernel:')
            for i in os.listdir(temppath):
                log.info(i)
            try:
                install_kernel_spec(temppath, 'SAS', user=False, replace=True)
                print("SAS Kernel installed as superuser: %s " % self.user)
            except:
                install_kernel_spec(temppath, 'SAS', user=True, replace=True)
                print("SAS Kernel installed as user: %s " % self.user)

setup(name='SAS_kernel',
      version='1.2',
      description='A SAS kernel for IPython',
      long_description=open('README.rst', 'rb').read().decode('utf-8'),
      author='Jared Dean',
      license='Apache Software License',
      author_email='jared.dean@sas.com',
      url='https://github.com/sassoftware/sas_kernel',
      packages=find_packages(),
      cmdclass={'install': InstallWithKernelspec},
      package_data={'': ['*.js', '*.md', '*.yaml', '*.css'], 'sas_kernel': ['data/*.json', 'data/*.png']},
      data_files=[(temppath, ['sas_kernel/data/logo-64x64.png'])],
      install_requires=['pexpect>=3.3', 'metakernel', 'saspy>=1.2.1', 'ipykernel', 'pygments', 'jupyter'],
      classifiers=[
          'Framework :: IPython',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3',
      ]
      )
