from distutils.core import setup
from distutils.command.install import install
from distutils import log
import json
import os
import sys

kernel_json = {"argv":["python3.4","-m","sas_kernel", "-f", "{connection_file}"],
 "display_name":"SAS pip",
 #"codemirror_mode":"shell",
 #"env":{"PS1": "$"},
 "language":"SAS"
}

class install_with_kernelspec(install):
    def run(self):
        # Regular installation
        install.run(self)

        # Now write the kernelspec
        from IPython.kernel.kernelspec import install_kernel_spec
        from IPython.utils.tempdir import TemporaryDirectory
        with TemporaryDirectory() as td:
            os.chmod(td, 0o755) # Starts off as 700, not user readable
            with open(os.path.join(td, 'kernel.json'), 'w') as f:
                json.dump(kernel_json, f, sort_keys=True)
            # TODO: Copy resources once they're specified

            log.info('Installing IPython kernel spec')
            install_kernel_spec(td, 'SAS', user=self.user, replace=True)

with open('README.rst') as f:
    readme = f.read()

svem_flag = '--single-version-externally-managed'
if svem_flag in sys.argv:
    # Die, setuptools, die.
    sys.argv.remove(svem_flag)

setup(name='SAS_kernel',
      version='0.1',
      description='A SAS kernel for IPython',
      long_description=readme,
      author='Jared Dean',
      author_email='jared.dean@sas.com',
      #url='https://github.com/takluyver/bash_kernel',
      packages=['sas_kernel'],
      cmdclass={'install': install_with_kernelspec},
      install_requires=['pexpect>=3.3'],
      classifiers = [
      #    'License :: OSI Approved :: BSD License',
      #    'Programming Language :: Python :: 3',
      #    'Topic :: System :: Shells',
        'Framework :: IPython'
      ]
)
