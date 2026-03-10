#!/usr/bin/env python3
import os
from weis import weis_main

TEST_RUN = True

run_dir = os.path.dirname( os.path.realpath(__file__) )
fname_wt_input = os.path.join(run_dir, "..", "..", "2_models", "new-20-270-RWT_Floater.yaml")
fname_modeling_options = os.path.join(run_dir, "stage-4-dlcs_modeling.yaml")
fname_analysis_options = os.path.join(run_dir, "stage-4-dlcs_analysis.yaml")

wt_opt, modeling_options, analysis_options = weis_main(
        fname_wt_input, fname_modeling_options, fname_analysis_options, test_run=TEST_RUN
    )

