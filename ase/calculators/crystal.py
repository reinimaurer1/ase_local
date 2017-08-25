"""This module defines an ASE interface to CRYSTAL14

http://www.crystal.unito.it/

daniele.selli@unimib.it
g.fazio3@campus.unimib.it

The file 'geom.f34' contains the input and output geometry
and it will be updated during the crystal calculations.

The keywords are given, for instance, as follows::

    DFT = True,
    DFT_CORRELAT = 'PBE',
    DFT_EXCHANGE = 'PBE',
    DFT_MET = 'B3LYP',
    DFT_POL = 'SPIN',
    TOLDEE = 8,
    ANDERSON = 'Yes',
    FMIXING = 95,
    ... # put other examples

"""

import os

import numpy as np

from ase.calculators.calculator import FileIOCalculator, kpts2mp


class crystal(FileIOCalculator):
    """ A crystal calculator with ase-FileIOCalculator nomenclature
    """
    if 'CRY_COMMAND' in os.environ:
        command = os.environ['CRY_COMMAND'] + ' < INPUT > OUTPUT'
    else:
        command = 'crystal < INPUT > OUTPUT'

    implemented_properties = ['energy', 'forces']

    def __init__(self, restart=None, ignore_bad_restart_file=False, 
                 label='cry', atoms=None, kpts=None,
                 **kwargs):
        """Construct a crystal calculator.

        """
        from ase.dft.kpoints import monkhorst_pack

  #      [TO BE DONE]
  #      if 'CRY_BASIS' in os.environ:
  #          basis_dir = os.environ['CRY_BASIS']
  #      else:
  #          basis_dir = './'
  #
  #      # call crystal only to run a single point calculation
  #      # [PUT HERE DEFAULT PARAMETERS]
  #      self.default_parameters = dict(
  #          Hamiltonian_='DFTB',
  #          Driver_='ConjugateGradient',
  #          Driver_MaxForceComponent='1E-4',
  #          Driver_MaxSteps=0,
  #          Hamiltonian_SlaterKosterFiles_='Type2FileNames',
  #          Hamiltonian_SlaterKosterFiles_Prefix=slako_dir,
  #          Hamiltonian_SlaterKosterFiles_Separator='"-"',
  #          Hamiltonian_SlaterKosterFiles_Suffix='".skf"',
  #          Hamiltonian_MaxAngularMomentum_='')

        self.lines = None
        self.atoms = None
        self.atoms_input = None
        self.outfilename = 'cry.out'

        FileIOCalculator.__init__(self, restart, ignore_bad_restart_file, 
                                  label, atoms,
                                  **kwargs)
        self.kpts = kpts

    def write_crystal_in(self, filename):
        """ Write the input file for the crystal calculation.
            Geometry is taken always from the file 'fort.34'
        """

        # write BLOCK 1 of crystal input (only SP with gradients)
        outfile = open(filename, 'w')
        outfile.write('Single point + Gradient crystal calculation \n')
        outfile.write('EXTERNAL \n')
        outfile.write('OPTGEOM \n')
        outfile.write('FINALRUN \n')
        outfile.write('0 \n')
        outfile.write('MAXCYCLE \n')
        outfile.write('1 \n')
        outfile.write('END \n')
        outfile.write('END \n')
       
        
        # write BLOCK 2 of crystal input from file (basis sets)
        basisfile = open(os.path.join(self.directory, 'basis'))
	basis = basisfile.readlines()
	for line in basis:
	    outfile.write(line)
	
        # write BLOCK 3 according to parameters set as input
        newline = '\n'
        for key, value in sorted(self.parameters.items()):
            if value:	
                outfile.write(key+newline)

        outfile.write('END \n')
        
        outfile.close()

    def write_input(self, atoms, properties=None, system_changes=None):
        from ase.io import write
        FileIOCalculator.write_input(
            self, atoms, properties, system_changes)
        self.write_crystal_in(os.path.join(self.directory, 'INPUT'))
        write(os.path.join(self.directory, 'fort.34'), atoms)
        # self.atoms is none until results are read out,
        # then it is set to the ones at writing input
        self.atoms_input = atoms
        self.atoms = None

