from distutils.core import setup
from distutils.command.install import install
from distutils import log
import json
import os
import sys

kernel_json = {
        "argv":[sys.executable,
            "-m","sas_kernel", "-f", "{connection_file}"],
 "display_name":"SAS",
 #"codemirror_mode":"sas",
 "language":"sas"
}
class install_with_kernelspec(install):
    def run(self):
        # Regular installation
        install.run(self)

        # Now write the kernelspec
        from jupyter_client.kernelspec import install_kernel_spec
        from IPython.utils.tempdir import TemporaryDirectory
        with TemporaryDirectory() as td:
            os.chmod(td, 0o755) # Starts off as 700, not user readable
            with open(os.path.join(td, 'kernel.json'), 'w') as f:
                json.dump(kernel_json, f, sort_keys=True)
            # TODO: Copy resources once they're specified

            log.info('Installing IPython kernel spec')
            install_kernel_spec(td, 'SAS', user=self.user, replace=True)

svem_flag = '--single-version-externally-managed'
if svem_flag in sys.argv:
    # Die, setuptools, die.
    sys.argv.remove(svem_flag)

setup(name='SAS_kernel',
      version='0.2',
      description='A SAS kernel for IPython',
      long_description=open('README.rst', 'rb').read().decode('utf-8'),
      author='Jared Dean',
      author_email='jared.dean@sas.com',
      packages=['sas_kernel','sas_kernel.magics'],
      cmdclass={'install': install_with_kernelspec},
      install_requires=['pexpect>=3.3','saspy','metakernel'],
      classifiers = [
        'Framework :: IPython',
        'Programming Language :: Python :: 3',
        'Programming Language :: SAS    :: 9',
      ]
)
