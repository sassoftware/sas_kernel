
from __future__ import print_function
from metakernel import Magic
#from saspy import *
import re

class SASMagic(Magic):
    def __init__(self, kernel):
        '''
        Initialize method
        '''
        from saspy import *
        #super(SASMagic, self).__init__(kernel)
        #self.repl = None
        #self.cmd = None
        #self.start_process()

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
