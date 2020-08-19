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

class logMagic(Magic):
    def __init__(self, *args, **kwargs):
        super(logMagic, self).__init__(*args, **kwargs)

    def line_showLog(self):
        """
        SAS Kernel magic to show the SAS log for the previous submitted code.
        This magic is only available within the SAS Kernel
        """
        if self.kernel.mva is None:
            print("Can't show log because no session exists")
        else:
            return self.kernel._which_display(self.kernel.cachedlog)


    def line_showFullLog(self):
        """
        SAS Kernel magic to show the entire SAS log since the kernel was started (last restarted)
        This magic is only available within the SAS Kernel
        """
        if self.kernel.mva is None:
            self.kernel._allow_stdin = True
            self.kernel._start_sas()
            print("Session Started probably not the log you want")
        return self.kernel._which_display(self.kernel.mva.saslog())

def register_magics(kernel):
    kernel.register_magics(logMagic)


def register_ipython_magics():
    from metakernel import IPythonKernel
    from IPython.core.magic import register_line_magic
    kernel = IPythonKernel()
    magic = logMagic(kernel)
    # Make magics callable:
    kernel.line_magics["showLog"] = magic
    kernel.line_magics["showFullLog"] = magic

    @register_line_magic
    def showLog(line):
        kernel.call_magic("%showLog " + line)

    @register_line_magic
    def showFullLog(line):
        kernel.call_magic("%showFullLog " + line)