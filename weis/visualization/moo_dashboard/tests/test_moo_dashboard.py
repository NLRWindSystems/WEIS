"""
Tests for the MOO Dashboard application.

Covers: data_processing utilities, plot_helpers, detect_array_columns,
        layout components, and key callbacks.
"""

import sys
import os
import io
import json
import tempfile

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest

# Add moo_dashboard root to sys.path so relative imports in the app work
MOO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if MOO_DIR not in sys.path:
    sys.path.insert(0, MOO_DIR)

from utils.data_processing import (
    extract_variable_names,
    process_yaml_config,
    load_csv_from_path,
    load_yaml_from_path,
    prepare_dataframe_for_splom,
    find_pareto_front,
)
from utils.plot_helpers import (
    calculate_font_size,
    truncate_labels,
    calculate_margin_size,
    create_splom_figure,
    create_empty_figure_with_message,
    create_table_figure,
)
from callbacks.channel_selection import detect_array_columns


# ---------------------------------------------------------------------------
#   Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_csv_path(tmp_path):
    """Create a small CSV file and return its path."""
    df = pd.DataFrame({
        "obj1": [1.0, 2.0, 3.0, 4.0, 5.0],
        "obj2": [5.0, 4.0, 3.0, 2.0, 1.0],
        "constr1": [0.1, 0.2, 0.3, 0.4, 0.5],
        "dv1": [10.0, 20.0, 30.0, 40.0, 50.0],
        "dv2": [100.0, 90.0, 80.0, 70.0, 60.0],
    })
    path = tmp_path / "test.csv"
    df.to_csv(path, index=False)
    return str(path)


@pytest.fixture
def sample_csv_with_arrays_path(tmp_path):
    """Create a CSV with array-valued columns (string-encoded)."""
    df = pd.DataFrame({
        "obj1": [1.0, 2.0, 3.0],
        "arr_col": ["[1.0, 2.0, 3.0]", "[4.0, 5.0, 6.0]", "[7.0, 8.0, 9.0]"],
        "np_arr_col": ["[1. 2. 3.]", "[4. 5. 6.]", "[7. 8. 9.]"],
    })
    path = tmp_path / "test_arrays.csv"
    df.to_csv(path, index=False)
    return str(path)


@pytest.fixture
def sample_yaml_config():
    """Return a sample problem_vars-style YAML dict."""
    return {
        "objectives": [
            ["obj1", {"lower": 0, "upper": 10}],
            "obj2",
        ],
        "constraints": [
            ["constr1", {"lower": 0, "upper": 1}],
        ],
        "design_vars": [
            ["dv1", {"lower": 0, "upper": 100}],
            ["dv2", {"lower": 50, "upper": 200}],
        ],
    }


@pytest.fixture
def sample_yaml_path(tmp_path, sample_yaml_config):
    """Write sample YAML config to a file."""
    import yaml
    path = tmp_path / "problem_vars.yaml"
    with open(path, "w") as f:
        yaml.safe_dump(sample_yaml_config, f)
    return str(path)


@pytest.fixture
def processed_yaml(sample_yaml_config):
    """Return processed YAML config (as produced by process_yaml_config)."""
    return process_yaml_config(sample_yaml_config)


@pytest.fixture
def sample_df():
    """Return a DataFrame matching the sample YAML variables."""
    return pd.DataFrame({
        "obj1": [1.0, 2.0, 3.0, 4.0, 5.0],
        "obj2": [5.0, 4.0, 3.0, 2.0, 1.0],
        "constr1": [0.1, 0.2, 0.3, 0.4, 0.5],
        "dv1": [10.0, 20.0, 30.0, 40.0, 50.0],
        "dv2": [100.0, 90.0, 80.0, 70.0, 60.0],
    })


# ===================================================================
#   utils/data_processing.py
# ===================================================================


class TestExtractVariableNames:
    def test_simple_strings(self):
        result = extract_variable_names(["a", "b", "c"])
        assert set(result.keys()) == {"a", "b", "c"}
        assert all(v is None for v in result.values())

    def test_nested_with_bounds(self):
        result = extract_variable_names([["obj1", {"lower": 0, "upper": 10}]])
        assert "obj1" in result
        assert result["obj1"]["lower"] == 0
        assert result["obj1"]["upper"] == 10

    def test_mixed(self):
        result = extract_variable_names(["plain", ["bounded", {"lower": -1}]])
        assert result["plain"] is None
        assert result["bounded"] == {"lower": -1.0}

    def test_empty(self):
        assert extract_variable_names([]) == {}


class TestProcessYamlConfig:
    def test_full_config(self, sample_yaml_config):
        result = process_yaml_config(sample_yaml_config)
        assert "objectives" in result
        assert "constraints" in result
        assert "design_vars" in result
        assert "obj1" in result["objectives"]
        assert "constr1" in result["constraints"]
        assert "dv1" in result["design_vars"]

    def test_missing_keys(self):
        result = process_yaml_config({"objectives": ["x"]})
        assert "x" in result["objectives"]
        assert result["constraints"] == {}
        assert result["design_vars"] == {}

    def test_empty_config(self):
        result = process_yaml_config({})
        assert result == {"objectives": {}, "constraints": {}, "design_vars": {}}


class TestLoadCsvFromPath:
    def test_valid_csv(self, sample_csv_path):
        json_str = load_csv_from_path(sample_csv_path)
        assert json_str is not None
        import io
        df = pd.read_json(io.StringIO(json_str), orient="split")
        assert len(df) == 5
        assert "obj1" in df.columns

    def test_nonexistent_file(self):
        assert load_csv_from_path("/nonexistent/path.csv") is None

    def test_unsupported_format(self, tmp_path):
        p = tmp_path / "data.txt"
        p.write_text("hello")
        assert load_csv_from_path(str(p)) is None


class TestLoadYamlFromPath:
    def test_valid_yaml(self, sample_yaml_path):
        result = load_yaml_from_path(sample_yaml_path)
        assert result is not None
        assert "objectives" in result

    def test_nonexistent_file(self):
        assert load_yaml_from_path("/nonexistent/file.yaml") is None


class TestPrepareDataframeForSplom:
    def test_regular_vars(self, sample_df, processed_yaml):
        selected = ["obj1", "obj2"]
        sdf, dims, cats = prepare_dataframe_for_splom(sample_df, selected, processed_yaml)
        assert sdf is not None
        assert len(dims) == 2
        assert "sample_id" in sdf.columns
        assert cats.get("obj1") == "objectives"
        assert cats.get("obj2") == "objectives"

    def test_array_min_max(self):
        df = pd.DataFrame({
            "arr": ["[1.0, 2.0, 3.0]", "[4.0, 5.0, 6.0]", "[7.0, 8.0, 9.0]"]
        })
        yaml_data = {"objectives": {}, "constraints": {}, "design_vars": {}}
        selected = ["arr_min", "arr_max"]
        sdf, dims, cats = prepare_dataframe_for_splom(df, selected, yaml_data)
        assert sdf is not None
        assert "arr_min" in sdf.columns
        assert "arr_max" in sdf.columns
        assert len(dims) == 2
        assert list(sdf["arr_min"]) == [1.0, 4.0, 7.0]
        assert list(sdf["arr_max"]) == [3.0, 6.0, 9.0]

    def test_missing_column(self, sample_df, processed_yaml):
        selected = ["nonexistent"]
        sdf, dims, cats = prepare_dataframe_for_splom(sample_df, selected, processed_yaml)
        assert sdf is None
        assert dims == []

    def test_empty_selection(self, sample_df, processed_yaml):
        sdf, dims, cats = prepare_dataframe_for_splom(sample_df, [], processed_yaml)
        assert sdf is None


class TestFindParetoFront:
    def test_two_objective_minimize(self):
        df = pd.DataFrame({
            "f1": [1, 2, 3, 4],
            "f2": [4, 3, 2, 1],
        })
        # All points are Pareto optimal on a strict tradeoff
        result = find_pareto_front(["f1", "f2"], df)
        assert set(result) == {0, 1, 2, 3}

    def test_dominated_points(self):
        df = pd.DataFrame({
            "f1": [1, 2, 3, 1],
            "f2": [1, 2, 3, 2],
        })
        # Point 0 (1,1) dominates 1 (2,2) and 2 (3,3); point 3 (1,2) is dominated by 0
        result = find_pareto_front(["f1", "f2"], df)
        assert 0 in result
        assert 1 not in result
        assert 2 not in result

    def test_mixed_senses(self):
        df = pd.DataFrame({
            "f1": [1, 2, 3],
            "f2": [3, 2, 1],
        })
        senses = {"f1": "minimize", "f2": "maximize"}
        # minimize f1, maximize f2 → point 0 (f1=1, f2=3) dominates all
        result = find_pareto_front(["f1", "f2"], df, senses)
        assert result == [0]

    def test_all_same(self):
        df = pd.DataFrame({"f1": [1, 1, 1], "f2": [2, 2, 2]})
        result = find_pareto_front(["f1", "f2"], df)
        # No point dominates another — all are Pareto optimal
        assert set(result) == {0, 1, 2}

    def test_single_point(self):
        df = pd.DataFrame({"f1": [5], "f2": [10]})
        assert find_pareto_front(["f1", "f2"], df) == [0]

    def test_empty(self):
        df = pd.DataFrame({"f1": [], "f2": []})
        assert find_pareto_front(["f1", "f2"], df) == []

    def test_no_objectives(self):
        df = pd.DataFrame({"f1": [1, 2]})
        assert find_pareto_front([], df) == []

    def test_three_objectives(self):
        df = pd.DataFrame({
            "f1": [1, 2, 1],
            "f2": [1, 1, 2],
            "f3": [2, 1, 1],
        })
        result = find_pareto_front(["f1", "f2", "f3"], df)
        assert set(result) == {0, 1, 2}


# ===================================================================
#   utils/plot_helpers.py
# ===================================================================


class TestCalculateFontSize:
    def test_many_vars_small_subplots(self):
        # 10 vars at 800px → 80px per subplot → should hit smallest tier
        size = calculate_font_size(10, 800)
        assert size >= 6  # MIN_FONT_SIZE

    def test_few_vars_large_subplots(self):
        # 2 vars at 800px → 400px per subplot → full size
        size = calculate_font_size(2, 800)
        assert size <= 14  # MAX_FONT_SIZE

    def test_monotonic_decrease(self):
        sizes = [calculate_font_size(n, 800) for n in range(2, 12)]
        # Should be non-increasing as more vars consume space
        for i in range(len(sizes) - 1):
            assert sizes[i] >= sizes[i + 1]


class TestTruncateLabels:
    def test_short_names(self):
        labels = ["abc", "def"]
        assert truncate_labels(labels) == labels

    def test_underscore_truncation(self):
        result = truncate_labels(["very_long_variable_name_here"], max_length=15)
        assert len(result[0]) <= 15

    def test_no_underscore_truncation(self):
        result = truncate_labels(["abcdefghijklmnopqrstuvwxyz"], max_length=10)
        assert result[0].endswith("..")
        assert len(result[0]) <= 10


class TestCalculateMarginSize:
    def test_few_vars(self):
        m = calculate_margin_size(3, 12)
        assert m == 60  # BASE_MARGIN

    def test_medium_vars(self):
        m = calculate_margin_size(5, 12)
        assert m == 60 + 12  # BASE_MARGIN + font_size

    def test_many_vars(self):
        m = calculate_margin_size(8, 12)
        assert m == 60 + 24  # BASE_MARGIN + font_size * 2

    def test_max_cap(self):
        m = calculate_margin_size(20, 50)
        assert m <= 120  # MAX_MARGIN


class TestCreateSplomFigure:
    def test_empty_df(self):
        fig = create_splom_figure(pd.DataFrame(), [], 0)
        assert isinstance(fig, go.Figure)

    def test_single_dimension_message(self):
        df = pd.DataFrame({"a": [1, 2, 3], "sample_id": [0, 1, 2]})
        dims = [{"label": "a", "values": [1, 2, 3]}]
        result = create_splom_figure(df, dims, 1)
        # Should return a message figure (dict), not a full SPLOM
        assert isinstance(result, dict)
        assert "Select at least 2" in result["layout"]["title"]

    def test_two_dimensions(self):
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "sample_id": [0, 1, 2]})
        dims = [{"label": "a", "values": [1, 2, 3]}, {"label": "b", "values": [4, 5, 6]}]
        fig = create_splom_figure(df, dims, 2)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 1

    def test_with_highlight(self):
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "sample_id": [0, 1, 2]})
        dims = [{"label": "a", "values": [1, 2, 3]}, {"label": "b", "values": [4, 5, 6]}]
        fig = create_splom_figure(df, dims, 2, highlighted_iteration=1)
        assert isinstance(fig, go.Figure)
        # Should have main trace + highlight trace
        assert len(fig.data) >= 2

    def test_with_pareto(self):
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "sample_id": [0, 1, 2]})
        dims = [{"label": "a", "values": [1, 2, 3]}, {"label": "b", "values": [4, 5, 6]}]
        fig = create_splom_figure(df, dims, 2, pareto_indices=[0, 2])
        assert isinstance(fig, go.Figure)
        # Should have main trace + pareto trace
        assert len(fig.data) >= 2

    def test_diagonal_hidden_two_vars(self):
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "sample_id": [0, 1, 2]})
        dims = [{"label": "a", "values": [1, 2, 3]}, {"label": "b", "values": [4, 5, 6]}]
        result = create_splom_figure(df, dims, 2, diagonal_visible=False)
        # With only 2 vars and diagonal hidden, should show a warning
        assert isinstance(result, dict)


class TestCreateEmptyFigureWithMessage:
    def test_returns_valid_figure(self):
        result = create_empty_figure_with_message("Hello")
        assert "data" in result
        assert "layout" in result
        assert result["layout"]["annotations"][0]["text"] == "Hello"


class TestCreateTableFigure:
    def test_with_data(self):
        df = pd.DataFrame({"val": [1.23456, 2.34567]}, index=["obj1", "obj2"])
        cats = {"obj1": "objectives", "obj2": "objectives"}
        result = create_table_figure(df, cats)
        assert "data" in result
        assert result["data"][0]["type"] == "table"

    def test_empty_dataframe(self):
        df = pd.DataFrame()
        result = create_table_figure(df)
        assert "data" in result


# ===================================================================
#   callbacks/channel_selection.py — detect_array_columns
# ===================================================================


class TestDetectArrayColumns:
    def test_python_list_strings(self):
        df = pd.DataFrame({
            "scalar": [1.0, 2.0],
            "arr": ["[1.0, 2.0, 3.0]", "[4.0, 5.0, 6.0]"],
        })
        csv_json = df.to_json(orient="split")
        result = detect_array_columns(csv_json)
        assert "arr" in result
        assert "scalar" not in result

    def test_numpy_style_strings(self):
        df = pd.DataFrame({
            "np_arr": ["[1. 2. 3.]", "[4. 5. 6.]"],
        })
        csv_json = df.to_json(orient="split")
        result = detect_array_columns(csv_json)
        assert "np_arr" in result

    def test_scalar_only(self):
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        csv_json = df.to_json(orient="split")
        result = detect_array_columns(csv_json)
        assert result == set()

    def test_none_input(self):
        assert detect_array_columns(None) == set()


# ===================================================================
#   layouts/components.py
# ===================================================================


class TestCreateButtonGroup:
    def test_empty_variables(self):
        from layouts.components import create_button_group
        assert create_button_group([], "Test", "primary", []) == []

    def test_basic_buttons(self):
        from layouts.components import create_button_group
        result = create_button_group(["obj1", "obj2"], "Objectives", "primary", [])
        assert len(result) > 0

    def test_selected_state(self):
        from layouts.components import create_button_group
        result = create_button_group(["obj1"], "Objectives", "primary", ["obj1"])
        # At minimum, should return components without error
        assert len(result) > 0


class TestCreateMainLayout:
    def test_returns_div(self):
        from layouts.layout import create_main_layout
        from dash import html
        layout = create_main_layout()
        assert isinstance(layout, html.Div)


# ===================================================================
#   Integration: end-to-end pipeline using generated SQL fixture
# ===================================================================

WEIS_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(MOO_DIR)))

# Add the postprocess_results script to the path
POSTPROCESS_DIR = os.path.join(WEIS_ROOT, "examples", "06_parametric_analysis")
if POSTPROCESS_DIR not in sys.path:
    sys.path.insert(0, POSTPROCESS_DIR)

# Import the fixture generator (co-located with this test file)
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
if TESTS_DIR not in sys.path:
    sys.path.insert(0, TESTS_DIR)
from _gen_fixture import build_sql_fixture


@pytest.fixture(scope="class")
def moo_fixture(tmp_path_factory):
    """Generate a small OpenMDAO SQL log + problem_vars.yaml for testing."""
    output_dir = str(tmp_path_factory.mktemp("moo_output"))
    build_sql_fixture(output_dir)

    from postprocess_results import sql_to_csv
    df = sql_to_csv(output_dir, use_multiprocessing=False)

    yaml_data = load_yaml_from_path(os.path.join(output_dir, "problem_vars.yaml"))
    processed = process_yaml_config(yaml_data)

    return {
        "output_dir": output_dir,
        "df": df,
        "yaml_data": yaml_data,
        "processed": processed,
    }


class TestIntegration:
    def test_sql_to_csv_produces_per_iteration_df(self, moo_fixture):
        """sql_to_csv should return one row per iteration."""
        df = moo_fixture["df"]
        assert len(df) == 5, "Expected 5 iterations from generated fixture"
        assert "variables" not in df.columns
        assert any("." in c for c in df.columns), "Columns should be dot-separated variable names"

    def test_csv_matches_yaml_variables(self, moo_fixture):
        """All objectives and design vars from YAML should appear in the CSV columns."""
        df = moo_fixture["df"]
        processed = moo_fixture["processed"]

        for obj_name in processed["objectives"]:
            assert obj_name in df.columns, f"Objective '{obj_name}' missing from CSV"
        for dv_name in processed["design_vars"]:
            assert dv_name in df.columns, f"Design var '{dv_name}' missing from CSV"

    def test_end_to_end_splom(self, moo_fixture):
        """Full pipeline: SQL → CSV → YAML → prepare_dataframe_for_splom."""
        df = moo_fixture["df"]
        processed = moo_fixture["processed"]

        selected = list(processed["objectives"]) + list(processed["design_vars"])
        sdf, dims, cats = prepare_dataframe_for_splom(df, selected, processed)

        assert sdf is not None, "prepare_dataframe_for_splom returned None"
        assert len(dims) >= 2, "Need at least 2 dimensions for SPLOM"
        assert len(sdf) == len(df), "Row count should match iterations"

    def test_detect_arrays_in_moo_csv(self, moo_fixture):
        """Array columns (e.g. constraint margins) should be detected."""
        df = moo_fixture["df"]
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            df.to_csv(f, index=False)
            tmp_csv = f.name
        try:
            csv_json = load_csv_from_path(tmp_csv)
            array_cols = detect_array_columns(csv_json)
            assert len(array_cols) > 0, "Expected array-valued constraint columns"
        finally:
            os.unlink(tmp_csv)

    def test_pareto_front_on_objectives(self, moo_fixture):
        """Pareto front should return valid indices."""
        df = moo_fixture["df"]
        processed = moo_fixture["processed"]
        obj_names = list(processed["objectives"])

        pareto = find_pareto_front(obj_names, df)
        assert len(pareto) >= 1, "Expected at least one Pareto-optimal point"
        assert all(0 <= i < len(df) for i in pareto), "Pareto indices out of range"
