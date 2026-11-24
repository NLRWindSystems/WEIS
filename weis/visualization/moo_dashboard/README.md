# Dashboard for Multi-Objective Optimization

This dashboard is for visualizing multi objective optimization results to support better trade-off analysis.
This has the same coding environment as WEIS Input/Output Viz tool (appServer/) where it's mainly based on Dash and Plotly. This is separate and works independently for now, but could be potentially merged later.

## How to Run

```
conda activate weis-env
python main.py      # Make sure run this command at moo_dashboard directory
```

<!-- ## Action Items
- [X] Data Upload
- [X] Dynamic Scatter plot matrix renderer with toggle buttons - channel multi-selection from the user
- [X] Link samples
    - [X] Highlight samples once clicked
    - [X] Maybe add text field to show all information on that iteration -> Created data table
- How to visualize array values?
    - [X] Constraints (e.g., constr_fixed_margin, constr_draft_heel_margin, etc.):
        - Show dropdown list when array-value channel is clicked (combined single plot vs separated plots). Either way, show both min and max where constraints bounds (min < min, max > max) are already checked
    - [ ] Design variables:
        - Different approach would be needed. Work on this after getting new dataset from Dan
- [X] Show Pareto Fronts (Higher priority)
    - [X] Calculate from scratch
- [X] Download interactive version of html
- [X] Add toggle button to show or not show diagonal line in SPLOM
- [X] Add objective options (min vs max) next to buttons
- [ ] Add testing script to check if app works
- [X] Submit PR when it's ready

- How to calculate Pareto Fronts with 3 objective functions?
    - Should be okay with Cory's function
    - For cross checking, we need SPLOM visualization

- Debug
    - [X] SPLOM initialization doesn't work properly, where the first Objective channel is automatically selected by default.
    - [X] Not AEP showing on SPLOM due to extremely small variance -- added special handling for this (but not necessary for general)
    - [X] Layout to leverage full screen width and remove empty spaces

## Food for Thoughts
- How to work on 3+ objectives?
- 3D+ Pareto Fronts?
- Connect all of the optimization results (DoE, DLC, Timeseries, etc.) -->
