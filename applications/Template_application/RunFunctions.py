import sys
import os
import contextlib
import subprocess
import numpy as np

from vebio.FileModifiers import write_file_with_replacements
from vebio.Utilities import check_dict_for_nans, dict_to_yaml, yaml_to_dict, print_dict
from vebio.WidgetFunctions import OptimizationWidget

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'models'))
cwd = os.getcwd()

class VE_params(object):
    ''' This  class is used for storing Virtual Engineering parameters 
        so they can be accesed from any model. It uses the Borg pattern. 
        The Borg pattern (also known as the Monostate pattern) is a way to
        implement singleton behavior, but instead of having only one instance
        of a class, there are multiple instances that share the same state. In
        other words, the focus is on sharing state instead of sharing instance.
    '''

    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state

    @classmethod
    def load_from_file(cls, yaml_filename, verbose=False):
        ve = cls()
        for k, item in yaml_to_dict(yaml_filename, verbose).items():
            setattr(ve, k, item)
        return ve

    def write_to_file(self, yaml_filename, merge_with_existing=False, verbose=False):
        dict_to_yaml(self.__dict__,  yaml_filename, merge_with_existing, verbose)
    
    def __str__(self):
        return str(print_dict(self.__dict__))


class Model1:
    def __init__(self, model1_options):
        ''' 
        :param model1_options: (WidgetCollection) or (dict)
            A ``WidgetCollection`` object containing all of widgets used
            to solicit user input for feedstock properties 
            or dictionary with feedstock properties.
        '''
        self.ve= VE_params()
        self.ve.model1 = {}
        if type(model1_options) is dict:
            self.var1 = model1_options['var1']
            self.var2 = model1_options['var2']
            self.var2 = model1_options['var3']
        else:
            for widget_name, widget in model1_options.__dict__.items(): 
                if isinstance(widget, OptimizationWidget):
                    setattr(self, widget_name, widget.widget.value)
                else:
                    setattr(self, widget_name, widget.value)

        self.model1_module_path = os.path.join(root_path, 'model1')
        sys.path.append(self.model1_module_path)

    ##############################################
    ### Properties
    ##############################################
    @property
    def var1(self):
        return self.ve.model1['var1']

    @var1.setter
    def var1(self, a):
        if not 0 <= a <= 1:
            raise ValueError(f"Value {a} is outside allowed interval [0, 1]")
        self.ve.feedstock['var'] = float(a)

    @property
    def var2(self):
        return self.ve.model1['var1']

    @var2.setter
    def var2(self, a):
        if not 0 <= a <= 1:
            raise ValueError(f"Value {a} is outside allowed interval [0, 1]")
        self.ve.feedstock['var'] = float(a)

    @property
    def var3(self):
        return self.ve.model1['var1']

    @var3.setter
    def var3(self, a):
        if not 0 <= a <= 1:
            raise ValueError(f"Value {a} is outside allowed interval [0, 1]")
        self.ve.feedstock['var'] = float(a)

    
    ##############################################
    ### run model
    ##############################################
    def run(self, verbose=False):
        self.ve.model1_out = run_model1() 
        if check_dict_for_nans(self.ve.model1_out):
            return True
        return False


    ##############################################
    #
    ##############################################
    def run(self, verbose=True, show_plots=None):
        """Run pretreatment code specified in 
        pretreatment_model/dolfinx/run_pretreatment.py

        :param verbose: (bool, optional) 
            Option to show print messages from executed file, default True.
        :param show_plots: (bool, optional) 
            Option to show plots, default True.
        """
        if verbose:
            print('\nRunning Pretreatment')
    
        if show_plots is None:
            show_plots = self.show_plots
        if not self.hpc_run:
            from run_pretreatment import run_pt
            self.ve.pt_out = run_pt(self.ve, verbose, show_plots)
        else:
            os.chdir(os.path.join(self.pt_module_path, 'dolfinx'))
            self.ve.write_to_file('ve_params.yml')
            command = f'python run_pretreatment.py {verbose} {show_plots}'
            subprocess.call(command.split(), text=True)
            self.ve = VE_params.load_from_file('ve_params.yml', verbose=False)
            os.chdir(root_path)
        if verbose:
            print('Finished Pretreatment')
        if check_dict_for_nans(self.ve.pt_out):
            print(f't_final = {self.t_final}')
            return True
        return False