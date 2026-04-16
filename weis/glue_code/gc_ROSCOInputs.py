import numpy as np

def assign_ROSCO_values(wt_opt, wt_init, modeling_options, opt_options):

    rosco_init_options = modeling_options["ROSCO"]

    # Control inputs from windio schema (not used in WISDEM)
    wt_opt["tune_rosco_ivc.max_pitch_rate"] = np.radians(wt_init["control"]["max_pitch_rate"])  # windio schema is in deg/s, ROSCO uses rad/s

    if "max_torque_rate" in wt_init["control"]:
        wt_opt["tune_rosco_ivc.max_torque_rate"] = wt_init["control"]["max_torque_rate"]
    
    # Generic input variables
    rosco_tuning_dvs = opt_options['design_variables']['control']['rosco_tuning']
    for dv in rosco_tuning_dvs:
        wt_opt[f"tune_rosco_ivc.{dv['name']}"] = dv['start']
        
    # DISCON inputs (ROSCO)
    discon_dvs = opt_options['design_variables']['control']['discon']
    for dv in discon_dvs:
        wt_opt[f"tune_rosco_ivc.discon:{dv['name']}"] = dv['start']

    # TODO: see if this is still needed
    # other optional parameters
    optional_params = [
         'max_pitch',
         'min_pitch',
         'vs_minspd',
         'ss_vsgain',
         'ss_pcgain',
         'ps_percent',
    ]
    for param in optional_params:
        if param in rosco_init_options:
            wt_opt[f'tune_rosco_ivc.{param}'] = rosco_init_options[param]
    
    # Check for proper Flp_Mode, print warning
    #if modeling_options["WISDEM"]["RotorSE"]["n_tab"] > 1 and rosco_init_options["Flp_Mode"] == 0:
    #        raise Exception("A distributed aerodynamic control device is specified in the geometry yaml, but Flp_Mode is zero in the modeling options.")
    if rosco_init_options["Flp_Mode"] > 0:
        raise Exception("Flp_Mode is non zero in the modeling options, but no distributed aerodynamic control device is allowed in the geometry yaml. anymore")

    return wt_opt
