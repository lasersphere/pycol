# -*- coding: utf-8 -*-
"""
examples.physics_ex

Created on 12.05.2021

@author: Patrick Mueller

Example script / Guide for the PyCLS.physics module.
"""

import numpy as np
import scipy.constants as sc
import matplotlib.pyplot as plt

from pycol.types import *
import pycol.physics as ph
import pycol.tools as tools


def example(n: Union[set, int] = None):
    """
    Run one or several of the available examples. Scroll down for the function call.

    :param n: The number of the example or a list of numbers.

    Example 0: Calculation of energies, velocities and Doppler shifts.

    Example 1: Calculation of Doppler shifts for an ensemble of ion-velocity vectors.

    Example 2: Calculation of optical parameters.

    :returns: None.
    """
    if n is None:
        n = {0, 1, 2, 3}
    if isinstance(n, int):
        n = {n, }

    if 0 in n:
        """
        Example 0: Calculation of energies, velocities and Doppler shifts.
        
        The physics module provides functions to calculate basic observables.
        In example 0 basic properties of charged carbon isotopes are calculated.
        """

        m = 12  # The mass of the most abundant stable carbon isotope (u).
        q = 4  # The charge of the ions (e).
        f0 = (2455169.9 - 2411271.2) * sc.c * 1e-4  # The 3S1 -> 3P0 transition of C4+.

        # a) Typical COALA calculation.
        U = 20e3  # The acceleration voltage (V).
        e_el = ph.e_el(U, q)  # The potential energy difference corresponding to the voltage (eV)

        v = ph.v_el(U, q, m, v0=0, relativistic=True)  # The velocity of the accelerated carbon ions (m/s).
        gamma = ph.gamma(v)  # The Lorentzian time-dilation factor.

        f_col = ph.doppler(f0, v, alpha=0, return_frame='lab')
        # The resonant laser frequency in collinear direction (MHz).
        f_acol = ph.doppler(f0, v, alpha=np.pi, return_frame='lab')  # " in anticollinear direction (MHz).

        f_div_col = ph.doppler_el_d1(f_col, 0, U, q, m, 0, return_frame='atom')
        # The differential Doppler factor in the atoms rest frame (MHz / V).
        # == The change of the laser frequency in the atoms rest frame with the voltage.
        f_div_acol = ph.doppler_el_d1(f_acol, np.pi, U, q, m, 0, return_frame='atom')

        # b) Typical CRYRING calculation.
        v = ph.inverse_doppler(f0, f_col, alpha=0)  # The velocity of the carbon ions (m/s).
        beta = ph.beta(v)  # The relative velocity of the carbon ions.
        e_kin = ph.e_kin(v, m, relativistic=True)  # The kinetic energy of the carbon ions (eV).

        for k, v in locals().items():
            print('{} = {}'.format(k, v))

    if 1 in n:
        """
        Example 1: Calculation of Doppler shifts for an ensemble of ion-velocity vectors.
        
        Most of the functions in the physics module are array compatible.
        In the following ions from example 0a) are simulated.
        """

        num = 100000  # The number of samples.

        m = 12  # The mass of the most abundant stable carbon isotope (u).
        q = 4  # The charge of the ions (e).
        f0 = (2455169.9 - 2411271.2) * sc.c * 1e-4  # The 3S1 -> 3P0 transition of C4+.

        U = 20e3  # The acceleration voltage (V).
        f_col = 1321038455  # Resonant collinear laser frequency at 20kV.

        v_vec = ph.thermal_v_rvs(m, 2500, (num, 3))
        # Generate 100,000 thermally distributed velocity values for each direction.

        v_vec[:, 0] = ph.v_el(U, q, m, v_vec[:, 0], relativistic=True)
        # Offset the kinetic energy by 20 kV =1a)= 80 keV in the x direction.

        gamma3d = np.mean(ph.gamma_3d(v_vec, axis=-1), axis=0)
        # The mean Lorentzian time-dilation factor for the 3d vectors.

        f_vec = np.array([[f_col, f_col, 0, 0], ])  # The collinear frequency 4-vector.
        # Note that it was expanded along axis 0 to match the shape of v_vec.

        f_vec_atom = ph.boost(f_vec, v_vec, axis=-1)  # The Lorentz boosts of the frequency 4-vector.
        # Note that the vector components are aligned with the last axis.

        f_atom = tools.absolute(f_vec_atom[:, 1:], axis=-1)
        # The length of the cartesian components of the boosted 4-vectors.

        num_test = f_atom - f_vec_atom[:, 0]  # That length must be equal to the zeroth component of the 4-vectors.
        # plt.plot(num_test / f_vec_atom[:, 0])  # Plot relative numeric variation.
        # plt.show()

        for k, v in locals().items():
            print('{} = {}'.format(k, v))

        plt.xlabel('Laser freq. in the ion system relative to the resonance (MHz)')
        plt.ylabel('Abundance')
        plt.hist((f_atom - f0), bins=200)
        plt.show()

        plt.xlabel('Laser freq. in the ion system relative to its x-component (MHz)')
        plt.ylabel('Abundance')
        plt.hist(f_atom - f_vec_atom[:, 1], bins=200)
        plt.show()

    if 2 in n:
        """
        Example 2: Calculation of optical parameters.
        """
        pass

    if 3 in n:
        """
        Example 3: Calculation of mean square charge radii from Fricke et al for barium.
        """
        a = [134, 135, 136, 137, 138]
        barrett = [6.1782, 6.1747, 6.1825, 6.1818, 6.1906]
        barrett_d = [0.0015, 0.0014, 0.0015, 0.0014, 0.0015]
        delta_barret = [-0.0124, -0.0142, -0.008, -0.0084, 0.]
        delta_barret_d = [0.0005, ] * 4 + [0., ]
        v2, v4, v6 = 1.27976, 1.1974, 1.1370
        c2c1, c3c1 = -7.03e-3, 2.04e-6

        dr2, dr2_d = ph.delta_r2(barrett, barrett_d, barrett[-1], barrett_d[-1], delta_barret, delta_barret_d, v2, v2)
        dr4, dr4_d = ph.delta_r2(barrett, barrett_d, barrett[-1], barrett_d[-1], delta_barret, delta_barret_d, v4, v4)
        dr6, dr6_d = ph.delta_r2(barrett, barrett_d, barrett[-1], barrett_d[-1], delta_barret, delta_barret_d, v6, v6)
        lambda_rn, lambda_rn_d = ph.lambda_rn(dr2, dr2_d, dr4, dr4_d, dr6, dr6_d, c2c1, c3c1)

        for k, v in locals().items():
            print('{} = {}'.format(k, v))


if __name__ == '__main__':
    example({3})
