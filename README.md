## VAS One-Click Pipeline

To refresh the data pipeline and generate all reports in one step, use the one-click script:

```
python3 scripts/one_click_vas.py
```

This script will:
- Run `scripts/processing.py` to refresh the data pipeline
- Run `scripts/create_charts.py` to generate all reports, including Case 1, Case 2, and Case 3 (VAS)
- Log progress and details to `scripts/logs/` (DEBUG level) and print user-friendly messages to the terminal (INFO level)

You can find detailed logs in the `scripts/logs/` folder after running the script.
# VAS - Data Analysis and Visualization

This project processes and visualizes VAS (Visual Analysis System) data, creating interactive charts for offset analysis.

## Project Structure

- `data/` - Contains source data, processed data, and views
  - `source_data/` - Raw data files and templates
  - `processed/` - Processed CSV files
  - `views/` - Data views for different cases
- `scripts/` - Python scripts for data processing and chart creation
- `output/` - Generated charts and reports

## Main Scripts

- `scripts/create_charts.py` - Main script for generating interactive HTML charts
- `scripts/parameters.yaml` - Configuration file for filtering and settings
- `scripts/spotnumber_colors.csv` - Color mappings for spot numbers

## Features


- **Case 01**: Scatterplot analysis grouped by run_id and SpotNumber
- **Case 02**: Scatterplot analysis grouped by run_id and PalletteNumber
- **Case 03 (VAS)**: Scatterplot analysis grouped by run_id and PalletteNumber, colored by RowNumber, with row color legend, axis centering, cross axes, 2σ circle, tolerance circle, global legend, filter summary, and data point count per row displayed in each chart.
- Interactive HTML charts with filtering capabilities
- Statistical analysis with density circles (86% of data points)
- Tolerance area visualization
- Grid and non-grid layout options

## Usage

```bash
python scripts/create_charts.py
```

## Chart Features

- **Black circle**: Density area (86% of data points)
- **Blue dotted line**: Tolerance area
- Dynamic color palette for maximum contrast
- Fixed axis scaling for consistent comparison
- Statistical metrics displayed on each chart
