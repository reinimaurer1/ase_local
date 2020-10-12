import os
from pathlib import Path

import numpy as np

from ase.units import Bohr, Hartree
from ase.io import write
from ase.io.elk import read_elk, ElkReader
from ase.calculators.calculator import (FileIOCalculator, Parameters, kpts2mp,
                                        ReadError, PropertyNotImplementedError,
                                        EigenvalOccupationMixin)


class ELK(FileIOCalculator, EigenvalOccupationMixin):
    command = 'elk > elk.out'
    implemented_properties = ['energy', 'forces']
    ignored_changes = {'pbc'}
    discard_results_on_any_change = True

    def __init__(self, **kwargs):
        """Construct ELK calculator.

        The keyword arguments (kwargs) can be one of the ASE standard
        keywords: 'xc', 'kpts' and 'smearing' or any of ELK'
        native keywords.
        """

        super().__init__(**kwargs)

    def write_input(self, atoms, properties=None, system_changes=None):
        FileIOCalculator.write_input(self, atoms, properties, system_changes)
        self.initialize(atoms)

        parameters = dict(self.parameters)
        if 'forces' in properties:
            parameters['tforce'] = True

        directory = Path(self.directory)
        write(directory / 'elk.in', atoms, parameters=parameters,
              format='elk-in')

    def read_results(self):
        results = dict(self._reader().read_everything())
        self.results.update(results)

    def initialize(self, atoms):
        if 'spinpol' not in self.parameters:  # honor elk.in settings
            self.spinpol = atoms.get_initial_magnetic_moments().any()
        else:
            self.spinpol = self.parameters['spinpol']

    def get_electronic_temperature(self):
        return self.width * Hartree

    def get_number_of_bands(self):
        return self.nbands

    def get_number_of_electrons(self):
        return self.nelect

    def get_number_of_iterations(self):
        return self.niter

    def get_number_of_spins(self):
        return 1 + int(self.spinpol)

    def get_magnetic_moment(self, atoms=None):
        return self.magnetic_moment

    def get_magnetic_moments(self, atoms):
        # not implemented yet, so
        # so set the total magnetic moment on the atom no. 0 and fill with 0.0
        magmoms = [0.0 for a in range(len(atoms))]
        magmoms[0] = self.get_magnetic_moment(atoms)
        return np.array(magmoms)

    def get_spin_polarized(self):
        return self.spinpol

    def _reader(self):
        return ElkReader(self.directory)

    def get_eigenvalues(self, kpt=0, spin=0):
        return self._reader().read_eigenvalues(kpt, spin, 'eigenvalues')

    def get_occupation_numbers(self, kpt=0, spin=0):
        return self._reader().read_eigenvalues(kpt, spin, 'occupations')

    def get_ibz_k_points(self):
        return self._reader().read_kpts(mode='ibz_k_points')

    def get_k_point_weights(self):
        return self._reader().read_kpts(mode='k_point_weights')

    def get_fermi_level(self):
        return self._reader().read_fermi()

