import os
import tempfile
import unittest

import numpy as np
import openmdao.api as om
from openfast_io.FileTools import save_yaml
from wisdem.inputs.validation import simple_types

from weis.visualization.utils import load_problem_vars_yaml


class TestLoadProblemVarsYaml(unittest.TestCase):
    def test_scalar_and_array_bounds(self):
        """Bounds written the way runWEIS writes problem_vars.yaml, including array
        constraints, which OpenMDAO writes with one bound per element."""
        prob = om.Problem()
        prob.model.add_subsystem(
            "c",
            om.ExecComp(["y = x**2", "arr = x + offset", "one = 2 * x"], offset={"val": np.zeros(3)}, arr={"val": np.zeros(3)}),
            promotes=["*"],
        )
        prob.model.add_design_var("x", lower=0.5, upper=3.0)
        prob.model.add_objective("y")
        prob.model.add_constraint("arr", lower=[0.1, 0.4, 0.2], upper=2.0)  # array, two-sided
        prob.model.add_constraint("one", upper=5.0)  # scalar, one-sided
        prob.setup()
        prob.final_setup()

        problem_var_dict = prob.list_driver_vars(
            desvar_opts=["lower", "upper"],
            cons_opts=["lower", "upper", "equals"],
            out_stream=None,
        )
        with tempfile.TemporaryDirectory() as tmp:
            save_yaml(tmp, "problem_vars.yaml", simple_types(problem_var_dict))
            bounds = load_problem_vars_yaml(os.path.join(tmp, "problem_vars.yaml"))

        self.assertEqual(bounds["x"], {"lower": 0.5, "upper": 3.0})
        # array bounds reduce to the tightest finite value
        self.assertEqual(bounds["arr"], {"lower": 0.4, "upper": 2.0})
        # the unbounded side of a one-sided constraint is None
        self.assertEqual(bounds["one"], {"lower": None, "upper": 5.0})

    def test_missing_file(self):
        self.assertEqual(load_problem_vars_yaml("does_not_exist.yaml"), {})


if __name__ == "__main__":
    unittest.main()
