"""
Data loading callbacks for CSV and YAML files
"""
from dash import Input, Output, State, callback, callback_context
import io
import logging
import pandas as pd

from utils.data_processing import (
    parse_uploaded_contents, 
    load_csv_from_path, 
    load_yaml_from_path, 
    process_yaml_config
)

logger = logging.getLogger(__name__)


def register_data_loading_callbacks(app):
    """Register all data loading related callbacks."""
    
    @callback(Output('csv-file-path', 'value'),
              Input('csv-upload-data', 'filename'),
              prevent_initial_call=True)
    def update_csv_file_path(filename):
        """Update CSV file path when file is browsed."""
        if filename:
            return filename
        return ""

    @callback(Output('yaml-file-path', 'value'),
              Input('yaml-upload-data', 'filename'),
              prevent_initial_call=True)
    def update_yaml_file_path(filename):
        """Update YAML file path when file is browsed."""
        if filename:
            return filename
        return ""

    @callback(Output('csv-df', 'data'),
              [Input('csv-upload-data', 'contents'),
               Input('csv-load-btn', 'n_clicks')],
              [State('csv-upload-data', 'filename'),
               State('csv-upload-data', 'last_modified'),
               State('csv-file-path', 'value')],
              prevent_initial_call=True)
    def load_csv_data(contents, load_clicks, filename, date, file_path):
        """Load CSV data from upload or file path."""
        ctx = callback_context
        if not ctx.triggered:
            return None
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'csv-upload-data' and contents is not None:
            # File was uploaded via browse button
            return parse_uploaded_contents(contents, filename)
        elif trigger_id == 'csv-load-btn' and load_clicks and file_path:
            # File path was entered and load button clicked
            result = load_csv_from_path(file_path)
            if result:
                # Print preview for debugging
                df = pd.read_json(io.StringIO(result), orient='split')
                logger.debug(f"CSV loaded with shape: {df.shape}")
                logger.debug(f"CSV preview:\n{df.head()}")
            return result
        
        return None

    @callback(Output('yaml-df', 'data'),
              [Input('yaml-upload-data', 'contents'),
               Input('yaml-load-btn', 'n_clicks')],
              [State('yaml-upload-data', 'filename'),
               State('yaml-upload-data', 'last_modified'),
               State('yaml-file-path', 'value')],
              prevent_initial_call=True)
    def load_yaml_data(contents, load_clicks, filename, date, file_path):
        """Load YAML data from upload or file path."""
        ctx = callback_context
        if not ctx.triggered:
            return None
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        config = None
        if trigger_id == 'yaml-upload-data' and contents is not None:
            # File was uploaded via browse button
            config = parse_uploaded_contents(contents, filename)
        elif trigger_id == 'yaml-load-btn' and load_clicks and file_path:
            # File path was entered and load button clicked
            config = load_yaml_from_path(file_path)
        
        if config:
            result = process_yaml_config(config)
            logger.info(f"Objectives: {result['objectives']}")
            logger.info(f"Constraints: {result['constraints']}")
            logger.info(f"Design Variables: {result['design_vars']}")
            return result
        
        return None
