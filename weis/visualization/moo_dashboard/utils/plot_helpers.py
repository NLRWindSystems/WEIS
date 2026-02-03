"""
Plot helpers and formatting utilities
"""
import logging
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, List
from config.settings import (
    DEFAULT_PLOT_WIDTH, DEFAULT_PLOT_HEIGHT, MARKER_SIZE, MARKER_LINE_WIDTH,
    BASE_FONT_SIZE, MIN_FONT_SIZE, MAX_FONT_SIZE, BASE_MARGIN, MAX_MARGIN,
    HIGHLIGHT_COLOR, HIGHLIGHT_SIZE_MULTIPLIER, HIGHLIGHT_OPACITY, 
    NON_HIGHLIGHT_OPACITY, HIGHLIGHT_LINE_WIDTH, COLOR_SCALES, HIGHLIGHT_SYMBOL
)

logger = logging.getLogger(__name__)


def calculate_font_size(num_vars: int, plot_width: int = DEFAULT_PLOT_WIDTH) -> int:
    """
    Calculate optimal font size based on number of variables and plot width.
    
    Args:
        num_vars: Number of variables in the SPLOM
        plot_width: Width of the plot
        
    Returns:
        Optimal font size for axis labels
    """
    # Calculate space available per subplot
    subplot_width = plot_width / num_vars
    
    # Adjust font size based on available space
    if subplot_width < 100:
        font_size = max(MIN_FONT_SIZE, int(BASE_FONT_SIZE * 0.5))
    elif subplot_width < 150:
        font_size = max(MIN_FONT_SIZE + 2, int(BASE_FONT_SIZE * 0.7))
    elif subplot_width < 200:
        font_size = max(MIN_FONT_SIZE + 4, int(BASE_FONT_SIZE * 0.85))
    else:
        font_size = BASE_FONT_SIZE
    
    return min(font_size, MAX_FONT_SIZE)


def truncate_labels(dimensions: List[str], max_length: int = 15) -> List[str]:
    """
    Intelligently truncate long variable names for better display.
    
    Args:
        dimensions: List of dimension names
        max_length: Maximum length for labels
        
    Returns:
        List of truncated dimension names
    """
    truncated = []
    for dim in dimensions:
        if len(dim) <= max_length:
            truncated.append(dim)
        else:
            # Try to keep meaningful parts
            if '_' in dim:
                # Split by underscore and take first and last parts
                parts = dim.split('_')
                if len(parts) >= 2:
                    truncated_name = f"{parts[0]}_{parts[-1]}"
                    if len(truncated_name) <= max_length:
                        truncated.append(truncated_name)
                    else:
                        truncated.append(dim[:max_length-2] + "..")
                else:
                    truncated.append(dim[:max_length-2] + "..")
            else:
                # Simple truncation with ellipsis
                truncated.append(dim[:max_length-2] + "..")
    
    return truncated


def calculate_margin_size(num_vars: int, font_size: int) -> int:
    """
    Calculate optimal margin size based on number of variables and font size.
    
    Args:
        num_vars: Number of variables in the SPLOM
        font_size: Font size being used
        
    Returns:
        Optimal margin size
    """
    # Increase margin for smaller fonts and more variables
    if num_vars > 6:
        margin = BASE_MARGIN + (font_size * 2)
    elif num_vars > 4:
        margin = BASE_MARGIN + font_size
    else:
        margin = BASE_MARGIN
    
    return min(margin, MAX_MARGIN)


def create_splom_figure(df: pd.DataFrame, dimensions: List[Dict], num_vars: int, highlighted_iteration: int = None, pareto_indices: List[int] = None, variable_categories: Dict[str, str] = None, diagonal_visible: bool = True):
    """
    Create a scatter plot matrix (SPLOM) with color-coded samples and auto-sized labels.
    Uses plotly.graph_objects for better control of marker properties and highlighting.
    
    Args:
        df: DataFrame with simplified column names and sample_id
        dimensions: List of dimension dictionaries with 'label' and 'values' keys
        num_vars: Number of variables for title
        highlighted_iteration: Optional iteration to highlight across all subplots
        pareto_indices: Optional list of indices for Pareto front points
        variable_categories: Dict mapping variable names to categories (objectives, constraints, design_vars)
        diagonal_visible: Whether to show diagonal plots (default True)

    Returns:
        Plotly figure with SPLOM
    """
    
    # Define category colors for axis labels
    category_colors = {
        'objectives': '#0d6efd',      # Bootstrap primary blue
        'constraints': '#fd7e14',     # Bootstrap warning orange
        'design_vars': '#198754',     # Bootstrap success green
    }
    if df.empty or not dimensions:
        return go.Figure()
    
    # Check if we have enough dimensions for a proper SPLOM
    if len(dimensions) < 2:
        return create_empty_figure_with_message(
            'Select at least 2 variables to create a Scatter Plot Matrix',
            'orange'
        )
    
    # With only 2 dimensions and diagonal hidden, show a warning
    if len(dimensions) == 2 and not diagonal_visible:
        return create_empty_figure_with_message(
            'Cannot hide diagonal with only 2 variables selected. Please select more variables or show diagonal.',
            'orange'
        )

    # Calculate optimal font size and margins
    font_size = calculate_font_size(num_vars, DEFAULT_PLOT_WIDTH)
    margin_size = calculate_margin_size(num_vars, font_size)
    
    # Determine max label length based on number of variables
    max_label_length = 20 if num_vars <= 3 else 15 if num_vars <= 5 else 12 if num_vars <= 7 else 10
    
    # Extract labels from dimensions and truncate them
    dimension_labels = [dim['label'] for dim in dimensions]
    truncated_labels = truncate_labels(dimension_labels, max_label_length)
    
    # Debug: Check for problematic dimensions
    logger.debug(f"Creating SPLOM with {len(dimensions)} dimensions")
    for i, dim in enumerate(dimensions):
        values = np.array(dim['values'])
        values_clean = values[~np.isnan(values)]  # Remove NaN values for stats
        
        if len(values_clean) > 0:
            val_min = np.min(values_clean)
            val_max = np.max(values_clean)
            val_range = val_max - val_min
            
            logger.debug(f"Dimension '{dim['label']}':")
            logger.debug(f"  - Values count: {len(values_clean)}/{len(values)}")
            logger.debug(f"  - Range: {val_min:.6f} to {val_max:.6f} (range: {val_range:.6f})")
            
            # Note potential visualization issues but don't modify data
            if val_range == 0:
                logger.warning(f"  - All values are identical ({val_min}) - may appear as single point")
            elif val_range < 1e-10:
                logger.warning(f"  - Very small range - points may cluster tightly")
        else:
            logger.warning(f"Dimension '{dim['label']}' has no valid values (all NaN)")
    
    # Create updated dimensions with truncated labels
    truncated_dimensions = []
    for i, dim in enumerate(dimensions):
        truncated_dimensions.append({
            'label': truncated_labels[i],
            'values': dim['values']
        })
    
    # Prepare data for SPLOM
    n_vars = num_vars
    n_samples = len(df)
        
    # Create color array based on iteration index
    colors = np.arange(n_samples)  # Use actual iteration numbers for colors
    
    # Create text labels
    text_labels = [f"Iteration {i}" for i in range(n_samples)]

    # Create main SPLOM trace with normal points
    splom_trace = go.Splom(
        dimensions=truncated_dimensions,
        text=text_labels,
        marker=dict(
            color=colors,
            colorscale=COLOR_SCALES['samples'],
            size=8,
            symbol='circle',
            line=dict(
                color='white',
                width=0.5
            ),
            opacity=1.0 if highlighted_iteration is None else NON_HIGHLIGHT_OPACITY,
            colorbar=dict(
                title="Iteration",
                title_side="right",
                thickness=15,
                len=0.7,
                x=1.02,
                tickmode='linear',
                tick0=0,
                dtick=max(1, n_samples // 10)  # Show reasonable number of ticks
            )
        ),
        diagonal_visible=diagonal_visible,
        showupperhalf=True,
        showlowerhalf=False,
        name=f"",
        showlegend=False
    )
    
    traces = [splom_trace]
    
    # Add Pareto front trace first (so it's drawn before highlights)
    if pareto_indices is not None and len(pareto_indices) > 0:
        # Create dimensions for Pareto front points
        pareto_dimensions = []
        for dim_dict in truncated_dimensions:
            dim_label = dim_dict['label']
            dim_values = dim_dict['values']
            
            # Extract values for Pareto front points
            pareto_values = [dim_values[i] for i in pareto_indices if i < len(dim_values)]
            
            pareto_dimensions.append(dict(
                label=dim_label,
                values=pareto_values
            ))
        
        # Create Pareto front trace
        pareto_trace = go.Splom(
            dimensions=pareto_dimensions,
            text=[f"Iteration {i} (Pareto)" for i in pareto_indices],
            marker=dict(
                color='#FF2400',
                size=MARKER_SIZE * 3.0,  # Slightly larger than normal
                symbol='diamond',  # Different symbol for Pareto points
                line=dict(
                    color='black',
                    width=2
                ),
                opacity=0.8
            ),
            diagonal_visible=diagonal_visible,
            showupperhalf=True,
            showlowerhalf=False,
            name=f"Pareto Front ({len(pareto_indices)} points)",
            showlegend=False
        )
        
        traces.append(pareto_trace)

    # Add highlighted trace
    if highlighted_iteration is not None and highlighted_iteration < n_samples:
        # Create dimensions for highlighted point using truncated dimensions
        highlighted_dimensions = []
        for dim_dict in truncated_dimensions:
            dim_label = dim_dict['label']
            dim_values = dim_dict['values']
            
            # Extract the value for the highlighted iteration
            highlighted_value = dim_values[highlighted_iteration]
            
            highlighted_dimensions.append(dict(
                label=dim_label,
                values=[highlighted_value]  # Single value as list
            ))
        
        highlighted_trace = go.Splom(
            dimensions=highlighted_dimensions,
            text=[f"Iteration {highlighted_iteration} (Selected)"],
            marker=dict(
                color=HIGHLIGHT_COLOR,
                size=MARKER_SIZE * HIGHLIGHT_SIZE_MULTIPLIER,
                symbol=HIGHLIGHT_SYMBOL,  # Use star for high visibility
                line=dict(
                    color='black',  # Black border for maximum contrast
                    width=HIGHLIGHT_LINE_WIDTH
                ),
                opacity=HIGHLIGHT_OPACITY
            ),
            diagonal_visible=diagonal_visible,
            showupperhalf=True,
            showlowerhalf=False,
            name=f"Iteration {highlighted_iteration} (Selected)",
            showlegend=False
        )
        
        traces.append(highlighted_trace)

    fig = go.Figure(data=traces)

    # Update layout
    fig.update_layout(
        title={
            'text': f'Scatterplot Matrix (SPLOM) - {n_vars} Variables × {n_samples} Iterations',
            'x': 0.5,
            'xanchor': 'center'
        },
        plot_bgcolor='rgba(240,240,240,0.95)',
        # Add margins to prevent label cutoff and accommodate colorbar
        margin=dict(
            l=margin_size,
            r=margin_size + 60,  # Extra space for colorbar
            t=margin_size + 20,  # Extra space for title
            b=margin_size
        ),
        # Configure font sizes for all text elements
        font=dict(size=font_size),
        # Adjust axis label properties
        showlegend=False,
        dragmode='select',
        hovermode='closest'
    )
    
    return fig


def create_empty_figure_with_message(message: str, message_color: str = 'gray') -> Dict:
    """
    Create an empty figure with a centered message.
    
    Args:
        message: Message to display
        message_color: Color of the message text
        
    Returns:
        Plotly figure dictionary
    """
    return {
        'data': [],
        'layout': {
            'title': message,
            'xaxis': {'visible': False},
            'yaxis': {'visible': False},
            'annotations': [{
                'text': message,
                'xref': 'paper',
                'yref': 'paper',
                'x': 0.5,
                'y': 0.5,
                'xanchor': 'center',
                'yanchor': 'middle',
                'showarrow': False,
                'font': {'size': 16, 'color': message_color}
            }]
        }
    }


def create_table_figure(data: pd.DataFrame, variable_categories: Dict[str, str] = None) -> Dict:
    """
    Create a table figure from a DataFrame with index (which is prior cols) and color-coded variable names.

    Args:
        data: DataFrame to display in the table
        variable_categories: Dict mapping variable names to categories
        
    Returns:
        Plotly figure dictionary
    """
    # Define category colors
    category_colors = {
        'objectives': '#0d6efd',
        'constraints': '#fd7e14',
        'design_vars': '#198754',
    }
    
    # Format numeric values for better display
    formatted_data = data.copy()
    
    # Round numeric columns to 4 decimal places and format
    for col in formatted_data.columns:
        if formatted_data[col].dtype in ['float64', 'float32']:
            formatted_data[col] = formatted_data[col].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "N/A")
        elif formatted_data[col].dtype in ['int64', 'int32']:
            formatted_data[col] = formatted_data[col].apply(lambda x: f"{x:,}" if pd.notna(x) else "N/A")
    
    # Create alternating row colors
    num_rows = len(formatted_data)
    row_colors = ['#f8f9fa' if i % 2 == 0 else '#ffffff' for i in range(num_rows)]
    
    # Color code the index (variable names) based on categories
    index_colors = []
    for var_name in formatted_data.index:
        category = variable_categories.get(var_name) if variable_categories else None
        if category and category in category_colors:
            index_colors.append(category_colors[category])
        else:
            index_colors.append('#2c3e50')  # Default color
    
    # Prepare header values with better formatting
    header_values = ['Variable'] + [f"<b>{col}</b>" for col in formatted_data.columns]
    
    # Prepare cell values with index
    cell_values = [formatted_data.index.tolist()] + [formatted_data[col].tolist() for col in formatted_data.columns]
    
    return {
        'data': [
            {
                'type': 'table',
                'header': {
                    'values': header_values,
                    'fill': {
                        'color': '#2c3e50'  # Dark blue-gray header
                    },
                    'align': ['left'] * (len(formatted_data.columns) + 1),
                    'font': {
                        'color': 'white',
                        'size': MAX_FONT_SIZE,
                    },
                    'height': 40,
                    'line': {'color': '#34495e', 'width': 1}
                },
                'cells': {
                    'values': cell_values,
                    'fill': {
                        'color': [['#e8f4fd'] + row_colors]  # Light blue for index column, alternating for data
                    },
                    'align': ['left'] * (len(formatted_data.columns) + 1),
                    'font': {
                        'color': [index_colors] + [['#2c3e50'] * num_rows] * len(formatted_data.columns),  # Colored variable names
                        'size': BASE_FONT_SIZE,
                    },
                    'height': 35,
                    'line': {'color': '#bdc3c7', 'width': 0.5}
                }
            }
        ],
        'layout': {
            'margin': {'l': 20, 'r': 20, 't': 60, 'b': 20},
            'paper_bgcolor': '#ffffff',
            'plot_bgcolor': '#ffffff',
            'font': {
                'family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                'size': 13
            },
            'height': max(300, min(600, num_rows * 40 + 120))  # Dynamic height based on data
        }
    }