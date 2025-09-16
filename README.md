## VAS One-Click Pipeline

To refresh the data pipeline and generate all reports in one step, use the one-click script:

```
python scripts/one_click_vas.py
```

This script will:
- Run `scripts/processing.py` to refresh the data pipeline
- Run `scripts/create_charts.py` to generate all reports, including Case 1, Case 2, and Case 3 (VAS)
- Log progress and details to `scripts/logs/` (DEBUG level) and print user-friendly messages to the terminal (INFO level)

You can find detailed logs in the `scripts/logs/` folder after running the script.
# VAS - Data Analysis and Visualization

This project processes and visualizes multiple CTD2 runs data, creating interactive charts for offset analysis.


**Project Folder Architecture**

This diagram shows the main folders and files, their purposes, and how data flows from raw sources to processed outputs and reports.

```
vas_1.5/
├── data/
│   ├── processed/         # Processed CSV files
│   ├── source_data/       # Raw data files and templates (printing_raw_data_report .csv AND run_parameters_template .xlsx)
│   └── views/             # Data views for different cases
├── output/
│   └── charts/            # Generated charts and reports (html)
├── scripts/
│   ├── create_charts.py   # Main script for generating charts
│   ├── one_click_vas.py   # Pipeline runner script (main script to generate the analysis)
│   ├── parameters.yaml    # Configuration file (parameters configuration for a customized analysis)
│   ├── processing.py      # Data processing script (for data intake)
│   ├── spotnumber_colors.csv # Color mappings for spot numbers
│   └── logs/              # Log files (for debbuging)
├── README.md
├── requirements.txt       # Essencial libraries to run the scripts
└── .gitignore             # What to be ignored in git (e.g: big data files)
```

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
