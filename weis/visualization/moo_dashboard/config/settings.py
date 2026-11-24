"""
Configuration settings for the MOO Dashboard
"""
import logging

# Logging configuration
logging.basicConfig(
    level=logging.DEBUG if True else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# App configuration
DEBUG = True
HOST = '0.0.0.0'
PORT = 8050

# UI Configuration
DEFAULT_PLOT_WIDTH = 800
DEFAULT_PLOT_HEIGHT = 800
MARKER_SIZE = 4
MARKER_LINE_WIDTH = 0.5

# Font size configuration
BASE_FONT_SIZE = 12
MIN_FONT_SIZE = 6
MAX_FONT_SIZE = 14

# Margin configuration
BASE_MARGIN = 60
MAX_MARGIN = 120

# Highlighting configuration
HIGHLIGHT_COLOR = '#00FF41'  # Bright green - high contrast against red Pareto points
HIGHLIGHT_SIZE_MULTIPLIER = 3  # Larger size for better visibility
HIGHLIGHT_OPACITY = 1.0
NON_HIGHLIGHT_OPACITY = 0.4
HIGHLIGHT_LINE_WIDTH = 4  # Thicker border
HIGHLIGHT_SYMBOL = 'star'  # Distinctive shape

# Color schemes
COLOR_SCALES = {
    'samples': 'viridis',
    'objectives': 'primary',
    'constraints': 'warning', 
    'design_vars': 'success'
}

# File upload settings
ALLOWED_CSV_EXTENSIONS = ['.csv', '.xls', '.xlsx']
ALLOWED_YAML_EXTENSIONS = ['.yaml', '.yml']
