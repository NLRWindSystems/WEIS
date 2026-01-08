#!/usr/bin/env python3
import os
from weis import weis_main
from openmdao.utils.mpi import MPI


## File management
run_dir = os.path.dirname( os.path.realpath(__file__) )
fname_wt_input = os.path.join(run_dir, "..", "..", "2_models", "stage-3-semisub_raft_v2p0.yaml")
fname_modeling_options = os.path.join(run_dir, "stage-3.5-semisub_of_modeling.yaml")
fname_analysis_options = os.path.join(run_dir, "stage-3.5-semisub_of_analysis.yaml")

wt_opt, modeling_options, analysis_options = weis_main(
        fname_wt_input, fname_modeling_options, fname_analysis_options, test_run=True
    )

