import numpy as np
import pytest
from openfast_io.FileTools import load_yaml

from weis.aeroelasticse.CaseGen_General import CaseGen_General


def test_array_values_in_grouped_cases(tmp_path):
    lin_times = ("Fst", "LinTimes")
    n_lin_times = ("Fst", "NLinTimes")
    t_max = ("Fst", "TMax")
    first = [30.0, 45.0, 60.0]
    second = [90.0, 120.0]
    case_inputs = {
        lin_times: {"vals": [np.array(first), np.array(second)], "group": 0},
        n_lin_times: {"vals": np.array([3, 2]), "group": 0},
        t_max: {"vals": [150.0, 180.0], "group": 1},
    }

    # A short display threshold must not shorten the case values or the saved matrix.
    with np.printoptions(threshold=1, edgeitems=1):
        cases, names = CaseGen_General(case_inputs, tmp_path, namebase="linear")

    assert names == ["linear_0", "linear_1", "linear_2", "linear_3"]
    assert cases == [
        {lin_times: first, n_lin_times: 3, t_max: 150.0},
        {lin_times: first, n_lin_times: 3, t_max: 180.0},
        {lin_times: second, n_lin_times: 2, t_max: 150.0},
        {lin_times: second, n_lin_times: 2, t_max: 180.0},
    ]
    assert cases[0][lin_times] is not cases[1][lin_times]

    matrix = load_yaml(tmp_path / "case_matrix.yaml", package=1)
    assert matrix[lin_times] == [str(first), str(first), str(second), str(second)]
    assert matrix["Case_Name"] == names
    assert str(first) in (tmp_path / "case_matrix.txt").read_text()


@pytest.mark.parametrize("times", [[30.0, 60.0], "[30.0,60.0]"])
def test_python_lists_and_existing_list_strings(times):
    lin_times = ("Fst", "LinTimes")
    cases, _ = CaseGen_General({lin_times: {"vals": [times], "group": 0}}, save_matrix=False)

    assert cases == [{lin_times: [30.0, 60.0]}]
