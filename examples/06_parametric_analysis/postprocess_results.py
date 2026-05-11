"""
Postprocess WEIS optimization results from OpenMDAO SQL logs.

Reads driver-recorded cases from one or more ``log_opt.sql`` files and
produces a flat CSV with **one row per design iteration** and one column per
recorded variable.  This CSV is the expected input for the
:ref:`MOO Dashboard <moo_dashboard>`.

Usage
-----
As a script (from this example directory)::

    python postprocess_results.py

As a library from any directory::

    from postprocess_results import load_OMsql, sql_to_csv
    df = sql_to_csv("/path/to/output_dir")
"""

import glob
import os

import numpy as np
import pandas as pd
import multiprocessing as mp

import openmdao.api as om


def load_OMsql(log):
    """Read all driver cases from a single SQL log and return a dict of lists."""
    print("loading {}".format(log))
    cr = om.CaseReader(log)
    rec_data = {}
    cases = cr.get_cases("driver")
    for case in cases:
        for key in case.outputs.keys():
            if key not in rec_data:
                rec_data[key] = []
            rec_data[key].append(case[key])

    return rec_data


def sql_to_csv(output_dir, sql_pattern="log_opt.sql*", use_multiprocessing=True):
    """
    Read all SQL logs in *output_dir* and return a DataFrame with one row per
    design iteration.

    Parameters
    ----------
    output_dir : str
        Directory containing ``log_opt.sql`` file(s).
    sql_pattern : str
        Glob pattern for the SQL files (default ``"log_opt.sql*"``).
    use_multiprocessing : bool
        Use ``multiprocessing.Pool`` for parallel loading (default ``True``).

    Returns
    -------
    pd.DataFrame
        Flat DataFrame — one row per iteration, one column per variable.
        Scalar variables are stored as floats; array variables are stored as
        string representations (e.g. ``"[1.0, 2.0, 3.0]"``).
    """
    doe_logs = glob.glob(os.path.join(output_dir, sql_pattern))
    # Remove the "meta" log
    doe_logs = [log for log in doe_logs if "meta" not in log]

    if len(doe_logs) < 1:
        raise FileNotFoundError(
            f"No SQL logs matching '{sql_pattern}' found in {output_dir}"
        )

    if use_multiprocessing and len(doe_logs) > 1:
        cores = mp.cpu_count()
        pool = mp.Pool(min(len(doe_logs), cores))
        outdata = pool.map(load_OMsql, doe_logs)
        pool.close()
        pool.join()
    else:
        outdata = [load_OMsql(log) for log in doe_logs]

    collected_data = {}
    for data in outdata:
        for key in data:
            if key not in collected_data:
                collected_data[key] = []

            for val in data[key]:
                if isinstance(val, int):
                    collected_data[key].append(np.array(val))
                elif len(val) == 1:
                    try:
                        collected_data[key].append(np.array(val[0]))
                    except Exception:
                        collected_data[key].append(np.array(val))
                else:
                    collected_data[key].append(np.array(val))

    return pd.DataFrame.from_dict(collected_data)


if __name__ == "__main__":
    # sql outfile directory
    run_dir = os.path.dirname(os.path.realpath(__file__))
    output_dir = os.path.join(run_dir, "outputs/06_openfast_doe")

    df = sql_to_csv(output_dir)

    outdata_fpath = os.path.join(output_dir, "doe_outdata.csv")
    df.to_csv(outdata_fpath, index=False)
    print("Saved {}".format(outdata_fpath))   

