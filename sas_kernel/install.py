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

"""Script that installs the kernel"""

import os
import sys
import json
import getopt
from shutil import copyfile
from .data import _dataRoot

try:
    from jupyter_client.kernelspec import install_kernel_spec
except ImportError:
    try:
        from IPython.kernel.kernelspec import install_kernel_spec
    except ImportError:
        print("Please install either Jupyter to IPython before continuing")
from IPython.utils.tempdir import TemporaryWorkingDirectory

kernel_json = {
    "argv": [sys.executable,
             "-m", "sas_kernel", "-f", "{connection_file}"],
    "display_name": "SAS",
    "codemirror_mode": "sas",
    "language": "sas",
    "name": "sas",
}


def install_my_kernel_spec(user=True, prefix=None):
    user = '--user' in sys.argv or not _is_root()
    with TemporaryWorkingDirectory() as td:
        os.chmod(td, 0o755)  # Starts off as 700, not user readable

        with open(os.path.join(td, 'kernel.json'), 'w') as f:
            json.dump(kernel_json, f, sort_keys=True)

        copyfile(os.path.join(_dataRoot, 'logo-64x64.png'),
                 os.path.join(td, 'logo-64x64.png'))

        try:
            install_kernel_spec(td, kernel_json['name'], user=user,
                                replace=True, prefix=prefix)
        except OSError:
            install_kernel_spec(td, kernel_json['name'], user=not user,
                                replace=True, prefix=prefix)


def main(argv=()):
    prefix = None
    user = not _is_root()

    opts, _ = getopt.getopt(argv[1:], '', ['user', 'prefix='])
    for k, v in opts:
        if k == '--user':
            user = True
        elif k == '--prefix':
            prefix = v
            user = False

    install_my_kernel_spec(user=user, prefix=prefix)


def _is_root():
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False  # assume not an admin on non-Unix platforms


if __name__ == '__main__':
    main(argv=sys.argv)
