"""
Visualization callbacks for plot generation
"""
import io
import logging
import pandas as pd
from dash import Input, Output, State, callback, callback_context

from utils.data_processing import prepare_dataframe_for_splom, find_pareto_front
from utils.plot_helpers import (
    create_splom_figure, create_empty_figure_with_message, 
    create_table_figure
)

from config.settings import *

logger = logging.getLogger(__name__)


def register_visualization_callbacks(app):
    """Register all visualization related callbacks."""
    
    @callback(Output('pareto-front-enabled', 'data'),
              Input('pareto-toggle-btn', 'n_clicks'),
              State('pareto-front-enabled', 'data'),
              prevent_initial_call=True)
    def toggle_pareto_front(n_clicks, current_state):
        """Toggle Pareto front visualization on/off."""
        if n_clicks is None:
            return current_state
        return not current_state
    
    @callback(Output('pareto-toggle-btn', 'children'),
              Input('pareto-front-enabled', 'data'))
    def update_pareto_button_text(pareto_enabled):
        """Update button text based on Pareto front state."""
        if pareto_enabled:
            return "Hide Pareto Front"
        else:
            return "Show Pareto Front"
    
    @callback(Output('diagonal-visible', 'data'),
              Input('diagonal-toggle-btn', 'n_clicks'),
              State('diagonal-visible', 'data'),
              prevent_initial_call=True)
    def toggle_diagonal(n_clicks, current_state):
        """Toggle diagonal visibility."""
        if n_clicks is None:
            return current_state
        return not current_state
    
    @callback(Output('diagonal-toggle-btn', 'children'),
              Input('diagonal-visible', 'data'))
    def update_diagonal_button_text(diagonal_visible):
        """Update button text based on diagonal visibility state."""
        if diagonal_visible:
            return "Hide Diagonal"
        else:
            return "Show Diagonal"
    
    @callback([Output('splom', 'figure'),
               Output('selected-iteration', 'data'),
               Output('simplified-df', 'data'),
               Output('dimensions-data', 'data'),
               Output('variable-categories-data', 'data')],
              [Input('csv-df', 'data'),
               Input('selected-channels', 'data'),
               Input('clear-highlight-btn', 'n_clicks'),
               Input('splom', 'clickData'),
               Input('pareto-front-enabled', 'data'),
               Input('objective-senses', 'data'),
               Input('diagonal-visible', 'data')],
              State('yaml-df', 'data'))
    def update_splom(csv_data, selected_channels, clear_clicks, click_data, pareto_enabled, objective_senses, diagonal_visible, yaml_data):
        """Update the scatter plot matrix based on selected channels and highlighted sample."""

        if csv_data is None:
            return create_empty_figure_with_message(
                'Load data to view plots', 'gray'
            ), None, None, None, None
        
        ctx = callback_context
        highlighted_iteration = None

        if ctx.triggered:
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            logger.debug(f"Trigger ID: {trigger_id}")

            if trigger_id == 'clear-highlight-btn':
                highlighted_iteration = None
            
            elif trigger_id == 'splom' and click_data:
                # Handle plot clicks
                if 'points' in click_data and len(click_data['points']) > 0:
                    point = click_data['points'][0]
                    logger.debug(f"Clicked point: {point}")
                    new_iteration = point['pointNumber']

                    # Toggle selection
                    if highlighted_iteration == new_iteration:
                        highlighted_iteration = None
                        logger.debug("Deselecting point")
                    else:
                        highlighted_iteration = new_iteration
                        logger.debug(f"Highlighting iteration: {highlighted_iteration}")

        # Convert JSON back to DataFrame
        df = pd.read_json(io.StringIO(csv_data), orient='split')
        
        # Ensure selected variables are lists
        selected_channels = selected_channels or []
        all_selected_vars = list(set(selected_channels))
        
        # Check if we have enough variables for a SPLOM (need at least 2)
        if len(all_selected_vars) < 2:
            return create_empty_figure_with_message(
                'Select at least 2 variables to create a Scatter Plot Matrix', 'orange'
            ), highlighted_iteration, None, None, None

        # Prepare data for SPLOM
        result = prepare_dataframe_for_splom(df, all_selected_vars, yaml_data)
        if result[0] is None:  # No valid data
            return create_empty_figure_with_message(
                'Click variable buttons to select channels for SPLOM', 'blue'
            ), highlighted_iteration, None, None, None

        simplified_df, dimensions, variable_categories = result
        logger.debug(f"Dimensions after update splom: {[dim['label'] for dim in dimensions]}")
        
        # Serialize dimensions and simplified_df for storage
        dimensions_serializable = []
        for dim in dimensions:
            dim_copy = dict(dim)
            if hasattr(dim_copy['values'], 'tolist'):
                dim_copy['values'] = dim_copy['values'].tolist()
            dimensions_serializable.append(dim_copy)
        
        simplified_df_json = simplified_df.to_json(orient='split') if simplified_df is not None else None

        # Calculate Pareto front if enabled
        pareto_indices = None
        if pareto_enabled and yaml_data is not None:
            try:
                # Get objectives from YAML data
                objectives_dict = yaml_data['objectives']
                objectives = list(objectives_dict.keys())
                
                # Use user-selected objective senses from UI (or default to minimize)
                if not objective_senses:
                    objective_senses = {obj: 'minimize' for obj in objectives}
                
                if len(objectives) >= 2:
                    logger.debug(f"Calculating Pareto front for objectives: {objectives}")
                    logger.debug(f"Objective senses (from UI): {objective_senses}")
                    pareto_indices = find_pareto_front(objectives, df, objective_senses)
                    logger.debug(f"Found {len(pareto_indices) if pareto_indices else 0} Pareto optimal points")
                else:
                    logger.debug(f"Not enough objectives ({len(objectives)}) for Pareto front calculation")
            except Exception as e:
                logger.error(f"Error calculating Pareto front: {e}")
                import traceback
                traceback.print_exc()
                pareto_indices = None

        # Create and return the SPLOM figure with highlighting and Pareto front
        return create_splom_figure(
            simplified_df, 
            dimensions, 
            len(all_selected_vars),
            highlighted_iteration,
            pareto_indices,
            variable_categories,
            diagonal_visible
        ), highlighted_iteration, simplified_df_json, dimensions_serializable, variable_categories


    @callback(
        Output('download-splom-html', 'data'),
        Input('download-html-btn', 'n_clicks'),
        State('splom', 'figure'),
        State('csv-df', 'data'),
        State('yaml-df', 'data'),
        State('selected-channels', 'data'),
        State('objective-senses', 'data'),
        State('simplified-df', 'data'),
        State('dimensions-data', 'data'),
        State('selected-iteration', 'data'),
        prevent_initial_call=True
    )
    def download_splom_html(n_clicks, splom_figure, csv_data, yaml_data, selected_channels, objective_senses, simplified_df_json, dimensions_serializable, selected_iteration):
        """Download an interactive HTML file with SPLOM, data table, and working controls."""
        if n_clicks is None or splom_figure is None or csv_data is None:
            return None
        
        import json
        from datetime import datetime
        
        # Ensure the SPLOM figure has the main data trace visible
        # The issue is that splom_figure might not have the base data trace if it's been filtered
        # So we need to ensure all traces are present
        all_traces = []
        
        # Use the stored result from update_splom instead of recalculating
        # Deserialize simplified_df if available
        simplified_df = None
        if simplified_df_json:
            simplified_df = pd.read_json(io.StringIO(simplified_df_json), orient='split')
        
        # dimensions_serializable and variable_categories are already in the correct format from storage
        if dimensions_serializable:
            logger.debug("Dimensions: %s", [dim['label'] for dim in dimensions_serializable])

            # Reconstruct main trace from data
            colors = list(range(len(simplified_df)))
            text_labels = [f"Iteration {i}" for i in range(len(simplified_df))]
            
            main_trace_reconstructed = {
                'type': 'splom',
                'name': 'Data Points',
                'dimensions': dimensions_serializable,
                'text': text_labels,
                'marker': {
                    'color': colors,
                    'colorscale': 'Viridis',
                    'size': 8,
                    'symbol': 'circle',
                    'line': {'color': 'white', 'width': 0.5},
                    'opacity': 1.0,
                    'colorbar': {
                        'title': 'Iteration',
                        'title_side': 'right',
                        'thickness': 15,
                        'len': 0.7,
                        'x': 1.02
                    }
                },
                'diagonal': {'visible': False},
                'showupperhalf': True,
                'showlowerhalf': False,
                'visible': True
            }
            all_traces.append(main_trace_reconstructed)
        
        # Calculate and add Pareto front trace
        if simplified_df is not None and not simplified_df.empty and yaml_data:
            # Get objective columns
            objective_cols_original = [col for col in selected_channels if col in yaml_data.get('objectives', {})]
            
            if len(objective_cols_original) >= 2:
                # Map original column names to simplified names in simplified_df
                objective_cols_simplified = []
                for col in objective_cols_original:
                    simplified_name = col.split('.')[-1]
                    if simplified_name in simplified_df.columns:
                        objective_cols_simplified.append(simplified_name)
                
                if len(objective_cols_simplified) >= 2:
                    # Map objective_senses from original names to simplified names
                    objective_senses_simplified = {}
                    if objective_senses:
                        for orig_col in objective_cols_original:
                            simplified_name = orig_col.split('.')[-1]
                            if orig_col in objective_senses and simplified_name in simplified_df.columns:
                                objective_senses_simplified[simplified_name] = objective_senses[orig_col]
                    
                    # If no objective senses provided, default to minimize for all objectives
                    if not objective_senses_simplified:
                        for simplified_name in objective_cols_simplified:
                            objective_senses_simplified[simplified_name] = 'minimize'
                    
                    # Calculate Pareto front using simplified column names and mapped senses
                    pareto_indices = find_pareto_front(objective_cols_simplified, simplified_df, objective_senses_simplified)
                
                    if pareto_indices is not None and len(pareto_indices) > 0:
                        # Create Pareto dimensions from the main trace data
                        pareto_dimensions = []
                        for dim in dimensions_serializable:
                            pareto_values = [dim['values'][i] for i in pareto_indices]
                            pareto_dimensions.append({
                                'label': dim['label'],
                                'values': pareto_values
                            })
                        
                        pareto_text = [f"Pareto - Iteration {i}" for i in pareto_indices]
                        
                        pareto_trace_reconstructed = {
                            'type': 'splom',
                            'name': 'Pareto Front',
                            'dimensions': pareto_dimensions,
                            'text': pareto_text,
                            'marker': {
                                'color': '#FF2400',
                                'size': 10,
                                'symbol': 'diamond',
                                'line': {'color': 'black', 'width': 1.5},
                                'opacity': 1.0
                            },
                            'diagonal': {'visible': False},
                            'showupperhalf': True,
                            'showlowerhalf': False,
                            'visible': True
                        }
                        all_traces.append(pareto_trace_reconstructed)
        
        # Don't add any highlight trace by default - only when user clicks
        # The highlight will be added via JavaScript when user clicks a point
        
        # Create the complete figure for export with square dimensions
        export_layout = splom_figure.get('layout', {}).copy()
        # Set width and height to make SPLOM square (default to 800x800)
        export_layout['width'] = 800
        export_layout['height'] = 800
        
        export_figure = {
            'data': all_traces,
            'layout': export_layout
        }
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"moo_dashboard_{timestamp}.html"
        
        # Convert figures to JSON for embedding
        splom_json = json.dumps(export_figure)
        
        # Create comprehensive interactive HTML
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>WEIS MOO Dashboard - Interactive Export</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .container {{
            max-width: 1800px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .controls {{
            background: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .btn {{
            background-color: #0d6efd;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 5px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }}
        .btn:hover {{
            background-color: #0b5ed7;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        .btn-secondary {{
            background-color: #6c757d;
        }}
        .btn-secondary:hover {{
            background-color: #5a6268;
        }}
        .btn-success {{
            background-color: #198754;
        }}
        .btn-success:hover {{
            background-color: #157347;
        }}
        .btn-info {{
            background-color: #0dcaf0;
        }}
        .btn-info:hover {{
            background-color: #31d2f2;
        }}
        .plot-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .plot-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        @media (max-width: 1200px) {{
            .plot-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        h1 {{
            margin: 0;
            font-size: 28px;
        }}
        h2 {{
            margin-top: 0;
            color: #495057;
            font-size: 20px;
        }}
        .export-info {{
            font-size: 14px;
            color: rgba(255,255,255,0.9);
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>WEIS Multi-Objective Optimization Dashboard</h1>
            <div class="export-info">Exported on {datetime.now().strftime("%B %d, %Y at %H:%M:%S")}</div>
            <div class="export-info" id="objectiveGoals" style="margin-top: 10px;"></div>
        </div>
        
        <div class="controls">
            <button class="btn btn-success" id="paretoBtn" onclick="togglePareto()">Hide Pareto Front</button>
            <button class="btn btn-info" id="diagonalBtn" onclick="toggleDiagonal()">Show Diagonal</button>
        </div>
        
        <div class="plot-grid">
            <div class="plot-container">
                <h2>Scatter Plot Matrix (SPLOM)</h2>
                <div id="splom"></div>
            </div>
            
            <div class="plot-container">
                <h2>Data Table</h2>
                <div id="table"></div>
            </div>
        </div>
    </div>

    <script>
        // Store the original data
        const csvData = {json.dumps(csv_data)};
        const yamlData = {json.dumps(yaml_data)};
        const splomFigure = {splom_json};
        const objectiveSenses = {json.dumps(objective_senses or {})};
        
        // Store initial data (includes all traces: data points, pareto, etc.)
        const initialData = splomFigure.data.map(trace => ({{
            ...trace,
            visible: trace.visible !== false
        }}));
        
        // Detect if Pareto trace exists and set initial state
        const hasParetoTrace = initialData.some(trace => trace.name === 'Pareto Front');
        
        // State management
        let paretoVisible = hasParetoTrace;  // Initialize based on whether Pareto exists
        let diagonalVisible = false;
        let highlightedPoint = null;
        
        // Update button text based on initial state
        if (hasParetoTrace) {{
            document.getElementById('paretoBtn').textContent = 'Hide Pareto Front';
        }} else {{
            document.getElementById('paretoBtn').textContent = 'Show Pareto Front';
            document.getElementById('paretoBtn').disabled = true;  // Disable if no Pareto data
        }}
        
        // Display objective goals
        if (yamlData && yamlData.objectives && Object.keys(objectiveSenses).length > 0) {{
            const objectiveGoalsDiv = document.getElementById('objectiveGoals');
            const goalsList = [];
            for (const [objName, sense] of Object.entries(objectiveSenses)) {{
                const simpleName = objName.split('.').pop();
                const goal = sense === 'maximize' ? 'Maximize' : 'Minimize';
                goalsList.push(`${{goal}}: ${{simpleName}}`);
            }}
            if (goalsList.length > 0) {{
                objectiveGoalsDiv.textContent = 'Optimization Goals: ' + goalsList.join(' | ');
            }}
        }}
        
        // Define functions first
        function updateTable(pointIndex) {{
            console.log('=== updateTable called with pointIndex:', pointIndex);
            
            if (!csvData) {{
                console.error('No CSV data available');
                return;
            }}
            
            try {{
                // Parse CSV data
                const df = JSON.parse(csvData);
                const columns = df.columns;
                const data = df.data;
                
                if (!data || !data[pointIndex]) {{
                    console.error('No data for point index', pointIndex);
                    return;
                }}
                
                // Get row data for selected point
                const rowData = data[pointIndex];
                
                // Extract variable categories
                const variableCategories = {{}};
                if (yamlData) {{
                    if (yamlData.objectives) {{
                        Object.keys(yamlData.objectives).forEach(key => variableCategories[key] = 'objectives');
                    }}
                    if (yamlData.constraints) {{
                        Object.keys(yamlData.constraints).forEach(key => variableCategories[key] = 'constraints');
                    }}
                    if (yamlData.design_vars) {{
                        Object.keys(yamlData.design_vars).forEach(key => variableCategories[key] = 'design_vars');
                    }}
                }}
                
                // Create table data with color coding via font property
                const tableHeaders = ['Variable', `Iteration ${{pointIndex}}`];
                const variableNames = [];
                const variableColors = [];
                const values = [];
                
                columns.forEach((col, idx) => {{
                    const category = variableCategories[col] || 'other';
                    let color = '#212529';
                    if (category === 'objectives') color = '#0d6efd';
                    else if (category === 'constraints') color = '#fd7e14';
                    else if (category === 'design_vars') color = '#198754';
                    
                    variableNames.push(col);
                    variableColors.push(color);
                    
                    // Safely format value
                    const value = rowData[idx];
                    if (value !== null && value !== undefined && typeof value === 'number') {{
                        values.push(value.toFixed(6));
                    }} else if (value !== null && value !== undefined) {{
                        values.push(String(value));
                    }} else {{
                        values.push('N/A');
                    }}
                }});
                
                const tableData = [{{
                    type: 'table',
                    header: {{
                        values: tableHeaders,
                        fill: {{color: '#2c3e50'}},
                        align: 'left',
                        font: {{size: 16, color: 'white', family: 'Arial, sans-serif'}},
                        height: 40,
                        line: {{color: '#34495e', width: 1}}
                    }},
                    cells: {{
                        values: [variableNames, values],
                        align: ['left', 'right'],
                        fill: {{
                            color: [['#e8f4fd'].concat(variableNames.map((_, i) => i % 2 === 0 ? '#f8f9fa' : '#ffffff'))]
                        }},
                        font: [
                            {{size: 14, family: 'Arial, sans-serif', color: variableColors}},
                            {{size: 14, family: 'Arial, sans-serif', color: '#2c3e50'}}
                        ],
                        height: 35,
                        line: {{color: '#bdc3c7', width: 0.5}}
                    }}
                }}];
                
                const tableLayout = {{
                    margin: {{t: 10, b: 10, l: 10, r: 10}},
                    height: 600
                }};
                
                Plotly.newPlot('table', tableData, tableLayout);
                
                // Update iteration indicator
                const indicator = document.getElementById('iterationIndicator');
                if (indicator) {{
                    indicator.textContent = `Iteration: ${{pointIndex}}`;
                }}
                
                console.log('Table updated successfully for point index', pointIndex);
            }} catch (error) {{
                console.error('Error updating table:', error);
            }}
        }}
        
        function highlightPoint(pointIndex) {{
            console.log('=== highlightPoint called with pointIndex:', pointIndex);
            
            // Find the main trace to get dimensions structure
            const mainTrace = initialData.find(t => t.name === 'Data Points');
            if (!mainTrace || !mainTrace.dimensions) {{
                console.error('Main trace not found or no dimensions');
                return;
            }}
            
            // Create highlight trace with the selected point
            const highlightDimensions = mainTrace.dimensions.map(dim => ({{
                label: dim.label,
                values: [dim.values[pointIndex]]
            }}));
            
            // Get current plot data and remove existing highlight trace
            let currentData = [...initialData].filter(trace => trace.name !== 'Highlighted');
            
            // Add new highlight trace
            const highlightTrace = {{
                type: 'splom',
                name: 'Highlighted',
                dimensions: highlightDimensions,
                marker: {{
                    color: '#2ca02c',
                    size: 12,
                    symbol: 'star',
                    line: {{color: 'black', width: 2}}
                }},
                diagonal: {{visible: diagonalVisible}},
                showupperhalf: true,
                showlowerhalf: false
            }};
            
            currentData.push(highlightTrace);
            
            // Update the plot with new highlight
            Plotly.react('splom', currentData, splomFigure.layout);
            console.log('Highlight updated for point index', pointIndex);
        }}
        
        // Render SPLOM
        Plotly.newPlot('splom', initialData, splomFigure.layout);
        
        // Initialize with pointIndex 0
        console.log('Initializing with pointIndex 0');
        updateTable(0);
        
        // Click event handler for SPLOM
        document.getElementById('splom').on('plotly_click', function(data) {{
            console.log('SPLOM clicked! Data:', data);
            
            let pointIndex = 0;
            if (data.points && data.points.length > 0) {{
                const point = data.points[0];
                console.log('Clicked point:', point);
                
                // Get the point index - handle different trace types
                pointIndex = point.pointIndex;
                console.log('Point index from click:', pointIndex);
                
                // If clicked on Pareto or other trace, find the actual index in main data
                if (point.data.name !== 'Data Points') {{
                    console.log('Clicked on non-main trace, finding actual index...');
                    const clickedValue = point.data.dimensions[0].values[point.pointIndex];
                    const mainTrace = initialData.find(t => t.name === 'Data Points');
                    if (mainTrace) {{
                        pointIndex = mainTrace.dimensions[0].values.indexOf(clickedValue);
                        console.log('Found actual pointIndex:', pointIndex);
                    }}
                }}
            }}

            console.log('Final pointIndex to use:', pointIndex);
            
            // Update table based on clicked point
            updateTable(pointIndex);
            
            // Highlight the clicked point
            highlightPoint(pointIndex);
        }});
        
        function togglePareto() {{
            paretoVisible = !paretoVisible;
            const btn = document.getElementById('paretoBtn');
            btn.textContent = paretoVisible ? 'Hide Pareto Front' : 'Show Pareto Front';
            
            // Get current traces from the plot
            const splomDiv = document.getElementById('splom');
            const currentData = splomDiv.data;
            
            // Toggle Pareto trace visibility
            const updatedData = currentData.map(trace => {{
                if (trace.name === 'Pareto Front') {{
                    return {{...trace, visible: paretoVisible}};
                }}
                return trace;
            }});
            
            Plotly.react('splom', updatedData, splomFigure.layout);
        }}
        
        function toggleDiagonal() {{
            diagonalVisible = !diagonalVisible;
            const btn = document.getElementById('diagonalBtn');
            btn.textContent = diagonalVisible ? 'Hide Diagonal' : 'Show Diagonal';
            
            // Get current traces from the plot
            const splomDiv = document.getElementById('splom');
            const currentData = splomDiv.data;
            
            // Update all traces diagonal visibility
            const updatedData = currentData.map(trace => ({{
                ...trace,
                diagonal: {{visible: diagonalVisible}}
            }}));
            
            Plotly.react('splom', updatedData, splomFigure.layout);
        }}
    </script>
</body>
</html>
"""
        
        # Return the HTML content for download
        return dict(content=html_content, filename=filename)


def register_table_callbacks(app):
    @callback(Output('data-table', 'figure'),
              [Input('csv-df', 'data'),
               Input('selected-iteration', 'data'),
               Input('yaml-df', 'data')])
    def update_table(csv_data, selected_iteration, yaml_data):
        """Update the data table based on selected data point from SPLOM with enhanced statistics"""
        if selected_iteration is None:
            return create_empty_figure_with_message(
                'Click on a data point in the SPLOM to see detailed analysis', 'gray'
            )

        # Convert JSON back to DataFrame
        df = pd.read_json(io.StringIO(csv_data), orient='split')
        
        # Get the selected row data and transpose for display
        filtered_df = df.iloc[[selected_iteration]].T
        
        logger.info(f'Selected iteration: {selected_iteration}')
        logger.debug(f'Filtered DataFrame:\n{filtered_df}')

        # Use the enhanced table without color categories
        return create_table_figure(filtered_df, None)
