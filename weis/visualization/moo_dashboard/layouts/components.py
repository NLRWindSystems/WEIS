"""
Reusable UI components for the MOO Dashboard
"""
import dash_bootstrap_components as dbc
from dash import dcc, html
from config.settings import COLOR_SCALES


def create_file_input_row(file_type: str, file_id_prefix: str, tooltip_text: str) -> dbc.Row:
    """
    Create a reusable file input row for CSV or YAML files.
    
    Args:
        file_type: Display name for the file type (e.g., 'CSV File', 'YAML File')
        file_id_prefix: Prefix for component IDs (e.g., 'csv', 'yaml')
        tooltip_text: Tooltip text for the load button
        
    Returns:
        Dash Bootstrap Components Row
    """
    return dbc.Row([
        dbc.Col(
            dbc.Label(file_type, className="mb-0"), 
            width=1, 
            className="d-flex align-items-center"  # Vertically center label
        ),
        dbc.Col(
            dbc.Input(
                id=f'{file_id_prefix}-file-path',
                type='text',
                placeholder='Enter the absolute path for file to import'
            ),
            width=True  # Takes remaining space
        ),
        dbc.Col(
            dcc.Upload(
                id=f'{file_id_prefix}-upload-data',
                children=dbc.Button('Browse', n_clicks=0, color='secondary', className='me-1'),
                multiple=False
            ),
            width="auto"  # Only as wide as needed
        ),
        dbc.Col(
            dbc.Button('Load', id=f'{file_id_prefix}-load-btn', n_clicks=0, color='primary'),
            width="auto"  # Only as wide as needed
        ),
        dbc.Tooltip(tooltip_text, target=f'{file_id_prefix}-load-btn'),
    ], className="mb-3 g-2")  # g-2 adds small gutters between columns


def create_button_group(variables: list, category_name: str, color: str, selected_vars: list, array_columns: set = None) -> list:
    """
    Create a button group for variable selection with professional styling.
    
    Args:
        variables: List of variable names
        category_name: Display name for the category
        color: Bootstrap color for the buttons
        selected_vars: List of currently selected variables
        array_columns: Set of column names that contain arrays
        
    Returns:
        List of HTML components
    """
    if not variables:
        return []
    
    array_columns = array_columns or set()
    all_components = []
    
    for var in variables:
        is_array = var in array_columns
        
        # Check if any form of this variable is selected
        is_selected = (var in selected_vars or 
                      f"{var}_min" in selected_vars or 
                      f"{var}_max" in selected_vars)
        
        # Shorten variable name for display
        display_name = var.split('.')[-1]
        
        # For regular variables, create normal button
        if not is_array:
            button = dbc.Button(
                display_name,
                id={'type': 'channel-btn', 'index': var},
                color=color,
                outline=not is_selected,
                size='sm',
                className='flex-shrink-0 shadow-sm',
                style={
                    'marginRight': '0.5rem', 
                    'marginBottom': '0.5rem',
                    'borderRadius': '20px',
                    'fontWeight': '500',
                    'fontSize': '0.85em',
                    'padding': '0.375rem 0.75rem',
                    'transition': 'all 0.2s ease-in-out'
                },
                n_clicks=0,
            )
            all_components.append(button)
        else:
            # For array variables, create button that automatically uses separate mode
            button = dbc.Button([
                html.Span(display_name, style={'marginRight': '4px'}),
                html.Span("min/max", className="badge bg-light text-dark", style={'fontSize': '0.7em'})
            ],
                id={'type': 'array-channel-btn', 'index': var},
                color=color,
                outline=not is_selected,
                size='sm',
                className='flex-shrink-0 shadow-sm',
                style={
                    'marginRight': '0.5rem', 
                    'marginBottom': '0.5rem',
                    'borderRadius': '20px',
                    'fontWeight': '500',
                    'fontSize': '0.85em',
                    'padding': '0.375rem 0.75rem',
                    'transition': 'all 0.2s ease-in-out'
                },
                n_clicks=0,
            )
            
            all_components.append(button)
    
    if not category_name:
        # Return just the buttons without header (used for objectives section)
        return [html.Div(
            all_components,
            className="d-flex flex-wrap gap-2"
        )]
    
    return [
        html.Div([
            html.H6(category_name, className="fw-bold mb-3", style={
                'borderBottom': f'2px solid {_get_category_color(color)}',
                'paddingBottom': '8px',
                'color': _get_category_color(color)
            }),
            html.Div(
                all_components,
                className="d-flex flex-wrap gap-2"
            )
        ], className="mb-4", style={
            'backgroundColor': 'white',
            'padding': '15px',
            'borderRadius': '8px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
        })
    ]


def _get_category_color(color: str) -> str:
    """Get hex color for category styling."""
    color_map = {
        'primary': '#0d6efd',
        'warning': '#fd7e14',
        'success': '#198754',
        'secondary': '#6c757d'
    }
    return color_map.get(color, '#6c757d')


def create_data_stores() -> list:
    """
    Create dcc.Store components for data persistence.
    
    Returns:
        List of dcc.Store components
    """
    return [
        dcc.Store(id='csv-df'),
        dcc.Store(id='yaml-df'),
        dcc.Store(id='selected-channels', data=[]),
        dcc.Store(id='selected-iteration', data=""),  # Store for selected iteration (highlight)
        dcc.Store(id='pareto-front-enabled', data=False),  # Store for Pareto front toggle
        dcc.Store(id='objective-senses', data={}),  # Store for objective optimization directions
        dcc.Store(id='diagonal-visible', data=True),  # Store for diagonal visibility
        dcc.Store(id='simplified-df'),  # Store for simplified dataframe from prepare_dataframe_for_splom
        dcc.Store(id='dimensions-data'),  # Store for dimensions from prepare_dataframe_for_splom
        dcc.Store(id='variable-categories-data')  # Store for variable categories from prepare_dataframe_for_splom
    ]


def create_no_data_alert(message: str, color: str = "info") -> dbc.Alert:
    """
    Create a standardized alert for no data scenarios.
    
    Args:
        message: Alert message
        color: Bootstrap color for the alert
        
    Returns:
        Dash Bootstrap Alert component
    """
    return dbc.Alert(message, color=color, className="text-center")
