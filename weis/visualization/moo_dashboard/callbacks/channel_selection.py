"""
Channel selection callbacks for button interactions
"""
import ast
import io
import logging
import pandas as pd
import numpy as np
from dash import Input, Output, State, callback, callback_context, ALL, html, dcc

from layouts.components import create_button_group, create_no_data_alert
from config.settings import COLOR_SCALES

logger = logging.getLogger(__name__)


def detect_array_columns(csv_data):
    """
    Detect which columns contain array values.
    
    Args:
        csv_data: JSON string of CSV data
        
    Returns:
        Set of column names that contain arrays
    """
    if csv_data is None:
        return set()
    
    try:
        df = pd.read_json(io.StringIO(csv_data), orient='split')
        array_columns = set()
        
        for col in df.columns:
            # Check if any value in the column is array-like
            sample_values = df[col].dropna().head(3)  # Check first 3 non-null values
            for val in sample_values:
                is_array = False
                
                # Check if it's a string that could represent an array
                if isinstance(val, str):
                    try:
                        # Try to parse as a Python literal
                        parsed = ast.literal_eval(val)
                        if isinstance(parsed, (list, tuple)) and len(parsed) > 1:
                            is_array = True
                    except (ValueError, SyntaxError):
                        # Check for numpy array string format like '[0. 0. 0. 0. 0. 0. 0.]'
                        val_clean = val.strip()
                        if val_clean.startswith('[') and val_clean.endswith(']'):
                            inner_str = val_clean[1:-1].strip()
                            if inner_str and len(inner_str.split()) > 1:
                                # Multiple space-separated values indicate an array
                                is_array = True
                
                # Check if it's already a list/array
                elif isinstance(val, (list, tuple, np.ndarray)) and len(val) > 1:
                    is_array = True
                
                if is_array:
                    array_columns.add(col)
                    logger.debug(f"Detected array column '{col}' with sample value: {val}")
                    break  # Found array in this column, move to next

        logger.debug(f"Final detected array columns: {array_columns}")
        return array_columns
    except Exception as e:
        logger.error(f"Error detecting array columns: {e}")
        return set()


def register_channel_selection_callbacks(app):
    """Register all channel selection related callbacks."""
    
    @callback(Output('channels', 'children'),
              [Input('yaml-df', 'data'),
               Input('csv-df', 'data'),
               Input('selected-channels', 'data')])
    def update_channel_buttons(yaml_data, csv_data, selected_channels):
        """Create dynamic button groups for channel selection."""
        if yaml_data is None:
            no_data_msg = create_no_data_alert("Load YAML file to see variable options", "info")
            return [no_data_msg]
        
        selected_channels = selected_channels or []
        
        # Detect array columns from CSV data
        array_columns = detect_array_columns(csv_data)

        # Extract all variables
        objectives = list(yaml_data['objectives'].keys())
        constraints = list(yaml_data['constraints'].keys())
        design_vars = list(yaml_data['design_vars'].keys())

        all_variables = objectives + constraints + design_vars
        
        if not all_variables:
            no_vars_msg = create_no_data_alert("No variables found in YAML file", "warning")
            return [no_vars_msg]
        
        # Create button groups for each category
        buttons = []
        if objectives:
            # Add professional objective section with sense controls
            buttons.append(html.Div([
                html.Div([
                    html.H6("Objectives", className="fw-bold text-primary mb-3", style={'borderBottom': '2px solid #0d6efd', 'paddingBottom': '8px'}),
                    
                    # Optimization direction controls in a styled card
                    html.Div([
                        html.Div([
                            html.I(className="bi bi-sliders me-2"),  # Bootstrap icon
                            html.Span("Optimization Direction", className="fw-semibold text-secondary", style={'fontSize': '0.9em'})
                        ], className="mb-2"),
                        
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Label(
                                        obj.split('.')[-1], 
                                        className="form-label mb-1 text-dark",
                                        style={'fontSize': '0.85em', 'fontWeight': '500'}
                                    ),
                                    dcc.RadioItems(
                                        id={'type': 'obj-sense', 'index': obj},
                                        options=[
                                            {'label': ' Minimize', 'value': 'minimize'},
                                            {'label': ' Maximize', 'value': 'maximize'}
                                        ],
                                        value='minimize',
                                        inline=True,
                                        className="custom-radio-group",
                                        style={'fontSize': '0.85em'},
                                        labelStyle={
                                            'marginRight': '15px',
                                            'display': 'inline-block',
                                            'cursor': 'pointer'
                                        },
                                        inputStyle={'marginRight': '4px'}
                                    )
                                ], className="mb-2 pb-2", style={'borderBottom': '1px solid #e9ecef'} if i < len(objectives) - 1 else {})
                                for i, obj in enumerate(objectives)
                            ], className="d-flex flex-column")
                        ], style={
                            'backgroundColor': '#f8f9fa',
                            'padding': '12px 15px',
                            'borderRadius': '6px',
                            'border': '1px solid #dee2e6'
                        })
                    ], className="mb-3"),
                    
                    # Objective buttons
                    html.Div([
                        html.Small("Select Variables:", className="text-muted mb-2 d-block", style={'fontSize': '0.85em'})
                    ] + create_button_group(
                        objectives, "", COLOR_SCALES['objectives'], selected_channels, array_columns
                    )[0].children if create_button_group(objectives, "", COLOR_SCALES['objectives'], selected_channels, array_columns) else [])
                ])
            ], className="mb-4", style={
                'backgroundColor': 'white',
                'padding': '15px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
            }))
        if constraints:
            buttons.extend(create_button_group(
                constraints, "Constraints", COLOR_SCALES['constraints'], selected_channels, array_columns
            ))
        if design_vars:
            buttons.extend(create_button_group(
                design_vars, "Design Variables", COLOR_SCALES['design_vars'], selected_channels, array_columns
            ))

        return buttons

    @callback(Output('selected-channels', 'data'),
              [Input({'type': 'channel-btn', 'index': ALL}, 'n_clicks'),
               Input({'type': 'array-channel-btn', 'index': ALL}, 'n_clicks')],
              State('selected-channels', 'data'),
              prevent_initial_call=True)
    def handle_channels_selection(channel_clicks, array_channel_clicks, current_selected):
        """Handle channel button clicks for multi-select functionality."""
        ctx = callback_context
        if not ctx.triggered:
            return current_selected or []
        
        current_selected = current_selected or []

        # Check if any button was actually clicked (n_clicks > 0)
        total_channel_clicks = sum(click or 0 for click in channel_clicks)
        total_array_clicks = sum(click or 0 for click in array_channel_clicks)
        
        if total_channel_clicks == 0 and total_array_clicks == 0:
            return current_selected or []
        
        try:
            trigger_info = ctx.triggered_id
            
            if trigger_info['type'] == 'channel-btn':
                # Handle regular channel button clicks
                clicked_var = trigger_info['index']
                logger.debug(f"Regular channel clicked: {clicked_var}")
                
                # Toggle selection: add if not present, remove if present
                if clicked_var in current_selected:
                    current_selected.remove(clicked_var)
                    logger.debug(f"Removed {clicked_var}")
                else:
                    current_selected.append(clicked_var)
                    logger.debug(f"Added {clicked_var}")
                    
            elif trigger_info['type'] == 'array-channel-btn':
                # Handle array channel button clicks (automatically use separate mode)
                var_name = trigger_info['index']
                logger.debug(f"Array channel clicked: {var_name}")
                
                # Check if this array variable is already selected
                min_var = f"{var_name}_min"
                max_var = f"{var_name}_max"
                is_selected = min_var in current_selected and max_var in current_selected
                
                if is_selected:
                    # Remove both min and max
                    current_selected = [sel for sel in current_selected 
                                      if sel not in [min_var, max_var]]
                    logger.debug(f"Removed array: {min_var}, {max_var}")
                else:
                    # Remove any existing entries for this variable first
                    current_selected = [sel for sel in current_selected 
                                      if not (sel.startswith(f"{var_name}_") or sel == var_name)]
                    # Add min and max
                    current_selected.extend([min_var, max_var])
                    logger.debug(f"Added array: {min_var}, {max_var}")
            
            logger.debug(f"Current selected after: {current_selected}")
            return current_selected
            
        except Exception as e:
            logger.error(f"Error parsing button ID: {e}")
            logger.error(f"Trigger info: {trigger_info}")
            return current_selected


    @callback(Output('objective-senses', 'data'),
              Input({'type': 'obj-sense', 'index': ALL}, 'value'),
              State('yaml-df', 'data'),
              prevent_initial_call=True)
    def update_objective_senses(sense_values, yaml_data):
        """Store the user-selected optimization direction for each objective."""
        if not yaml_data or not sense_values:
            return {}
        
        objectives = list(yaml_data['objectives'].keys())
        
        # Create dictionary mapping objective names to their sense
        objective_senses = {}
        for i, obj in enumerate(objectives):
            if i < len(sense_values):
                objective_senses[obj] = sense_values[i]
        
        logger.debug(f"Updated objective senses: {objective_senses}")
        
        return objective_senses