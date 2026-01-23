#!/usr/bin/env python3
import os
from weis import weis_main

import numpy as np
from openfast_io import FileTools
import pandas as pd
import matplotlib.pyplot as plt


def plotter(x,y, xlabel, ylabel, title, ax=None):
    if ax is None:
        return None

    ax.plot(np.array(eval(x)), np.array(eval(y)))
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    return ax

# TEST_RUN will reduce the number and duration of simulations
TEST_RUN = False

## File management
run_dir = os.path.dirname( os.path.realpath(__file__) )
fname_wt_input = os.path.join(run_dir, "..", "..", "..", "00_setup", "ref_turbines", "IEA-22-280-RWT_Floater.yaml")
fname_modeling_options = os.path.join(run_dir, "stage-0-baseline_modeling.yaml")
fname_analysis_options = os.path.join(run_dir, "stage-0-baseline_analysis.yaml")

wt_opt, modeling_options, opt_options = weis_main(fname_wt_input, 
                                                 fname_modeling_options, 
                                                 fname_analysis_options,
                                                 test_run=TEST_RUN
                                                 )


weis_turb = pd.read_csv(os.path.join(run_dir,"outputs/stage-0-baseline.csv"), index_col=0)


# Creating Cp, Ct, power, thrust, pitch, induction vs WS
fig,ax = plt.subplots(3, 2, figsize=(12, 10),)
fig.suptitle("Turbine Performance Curves", fontsize=16)

ax[0, 0] = plotter(weis_turb.loc['rotorse.rp.powercurve.V']['values'],
                   weis_turb.loc['rotorse.rp.powercurve.Cp_aero']['values'],
                  xlabel='Wind Speed (m/s)', ylabel='Cp',
                  title='Power Coefficient (Cp)', ax=ax[0, 0])

ax[0, 1] = plotter(weis_turb.loc['rotorse.rp.powercurve.V']['values'],
                   weis_turb.loc['rotorse.rp.powercurve.Ct_aero']['values'],
                  xlabel='Wind Speed (m/s)', ylabel='Ct',
                  title='Thrust Coefficient (Ct)', ax=ax[0, 1])


ax[1, 0] = plotter(weis_turb.loc['rotorse.rp.powercurve.V']['values'],
                     weis_turb.loc['rotorse.rp.powercurve.P_aero']['values'],
                    xlabel='Wind Speed (m/s)', ylabel='Power (kW)',
                    title='Turbine Power Output', ax=ax[1, 0])

ax[1, 1] = plotter(weis_turb.loc['rotorse.rp.powercurve.V']['values'],
                     weis_turb.loc['rotorse.rp.powercurve.T']['values'],
                    xlabel='Wind Speed (m/s)', ylabel='Thrust (kN)',
                    title='Turbine Thrust Output', ax=ax[1, 1])

ax[2, 0] = plotter(weis_turb.loc['rotorse.rp.powercurve.V']['values'],
                     weis_turb.loc['rotorse.rp.powercurve.pitch']['values'],
                    xlabel='Wind Speed (m/s)', ylabel='Pitch Angle (deg)',
                    title='Turbine Pitch Angle', ax=ax[2, 0])

ax[2, 1] = plotter(weis_turb.loc['rotorse.rp.powercurve.V']['values'],
                     weis_turb.loc['rotorse.rp.powercurve.ax_induct_rotor']['values'],
                    xlabel='Wind Speed (m/s)', ylabel='Induction Factor',
                    title='Turbine Induction Factor', ax=ax[2, 1])

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig(os.path.join(run_dir,"outputs/turbine_performance_curves.png"), dpi=300)
