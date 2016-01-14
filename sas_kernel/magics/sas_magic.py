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

from __future__ import print_function
from metakernel import Magic
import Ipython.core.magic as ipym
#from saspy import *
import re
import os

@ipym.magics_class
class SASMagic(ipym.Magics):
    def __init__(self, kernel):
        '''
        Start a SAS Session for code submission 
        '''
        import saspy as saspy
        executable = os.environ.get('SAS_EXECUTABLE', 'sas')
        if executable=='sas':
            executable='/opt/sasinside/SASHome/SASFoundation/9.4/sas'
        e2=executable.split('/')
        self._path='/'.join(e2[0:e2.index('SASHome')+1])
        self._version=e2[e2.index('SASFoundation')+1]
        sas=saspy.SAS_session()
        sas._startsas(path=self._path, version=self._version)
        #super(SASMagic, self).__init__(kernel)
        #self.repl = None
        #self.cmd = None
        #self.start_process()
    
    @ipym.cell_magic
    def cell_SAS(self):

        '''
        %%SAS - send the code in the cell to a SAS Server

        This cell magic will execute the contents of the cell in a SAS
        session and return any generated output

        Example:
           %%SAS
           proc print data=sashelp.class;
           run;
        '''
        res=sas.submit(self.code,'html')
        output=_clean_output(res['LST'])
        log=_clean_log(res['LOG'])
        dis=_which_display(log,output)
        return dis

    @ipym.cell_magic
    def cell_IML(self):
        '''
        %%IML - send the code in the cell to a SAS Server
                for processing by PROC IML

        This cell magic will execute the contents of the cell in a
        PROC IML session and return any generated output. The leading 
        PROC IML and trailing QUIT; are submitted automatically.

        Example:
           %%IML
           a = I(6); * 6x6 identity matrix;
           b = j(5,5,0); *5x5 matrix of 0's;
           c = j(6,1); *6x1 column vector of 1's;
           d=diag({1 2 4});
           e=diag({1 2, 3 4});

        '''
        res=sas.submit("proc iml; "+ self.cold + " quit;")
        output=_clean_output(res['LST'])
        log=_clean_log(res['LOG'])
        dis=_which_display(log,output)
        return dis


    def _which_display(log,lst):
        lst_len=30762
        lines=re.split(r'[\n]\s*',log)
        i=0
        elog=[]
        debug1=0
        for line in lines:
            i+=1
            if line.startswith('ERROR'):
                elog=lines[(max(i-5,0)):(min(i+6,len(lines)))]
        tlog='\n'.join(elog)
        if len(elog)==0 and len(lst)>lst_len: #no error and LST output
            debug1=1
            return HTML(lst)
        elif len(elog)==0 and len(lst)<=lst_len: #no error and no LST
            debug1=2
            return log
        elif len(elog)>0 and len(lst)<=lst_len: #error and no LST
            debug1=3
            return tlog
        else: #errors and LST
            debug1=4
            return tlog,HTML(lst)

    def _clean_output(output):
        output = output.replace('\\n', chr(10)).replace('\\r',chr(ord('\r'))).replace('\\t',chr(ord('\t'))).replace('\\f',chr(ord('\f')))
        output=output[0:3].replace('\'',chr(00))+output[3:-4]+output[-4:].replace('\'',chr(00))
        return output

    def _clean_log(log):
        log    = log.replace('\\n', chr(10)).replace('\\r',chr(ord('\r'))).replace('\\t',        chr(ord('\t'))).replace('\\f',chr(ord('\f')))
        log=log[0:3].replace('\'',chr(00))+log[3:-4]+log[-4:].replace('\'',chr(00))
        return log




def register_magics(kernel):
    kernel.register_magics(SASMagic)

if __name__ == '__main__':
        from IPython import get_ipython
        get_ipython().register_magics(SASMagic)

