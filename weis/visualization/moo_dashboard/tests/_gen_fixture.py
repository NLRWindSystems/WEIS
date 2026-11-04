"""Helper script to verify the SQL fixture generation approach."""
import tempfile
import os
import shutil

import openmdao.api as om
import numpy as np


def build_sql_fixture(output_dir):
    """Create a small log_opt.sql + problem_vars.yaml in output_dir."""
    sql_path = os.path.join(output_dir, "log_opt.sql")

    prob = om.Problem()

    # Use subsystem-prefixed names to mimic WEIS (e.g. "tune_rosco_ivc.ps_percent")
    ivc = prob.model.add_subsystem("tune_rosco_ivc", om.IndepVarComp())
    ivc.add_output("Kp_float", val=-15.0)
    ivc.add_output("ps_percent", val=0.75)

    prob.model.add_subsystem(
        "aeroelastic",
        om.ExecComp(
            [
                "AEP = 4e11 + 1e10 * ps_percent - 5e8 * Kp_float**2",
                "DEL_TwrBsMyt = 80000 + 1000 * ps_percent + 200 * Kp_float",
                "rotor_overspeed = 0.05 + 0.002 * ps_percent - 0.001 * Kp_float",
                "constr_margin = ps_percent * arr",
            ],
            Kp_float={"val": -15.0},
            ps_percent={"val": 0.75},
            arr={"val": np.array([1.0, 2.0, 3.0])},
            constr_margin={"shape": 3},
        ),
    )
    prob.model.connect("tune_rosco_ivc.Kp_float", "aeroelastic.Kp_float")
    prob.model.connect("tune_rosco_ivc.ps_percent", "aeroelastic.ps_percent")

    cases_list = [
        [("tune_rosco_ivc.Kp_float", -20.0), ("tune_rosco_ivc.ps_percent", 0.65)],
        [("tune_rosco_ivc.Kp_float", -15.0), ("tune_rosco_ivc.ps_percent", 0.75)],
        [("tune_rosco_ivc.Kp_float", -10.0), ("tune_rosco_ivc.ps_percent", 0.80)],
        [("tune_rosco_ivc.Kp_float", -8.0),  ("tune_rosco_ivc.ps_percent", 0.85)],
        [("tune_rosco_ivc.Kp_float", -5.0),  ("tune_rosco_ivc.ps_percent", 0.90)],
    ]
    prob.driver = om.DOEDriver(om.ListGenerator(cases_list))
    prob.driver.add_recorder(om.SqliteRecorder(sql_path))

    prob.model.add_design_var("tune_rosco_ivc.Kp_float", lower=-30.0, upper=0.0)
    prob.model.add_design_var("tune_rosco_ivc.ps_percent", lower=0.6, upper=1.0)
    prob.model.add_objective("aeroelastic.AEP")
    prob.model.add_objective("aeroelastic.DEL_TwrBsMyt")
    prob.model.add_constraint("aeroelastic.rotor_overspeed", upper=0.2)
    prob.model.add_constraint("aeroelastic.constr_margin", upper=3.0)

    prob.setup()
    prob.run_driver()
    prob.cleanup()

    # Write a matching problem_vars.yaml
    import yaml

    yaml_data = {
        "design_vars": [
            ["tune_rosco_ivc.Kp_float", {"name": "tune_rosco_ivc.Kp_float", "lower": -30.0, "upper": 0.0, "size": 1}],
            ["tune_rosco_ivc.ps_percent", {"name": "tune_rosco_ivc.ps_percent", "lower": 0.6, "upper": 1.0, "size": 1}],
        ],
        "objectives": [
            ["aeroelastic.AEP", {"name": "aeroelastic.AEP", "size": 1}],
            ["aeroelastic.DEL_TwrBsMyt", {"name": "aeroelastic.DEL_TwrBsMyt", "size": 1}],
        ],
        "constraints": [
            ["aeroelastic.rotor_overspeed", {"name": "aeroelastic.rotor_overspeed", "upper": 0.2, "lower": 0.0, "size": 1}],
            ["aeroelastic.constr_margin", {"name": "aeroelastic.constr_margin", "upper": 3.0, "lower": -1e30, "size": 3}],
        ],
    }
    yaml_path = os.path.join(output_dir, "problem_vars.yaml")
    with open(yaml_path, "w") as f:
        yaml.safe_dump(yaml_data, f)

    return sql_path, yaml_path


if __name__ == "__main__":
    tmpdir = tempfile.mkdtemp()
    try:
        sql_path, yaml_path = build_sql_fixture(tmpdir)

        cr = om.CaseReader(sql_path)
        cases = cr.get_cases("driver")
        print(f"Cases: {len(cases)}")
        for k in sorted(cases[0].outputs.keys()):
            print(f"  {k}: {cases[0][k]}")
        print(f"SQL size: {os.path.getsize(sql_path)} bytes")
        print(f"YAML: {yaml_path}")
    finally:
        shutil.rmtree(tmpdir)
