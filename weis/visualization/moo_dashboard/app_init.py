"""
App initialization for the MOO Dashboard
"""
import dash_bootstrap_components as dbc
from dash import Dash

# Import callback registration functions
from callbacks.data_loading import register_data_loading_callbacks
from callbacks.channel_selection import register_channel_selection_callbacks
from callbacks.visualization import register_visualization_callbacks, register_table_callbacks

# Import layout
from layouts.layout import create_main_layout

# Import configuration
from config.settings import DEBUG, HOST, PORT


def create_app():
    """
    Create and configure the Dash application.
    
    Returns:
        Configured Dash app instance
    """
    # Initialize app with Bootstrap theme
    external_stylesheets = [dbc.themes.BOOTSTRAP]
    app = Dash(__name__, external_stylesheets=external_stylesheets)
    
    # Set layout
    app.layout = create_main_layout()
    
    # Register callbacks
    register_data_loading_callbacks(app)
    register_channel_selection_callbacks(app)
    register_visualization_callbacks(app)
    register_table_callbacks(app)
    
    return app


def run_app(app=None):
    """
    Run the Dash application.
    
    Args:
        app: Dash app instance (if None, creates new app)
    """
    if app is None:
        app = create_app()
    
    app.run(debug=DEBUG, host=HOST, port=PORT)
