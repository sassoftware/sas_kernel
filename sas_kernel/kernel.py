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
import os
import sys
import re
import json
import types
import importlib.machinery
# Create LOGGER
import logging
import saspy

from typing import Tuple
from IPython.display import HTML
from metakernel import MetaKernel
from ._version import __version__


# create a LOGGER to output messages to the Jupyter CONSOLE
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.WARN)
CONSOLE = logging.StreamHandler()
CONSOLE.setFormatter(logging.Formatter('%(name)-12s: %(message)s'))
LOGGER.addHandler(CONSOLE)

LOGGER.debug("sanity check")


class SASKernel(MetaKernel):
    """
    SAS Kernel for Jupyter implementation. This module relies on SASPy
    """
    implementation = 'sas_kernel'
    implementation_version = __version__
    language = 'sas'
    language_version = '9.4+',
    banner = "SAS Kernel"
    language_info = {'name': 'sas',
                     'mimetype': 'text/x-sas',
                     "codemirror_mode": "sas",
                     'file_extension': '.sas'
                     }

    def __init__(self, **kwargs):
        with open(os.path.dirname(os.path.realpath(__file__)) + \
            '/data/' + 'sasproclist.json') as proclist:
            self.proclist = json.load(proclist)
        with open(os.path.dirname(os.path.realpath(__file__)) + \
            '/data/' + 'sasgrammardictionary.json') as compglo:
            self.compglo = json.load(compglo)
        self.strproclist = '\n'.join(str(x) for x in self.proclist)
        self.promptDict = {}
        MetaKernel.__init__(self, **kwargs)
        self.mva = None
        self.cachedlog = None
        self.lst_len = -99  # initialize the length to a negative number to trigger function
        self._allow_stdin = False

    def do_apply(self, content, bufs, msg_id, reply_metadata):
        pass

    def do_clear(self):
        pass

    def get_usage(self):
        return "This is the SAS kernel."

    def _get_config_names(self):
        """
        get the config file used by SASPy
        """
        loader = importlib.machinery.SourceFileLoader('foo', saspy.SAScfg)
        cfg = types.ModuleType(loader.name)
        loader.exec_module(cfg)
        return cfg.SAS_config_names

    def _get_lst_len(self):
        code = "data _null_; run;"
        res = self.mva.submit(code)
        assert isinstance(res, dict)
        self.lst_len = len(res['LST'])
        assert isinstance(self.lst_len, int)
        return

    def _start_sas(self):
        try:
            # import saspy as saspy
            self.mva = saspy.SASsession(kernel=self)
        except KeyError:
            self.mva = None
        except OSError:#socket.gaierror
            msg = """Failed to connect to SAS!
    Please check your connection configuration here:{0}
    Here are the valid configurations:{1}
    You can load the configuration file into a Jupyter Lab cell using this command:
        %load {0}
    If the URL/Path are correct the issue is likely your username and/or password
    """.format(saspy.list_configs()[0], ', '.join(self._get_config_names()))
            self.Error_display(msg)
            self.mva = None
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise


    def _colorize_log(self, log: str) -> str:
        """
        takes a SAS log (str) and then looks for errors.
        Returns a tuple of error count, list of error messages
        """
        regex_note = r"(?m)(^NOTE.*((\n|\t|\n\t)[ ]([^WEN].*)(.*))*)"
        regex_warn = r"(?m)(^WARNING.*((\n|\t|\n\t)[ ]([^WEN].*)(.*))*)"
        regex_error = r"(?m)(^ERROR.*((\n|\t|\n\t)[ ]([^WEN].*)(.*))*)"

        sub_note = "\x1b[38;5;21m\\1\x1b[0m"
        sub_warn = "\x1b[38;5;2m\\1\x1b[0m"
        sub_error = "\x1B[1m\x1b[38;5;9m\\1\x1b[0m\x1b[0m"
        color_pattern = [
            (regex_error, sub_error),
            (regex_note, sub_note),
            (regex_warn, sub_warn)
        ]
        colored_log = log
        for pat, sub in color_pattern:
            colored_log = re.sub(pat, sub, colored_log)

        return colored_log

    def _is_error_log(self, log: str) -> Tuple:
        """
        takes a SAS log (str) and then looks for errors.
        Returns a tuple of error count, list of error messages
        """
        lines = re.split(r'[\n]\s*', log)
        error_count = 0
        error_log_msg_list = []
        error_log_line_list = []
        for index, line in enumerate(lines):
            # LOGGER.debug("line:{}".format(line))
            if line.startswith('ERROR'):
                error_count += 1
                error_log_msg_list.append(line)
                error_log_line_list.append(index)
        return (error_count, error_log_msg_list, error_log_line_list)

    def _which_display(self, log: str, output: str = '') -> str:
        """
        Determines if the log or lst should be returned as the
        results for the cell based on parsing the log
        looking for errors and the presence of lst output.

        :param log: str log from code submission
        :param output: None or str lst output if there was any
        :return: The correct results based on log and lst
        :rtype: str
        """
        error_count, msg_list, error_line_list = self._is_error_log(log)

        # store the log for display in the showSASLog nbextension
        #self.cachedlog = self._colorize_log(log)

        # no error and LST output
        if error_count == 0 and len(output) > self.lst_len:
            return self.Display(HTML(output))

        elif error_count > 0 and len(output) > self.lst_len:  # errors and LST
            # filter log to lines around first error
            # by default get 5 lines on each side of the first Error message.
            # to change that modify the values in {} below
            regex_around_error = r"(.*)(.*\n){6}^ERROR(.*\n){6}"

            # Extract the first match +/- 5 lines
            e_log = re.search(regex_around_error, log, re.MULTILINE).group()
            assert error_count == len(
                error_line_list), "Error count and count of line number don't match"
            return self.Error_display(msg_list[0],
                                      print(self._colorize_log(e_log)),
                                      HTML(output))

        # for everything else return the log
        return self.Print(self._colorize_log(log))

    def do_execute_direct(self, code: str, silent: bool = False) -> [str, dict]:
        """
        This is the main method that takes code from the Jupyter cell
        and submits it to the SAS server.

        :param code: code from the cell
        :param silent:
        :return: str with either the log or list
        """
        if not code.strip():
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}

        # If no mva session start a session
        if self.mva is None:
            self._allow_stdin = True
            self._start_sas()

        # This code is now handeled in saspy will remove in future version
        if self.lst_len < 0:
            self._get_lst_len()

        # This block uses special strings submitted by the Jupyter notebook extensions
        if not code.startswith('showSASLog_11092015') and \
           not code.startswith("CompleteshowSASLog_11092015"):
            if code.startswith("/*SASKernelTest*/"):
                res = self.mva.submit(code, "text")
            else:
                res = self.mva.submit(code, prompt=self.promptDict)
                self.promptDict = {}
            if res['LOG'].find("SAS process has terminated unexpectedly") > -1:
                print(res['LOG'], '\n' "Restarting SAS session on your behalf")
                self.do_shutdown(True)
                return res['LOG']

            # store the log for display in the showSASLog nbextension
            self.cachedlog = self._colorize_log(res['LOG'])

            # Parse the log to check for errors
            error_count, error_log_msg, _ = self._is_error_log(res['LOG'])

            if error_count > 0 and len(res['LST']) <= self.lst_len:
                return self.Error(error_log_msg[0], print(self._colorize_log(res['LOG'])))

            return self._which_display(res['LOG'], res['LST'])

        elif code.startswith("CompleteshowSASLog_11092015") and \
            not code.startswith('showSASLog_11092015'):
            return self.Print(self._colorize_log(self.mva.saslog()))
        else:
            return self.Print(self._colorize_log(self.cachedlog))

    def get_completions(self, info):
        """
        Get completions from kernel for procs and statements.
        """
        if info['line_num'] > 1:
            relstart = info['column'] - (info['help_pos'] - info['start'])
        else:
            relstart = info['start']
        seg = info['line'][:relstart]
        if relstart > 0 and re.match('(?i)proc', seg.rsplit(None, 1)[-1]):
            potentials = re.findall(
                '(?i)^' + info['obj'] + '.*', self.strproclist, re.MULTILINE)
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
                procer = re.search(r'(?i)proc\s\w+', info['code'][lastproc:])
                method = procer.group(0).split(' ')[-1].upper() + mykey
                mylist = self.compglo[method][0]
                potentials = re.findall(
                    '(?i)' + info['obj'] + '.+', '\n'.join(str(x) for x in mylist), re.MULTILINE)
                return potentials
            elif data:
                # we are in statements (probably if there is no data)
                # assuming we are in the middle of the code

                lastsemi = info['code'].rfind(';')
                mykey = 's'
                if lastproc > lastsemi:
                    mykey = 'p'
                mylist = self.compglo['DATA' + mykey][0]
                potentials = re.findall(
                    '(?i)^' + info['obj'] + '.*', '\n'.join(str(x) for x in mylist), re.MULTILINE)
                return potentials
            else:
                potentials = ['']
                return potentials

    @staticmethod
    def _get_right_list(s):
        proc_opt = re.search(
            r"proc\s(\w+).*?[^;]\Z", s, re.IGNORECASE | re.MULTILINE)
        proc_stmt = re.search(r"\s*proc\s*(\w+).*;.*\Z",
                              s, re.IGNORECASE | re.MULTILINE)
        data_opt = re.search(
            r"\s*data\s*[^=].*[^;]?.*$", s, re.IGNORECASE | re.MULTILINE)
        data_stmt = re.search(
            r"\s*data\s*[^=].*[^;]?.*$", s, re.IGNORECASE | re.MULTILINE)
        print(s)
        if proc_opt:
            return proc_opt.group(1).upper() + 'p'
        elif proc_stmt:
            return proc_stmt.group(1).upper() + 's'
        elif data_opt:
            return 'DATA' + 'p'
        elif data_stmt:
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
