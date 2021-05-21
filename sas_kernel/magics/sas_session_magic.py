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
from metakernel import Magic

class SASsessionMagic(Magic):
    def __init__(self, *args, **kwargs):
        super(SASsessionMagic, self).__init__(*args, **kwargs)

    def line_SASsession(self, *args):
        """
        SAS Kernel magic allows a programatic way to submit configuration
        details.
        This magic is only available within the SAS Kernel
        """
        if len(args) > 1:
            args = ''.join(args)
        elif len(args) == 1:
            args = ''.join(args[0])
        args = args.replace(' ', '')
        args = args.replace('"', '')
        args = args.replace("'", '')
        sess_params = dict(s.split('=') for s in args.split(','))
        self.kernel._allow_stdin = True
        self.kernel._start_sas(**sess_params)

def register_magics(kernel):
    kernel.register_magics(SASsessionMagic)


def register_ipython_magics():
    from metakernel import IPythonKernel
    from IPython.core.magic import register_line_magic
    kernel = IPythonKernel()
    magic = SASsessionMagic(kernel)
    # Make magics callable:
    kernel.line_magics["SASsession"] = magic

    @register_line_magic
    def SASsession(line):
        kernel.call_magic("%SASsession " + line)
