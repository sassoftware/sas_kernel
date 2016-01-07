#import warnings
#from  IPython.utils.shimmodule import ShimWarning
#warnings.filterwarnings('error','', ShimWarning)


from ipykernel.kernelapp import IPKernelApp
from .kernel import SASKernel
IPKernelApp.launch_instance(kernel_class=SASKernel)
