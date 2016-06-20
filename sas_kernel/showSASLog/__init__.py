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

def _jupyter_nbextension_paths():
    return [dict(section="notebook",
                 # the path is relative to the `my_fancy_module` directory
                 src="",
                 # directory in the `nbextension/` namespace
                 dest="showSASLog",
                 # _also_ in the `nbextension/` namespace
                 require="showSASLog/main")]
