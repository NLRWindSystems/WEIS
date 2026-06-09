"""
MHK DLC Generator for Tidal Energy Converters (TECs)
per IEC TS 62600-2:2019, Table 8

Subclass of DLCGenerator that overrides generate_* methods for MHK-specific
current models (NTM, ETM, OCM, ECM), flood/ebb/orientation-error directional
cases, and TEC wave conditions.
"""
import numpy as np
import logging

from weis.dlc_driver.dlc_generator import DLCGenerator

logger = logging.getLogger("wisdem/weis")


class MHKDLCGenerator(DLCGenerator):
    """DLC generator for MHK tidal-energy converters per IEC TS 62600-2."""

    def __init__(
            self,
            ws_cut_in=0.5,
            ws_cut_out=4.0,
            ws_rated=2.0,
            **kwargs
    ):
        # Set flow_key before calling super().__init__() so metocean validation uses 'current_speed'
        self.flow_key = 'current_speed'

        super().__init__(
            ws_cut_in=ws_cut_in,
            ws_cut_out=ws_cut_out,
            ws_rated=ws_rated,
            **kwargs
        )
        self.MHK = True

        # Add current_speed to openfast_input_map (if not already present from global)
        if 'current_speed' not in self.openfast_input_map:
            self.openfast_input_map['current_speed'] = [
                ("SeaState", "CurrDIV"),
                ("InflowWind", "HWindSpeed"),
            ]

        # Load MHK-specific metocean fields
        metocean = self.metocean
        self.wave_height5 = np.array([metocean.get('wave_height5', 0.)])
        self.wave_period5 = np.array([metocean.get('wave_period5', 0.)])
        self.wave_height_cutout = metocean.get('wave_height_cutout', 0.)
        self.current_peak_spring = metocean.get('current_peak_spring', 0.)
        self.current_mean_spring = metocean.get('current_mean_spring', 0.)

    # ──────────────────────────────────────────────────────────────────────
    # DLC 1.1 — Normal operation, NTM current, OSS waves
    # IEC TS 62600-2, Table 8: NTM Uin≤U≤Uout, flood/ebb/OE, OSS H=Hm0
    # γf = 1.35 (ULS), 1.00 (FLS, SLS)
    # ──────────────────────────────────────────────────────────────────────
    def generate_1p1(self, dlc_options):
        dlc_options.update(self.default_options)

        dlc_options['label'] = '1.1'
        dlc_options['sea_state'] = 'normal'
        dlc_options['PSF'] = 1.35
        dlc_options['wave_model'] = dlc_options.get('wave_model', 2)

        # User specifies yaw_misalign in YAML for flood/ebb/OE cases
        if 'yaw_misalign' not in dlc_options:
            dlc_options['yaw_misalign'] = [0]

        generic_case_inputs = []
        generic_case_inputs.append([])  # group 0
        generic_case_inputs.append([self.flow_key, 'wave_height', 'wave_period', 'wind_seed', 'wave_seed'])  # group 1
        generic_case_inputs.append(['yaw_misalign'])  # group 2

        self.generate_cases(generic_case_inputs, dlc_options)

    # ──────────────────────────────────────────────────────────────────────
    # DLC 1.2 — Normal operation, NTM current, wave direction sweep
    # IEC TS 62600-2, Table 8: NTM Uin≤U≤Uout, flood/ebb/OE,
    #   OSS H=Hm0,out, wave dir 0°–360° in 30° steps
    # γf = 1.35 (ULS), 1.00 (SLS)
    # ──────────────────────────────────────────────────────────────────────
    def generate_1p2(self, dlc_options):
        dlc_options.update(self.default_options)

        dlc_options['label'] = '1.2'
        dlc_options['sea_state'] = 'normal'
        dlc_options['PSF'] = 1.35
        dlc_options['wave_model'] = dlc_options.get('wave_model', 2)

        # Use cutout wave height Hm0,out for all current speeds
        met_options = self.gen_met_options(dlc_options, sea_state=dlc_options['sea_state'])
        if self.wave_height_cutout > 0:
            dlc_options['wave_height'] = self.wave_height_cutout * np.ones_like(met_options[self.flow_key])
        else:
            # Fallback: use max operational wave height
            max_wave_height = np.max(met_options['wave_height'])
            dlc_options['wave_height'] = max_wave_height * np.ones_like(met_options[self.flow_key])

        # Wave direction sweep 0°–360° in 30° steps
        default_wave_headings = np.arange(0, 360, 30)
        if len(dlc_options.get('wave_heading', [])) == 0:
            dlc_options['wave_heading'] = default_wave_headings

        # User specifies yaw_misalign in YAML for flood/ebb/OE cases
        if 'yaw_misalign' not in dlc_options:
            dlc_options['yaw_misalign'] = [0]

        generic_case_inputs = []
        generic_case_inputs.append([])  # group 0
        generic_case_inputs.append([self.flow_key, 'wave_height', 'wave_period', 'wind_seed', 'wave_seed'])  # group 1
        generic_case_inputs.append(['wave_heading'])  # group 2
        generic_case_inputs.append(['yaw_misalign'])  # group 3

        self.generate_cases(generic_case_inputs, dlc_options)

    # ──────────────────────────────────────────────────────────────────────
    # DLC 1.3 — Normal operation, ETM current, OSS waves
    # IEC TS 62600-2, Table 8: ETM Uin≤U≤Uout, flood/ebb/OE, OSS H=Hm0
    # γf = 1.35 (ULS), 1.00 (SLS)
    # ──────────────────────────────────────────────────────────────────────
    def generate_1p3(self, dlc_options):
        dlc_options.update(self.default_options)

        dlc_options['label'] = '1.3'
        dlc_options['sea_state'] = 'normal'
        dlc_options['PSF'] = 1.35
        dlc_options['IEC_WindType'] = '1ETM'  # Extreme turbulence model
        dlc_options['wave_model'] = dlc_options.get('wave_model', 2)

        # User specifies yaw_misalign in YAML for flood/ebb/OE cases
        if 'yaw_misalign' not in dlc_options:
            dlc_options['yaw_misalign'] = [0]

        generic_case_inputs = []
        generic_case_inputs.append([])  # group 0
        generic_case_inputs.append([self.flow_key, 'wave_height', 'wave_period', 'wind_seed', 'wave_seed'])  # group 1
        generic_case_inputs.append(['yaw_misalign'])  # group 2

        self.generate_cases(generic_case_inputs, dlc_options)

    # ──────────────────────────────────────────────────────────────────────
    # Wind-only DLCs — blocked for MHK TECs
    # ──────────────────────────────────────────────────────────────────────
    def generate_1p4(self, dlc_options):
        raise NotImplementedError("DLC 1.4 (ECD) is wind-only and does not apply to MHK TECs per IEC TS 62600-2.")

    def generate_1p5(self, dlc_options):
        raise NotImplementedError("DLC 1.5 (EWS) is wind-only and does not apply to MHK TECs per IEC TS 62600-2.")

    def generate_1p6(self, dlc_options):
        raise NotImplementedError("DLC 1.6 (SSS+NTM) is wind-dominated and does not apply to MHK TECs per IEC TS 62600-2.")

    def generate_2p4(self, dlc_options):
        raise NotImplementedError("DLC 2.4 (EOG + grid loss) is wind-only and does not apply to MHK TECs per IEC TS 62600-2.")

    def generate_3p3(self, dlc_options):
        raise NotImplementedError("DLC 3.3 (EDC + startup) is wind-only and does not apply to MHK TECs per IEC TS 62600-2.")

    def generate_6p3(self, dlc_options):
        raise NotImplementedError("DLC 6.3 (parked in normal wind) is wind-only and does not apply to MHK TECs per IEC TS 62600-2.")

    def generate_6p4(self, dlc_options):
        raise NotImplementedError("DLC 6.4 (50-yr wind + reduced waves) is wind-dominated and does not apply to MHK TECs per IEC TS 62600-2.")

    def generate_6p5(self, dlc_options):
        raise NotImplementedError("DLC 6.5 (EWM + loss of grid) is wind-dominated and does not apply to MHK TECs per IEC TS 62600-2.")

    def generate_9p1(self, dlc_options):
        raise NotImplementedError("DLC 9.1 is wind-only (standstill) and does not apply to MHK TECs per IEC TS 62600-2.")

    def generate_9p2(self, dlc_options):
        raise NotImplementedError("DLC 9.2 is wind-only (standstill) and does not apply to MHK TECs per IEC TS 62600-2.")

    def generate_10p1(self, dlc_options):
        raise NotImplementedError("DLC 10.1 is wind-only (blade inspection) and does not apply to MHK TECs per IEC TS 62600-2.")

    def generate_10p2(self, dlc_options):
        raise NotImplementedError("DLC 10.2 is wind-only (blade inspection) and does not apply to MHK TECs per IEC TS 62600-2.")

    def generate_12p1(self, dlc_options):
        raise NotImplementedError("DLC 12.1 (power production + 50-yr wind + grid loss) is wind-only and does not apply to MHK TECs per IEC TS 62600-2.")
