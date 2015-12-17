from ase.units import Ry

from ase.calculators.siesta import Siesta
from ase.calculators.siesta.parameters import Specie
from ase.optimize import QuasiNewton
from ase import Atoms

h = Atoms(
    '3H',
    [(0.0, 0.0, 0.0),
     (0.0, 0.0, 0.5),
     (0.0, 0.0, 1.0)],
    cell=[10, 10, 10])

h.set_tags([1, 2, 3])
h.set_initial_magnetic_moments([0, 0, 0])

siesta = Siesta(
    mesh_cutoff=200 * Ry,
    basis_set='SZ',
    spin='COLLINEAR',
    xc='PBE',
    pseudo_qualifier='gga',
    species=[
        Specie(symbol='H', tag=2, basis_set='DZP', ghost=True)],
    fdf_arguments={'DM.Tolerance': 1e-3})

h.set_calculator(siesta)
dyn = QuasiNewton(h, trajectory='h.traj')
dyn.run(fmax=0.02)