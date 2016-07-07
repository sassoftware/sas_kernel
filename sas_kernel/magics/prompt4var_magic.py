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
from collections import OrderedDict

from metakernel import Magic


class Prompt4VarMagic(Magic):
    def __init__(self, *args, **kwargs):
        super(Prompt4VarMagic, self).__init__(*args, **kwargs)

    def line_prompt4var(self, *args):
        """
        %%prompt4var - Prompt for macro variables that will
        be assigned to the SAS session. The variables will be
        prompted each time the line magic is executed.
        Example:
        %prompt4var libpath file1
        filename myfile "~&file1.";
        libname data "&libpath";
        """
        prmpt = OrderedDict()
        for arg in args:
            assert isinstance(arg, str)
            prmpt[arg] = False
        if not len(self.code):
            if self.kernel.mva is None:
                self.kernel._allow_stdin = True
                self.kernel._start_sas()
            self.kernel.mva.submit(code=self.code, results="html", prompt=prmpt)
        else:
            self.kernel.promptDict = prmpt

    def cell_prompt4var(self, *args):
        """
        %%prompt4var - The cell magic prompts users for variables that are
        intended to be private -- passwords and such. The macro variables
        will be deleted from the when the cell finishes processing.
        Libnames assigned will still be active but the password will not
        be stored anywhere.

        Examples:
        %%prompt4var alter read
        data work.cars(alter="&alter" read="&read");
            set sashelp.cars;
            id = _n_;
        run;
        proc print data=cars(read="badpw" obs=10);
        run;
        proc print data=cars(read="&read" obs=10);
        run;


        %%prompt4var pw1 pw2
        libname foo teradata user=scott password=&pw1;
        libname bar oracle user=tiger password=&pw2;
        """
        prmpt = OrderedDict()
        for arg in args:
            assert isinstance(arg, str)
            prmpt[arg] = True
        if not len(self.code):
            if self.kernel.mva is None:
                self._allow_stdin = True
                self.kernel._start_sas()
            self.kernel.mva.submit(code=self.code, results="html", prompt=prmpt)
        else:
            self.kernel.promptDict = prmpt


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
