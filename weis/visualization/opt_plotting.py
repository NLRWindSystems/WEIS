import glob

import glob
import json
import multiprocessing as mp

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import openmdao.api as om

from weis.visualization.utils import *


def plot_conv(
    keyset_in,
    map_dataOM_vars,
    use_casewise_feasibility=False,
    feas_tol=1e-5,
    figax=None,
    alpha=None,
):
    """
    plot a set of keys

    args:
        keyset_in: list[str]
            list of keys to plot the convergence data for
        map_dataOM_vars: dict[str -> dict]
            map from a case of interest by name to an OM data dict to plot
        use_casewise_feasibility: bool
            if plotting a constraint should we plot feasibility w.r.t. that constraint (vs. all)

    returns:
        fig : plt.Figure
        ax : plt.Axes
    """

    if len(keyset_in) == 0:
        return

    markerstyle = "x"
    markersize = 5
    linestyle = "-"


    fig, axes = figax if figax else plt.subplots(
        len(keyset_in),
        1,
        sharex=True,
        figsize=(6, 0.60 * 4 * len(keyset_in)),
        squeeze=False,
        dpi=150,
    )

    has_ref_vals = type(keyset_in) == dict

    if has_ref_vals:
        key_val_map = keyset_in
        keyset = keyset_in.keys()
    else:
        keyset = keyset_in

    pt_imethod = []
    for imethod, method in enumerate(map_dataOM_vars.keys()):
        if imethod == 0:
            markerstyle = "o"
        elif imethod == 1:
            markerstyle = "p"
        elif imethod == 2:
            markerstyle = "s"
        else:
            markerstyle = "P"

        pt0 = axes[0, 0].plot(
            [],
            [],
            markerstyle + linestyle,
            label=method,
            markersize=markersize,
            # color=(0.5,0.5,0.5),
            alpha=alpha,
        )
        dataOM = map_dataOM_vars[method][0]
        vars = map_dataOM_vars[method][1]
        tfeas, varfeas = get_feasible_iterations(dataOM, vars, feas_tol=feas_tol)

        for idx_ax, key in enumerate(keyset):
            if key in ["rank", "iter",]: continue
            if use_casewise_feasibility and key in varfeas.keys():
                feas_val = varfeas[key]
            else:
                feas_val = tfeas  # use total feasibility

            axes[idx_ax, 0].plot(
                np.squeeze(dataOM[key]),
                linestyle,
                label="".join(["_", method, "_"]),
                color=pt0[-1].get_color(),
                markersize=markersize,
                alpha=alpha,
            )
            axes[idx_ax, 0].plot(
                np.ma.array(
                    dataOM[key],
                    mask=~(
                        feas_val * np.ones(
                            (
                                1,
                                np.array(dataOM[key]).shape[1]
                                if len(np.array(dataOM[key]).shape) > 1
                                else 1
                            ),
                            dtype=bool,
                        )
                    )
                ),
                markerstyle,
                label="".join(["_", method, "_"]),
                color=pt0[-1].get_color(),
                alpha=alpha,
                fillstyle="full",
                markersize=markersize,
            )
            axes[idx_ax, 0].plot(
                np.ma.array(
                    dataOM[key],
                    mask=(
                        feas_val * np.ones(
                            (
                                1,
                                np.array(dataOM[key]).shape[1]
                                if len(np.array(dataOM[key]).shape) > 1
                                else 1
                            ),
                            dtype=bool,
                        )
                    )
                ),
                markerstyle,
                label="".join(["_", method, "_"]),
                color=pt0[-1].get_color(),
                alpha=alpha,
                fillstyle="none",
                markersize=markersize,
            )
            if has_ref_vals:
                cval = key_val_map[key]
                if (cval[0] is not None) and (np.log10(np.abs(cval[0])) < 18):
                    axes[idx_ax, 0].plot([0, len(dataOM[key])], [cval[0], cval[0]], "b:", label="_lower bound_")
                if (cval[1] is not None) and (np.log10(np.abs(cval[1])) < 18):
                    axes[idx_ax, 0].plot([0, len(dataOM[key])], [cval[1], cval[1]], "r:", label="_upper bound_")
            axes[idx_ax, 0].set_title(key)

    if has_ref_vals:
        axes[0, 0].plot([], [], "b:", label="lower bound")
        axes[0, 0].plot([], [], "r:", label="upper bound")
    axes[0, 0].legend()
    fig.tight_layout()

    return fig, axes


def plot_convergence(data, vars_to_plot, title_prefix, bounds=None,
                     aliases=None, save_path=None):
    """Plot iteration history for a list of recorded variables with optional bound lines.

    This is a lightweight alternative to :func:`plot_conv` that works directly
    with the dict returned by :func:`~weis.visualization.utils.load_OMsql`
    and accepts a *bounds* dict (e.g. from
    :func:`~weis.visualization.utils.load_problem_vars_yaml` or
    :func:`~weis.visualization.utils.load_bounds_from_analysis_yaml`).

    Parameters
    ----------
    data : dict
        ``{var_name: list_of_values_per_iteration}`` as returned by
        :func:`~weis.visualization.utils.load_OMsql`.
    vars_to_plot : list[str]
        OpenMDAO variable names to include in the figure.
    title_prefix : str
        Text used as the figure super-title.
    bounds : dict, optional
        ``{var_name: {"lower": float | None, "upper": float | None}}``.
        When provided, horizontal dashed lines are drawn at the bound values.
    aliases : dict, optional
        ``{var_name: "Human-Readable Label"}``.  Falls back to the raw
        variable name when not provided.
    save_path : str, optional
        If given, the figure is saved to this path (PNG recommended).

    Returns
    -------
    fig : matplotlib.figure.Figure or None
        The generated figure, or ``None`` if no plottable variables were found.
    """
    bounds = bounds or {}
    aliases = aliases or {}

    # Filter to variables actually present in data
    vars_present = [v for v in vars_to_plot if v in data]
    vars_missing = [v for v in vars_to_plot if v not in data]
    if vars_missing:
        print(f"  Skipping (not recorded): {vars_missing}")
    if not vars_present:
        print(f"  No variables found for '{title_prefix}' — skipping plot.")
        return None

    n = len(vars_present)
    fig, axes = plt.subplots(n, 1, figsize=(10, 3 * n), sharex=True)
    if n == 1:
        axes = [axes]
    fig.suptitle(title_prefix, fontsize=13)

    for ax, var in zip(axes, vars_present):
        vals = np.array(data[var])
        if vals.ndim == 1:
            ax.plot(vals, marker="o", ms=4)
        else:
            for i in range(vals.shape[1]):
                ax.plot(vals[:, i], marker="o", ms=4, label=f"[{i}]")
            ax.legend(fontsize=8)

        # Draw bounds as horizontal dashed lines
        if var in bounds:
            if bounds[var].get("upper") is not None:
                ax.axhline(bounds[var]["upper"], color="r", ls="--", lw=1.2,
                           label=f"upper={bounds[var]['upper']:.3g}")
            if bounds[var].get("lower") is not None:
                ax.axhline(bounds[var]["lower"], color="b", ls="--", lw=1.2,
                           label=f"lower={bounds[var]['lower']:.3g}")
            ax.legend(fontsize=8)

        ax.set_title(aliases.get(var, var), pad=3)
        ax.set_ylabel("value", labelpad=4)
        ax.grid(True)

    axes[-1].set_xlabel("Optimizer iteration")
    plt.tight_layout(rect=[0, 0, 1, 0.98])
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Saved: {save_path}")
    plt.close(fig)
    return fig

