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
from collections import OrderedDict


class Prompt4VarMagic(Magic):
    def __init__(self, *args, **kwargs):
        super(Prompt4VarMagic, self).__init__(*args, **kwargs)

    def line_prompt4var(self, *args):
        """
        %%prompt4var - Create secret macro variables that will
        not be recorded in the Jupyter notebook or SAS log
        Example:
        %prompt4var fpath1 lib1
        filename file1 "&fpath1";
        libname foo "&lib1"
        """
        prmpt = OrderedDict()
        for arg in args:
            assert isinstance(arg, str)
            prmpt[arg] = False
        self.kernel.mva.submit(code=self.code, results="text", prompt=prmpt)

    def cell_prompt4var(self, *args):
        """
        %%prompt4var - Create secret macro variables that will
        not be recorded in the Jupyter notebook or SAS log
        Example:
        %%prompt4var pw1 pw2
        libname foo terdata user=scott password=&pw1;
        libname bar oracle user=jld23 password=&pw1;
        """

        prmpt = OrderedDict()
        for arg in args:
            assert isinstance(arg, str)
            prmpt[arg] = True
        res = self.kernel.mva.submit(code=self.code, results="HTML", prompt=prmpt)
        dis = self.kernel._which_display(res['LOG'], res['LST'])
        return dis


def register_magics(kernel):
    kernel.register_magics(Prompt4VarMagic)


def register_ipython_magics():
    from metakernel import IPythonKernel
    from IPython.core.magic import register_line_magic
    kernel = IPythonKernel()
    magic = Prompt4VarMagic(kernel)
    # Make magics callable:
    kernel.line_magics["prompt4var"] = magic

    @register_line_magic
    def prompt4var(line):
        kernel.call_magic("%prompt4var " + line)
