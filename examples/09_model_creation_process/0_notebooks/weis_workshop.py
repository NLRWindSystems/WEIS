# Simple Colab detection
import sys
import numpy as np
import matplotlib.pyplot as plt
import openmdao.api as om


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