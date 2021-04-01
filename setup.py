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

from distutils.command.install import install
import sys
import os
from setuptools import setup, find_packages
exec(open('./sas_kernel/version.py').read())
print("Installing sas_kernel version:{}".format(__version__))


SVEM_FLAG = '--single-version-externally-managed'
if SVEM_FLAG in sys.argv:
    sys.argv.remove(SVEM_FLAG)


class InstallWithKernelspec(install):
    def run(self):
        # Regular installation
        install.run(self)

        # Kernel installation
        if "NO_KERNEL_INSTALL" in os.environ:
            # If the NO_KERNEL_INSTALL env variable is set then skip the kernel installation.
            return
        else:
            import sas_kernel.install as kernel_install
            kernel_install.main(argv=sys.argv)


setup(name='SAS_kernel',
      version=__version__,
      packages=find_packages(),
      cmdclass={'install': InstallWithKernelspec},
      package_data={'': ['*.js', '*.md', '*.yaml', '*.css'],
                    'sas_kernel': ['data/*.json', 'data/*.png']}
      )
