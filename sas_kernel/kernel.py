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

from IPython.display import HTML
import os
import re
import json
from . import __version__


# color syntax for the SASLog
from saspy.SASLogLexer import SASLogStyle, SASLogLexer
from pygments.formatters import HtmlFormatter
from pygments import highlight

# Create Logger
import logging

logger = logging.getLogger('')
logger.setLevel(logging.WARN)

version_pat = re.compile(r'version (\d+(\.\d+)+)')


class SASKernel(MetaKernel):
    implementation = 'sas_kernel'
    implementation_version = '1.0'
    language = 'sas'
    language_version = __version__,
    banner = "SAS Kernel"
    language_info = {'name': 'sas',
                     'mimetype': 'text/x-sas',
                     "codemirror_mode": "sas",
                     'file_extension': '.sas'
                     }

    def __init__(self, **kwargs):
        with open(os.path.dirname(os.path.realpath(__file__)) + '/data/' + 'sasproclist.json') as proclist:
            self.proclist = json.load(proclist)
        with open(os.path.dirname(os.path.realpath(__file__)) + '/data/' + 'sasgrammardictionary.json') as compglo:
            self.compglo = json.load(compglo)
        self.strproclist = '\n'.join(str(x) for x in self.proclist)
        self.promptDict = {}
        MetaKernel.__init__(self, **kwargs)
        self.mva = None
        self.cachedlog = None
        self.lst_len = -99  # initialize the length to a negative number to trigger function
        # print(dir(self))

    def do_apply(self, content, bufs, msg_id, reply_metadata):
        pass

    def do_clear(self):
        pass

    def get_usage(self):
        return "This is the SAS kernel."

    def _get_lst_len(self):
        code = "data _null_; run;"
        res = self.mva.submit(code)
        assert isinstance(res, dict)
        self.lst_len = len(res['LST'])
        assert isinstance(self.lst_len, int)
        return

    def _start_sas(self):
        try:
            import saspy as saspy
            self.mva = saspy.SASsession(kernel=self)
        except:
            self.mva = None

    def _which_display(self, log, output):
        lines = re.split(r'[\n]\s*', log)
        i = 0
        elog = []
        for line in lines:
            i += 1
            e = []
            if line.startswith('ERROR'):
                logger.debug("In ERROR Condition")
                e = lines[(max(i - 15, 0)):(min(i + 16, len(lines)))]
            elog = elog + e
        tlog = '\n'.join(elog)
        logger.debug("elog count: " + str(len(elog)))
        logger.debug("tlog: " + str(tlog))

        color_log = highlight(log, SASLogLexer(), HtmlFormatter(full=True, style=SASLogStyle, lineseparator="<br>"))
        # store the log for display in the showSASLog nbextension
        self.cachedlog = color_log
        # Are there errors in the log? if show the lines on each side of the error
        if len(elog) == 0 and len(output) > self.lst_len:  # no error and LST output
            debug1 = 1
            logger.debug("DEBUG1: " + str(debug1) + " no error and LST output ")
            return HTML(output)
        elif len(elog) == 0 and len(output) <= self.lst_len:  # no error and no LST
            debug1 = 2
            logger.debug("DEBUG1: " + str(debug1) + " no error and no LST")
            return HTML(color_log)
        elif len(elog) > 0 and len(output) <= self.lst_len:  # error and no LST
            debug1 = 3
            logger.debug("DEBUG1: " + str(debug1) + " error and no LST")
            return HTML(color_log)
        else:  # errors and LST
            debug1 = 4
            logger.debug("DEBUG1: " + str(debug1) + " errors and LST")
            return HTML(color_log + output)

    def do_execute_direct(self, code, silent=False):
        if not code.strip():
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}

        if self.mva is None:
            self._allow_stdin = True
            self._start_sas()

        if self.lst_len < 0:
            self._get_lst_len()

        if code.startswith('Obfuscated SAS Code'):
            logger.debug("decoding string")
            tmp1 = code.split()
            decode = base64.b64decode(tmp1[-1])
            code = decode.decode('utf-8')

        if code.startswith('showSASLog_11092015') == False and code.startswith("CompleteshowSASLog_11092015") == False:
            logger.debug("code type: " + str(type(code)))
            logger.debug("code length: " + str(len(code)))
            logger.debug("code string: " + code)
            if code.startswith("/*SASKernelTest*/"):
                res = self.mva.submit(code, "text")
            else:
                res = self.mva.submit(code, prompt=self.promptDict)
                self.promptDict = {}
            if res['LOG'].find("SAS process has terminated unexpectedly") > -1:
                print(res['LOG'], '\n' "Restarting SAS session on your behalf")
                self.do_shutdown(True)
                return res['LOG']

            output = res['LST']
            log = res['LOG']
            dis = self._which_display(log, output)
            return dis
        elif code.startswith("CompleteshowSASLog_11092015") == True and code.startswith('showSASLog_11092015') == False:
            full_log = highlight(self.mva._log, SASLogLexer(),
                                 HtmlFormatter(full=True, style=SASLogStyle, lineseparator="<br>",
                                               title="Full SAS Log"))
            return full_log.replace('\n', ' ')
        else:
            return self.cachedlog.replace('\n', ' ')

    def get_completions(self, info):
        if info['line_num'] > 1:
            relstart = info['column'] - (info['help_pos'] - info['start'])
        else:
            relstart = info['start']
        seg = info['line'][:relstart]
        if relstart > 0 and re.match('(?i)proc', seg.rsplit(None, 1)[-1]):
            potentials = re.findall('(?i)^' + info['obj'] + '.*', self.strproclist, re.MULTILINE)
            return potentials
        else:
            lastproc = info['code'].lower()[:info['help_pos']].rfind('proc')
            lastdata = info['code'].lower()[:info['help_pos']].rfind('data ')
            proc = False
            data = False
            if lastproc + lastdata == -2:
                pass
            else:
                if lastproc > lastdata:
                    proc = True
                else:
                    data = True

            if proc:
                # we are not in data section should see if proc option or statement
                lastsemi = info['code'].rfind(';')
                mykey = 's'
                if lastproc > lastsemi:
                    mykey = 'p'
                procer = re.search('(?i)proc\s\w+', info['code'][lastproc:])
                method = procer.group(0).split(' ')[-1].upper() + mykey.encode()
                mylist = self.compglo[method][0]
                potentials = re.findall('(?i)' + info['obj'] + '.+', '\n'.join(str(x) for x in mylist), re.MULTILINE)
                return potentials
            elif data:
                # we are in statements (probably if there is no data)
                # assuming we are in the middle of the code

                lastsemi = info['code'].rfind(';')
                mykey = 's'
                if lastproc > lastsemi:
                    mykey = 'p'
                mylist = self.compglo['DATA' + mykey][0]
                potentials = re.findall('(?i)^' + info['obj'] + '.*', '\n'.join(str(x) for x in mylist), re.MULTILINE)
                return potentials
            else:
                potentials = ['']
                return potentials

    @staticmethod
    def _get_right_list(s):
        proc_opt = re.search(r"proc\s(\w+).*?[^;]\Z", s, re.IGNORECASE | re.MULTILINE)
        proc_stmt = re.search(r"\s*proc\s*(\w+).*;.*\Z", s, re.IGNORECASE | re.MULTILINE)
        data_opt = re.search(r"\s*data\s*[^=].*[^;]?.*$", s, re.IGNORECASE | re.MULTILINE)
        data_stmt = re.search(r"\s*data\s*[^=].*[^;]?.*$", s, re.IGNORECASE | re.MULTILINE)
        print(s)
        if proc_opt:
            logger.debug(proc_opt.group(1).upper() + 'p')
            return proc_opt.group(1).upper() + 'p'
        elif proc_stmt:
            logger.debug(proc_stmt.group(1).upper() + 's')
            return proc_stmt.group(1).upper() + 's'
        elif data_opt:
            logger.debug("data step")
            return 'DATA' + 'p'
        elif data_stmt:
            logger.debug("data step")
            return 'DATA' + 's'
        else:
            return None

    def initialize_debug(self, code):
        """SAS does not have formal debug tools from this interface"""
        print(code)
        return None

    def do_shutdown(self, restart):
        """
        Shut down the app gracefully, saving history.
        """
        print("in shutdown function")
        if self.hist_file:
            with open(self.hist_file, 'wb') as fid:
                data = '\n'.join(self.hist_cache[-self.max_hist_cache:])
                fid.write(data.encode('utf-8'))
        if self.mva:
            self.mva._endsas()
            self.mva = None
        if restart:
            self.Print("Restarting kernel...")
            self.reload_magics()
            self.restart_kernel()
            self.Print("Done!")
        return {'status': 'ok', 'restart': restart}


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp

    IPKernelApp.launch_instance(kernel_class=SASKernel)
