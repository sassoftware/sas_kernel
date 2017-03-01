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
from distutils import log
from shutil import copyfile

import json
import os
import sys
from sas_kernel import __version__
from sas_kernel.data import _dataRoot

kernel_json = {
    "argv": [sys.executable,
             "-m", "sas_kernel", "-f", "{connection_file}"],
    "display_name": "SAS",
    "codemirror_mode": "sas",
    "language": "sas"
}

svem_flag = '--single-version-externally-managed'
if svem_flag in sys.argv:
    sys.argv.remove(svem_flag)


class InstallWithKernelspec(install):
    def run(self):
        try:
            from jupyter_client.kernelspec import install_kernel_spec
        except ImportError:
            try:
                from IPython.kernel.kernelspec import install_kernel_spec
            except ImportError:
                print("Please install either Jupyter to IPython before continuing")

        # Regular installation
        install.run(self)

        from IPython.utils.tempdir import TemporaryDirectory

        # Now write the kernelspec
        with TemporaryDirectory() as temppath:
            os.chmod(temppath, 0o755)  # Starts off as 700, not user readable
            log.info('Installing Jupyter kernel spec')
            with open(os.path.join(temppath, 'kernel.json'), 'w') as f:
                json.dump(kernel_json, f, sort_keys=True)
            copyfile(os.path.join(_dataRoot, 'logo-64x64.png'), os.path.join(temppath, 'logo-64x64.png'))

            log.info('files copied to kernel:')
            for i in os.listdir(temppath):
                log.info(i)
            try:
                install_kernel_spec(temppath, 'SAS', user=False, replace=True)
                print("SAS Kernel installed as superuser")
            except:
                install_kernel_spec(temppath, 'SAS', user=True, replace=True)
                print("SAS Kernel installed as user")

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
      install_requires=['saspy>=1.2.2', 'pygments', "metakernel>=0.18.0", "jupyter_client >=4.4.0",
                        "ipython>=4.0.0"
                        ],
      classifiers=['Framework :: IPython',
                   'License :: OSI Approved :: Apache Software License',
                   "Programming Language :: Python :: 3.4",
                   "Programming Language :: Python :: 3.5",
                   "Topic :: System :: Shells"]
      )
