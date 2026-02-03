.. _moo_dashboard:


WEIS Multi-Objective Optimization Dashboard
============================================

The MOO Dashboard is an interactive visualization tool for analyzing multi-objective optimization results from WEIS. It provides real-time exploration of design space, Pareto fronts, and trade-offs between competing objectives.

Overview
--------

The dashboard enables users to:

* Visualize high-dimensional optimization results using Scatter Plot Matrix (SPLOM)
* Identify and explore Pareto-optimal solutions
* Analyze relationships between design variables, objectives, and constraints
* Export interactive visualizations for reports and presentations
* Compare individual design iterations with detailed data tables

.. video:: images/viz/MOO/dashboard.mov
   :width: 900
   :autoplay:

Installation
------------

The MOO Dashboard is included with WEIS. Ensure you have the required dependencies:

.. code-block:: bash

   conda activate weis-env
   pip install dash plotly pandas numpy pyyaml dash-bootstrap-components

Running the Dashboard
---------------------

Launch the dashboard from the command line:

.. code-block:: bash

   conda activate weis-env
   cd weis/visualization/moo_dashboard
   python main.py

The dashboard will open in your default browser at ``http://localhost:8050``.

User Interface
--------------

The dashboard consists of four main sections:

1. **File Loaders**
   
   * **CSV File**: Load optimization results (design variables, objectives, constraints)
   * **YAML File**: Load problem definition (variable categories, optimization goals)


2. **Controls & Variables**
   
   Select which variables to visualize:
   
   * **Objectives** (blue): Quantities to minimize or maximize
   * **Constraints** (orange): Feasibility requirements
   * **Design Variables** (green): Parameters that can be modified
   
   For each objective, select whether to minimize or maximize using toggle buttons.


3. **Scatter Plot Matrix (SPLOM)**
   
   Interactive matrix showing all pairwise relationships between selected variables:
   
   * **Color scale**: Represents iteration number
   * **Red diamonds**: Pareto-optimal solutions (if enabled)
   * **Green star**: Currently highlighted point (when clicked)
   * **Click** on any point to see detailed values in the data table
   
   Controls:
   
   * ``Show/Hide Pareto Front``: Toggle visualization of optimal solutions
   * ``Show/Hide Diagonal``: Toggle diagonal histogram plots
   * ``Clear Highlighting``: Remove point selection
   * ``Download Dashboard``: Export as standalone interactive HTML


4. **Data Table**
   
   Displays detailed values for the selected iteration.


Input File Formats
------------------

CSV File
~~~~~~~~

The CSV file should contain one row per optimization iteration with columns for:

* Design variables (e.g., ``tune_rosco_ivc.Kp_float``)
* Objectives (e.g., ``aeroelastic.AEP``)
* Constraints (e.g., ``aeroelastic.rotor_overspeed``)

Example:

.. csv-table::
   :header: "aeroelastic.AEP", "aeroelastic.DEL_TwrBsMyt", "aeroelastic.rotor_overspeed", "aeroelastic.Max_PtfmPitch", "tune_rosco_ivc.Kp_float", "tune_rosco_ivc.ps_percent"
   :widths: 15, 15, 15, 15, 15, 15

   "410786235558.229", "87616.5338", "0.0905", "5.0551", "-20.4375", "0.6525"
   "421847787601.9160", "101079.1819", "0.0848", "5.2194", "-8.4375", "0.8725"


YAML File
~~~~~~~~~

The YAML file defines the optimization problem structure:

.. code-block:: yaml

  design_vars:
    -     -  tune_rosco_ivc.Kp_float
          -  name: tune_rosco_ivc.Kp_float
              upper: 0.0
              lower: -30.0
              size: 1
              val: [-9.937499999999996]
    -     -  tune_rosco_ivc.ps_percent
          -  name: tune_rosco_ivc.ps_percent
              upper: 1.0
              lower: 0.6
              size: 1
              val: [0.8775]
  constraints:
    -     -  aeroelastic.rotor_overspeed
          -  name: aeroelastic.rotor_overspeed
              lower: 0.0
              upper: 0.2
              equals: ''
              size: 1
              val: [0.1168584634534533]
    -     -  aeroelastic.Max_PtfmPitch
          -  name: aeroelastic.Max_PtfmPitch
              lower: -1e+30
              upper: 5.5
              equals: ''
              size: 1
              val: [5.111509323120117]
  objectives:
    -     -  aeroelastic.AEP
          -  name: aeroelastic.AEP
              size: 1
              val: [-4209011.602067122]
    -     -  aeroelastic.DEL_TwrBsMyt
          -  name: aeroelastic.DEL_TwrBsMyt
              size: 1
              val: [0.9920550255927588]

Features
--------

Pareto Front Calculation
~~~~~~~~~~~~~~~~~~~~~~~~

The dashboard automatically calculates Pareto-optimal solutions based on:

* Selected objectives and their optimization sense (minimize/maximize)
* Non-dominated sorting algorithm
* Visual distinction with red diamond markers

The Pareto front represents the set of solutions where no objective can be improved without degrading another.

Array Variable Handling
~~~~~~~~~~~~~~~~~~~~~~~

Variables containing arrays (e.g., blade chord distribution) are automatically detected and split into:

* ``variable_min``: Minimum value in the array
* ``variable_max``: Maximum value in the array

This allows visualization of array-valued design variables in the SPLOM.

Interactive HTML Export
~~~~~~~~~~~~~~~~~~~~~~~

The ``Download Dashboard`` button creates a standalone HTML file that saves the current status of the dashboard, allowing you to continue analysis offline. The exported file contains:

* Full interactive SPLOM with all data points
* Current selections and highlighted points
* Click-through functionality for data table updates
* Toggle controls for Pareto front and diagonal visibility
* All optimization data embedded for complete offline access
* No external dependencies or internet connection required

.. video:: images/viz/MOO/export.mov
   :width: 900
   :autoplay:

Configuration
-------------

Settings can be modified in ``config/settings.py``:

.. code-block:: python

   # Server configuration
   HOST = '0.0.0.0'
   PORT = 8050
   
   # Plot styling
   DEFAULT_PLOT_WIDTH = 800
   DEFAULT_PLOT_HEIGHT = 800
   MARKER_SIZE = 4
   
   # Color schemes
   HIGHLIGHT_COLOR = '#00FF41'  # Bright green
   COLOR_SCALES = {
       'objectives': 'primary',    # Blue
       'constraints': 'warning',   # Orange
       'design_vars': 'success'    # Green
   }


Architecture
------------

The dashboard follows a modular architecture:

.. code-block:: text

   moo_dashboard/
   ├── main.py              # Entry point
   ├── app_init.py          # Application initialization
   ├── config/
   │   └── settings.py      # Configuration constants
   ├── layouts/
   │   ├── layout.py        # Main page layout
   │   └── components.py    # Reusable UI components
   ├── callbacks/
   │   ├── data_loading.py      # File upload/loading
   │   ├── channel_selection.py # Variable selection
   │   └── visualization.py     # Plot updates and interactions
   └── utils/
       ├── data_processing.py   # Data transformation and Pareto calculation
       └── plot_helpers.py      # Plotly figure creation


Troubleshooting
---------------

Dashboard won't start
~~~~~~~~~~~~~~~~~~~~~

Check that the port is not already in use:

.. code-block:: bash

   lsof -i :8050

Change the port in ``config/settings.py`` if needed.

Data not loading
~~~~~~~~~~~~~~~~

Verify:

* CSV file has proper column headers
* YAML file follows the required structure
* File paths are absolute (not relative)
* Files are accessible with read permissions

Pareto front not showing
~~~~~~~~~~~~~~~~~~~~~~~~

Ensure:

* At least 2 objectives are selected
* Objective senses (min/max) are configured correctly
* CSV data contains valid numeric values for objectives

Click events not working
~~~~~~~~~~~~~~~~~~~~~~~~

This is a known issue with some browser configurations. Try:

* Using a different browser (Chrome/Firefox recommended)
* Clearing browser cache
* Disabling browser extensions that might interfere with JavaScript

