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
from IPython.kernel.zmq.kernelbase import Kernel
from pexpect import replwrap, EOF

from subprocess import check_output
from os import unlink

import base64
import imghdr
import re
import signal
import urllib

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
            self._banner = check_output(['sas', '--version']).decode('utf-8')
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
            startsas=self.saswrapper.run_command("python3.4")
            startsas=self.saswrapper.run_command("import pysas")
            startsas=self.saswrapper.run_command('pysas.startsas("hi")')
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
        submit_pre=str('pysas.submit("')
        submit_post=str('")')
        sas_log=str('pysas.getlog()')
        sas_lst=str('pysas.getlst()')
        #code='proc print data=sashelp.class; run;'
        try:
            rc = self.saswrapper.run_command(submit_pre + code.rstrip() + submit_post, timeout=None)
            time.sleep(3)
            output=self.saswrapper.run_command(sas_lst, timeout=None)
        except KeyboardInterrupt:
            self.saswrapper.child.sendintr()
            interrupted = True
            self.saswrapper._expect_prompt()
            output = self.saswrapper.child.before
        except EOF:
            output = self.saswrapper.child.before + 'Restarting SAS'
            self._start_sas()

        if not silent:
            image_filenames, output = extract_image_filenames(output)

            # Send standard output
            stream_content = {'name': 'stdout', 'text': output}
            self.send_response(self.iopub_socket, 'stream', stream_content)

            # Send images, if any
            for filename in image_filenames:
                try:
                    data = display_data_for_image(filename)
                except ValueError as e:
                    message = {'name': 'stdout', 'text': str(e)}
                    self.send_response(self.iopub_socket, 'stream', message)
                else:
                    self.send_response(self.iopub_socket, 'display_data', data)

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


