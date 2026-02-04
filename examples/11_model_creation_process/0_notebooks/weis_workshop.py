# Simple Colab detection
import sys
import numpy as np
import matplotlib.pyplot as plt
import openmdao.api as om
import pandas as pd
import pickle

# TODO:
# 1. Add structural plots for the blade!

# Global variable to check if we're in Google Colab
IN_COLAB = 'google.colab' in sys.modules

if IN_COLAB:
    print("Running in Google Colab")
else:
    print("Running in local environment")

def plotter(x,y, xlabel=None, ylabel=None, title=None, ax=None, label=None):
    if ax is None:
        return None

    ax.plot(np.array(eval(x)), np.array(eval(y)), label=label)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if label:
        ax.legend()
    return ax

# This function loads the openmdao sql file and does most of the work here
def load_OMsql(log):
    print('loading {}'.format(log))
    cr = om.CaseReader(log)
    rec_data = {}
    cases = cr.get_cases('driver')
    for case in cases:
        for key in case.outputs.keys():
            if key not in rec_data:
                rec_data[key] = []
            rec_data[key].append(case[key])
        
    return rec_data

def plot_convergence(logs, vars):

    # create the figure
    fig, ax = plt.subplots(nrows=len(vars), figsize=(10, 6*len(vars)))

    for var in vars:

        # start by squeezing the data
        data = np.squeeze(logs[var])

        ax[vars.index(var)].plot(data, marker='o')
        ax[vars.index(var)].set_title(var)
        ax[vars.index(var)].grid(True)
        ax[vars.index(var)].set_xlabel('Iteration')
        # ax[vars.index(var)].set_ylabel(var)

    return None



def plot_comparison_plot(turb_csv, label, fig = None):

    if fig is None:
        fig,ax = plt.subplots(2, 3, figsize=(10, 10), sharex=True)
        fig.suptitle("Turbine Performance Curves", fontsize=16)

    ax[0, 0] = plotter(turb_csv.loc['rotorse.rp.powercurve.V']['values'],
                       turb_csv.loc['rotorse.rp.powercurve.Cp_aero']['values'],
                      ylabel='Cp',
                      title='Power Coefficient (Cp)', ax=ax[0, 0], label = label)
    ax[0, 0].grid(True)
    
    ax[0, 1] = plotter(turb_csv.loc['rotorse.rp.powercurve.V']['values'],
                       turb_csv.loc['rotorse.rp.powercurve.Ct_aero']['values'],
                      ylabel='Ct',
                      title='Thrust Coefficient (Ct)', ax=ax[0, 1], label = label)
    ax[0, 1].grid(True)
    
    ax[1, 0] = plotter(turb_csv.loc['rotorse.rp.powercurve.V']['values'],
                         turb_csv.loc['rotorse.rp.powercurve.P']['values'],
                        ylabel='Power (kW)',
                        title='Turbine Power Output', ax=ax[1, 0], label = label)
    ax[1, 0].grid(True)
    
    ax[1, 1] = plotter(turb_csv.loc['rotorse.rp.powercurve.V']['values'],
                         turb_csv.loc['rotorse.rp.powercurve.T']['values'],
                        xlabel='Wind Speed (m/s)', ylabel='Thrust (kN)',
                        title='Turbine Thrust Output', ax=ax[1, 1], label = label)
    ax[1, 1].grid(True)
    
    ax[0, 2] = plotter(turb_csv.loc['rotorse.rp.powercurve.V']['values'],
                         turb_csv.loc['rotorse.rp.powercurve.pitch']['values'],
                        xlabel='Wind Speed (m/s)', ylabel='Pitch (deg)',
                        title='Turbine Pitch Angle', ax=ax[0, 2], label = label)
    ax[0, 2].grid(True)
    
    ax[1, 2] = plotter(turb_csv.loc['rotorse.rp.powercurve.V']['values'],
                         turb_csv.loc['rotorse.rp.powercurve.Omega']['values'],
                        xlabel='Wind Speed (m/s)', ylabel='Rotor Speed (rpm)',
                        title='Turbine Rotor Speed', ax=ax[1, 2], label = label)
    ax[1, 2].grid(True)


def plot_rotor_comparison(baseline_turb, optimized_turb):

    def plotter(x,y, xlabel, ylabel, title, ax=None, label=None):
        if ax is None:
            return None

        ax.plot(np.array(eval(x)), np.array(eval(y)), label=label)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        if label:
            ax.legend()
        return ax
    

    # Creating Cp, Ct, power, thrust, pitch, induction vs WS
    fig,ax = plt.subplots(3, 2, figsize=(12, 10),)
    fig.suptitle("Turbine Performance Curves", fontsize=16)

    ax[0, 0] = plotter(optimized_turb.loc['rotorse.rp.powercurve.V']['values'],
                    optimized_turb.loc['rotorse.rp.powercurve.Cp_aero']['values'],
                    xlabel='Wind Speed (m/s)', ylabel='Cp',
                    title='Power Coefficient (Cp)', ax=ax[0, 0], label = 'Optimized')

    ax[0, 0] = plotter(baseline_turb.loc['rotorse.rp.powercurve.V']['values'],
                    baseline_turb.loc['rotorse.rp.powercurve.Cp_aero']['values'],
                    xlabel='Wind Speed (m/s)', ylabel='Cp',
                    title='Power Coefficient (Cp)', ax=ax[0, 0], label = 'Baseline')

    ax[0, 1] = plotter(optimized_turb.loc['rotorse.rp.powercurve.V']['values'],
                    optimized_turb.loc['rotorse.rp.powercurve.Ct_aero']['values'],
                    xlabel='Wind Speed (m/s)', ylabel='Ct',
                    title='Thrust Coefficient (Ct)', ax=ax[0, 1], label = 'Optimized')

    ax[0, 1] = plotter(baseline_turb.loc['rotorse.rp.powercurve.V']['values'],
                    baseline_turb.loc['rotorse.rp.powercurve.Ct_aero']['values'],
                    xlabel='Wind Speed (m/s)', ylabel='Ct',
                    title='Thrust Coefficient (Ct)', ax=ax[0, 1], label = 'Baseline')

    ax[1, 0] = plotter(optimized_turb.loc['rotorse.rp.powercurve.V']['values'],
                        optimized_turb.loc['rotorse.rp.powercurve.P']['values'],
                        xlabel='Wind Speed (m/s)', ylabel='Power (kW)',
                        title='Turbine Power Output', ax=ax[1, 0], label = 'Optimized')

    ax[1, 0] = plotter(baseline_turb.loc['rotorse.rp.powercurve.V']['values'],
                        baseline_turb.loc['rotorse.rp.powercurve.P']['values'],
                        xlabel='Wind Speed (m/s)', ylabel='Power (kW)',
                        title='Turbine Power Output', ax=ax[1, 0], label = 'Baseline')

    ax[1, 1] = plotter(optimized_turb.loc['rotorse.rp.powercurve.V']['values'],
                        optimized_turb.loc['rotorse.rp.powercurve.T']['values'],
                        xlabel='Wind Speed (m/s)', ylabel='Thrust (kN)',
                        title='Turbine Thrust Output', ax=ax[1, 1], label = 'Optimized')

    ax[1, 1] = plotter(baseline_turb.loc['rotorse.rp.powercurve.V']['values'],
                    baseline_turb.loc['rotorse.rp.powercurve.T']['values'],
                    xlabel='Wind Speed (m/s)', ylabel='Thrust (kN)',
                    title='Turbine Thrust Output', ax=ax[1, 1], label = 'Baseline')

    ax[2, 0] = plotter(optimized_turb.loc['rotorse.rp.powercurve.V']['values'],
                        optimized_turb.loc['rotorse.rp.powercurve.pitch']['values'],
                        xlabel='Wind Speed (m/s)', ylabel='Pitch Angle (deg)',
                        title='Turbine Pitch Angle', ax=ax[2, 0], label = 'Optimized')

    ax[2, 0] = plotter(baseline_turb.loc['rotorse.rp.powercurve.V']['values'],
                    baseline_turb.loc['rotorse.rp.powercurve.pitch']['values'],
                    xlabel='Wind Speed (m/s)', ylabel='Pitch Angle (deg)',
                    title='Turbine Pitch Angle', ax=ax[2, 0], label = 'Baseline')

    ax[2, 1] = plotter(optimized_turb.loc['rotorse.rp.powercurve.V']['values'],
                        optimized_turb.loc['rotorse.rp.powercurve.ax_induct_rotor']['values'],
                        xlabel='Wind Speed (m/s)', ylabel='Induction Factor',
                        title='Turbine Induction Factor', ax=ax[2, 1], label = 'Optimized')

    ax[2, 1] = plotter(baseline_turb.loc['rotorse.rp.powercurve.V']['values'],
                    baseline_turb.loc['rotorse.rp.powercurve.ax_induct_rotor']['values'],
                    xlabel='Wind Speed (m/s)', ylabel='Induction Factor',
                    title='Turbine Induction Factor', ax=ax[2, 1], label = 'Baseline')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    # plt.savefig("plots/turbine_performance_curves.png", dpi=300)


    # Geomtric plots

    fig,ax = plt.subplots(1, 2, figsize=(12, 5),)

    ax[0] = plotter(baseline_turb.loc['rotorse.r']['values'],
                    baseline_turb.loc['rotorse.chord']['values'],
                    xlabel='Span (m)', ylabel='Chord (m)',
                    title='Blade Chord Distribution', ax=ax[0], label = 'Baseline')

    ax[0] = plotter(optimized_turb.loc['rotorse.r']['values'],
                    optimized_turb.loc['rotorse.chord']['values'],
                    xlabel='Span (m)', ylabel='Chord (m)',
                    title='Blade Chord Distribution', ax=ax[0], label = 'Optimized')

    ax[1] = plotter(baseline_turb.loc['rotorse.r']['values'],
                    baseline_turb.loc['rotorse.ccblade.theta_in']['values'],
                    xlabel='Span (m)', ylabel='Twist (deg)',
                    title='Blade Twist Distribution', ax=ax[1], label = 'Baseline')

    ax[1] = plotter(optimized_turb.loc['rotorse.r']['values'],
                    optimized_turb.loc['rotorse.ccblade.theta_in']['values'],
                    xlabel='Span (m)', ylabel='Twist (deg)',
                    title='Blade Twist Distribution', ax=ax[1], label = 'Optimized')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    # plt.savefig("plots/blade_geometry.png", dpi=300)

def plot_weis_summary(data, y_params=None):
    """
    Create nx2 scatter plots of WEIS summary data using absolute values
    
    Parameters:
    data : pandas.DataFrame
        WEIS summary statistics dataframe with MultiIndex columns
    y_params : list of tuples, optional
        List of (parameter_name, statistic) tuples for y-axis parameters
        If None, uses default set of 4 parameters
    """
    # Create a copy to avoid modifying original data
    df = data.copy()
    
    # Extract DLC case from index - fix the extraction method
    dlc_cases = []
    for idx in df.index:
        match = pd.Series([idx]).str.extract(r'(DLC\d+\.\d+)')[0].iloc[0]
        dlc_cases.append(match)
    
    df['DLC_Case'] = dlc_cases
    
    # Define the parameters to plot (using absolute values - no normalization)
    x_param = ('Wind1VelX', 'mean')
    
    # Use provided y_params or default set
    if y_params is None:
        y_params = [
            ('GenSpeed', 'mean'),
            ('RootMyb1', 'max'),
            ('TwrBsAxMxyt', 'median'),
            ('PtfmPitch', 'max')
        ]
    
    # Calculate number of rows needed for nx2 layout
    n_plots = len(y_params)
    n_rows = (n_plots + 1) // 2  # Ceiling division
    
    # Create figure with nx2 subplots and shared x-axis
    fig, axes = plt.subplots(n_rows, 2, figsize=(15, 6*n_rows), sharex=True)
    
    # Handle case where we only have one row
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    
    # Get unique DLC cases for color coding
    unique_dlcs = df['DLC_Case'].dropna().unique()
    colors = plt.cm.Set1(np.linspace(0, 1, len(unique_dlcs)))
    color_map = dict(zip(unique_dlcs, colors))
    
    print(f"Found DLC cases: {unique_dlcs}")
    
    # Create each subplot
    for i, y_param in enumerate(y_params):
        row = i // 2
        col = i % 2
        ax = axes[row, col]
        
        # print(f"  Y-axis {i+1} ({y_param}): {df[y_param].min():.4f} to {df[y_param].max():.4f}")
        
        # Plot each DLC case with different color
        for j, dlc in enumerate(unique_dlcs):
            mask = df['DLC_Case'] == dlc
            subset = df[mask]
            
            # Use absolute values directly - no normalization, no alpha
            x_vals = subset[x_param].values
            y_vals = subset[y_param].values
            
            ax.scatter(x_vals, y_vals, 
                      color=colors[j], label=dlc, s=50)
        
        # Set labels and title
        ax.set_ylabel(f'{y_param[0]} ({y_param[1]})')
        ax.set_title(f'{y_param[0]} ({y_param[1]}) vs {x_param[0]} ({x_param[1]})')
        ax.grid(True, alpha=0.3)
        
        # Add legend only to subplot (0,0) - top left
        if row == 0 and col == 0:
            ax.legend(title='DLC Cases')
        
        # Let matplotlib handle the scaling automatically
        ax.autoscale()
    
    # Hide any unused subplots
    if n_plots % 2 == 1:  # If odd number of plots
        axes[-1, -1].set_visible(False)
    
    # Set x-label only on bottom row
    for col in range(2):
        if n_rows > 0:
            axes[-1, col].set_xlabel(f'{x_param[0]} ({x_param[1]})')
    
    plt.tight_layout()