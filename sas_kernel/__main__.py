from IPython.kernel.zmq.kernelapp import IPKernelApp
from .kernel import SASKernel
IPKernelApp.launch_instance(kernel_class=SASKernel)
