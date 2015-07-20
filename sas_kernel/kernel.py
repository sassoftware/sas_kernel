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
#from IPython.kernel.zmq.kernelbase import Kernel
from IPython.display import HTML, display
from IPython.display import Image
from pexpect import replwrap, EOF
from metakernel import MetaKernel
from IPython.utils.jsonutil import json_clean, encode_images

from subprocess import check_output
from os import unlink

import base64
import imghdr
import re
import signal
import urllib
import time

__version__ = '0.1'

version_pat = re.compile(r'version (\d+(\.\d+)+)')

from metakernel import MetaKernel

class SASKernel(MetaKernel):
    implementation = 'sas_kernel'
    implementation_version = '1.0'
    language = 'text'
    language_version = '0.1'
    banner = "SAS Kernel"
    language_info = {'name': 'sas',
                     'file_extension': '.sas'}

    def __init__(self,**kwargs):

        MetaKernel.__init__(self, **kwargs)
        self._start_sas()

    def get_usage(self):
        return "This is the SAS kernel."

    def _start_sas(self):
        # Signal handlers are inherited by forked processes, and we can't easily
        # reset it from the subprocess. Since kernelapp ignores SIGINT except in
        # message handlers, we need to temporarily reset the SIGINT handler here
        # so that SAS and its children are interruptible.
        sig = signal.signal(signal.SIGINT, signal.SIG_DFL)
        try:
            #create a shell session
            self.saswrapper = replwrap.python(command="/root/anaconda3/bin/python3.4")
            # start a SAS session within python bound to the shell session
            #startsas=self.saswrapper.run_command("from IPython.display import HTML")
            startsas=self.saswrapper.run_command("from saspy import pysas34 as mva")
            print(startsas)
            startsas=self.saswrapper.run_command('mva.startsas()')
            print(startsas)
        finally:
            signal.signal(signal.SIGINT, sig)

        # Register sas function to write image data to temporary file
        #self.saswrapper.run_command(image_setup_cmd)

    def do_execute_direct(self, code):

        if not code.strip():
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}
        interrupted = False
        submit_pre=str('mva.submit("')
        submit_post=str('","html")')
        sas_log='mva.getlog()'
        sas_lst='mva.getlst()'

        #remove whitespace characters
        remap = {
            ord('\t') : ' ',
            ord('\f') : ' ',
            ord('\r') : None,
            ord('\n') : None
        }
        try:
            rc = self.saswrapper.run_command(submit_pre + code.translate(remap) + submit_post, timeout=None)
            time.sleep(.5) # block until log send EOF
            # blocking is done automatically for HTML output b/c it can look for closing html tag


            log=self.saswrapper.run_command(sas_log,timeout=None)
            output=self.saswrapper.run_command(sas_lst,timeout=None)
        
            type(log)

        except EOF:
            output = self.saswrapper.child.before + 'Restarting SAS'
            self._start_sas()

        output = output.replace('\\n', chr(10)).replace('\\r',chr(ord('\r'))).replace('\\t',chr(ord('\t'))).replace('\\f',chr(ord('\f')))
        newcontent={'source':"Kernel",'data':{'text/plain':'<IPython.core.display.HTML object>','text/html': output},'metadata':{}}
           
        return HTML(output)


    #Get code complete file from EG for this
    def get_completions(self,info):
        list=['proc','print','optmodel','data']
        potentials=get_close_matches(info['obj'],list)
        return potentials

    
    # def do_complete(self, code, cursor_pos):
    #     code = code[:cursor_pos]
    #     default = {'matches': [], 'cursor_start': 0,
    #                'cursor_end': cursor_pos, 'metadata': dict(),
    #                'status': 'ok'}

    #     if not code or code[-1] == ' ':
    #         return default

    #     tokens = code.replace(';', ' ').split()
    #     if not tokens:
    #         return default

    #     matches = []
    #     token = tokens[-1]
    #     start = cursor_pos - len(token)

    #     if token[0] == '$':
    #         # complete variables
    #         cmd = 'compgen -A arrayvar -A export -A variable %s' % token[1:] # strip leading $
    #         output = self.saswrapper.run_command(cmd).rstrip()
    #         completions = set(output.split())
    #         # append matches including leading $
    #         matches.extend(['$'+c for c in completions])
    #     else:
    #         # complete functions and builtins
    #         cmd = 'compgen -cdfa %s' % token
    #         output = self.saswrapper.run_command(cmd).rstrip()
    #         matches.extend(output.split())
            
    #     if not matches:
    #         return default
    #     matches = [m for m in matches if m.startswith(token)]

    #     return {'matches': sorted(matches), 'cursor_start': start,
    #             'cursor_end': cursor_pos, 'metadata': dict(),
    #             'status': 'ok'}
    
    def do_shutdown(self,restart):
        if restart:
            self.saswrapper.run_command('mva.submit(";endsas;")')




