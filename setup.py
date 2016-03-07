try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from distutils.command.install import install
from distutils import log
import json
import os
import sys
#import saspy.sas_magic

try:
  from jupyter_client.kernelspec import install_kernel_spec
except ImportError:
  from IPython.kernel.kernelspec import install_kernel_spec
from IPython.utils.tempdir import TemporaryDirectory

kernel_json = {
        "argv":[sys.executable,
            "-m","sas_kernel", "-f", "{connection_file}"],
 "display_name":"SAS",
 "codemirror_mode":"sas",
 "language":"sas"
}
class install_with_kernelspec(install):
    def run(self):
        # Regular installation
        install.run(self)

        # Now write the kernelspec
        with TemporaryDirectory() as td:
            os.chmod(td, 0o755) # Starts off as 700, not user readable
            with open(os.path.join(td, 'kernel.json'), 'w') as f:
                json.dump(kernel_json, f, sort_keys=True)
            log.info('Installing IPython kernel spec')
            try:
              install_kernel_spec(td, 'SAS', user=self.user, replace=True)
            except:
              print("Could not install SAS Kernel as %s user" % self.user)

svem_flag = '--single-version-externally-managed'
if svem_flag in sys.argv:
    sys.argv.remove(svem_flag)

setup(name='SAS_kernel',
      version='0.2',
      description='A SAS kernel for IPython',
      long_description=open('README.rst', 'rb').read().decode('utf-8'),
      author='Jared Dean',
      author_email='jared.dean@sas.com',
      packages=['sas_kernel'],
      cmdclass={'install': install_with_kernelspec},
      package_data={'sas_kernel': ['data/*.json']},
      install_requires=['pexpect>=3.3','metakernel','saspy'],
      classifiers = [
        'Framework :: IPython',
        'Programming Language :: Python :: 3',
        'Programming Language :: SAS    :: 9',
      ]
)
