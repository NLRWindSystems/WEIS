#!/usr/bin/env python3
import os
from weis import weis_main
from openmdao.utils.mpi import MPI

# TEST_RUN will reduce the number and duration of simulations
TEST_RUN = True

## File management
run_dir = os.path.dirname( os.path.realpath(__file__) )
fname_wt_input = os.path.join(run_dir, "..", "..", "2_models", "stage-1-aeroStruct-aero_analysis_v2p0.yaml")
fname_modeling_options = os.path.join(run_dir, "stage-2-controller_modeling.yaml") # compare to examples/05_control_optimization/rosco_opt_modeling.yaml
fname_analysis_options = os.path.join(run_dir, "stage-2-controller_analysis.yaml") # same as examples/05_control_optimization/rosco_opt_analysis.yaml

wt_opt, modeling_options, analysis_options = weis_main(
    fname_wt_input, 
    fname_modeling_options, 
    fname_analysis_options,
    test_run=TEST_RUN,
    )

