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
from metakernel import MetaKernel
import base64

from IPython.display import HTML, display
import os
import re
import signal
import json

#color syntax for the SASLog
from saspy.SASLogLexer import *

#Create Logger
import logging
logger= logging.getLogger('')
logger.setLevel(logging.WARN)


__version__ = '0.1'

version_pat = re.compile(r'version (\d+(\.\d+)+)')

from metakernel import MetaKernel
from . import __version__


class SASKernel(MetaKernel):
    implementation = 'sas_kernel'
    implementation_version = '1.0'
    language = 'sas'
    language_version = __version__,
    banner = "SAS Kernel"
    language_info = {'name': 'sas',
                     'mimetype': 'text/x-sas',
                     "codemirror_mode": "SAS",
                     "version": __version__,
                     'file_extension': '.sas'
                     }
    def __init__(self,**kwargs):
        #the filepath below assumes that the json files are in the same directory as the kernel.py
        #which should be fine since they will be delivered as part of the pip module
        with open(os.path.dirname(os.path.realpath(__file__))+'/data/'+'sasproclist.json') as proclist:
            self.proclist=json.load(proclist)
        with open(os.path.dirname(os.path.realpath(__file__))+'/data/'+'sasgrammerdictionary.json') as compglo:
            self.compglo=json.load(compglo)
        self.strproclist='\n'.join(str(x) for x in self.proclist)
        MetaKernel.__init__(self, **kwargs)
        self.mva = None
        self.cachedlog= None
        executable = os.environ.get('SAS_EXECUTABLE', 'sas')
        if executable=='sas':
            executable='/opt/sasinside/SASHome/SASFoundation/9.4/sas'
        e2=executable.split('/')
        self._path='/'.join(e2[0:e2.index('SASHome')+1])
        self._version=e2[e2.index('SASFoundation')+1] 
        self._start_sas()
        print(dir(self))

    def get_usage(self):
        return "This is the SAS kernel."

    def _start_sas(self):
        # Signal handlers are inherited by forked processes, and we can't easily
        # reset it from the subprocess. Since kernelapp ignores SIGINT except in
        # message handlers, we need to temporarily reset the SIGINT handler here
        # so that SAS and its children are interruptible.
        sig = signal.signal(signal.SIGINT, signal.SIG_DFL)
        try:
            # start a SAS session within python bound to the shell session
            import saspy as saspy
            print("In _start_sas" + self._path + self._version)
            self.mva=saspy.SAS_session()
            self.mva._startsas(path=self._path, version=self._version)
        finally:
            signal.signal(signal.SIGINT, sig)

    def _which_display(self,log,output,lst_len):
        lines=re.split(r'[\n]\s*',log)
        i=0
        elog=[]
        debug1=0
        for line in lines:
            i+=1
            e=[]
            if line.startswith('ERROR'):
                logger.debug("In ERROR Condition")
                e=lines[(max(i-15,0)):(min(i+16,len(lines)))]
            elog=elog+e
        tlog='\n'.join(elog)
        logger.debug("elog count: "+str(len(elog))) 
        logger.debug("tlog: " +str(tlog))
        
        color_log=highlight(log,SASLogLexer(), HtmlFormatter(full=True, style=SASLogStyle, lineseparator="<br>"))
        #store the log for display in showSASLog
        self.cachedlog=color_log
        #Are there errors in the log? if show the lines on each side of the error
        if len(elog)==0 and len(output)>lst_len: #no error and LST output
            debug1=1
            logger.debug("DEBUG1: " +str(debug1)+ " no error and LST output ")
            return HTML(output)
        elif len(elog)==0 and len(output)<=lst_len: #no error and no LST
            debug1=2
            logger.debug("DEBUG1: " +str(debug1)+ " no error and no LST")
            return HTML(color_log)
        elif len(elog)>0 and len(output)<=lst_len: #error and no LST
            debug1=3
            logger.debug("DEBUG1: " +str(debug1)+ " error and no LST")
            return HTML(color_log)
        else: #errors and LST
            debug1=4
            logger.debug("DEBUG1: " +str(debug1)+ " errors and LST")
            return HTML(color_log+output)

    def do_execute_direct(self, code):
        if not code.strip():
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}
        interrupted = False
        lst_len=30762 # the length of the html5 with no real listing output

        if re.match(r'endsas;',code):
            self.do_shutdown(False)
        if code.startswith('Obfuscated SAS Code'):
            logger.debug("decoding string")
            tmp1=code.split()
            decode=base64.b64decode(tmp1[-1])
            code=decode.decode('utf-8')
        
        if (code.startswith('showSASLog_11092015')==False and code.startswith("CompleteshowSASLog_11092015")==False): 
            logger.debug("code type: " +str(type(code)))
            logger.debug("code length: " + str(len(code)))
            logger.debug("code string: "+ code)
            if code.startswith("/*SASKernelTest*/"):
                 res=self.mva.submit(code, "text")
            else: 
                 res=self.mva.submit(code)
            output=res['LST']
            log=res['LOG']            
            dis=self._which_display(log,output,lst_len)
            return dis
        elif code.startswith("CompleteshowSASLog_11092015")==True and code.startswith('showSASLog_11092015')==False:
            full_log=highlight(self.mva._log,SASLogLexer(), HtmlFormatter(full=True, style=SASLogStyle, lineseparator="<br>", title="Full SAS Log"))
            return full_log.replace('\n',' ')
        else:
            return self.cachedlog.replace('\n',' ')

    def get_completions(self,info):
        if info['line_num']>1:
            relstart=info['column']-(info['help_pos']-info['start'])
        else:
            relstart=info['start']
        seg=info['line'][:relstart]
        if relstart>0 and re.match('(?i)proc',seg.rsplit(None, 1)[-1]):
            #taking the path ro proclist
            #potentials=re.findall('(?i)'+info['obj']+'\W\w+',self.strproclist)
            potentials=re.findall('(?i)^'+info['obj']+'.*',self.strproclist,re.MULTILINE)
            return potentials
        else:
            #we are in the middle we should determine if it is "foop" or "foos"
            lastproc=info['code'].lower()[:info['help_pos']].rfind('proc')
            lastdata=info['code'].lower()[:info['help_pos']].rfind('data ')
            proc=False
            data=False
            if lastproc+lastdata==-2:
                somewhereelse=True
            else:
                if lastproc>lastdata: 
                    proc=True
                else: 
                    data=True
            

            if proc:
                #we are not in data section should see if proc option or statement
                lastsemi=info['code'].rfind(';')
                mykey='s'
                if lastproc>lastsemi:
                    mykey='p'
                procer=re.search('(?i)proc\s\w+',info['code'][lastproc:])
                method=procer.group(0).split(' ')[-1].upper()+mykey
                mylist=self.compglo[method][0]
                potentials=re.findall('(?i)'+info['obj']+'.+','\n'.join(str(x) for x in mylist),re.MULTILINE)
                return potentials
            elif data:
                #we are in statements (probably if there is no data)
                #assuming we are in the middle of the code
                
                lastsemi=info['code'].rfind(';')
                mykey='s'
                if lastproc>lastsemi:
                    mykey='p'
                mylist=self.compglo['DATA'+mykey][0]
                potentials=re.findall('(?i)^'+info['obj']+'.*','\n'.join(str(x) for x in mylist),re.MULTILINE)
                return potentials
        #keep in mind lin_num
            
            else:
                potentials=['']    
                return potentials
     
    def _get_right_list(s):
        proc_opt  = re.search(r"proc\s(\w+).*?[^;]\Z", s, re.IGNORECASE|re.MULTILINE)
        proc_stmt = re.search(r"\s*proc\s*(\w+).*;.*\Z", s, re.IGNORECASE|re.MULTILINE)
        data_opt  = re.search(r"\s*data\s*[^=].*[^;]?.*$", s, re.IGNORECASE|re.MULTILINE)
        data_stmt = re.search(r"\s*data\s*[^=].*[^;]?.*$", s, re.IGNORECASE|re.MULTILINE)
        print (s)
        if proc_opt:
            logger.debug(proc_opt.group(1).upper()+'p')
            return (proc_opt.group(1).upper()+'p')
        elif proc_stmt:
            logger.debug(proc_stmt.group(1).upper()+'s')
            return (proc_stmt.group(1).upper()+'s')
        elif data_opt:
            logger.debug("data step")
            return ('DATA'+'p')
        elif data_stmt:
            logger.debug("data step")
            return ('DATA'+'s')
        else:
            return(None)


    def initialize_debug(self,code):
        '''SAS does not have formal debug tools from this interface'''
        print (code)
        return None

    def do_shutdown(self,restart):
        """
        Shut down the app gracefully, saving history.
        """
        print ("in shutdown function")
        if self.hist_file:
            with open(self.hist_file, 'wb') as fid:
                data = '\n'.join(self.hist_cache[-self.max_hist_cache:])
                fid.write(data.encode('utf-8'))
        if restart:
            self.Print("Restarting kernel...")
            self.reload_magics()
            self.restart_kernel()
            self.Print("Done!")
        return {'status': 'ok', 'restart': restart}
        self.SASLog(0) # Delete the log file

if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=SASKernel)

