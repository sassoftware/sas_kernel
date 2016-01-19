
from __future__ import print_function
from metakernel import Magic
import re

class SASMagic(Magic):
    
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
        import saspy as saspy
        self.mva=saspy.SAS_session()
        self.mva._startsas()#path=self._path, version=self._version)
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
        import saspy as saspy
        self.mva=saspy.SAS_session()
        self.mva._startsas()#path=self._path, version=self._version)
        res=sas.submit("proc iml; "+ self.cold + " quit;")
        output=_clean_output(res['LST'])
        log=_clean_log(res['LOG'])
        dis=_which_display(log,output)
        return dis

    @ipym.cell_magic
    def OPTMODEL(self):
        '''
        %%OPTMODEL - send the code in the cell to a SAS Server
                for processing by PROC OPTMODEL

        This cell magic will execute the contents of the cell in a
        PROC OPTMODEL session and return any generated output. The leading 
        PROC OPTMODEL and trailing QUIT; are submitted automatically.

        Example:
        proc optmodel;
           /* declare variables */
           var choco >= 0, toffee >= 0;

           /* maximize objective function (profit) */
           maximize profit = 0.25*choco + 0.75*toffee;

           /* subject to constraints */
           con process1:    15*choco +40*toffee <= 27000;
           con process2:           56.25*toffee <= 27000;
           con process3: 18.75*choco            <= 27000;
           con process4:    12*choco +50*toffee <= 27000;
           /* solve LP using primal simplex solver */
           solve with lp / solver = primal_spx;
           /* display solution */
           print choco toffee;
        quit;

        '''
        import saspy as saspy
        self.mva=saspy.SAS_session()
        self.mva._startsas()#path=self._path, version=self._version)
        res=sas.submit("proc optmodel; "+ self.code + " quit;")
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
