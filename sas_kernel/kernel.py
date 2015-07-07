from IPython.kernel.zmq.kernelbase import Kernel
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


from .images import (
    extract_image_filenames, display_data_for_image, image_setup_cmd
)


class SASKernel(Kernel):
    implementation = 'sas_kernel'
    implementation_version = __version__

    @property
    def language_version(self):
        m = version_pat.search(self.banner)
        return m.group(1)

    _banner = None

    @property
    def banner(self):
        if self._banner is None:
            self._banner = check_output(['python3.4', '--version']).decode('utf-8')
        return self._banner

    language_info = {'name': 'sas',
                     #'codemirror_mode': 'shell',
                     #'mimetype': 'text/x-sh',
                     'file_extension': '.sas'}

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        self._start_sas()

    def _start_sas(self):
        # Signal handlers are inherited by forked processes, and we can't easily
        # reset it from the subprocess. Since kernelapp ignores SIGINT except in
        # message handlers, we need to temporarily reset the SIGINT handler here
        # so that sas and its children are interruptible.
        sig = signal.signal(signal.SIGINT, signal.SIG_DFL)
        try:
            #create a shell session
            self.saswrapper = replwrap.python(command="python3.4")
            # start a SAS session within python bound to the shell session
            #startsas=self.saswrapper.run_command("from IPython.display import HTML")
            #add path to Tom's playpen. Remove before production
            startsas=self.saswrapper.run_command("import sys")
            startsas=self.saswrapper.run_command("sys.path.append('/root/tom')")
            startsas=self.saswrapper.run_command("from pysas import mva")
            startsas=self.saswrapper.run_command('mva.startsas("")')
        finally:
            signal.signal(signal.SIGINT, sig)

        # Register sas function to write image data to temporary file
        self.saswrapper.run_command(image_setup_cmd)

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
        
        if not code.strip():
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}
 
        interrupted = False
        submit_pre=str('mva.submit("')
        submit_post=str('","html")')
        sas_log=str('mva.getlog()')
        sas_lst=str('mva.getlst()')

        #remove whitespace characters
        remap = {
            ord('\t') : ' ',
            ord('\f') : ' ',
            ord('\r') : None,
            ord('\n') : None
        }
        #code='proc print data=sashelp.class; run;'
        try:
            rc = self.saswrapper.run_command(submit_pre + code.translate(remap) + submit_post, timeout=None)
            time.sleep(.5)
            # block until log send EOF
            # blocking is done automatically for HTML output b/c it can look for closing html tag


            log=self.saswrapper.run_command(sas_log,timeout=None)
            output=self.saswrapper.run_command(sas_lst,timeout=None)
            if output.startswith('\''):
               re.sub(r'^\'',r'^', output)
               print ("startswith")
            if output.endswith('\''):
               re.sub(r'\'$',r'$', output)
               print("endswith")
            self.log.debug('execute: %s' % code)


            print ('code: ' + submit_pre + code.translate(remap) + submit_post)
            print ('rc: ' + rc)
            type(log)
            print ("Output type: " + str(type(output)))
            print('Silent: ' + str(silent))
        except KeyboardInterrupt:
            self.saswrapper.child.sendintr()
            interrupted = True
            self.saswrapper._expect_prompt()
            output = self.saswrapper.child.before
        except EOF:
            output = self.saswrapper.child.before + 'Restarting SAS'
            self._start_sas()
        
        if len(output)>0: #not silent:
            output = output.replace('\\n', chr(ord('\n'))).replace('\\r',chr(ord('\r'))).replace('\\t',chr(ord('\t'))).replace('\\f',chr(ord('\f')))
            #print(output)
            newcontent={'source':'Kernel','data':{'text/plain':'<IPython.core.display.HTML object>','text/html': output},'metadata':{}}
            #newcontent={'source':"Kernel",'data':{'text/html': 'output'},'metadata':{}}
            self.send_response(self.iopub_socket, 'display_data', newcontent)
            print ("Output type (not silent): " + str(type(output)))

        else:
            log = log.replace('\\n', chr(ord('\n'))).replace('\\r',chr(ord('\r'))).replace('\\t',chr(ord('\t'))).replace('\\f',chr(ord('\f')))
            #print(output)
            newcontent={'source':'Kernel','data':{'text/plain':'<IPython.core.display.HTML object>','text/html': log},'metadata':{}}
            #newcontent={'source':"Kernel",'data':{'text/html': 'output'},'metadata':{}}
            self.send_response(self.iopub_socket, 'display_data', newcontent)

            

        if interrupted:
            return {'status': 'abort', 'execution_count': self.execution_count}

        try:
            exitcode = int(self.saswrapper.run_command('&syserr;').rstrip())
        except Exception:
            exitcode = 1

        if exitcode:
            return {'status': 'error', 'execution_count': self.execution_count,
                    'ename': '', 'evalue': str(exitcode), 'traceback': []}
        else:
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}
    #Get code complete file from EG for this
    def do_complete(self, code, cursor_pos):
        code = code[:cursor_pos]
        default = {'matches': [], 'cursor_start': 0,
                   'cursor_end': cursor_pos, 'metadata': dict(),
                   'status': 'ok'}

        if not code or code[-1] == ' ':
            return default

        tokens = code.replace(';', ' ').split()
        if not tokens:
            return default

        matches = []
        token = tokens[-1]
        start = cursor_pos - len(token)

        if token[0] == '$':
            # complete variables
            cmd = 'compgen -A arrayvar -A export -A variable %s' % token[1:] # strip leading $
            output = self.saswrapper.run_command(cmd).rstrip()
            completions = set(output.split())
            # append matches including leading $
            matches.extend(['$'+c for c in completions])
        else:
            # complete functions and builtins
            cmd = 'compgen -cdfa %s' % token
            output = self.saswrapper.run_command(cmd).rstrip()
            matches.extend(output.split())
            
        if not matches:
            return default
        matches = [m for m in matches if m.startswith(token)]

        return {'matches': sorted(matches), 'cursor_start': start,
                'cursor_end': cursor_pos, 'metadata': dict(),
                'status': 'ok'}

    def do_shutdown(restart):
        if restart:
            self.saswrapper.run_command('mva.submit(";endsas;")')




