"""
Unit tests for weis.control.tune_rosco.resolve_tsr_operational

Regression test for a bug where setting 'TSR_operational' in rosco_tuning_inputs
(passed through to modeling_options['ROSCO']) had no effect on the TSR used to
tune ROSCO / write VS_TSRopt to DISCON.IN, because TuneROSCO.compute() only ever
read the WISDEM-provided tsr_operational input.
"""

import unittest

import numpy as np
from rosco.toolbox.turbine import RotorPerformance

from weis.control.tune_rosco import resolve_tsr_operational


def make_cp_surface():
    # Small synthetic Cp(TSR, pitch) surface with an unambiguous maximum
    # at TSR = 7.0, pitch = 0 rad.
    pitch_initial_rad = np.deg2rad(np.array([0.0, 5.0, 10.0]))
    tsr_initial = np.array([5.0, 6.0, 7.0, 8.0, 9.0])
    performance_table = np.array([
        [0.30, 0.20, 0.10],
        [0.40, 0.30, 0.20],
        [0.48, 0.35, 0.22],  # max at TSR=7.0, pitch=0
        [0.42, 0.32, 0.21],
        [0.33, 0.25, 0.15],
    ])
    return RotorPerformance(performance_table, pitch_initial_rad, tsr_initial)


class TestResolveTSROperational(unittest.TestCase):
    def setUp(self):
        self.Cp = make_cp_surface()
        self.rated_rotor_speed = 1.0    # rad/s
        self.rotor_radius = 50.0        # m
        self.tsr_operational_default = 6.0   # e.g. WISDEM's control.rated_TSR

    def test_auto_compute_from_cp_surface(self):
        # TSR_operational = 0 should auto-compute from the Cp surface (Cp.TSR_opt)
        rosco_init_options = {'TSR_operational': 0}
        tsr, v_rated = resolve_tsr_operational(
            rosco_init_options,
            self.tsr_operational_default,
            self.rated_rotor_speed,
            self.rotor_radius,
            self.Cp,
        )
        self.assertEqual(tsr, self.Cp.TSR_opt)
        self.assertEqual(tsr, 7.0)
        self.assertAlmostEqual(v_rated, self.rated_rotor_speed * self.rotor_radius / tsr)

    def test_explicit_override(self):
        # A positive TSR_operational should be used directly, overriding the WISDEM default
        rosco_init_options = {'TSR_operational': 8.5}
        tsr, v_rated = resolve_tsr_operational(
            rosco_init_options,
            self.tsr_operational_default,
            self.rated_rotor_speed,
            self.rotor_radius,
            self.Cp,
        )
        self.assertEqual(tsr, 8.5)
        self.assertAlmostEqual(v_rated, self.rated_rotor_speed * self.rotor_radius / 8.5)

    def test_default_unchanged_when_key_absent(self):
        # If 'TSR_operational' is not in rosco_init_options, the WISDEM-provided
        # default should pass through unchanged (pre-existing behavior).
        rosco_init_options = {}
        tsr, v_rated = resolve_tsr_operational(
            rosco_init_options,
            self.tsr_operational_default,
            self.rated_rotor_speed,
            self.rotor_radius,
            self.Cp,
        )
        self.assertEqual(tsr, self.tsr_operational_default)
        self.assertAlmostEqual(v_rated, self.rated_rotor_speed * self.rotor_radius / self.tsr_operational_default)


if __name__ == "__main__":
    unittest.main()
