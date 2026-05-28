"""
Main layout definition for the MOO Dashboard
"""
import dash_bootstrap_components as dbc
from dash import dcc, html
from layouts.components import create_file_input_row, create_data_stores


def create_main_layout() -> html.Div:
    """
    Create the main layout for the MOO Dashboard.
    
    Returns:
        Dash HTML Div containing the complete layout
    """
    # File input components
    csv_file_input = create_file_input_row(
        'CSV File', 'csv', 
        'Load the CSV file from the given path and enter this button'
    )
    
    yaml_file_input = create_file_input_row(
        'YAML File', 'yaml',
        'Load the YAML file from the given path and enter this button'
    )
    
    # Configuration panel
    cfg_graph_input = html.Div([
            html.Div(
                id='channels', 
                children=[
                    dbc.Alert("Load YAML file to see variable options", className="text-center")
                ],
                style={
                    'maxHeight': 'calc(100% - 160px)',
                    'overflowY': 'auto',
                    'padding': '10px',
                    'marginBottom': '15px',
                    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
                }
            ),
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "Clear Highlighting", 
                        id='clear-highlight-btn', 
                        color='secondary', 
                        outline=True, 
                        size='sm',
                        className='mb-2 me-2'
                    ),
                    dbc.Button(
                        "Show Pareto Front", 
                        id='pareto-toggle-btn', 
                        color='success', 
                        outline=True, 
                        size='sm',
                        className='mb-2 me-2'
                    ),
                    dbc.Button(
                        "Hide Diagonal", 
                        id='diagonal-toggle-btn', 
                        color='info', 
                        outline=True, 
                        size='sm',
                        className='mb-2 me-2'
                    ),
                    dbc.Button(
                        "Download Dashboard", 
                        id='download-html-btn', 
                        color='primary', 
                        outline=True, 
                        size='sm',
                        className='mb-2'
                    ),
                    dcc.Download(id='download-splom-html')
                ])
            ])
        ], style={'width': '100%'})
    
    # Simple layout with full width
    layout = html.Div([
        # Gradient header
        html.Div([
            html.H1("WEIS Multi-Objective Optimization Dashboard", style={'margin': '0', 'fontSize': '28px'}),
            html.Div(id='objective-goals-display', style={'fontSize': '14px', 'opacity': '0.9', 'marginTop': '5px'})
        ], style={
            'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'color': 'white',
            'padding': '20px',
            'borderRadius': '10px',
            'marginBottom': '20px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
        }),
        
        # File Loaders in cards
        html.Div([
            html.Div([
                html.H2("Load Data Files", style={'margin': '0 0 15px 0', 'fontSize': '20px', 'color': '#495057'}),
                csv_file_input,
                yaml_file_input
            ], style={
                'background': 'white',
                'padding': '15px',
                'borderRadius': '10px',
                'marginBottom': '15px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
            })
        ]),
        
        # Main content - 2x2 grid layout with card styling
        html.Div([
            # Left column with two stacked components
            html.Div([
                # Top left: cfg_graph_input in a card
                html.Div([
                    html.H2("Controls & Variables", style={
                        'margin': '0 0 15px 0',
                        'fontSize': '20px',
                        'color': '#495057',
                        'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
                    }),
                    cfg_graph_input
                ], style={
                    'height': '50%',
                    'background': 'white',
                    'padding': '20px',
                    'borderRadius': '10px',
                    'marginBottom': '20px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'overflowY': 'auto',
                    'boxSizing': 'border-box'
                }),
                # Bottom left: data-table in a card
                html.Div([
                    html.H2("Data Table", style={
                        'margin': '0 0 15px 0',
                        'fontSize': '20px',
                        'color': '#495057',
                        'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
                    }),
                    dcc.Graph(
                        id='data-table', 
                        style={'height': 'calc(100% - 50px)'},
                        config={'responsive': True}
                    )
                ], style={
                    'height': 'calc(50% - 20px)',
                    'background': 'white',
                    'padding': '20px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'boxSizing': 'border-box'
                })
            ], style={
                'width': '50%',
                'height': 'calc(100vh - 300px)',
                'overflowY': 'auto',
                'display': 'inline-block',
                'verticalAlign': 'top',
                'paddingRight': '20px',
                'boxSizing': 'border-box'
            }),
            # Right column: splom graph in a card
            html.Div([
                html.H2("Scatter Plot Matrix (SPLOM)", style={
                    'margin': '0 0 15px 0',
                    'fontSize': '20px',
                    'color': '#495057',
                    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
                }),
                dcc.Graph(
                    id='splom', 
                    style={'height': 'calc(100% - 50px)', 'width': '100%'},
                    config={'responsive': True}
                )
            ], style={
                'width': '50%',
                'height': 'calc(100vh - 300px)',
                'background': 'white',
                'padding': '20px',
                'borderRadius': '10px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'display': 'inline-block',
                'verticalAlign': 'top',
                'maxWidth': '67%',
                'boxSizing': 'border-box'
            })
        ], style={
            'width': '100%',
            'whiteSpace': 'nowrap'
        }),
        
        # Data stores
        *create_data_stores()
    ], style={
        'width': '100%',
        'maxWidth': '1800px',
        'margin': '0 auto',
        'padding': '20px',
        'boxSizing': 'border-box',
        'backgroundColor': '#f8f9fa',
        'minHeight': '100vh'
    })
    
    return layout
