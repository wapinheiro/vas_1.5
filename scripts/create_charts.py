import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Circle as MplCircle
import yaml
import glob
import openpyxl
import random
import csv
import base64
from io import BytesIO
import matplotlib
import numpy as np  
matplotlib.use('Agg')

def safe_int_sort_key(x):
    """
    Helper function for sorting that handles both numeric and alphanumeric values.
    Tries to convert to int first, falls back to string sorting if that fails.
    """
    try:
        return (0, int(x))  # (priority, numeric_value) - numeric values come first
    except (ValueError, TypeError):
        return (1, str(x))  # (priority, string_value) - alphanumeric values come second

def generate_spotnumber_colors():
    """
    Generates a CSV file mapping spot numbers 1-66 to random hex colors.
    Output: scripts/spotnumber_colors.csv
    """
    output_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'spotnumber_colors.csv'))
    spot_numbers = list(range(1, 67))
    colors = set()
    def random_color():
        return '#{:06x}'.format(random.randint(0, 0xFFFFFF))
    # Ensure unique colors
    while len(colors) < 66:
        colors.add(random_color())
    color_list = list(colors)
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['SpotNumber', 'Color'])
        for spot, color in zip(spot_numbers, color_list):
            writer.writerow([spot, color])
    print(f"Spot number colors saved to {output_file}")

def load_spotnumber_colors():
    """Load spot number to color mapping from scripts/spotnumber_colors.csv as a dict."""
    color_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'spotnumber_colors.csv'))
    df = pd.read_csv(color_file, dtype={'SpotNumber': str, 'Color': str})
    return {str(row['SpotNumber']): row['Color'] for _, row in df.iterrows()}

def load_parameters():
    """Load parameters.yaml as a dict."""
    param_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'parameters.yaml'))
    with open(param_file, 'r') as f:
        params = yaml.safe_load(f)
    return params

def create_chart_case_01(grid=False):
    """
    Create scatterplot(s) for XOffset vs YOffset from data/views/view_case_01.csv.
    Features:
    - Group by run_id and SpotNumber.
    - Use a dynamically generated, maximally distinct color palette for each run's filtered set of spot numbers:
        - For up to 12 spots, assign a fixed, ordered set of high-contrast colors (black, yellow, red, cyan, blue, lime, magenta, orange, green, pink, purple, brown) for maximum mutual contrast.
        - For more than 12, generate vivid HSV colors.
    - The color mapping is consistent for all charts and the legend within the report.
    - Add a color legend at the top of the report, showing the color assigned to each spot number.
    - Apply filters from parameters.yaml (spot_numbers, run_id).
    - Keep axis centered and fixed at [-0.3, 0.3] for both X and Y axes for all charts.
    - Draw cross axes at (0,0) for all charts.
    - Draw a black solid circle at 2× the standard deviation of the radius (2σ) for each chart, and display the value in the chart title.
    - Display the average std radius for each run below the run title.
    - Add a global legend at the top explaining the 2σ circle (black solid) and its statistical meaning.
    - Output: HTML file in output/charts/ (grid or non-grid layout).
    """
    # Load data
    data_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'views', 'view_case_01.csv'))
    df = pd.read_csv(data_file, dtype=str)
    df['XOffset'] = pd.to_numeric(df['XOffset'], errors='coerce')
    df['YOffset'] = pd.to_numeric(df['YOffset'], errors='coerce')
    df['SpotNumber'] = df['SpotNumber'].astype(str)
    df['run_id'] = df['run_id'].astype(str)

    # Remove outlier/placeholder values (e.g., 999.0)
    mask = (df['XOffset'] != 999.0) & (df['YOffset'] != 999.0)
    df = df[mask]

    # Load color mapping and parameters
    spot_colors = load_spotnumber_colors()
    params = load_parameters()
    spot_filter = set(str(s) for s in params.get('spot_numbers', [])) if params.get('spot_numbers') else None
    run_filter = set(str(r) for r in params.get('run_id', [])) if params.get('run_id') else None

    # Apply filters
    if spot_filter:
        df = df[df['SpotNumber'].isin(spot_filter)]
    if run_filter:
        df = df[df['run_id'].isin(run_filter)]

    # After filtering, get unique spot numbers
    unique_spots = sorted(df['SpotNumber'].unique(), key=lambda x: int(x))
    n_spots = len(unique_spots)
    import numpy as np
    import matplotlib.colors as mcolors
    import matplotlib.cm as cm
    # Hand-picked, ordered high-contrast colors for up to 12 spots (maximal mutual contrast)
    # Removed black since we'll use it for the high density circle
    high_contrast_colors = [
        '#FFD700',  # yellow
        '#FF0000',  # red
        '#00FFFF',  # cyan
        '#0000FF',  # blue
        '#00FF00',  # lime
        '#FF00FF',  # magenta
        '#FFA500',  # orange
        '#008000',  # green
        '#FFC0CB',  # pink
        '#800080',  # purple
        '#A52A2A',  # brown
        '#FF6347',  # tomato (added to replace black)
    ]
    if n_spots <= len(high_contrast_colors):
        color_list = high_contrast_colors[:n_spots]
        # Assign in order for maximum group contrast
        spot_colors = {spot: color for spot, color in zip(unique_spots, color_list)}
    else:
        # For more than 12, use HSV with high saturation and value for vividness
        color_indices = np.linspace(0, 1, n_spots, endpoint=False)
        np.random.shuffle(color_indices)
        spot_colors = {spot: mcolors.to_hex(mcolors.hsv_to_rgb([idx, 0.95, 0.95])) for spot, idx in zip(unique_spots, color_indices)}

    # Prepare output
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output', 'charts'))
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, 'case_01_grid.html' if grid else 'case_01.html')

    # Axis limits (centered, same for all)
    # x_min, x_max = df['XOffset'].min(), df['XOffset'].max()
    # y_min, y_max = df['YOffset'].min(), df['YOffset'].max()
    # x_c = (x_max + x_min) / 2
    # y_c = (y_max + y_min) / 2
    # x_range = max(abs(x_max - x_c), abs(x_min - x_c))
    # y_range = max(abs(y_max - y_c), abs(y_min - y_c))
    # axis_lim = max(x_range, y_range)
    # xlim = (x_c - axis_lim, x_c + axis_lim)
    # ylim = (y_c - axis_lim, y_c + axis_lim)
    xlim = (-0.3, 0.3)
    ylim = (-0.3, 0.3)

    # Grouping
    #runs = sorted(df['run_id'].unique()) # New line to flag runs with letters 
    runs = sorted(df['run_id'].unique(), key=safe_int_sort_key)
    spots = sorted(df['SpotNumber'].unique(), key=lambda x: int(x))

    # Build HTML legend for all spot numbers/colors (dynamic palette)
    legend_html = '<div style="margin-bottom:10px;"><b>Spot Color Legend:</b><br>'
    for spot in unique_spots:
        color = spot_colors.get(spot, '#000000')
        legend_html += f'<span style="display:inline-block;width:16px;height:16px;background:{color};margin-right:4px;"></span> {spot} '
    legend_html += '</div>'
    html = ['<html><head><title>Case 01 Charts</title></head><body>']
    # Add visual legend for circles
    html.append('<div style="margin-bottom:15px; padding:10px; background:#f9f9f9; border:1px solid #ddd;">')
    html.append('<div style="margin-bottom:5px;"><span style="display:inline-block; width:20px; height:3px; background:black; margin-right:8px; vertical-align:middle;"></span><b>Black circle:</b> Density area (86% of data points)</div>')
    html.append('<div><span style="display:inline-block; width:20px; height:2px; background:blue; border-top:2px dotted blue; margin-right:8px; vertical-align:middle;"></span><b>Blue dotted line:</b> Tolerance area</div>')
    html.append('</div>')
    html.append(legend_html)
    if grid:
        html.append('<h1>Case 01 Grid Layout</h1>')
        html.append('<table border="1" style="border-collapse:collapse;"><tr><th></th>')
        for run in runs:
            html.append(f'<th>Run {run}</th>')
        html.append('</tr>')
        for spot in spots:
            html.append(f'<tr><td>Spot {spot}</td>')
            for run in runs:
                subdf = df[(df['run_id'] == run) & (df['SpotNumber'] == spot)]
                fig, ax = plt.subplots(figsize=(2,2))
                scatter = ax.scatter(subdf['XOffset'], subdf['YOffset'], color=spot_colors.get(spot, '#000000'), s=1)
                ax.set_xlim(xlim)
                ax.set_ylim(ylim)
                ax.set_title("")
                # ax.set_xlabel('XOffset')
                # ax.set_ylabel('YOffset')
                # Draw cross axes at center
                # ax.axhline(y=y_c, color='gray', linestyle='--', linewidth=0.8)
                # ax.axvline(x=x_c, color='gray', linestyle='--', linewidth=0.8)
                ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.8)
                ax.axvline(x=0, color='gray', linestyle='--', linewidth=0.8)
                # Remove all legends
                if ax.get_legend():
                    ax.get_legend().remove()
                ax.set_aspect('equal')
                plt.tight_layout()
                buf = BytesIO()
                plt.savefig(buf, format='png')
                plt.close(fig)
                img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                html.append(f'<td><img src="data:image/png;base64,{img_b64}"/></td>')
            html.append('</tr>')
        html.append('</table>')
    else:
        html.append('<h1>Case 01 (XOffset x YOffset)</h1>')
        for run in runs:
            run_html = []
            run_html.append(f'<h2>Run {run}</h2>')
            run_spread_values = []  # Collect all spread values for this run
            for spot in spots:
                subdf = df[(df['run_id'] == run) & (df['SpotNumber'] == spot)]
                if subdf.empty:
                    continue
                fig, ax = plt.subplots(figsize=(3,3))
                scatter = ax.scatter(subdf['XOffset'], subdf['YOffset'], color=spot_colors.get(spot, '#000000'), s=1)
                # Draw spread circle at 2*std_radius
                spread_value = measure_spread(subdf['XOffset'], subdf['YOffset'], method='std_radius')
                circle_radius = 2 * spread_value
                run_spread_values.append(spread_value)
                if not subdf.empty:
                    import numpy as np
                    circle = plt.Circle((0, 0), circle_radius, color='black', fill=False, linestyle='-', linewidth=3, alpha=1.0)
                    ax.add_patch(circle)
                    # Draw tolerance circle at radius 0.2 (blue dotted)
                    tolerance_circle = plt.Circle((0, 0), 0.2, color='blue', fill=False, linestyle=':', linewidth=1.2, alpha=0.7)
                    ax.add_patch(tolerance_circle)
                    metric_text = f"Std Radius: {spread_value:.4f} (2σ circle)"
                else:
                    metric_text = "No data"
                ax.set_xlim(xlim)
                ax.set_ylim(ylim)
                ax.set_title(f'Spot {spot}\n{metric_text}')
                # ax.set_xlabel('XOffset')
                # ax.set_ylabel('YOffset')
                # Draw cross axes at center
                # ax.axhline(y=y_c, color='gray', linestyle='--', linewidth=0.8)
                # ax.axvline(x=x_c, color='gray', linestyle='--', linewidth=0.8)
                ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.8)
                ax.axvline(x=0, color='gray', linestyle='--', linewidth=0.8)
                # Remove all legends
                if ax.get_legend():
                    ax.get_legend().remove()
                ax.set_aspect('equal')
                plt.tight_layout()
                buf = BytesIO()
                plt.savefig(buf, format='png')
                plt.close(fig)
                img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                run_html.append(f'<div style="display:inline-block;margin:5px;"></b><br><img src="data:image/png;base64,{img_b64}"/></div>')
            # After all spots for this run, show average spread value for the run right below the run title
            if run_spread_values:
                avg_spread = sum(run_spread_values) / len(run_spread_values)
                run_html.insert(1, f'<div><b>Run {run} average std radius: {avg_spread:.4f}</b></div>')
            run_html.append('<hr/>')
            html.extend(run_html)
    html.append('</body></html>')
    with open(out_file, 'w') as f:
        f.write('\n'.join(html))
    print(f"Charts saved to {out_file}")

def measure_spread(x, y, method='std_radius', percentile=95):
    """
    Generic function to measure spread of (x, y) points.
    method:
      - 'std_radius': standard deviation of radius from (0,0) (default)
      - 'rms_radius': root mean square radius
      - 'percentile_radius': radius at given percentile (default 95)
    Returns: metric value (float)
    """
    import numpy as np
    if len(x) == 0:
        return float('nan')
    r = np.sqrt(np.array(x)**2 + np.array(y)**2)
    if method == 'std_radius':
        return float(np.std(r))
    elif method == 'rms_radius':
        return float(np.sqrt(np.mean(r**2)))
    elif method == 'percentile_radius':
        return float(np.percentile(r, percentile))
    return float('nan')

def create_chart_case_02(grid=False, spread_method='std_radius', percentile=95):
    """
    Create scatterplot(s) for XOffset vs YOffset from data/views/view_case_02.csv.
    Features:
    - For each run_id (columns), for each pallette_number (rows), plot all spot numbers in the same chart, colored by spot number.
    - Use a dynamically generated, maximally distinct color palette for each run's filtered set of spot numbers:
        - For up to 12 spots, assign a fixed, ordered set of high-contrast colors (black, yellow, red, cyan, blue, lime, magenta, orange, green, pink, purple, brown) for maximum mutual contrast.
        - For more than 12, generate vivid HSV colors.
    - The color mapping is consistent for all charts and the legend within the report.
    - Add a color legend at the top of the report, showing the color assigned to each spot number.
    - Apply filters from parameters.yaml (spot_numbers, run_id, pallette_number).
    - Keep axis centered and fixed at [-0.3, 0.3] for both X and Y axes for all charts.
    - Draw cross axes at (0,0) for all charts.
    - Draw a black solid circle at 2× the standard deviation of the radius (2σ) for each chart, and display the value in the chart title.
    - Draw a blue dotted circle at radius 0.2 to represent the tolerance area.
    - Display the average std radius for each run below the run title.
    - Add a global legend at the top explaining the 2σ circle (black solid), the tolerance circle (blue dotted), and their statistical meaning.
    - Output: HTML file in output/charts/ (grid or non-grid layout).
    """
    # Load data
    data_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'views', 'view_case_02.csv'))
    # print(f"[DEBUG] Loading data from {data_file}")
    df = pd.read_csv(data_file, dtype=str)
    # print(f"[DEBUG] Data loaded: {df.shape[0]} rows, columns: {list(df.columns)}")
    # print(f"[DEBUG] First 5 rows loaded:\n{df.head()}")
    df['XOffset'] = pd.to_numeric(df['XOffset'], errors='coerce')
    df['YOffset'] = pd.to_numeric(df['YOffset'], errors='coerce')
    if 'SpotNumber' in df.columns:
        df['SpotNumber'] = df['SpotNumber'].astype(str)
    else:
        df['SpotNumber'] = df['spot_number'].astype(str)
    df['run_id'] = df['run_id'].astype(str)
    df['pallette_number'] = df['pallette_number'].astype(str)

    # Remove outlier/placeholder values (e.g., 999.0)
    mask = (df['XOffset'] != 999.0) & (df['YOffset'] != 999.0)
    df = df[mask]
    # print(f"[DEBUG] After removing outliers (999.0): {df.shape[0]} rows")

    # Load color mapping and parameters
    spot_colors = load_spotnumber_colors()
    # print(f"[DEBUG] Loaded {len(spot_colors)} spot colors. Example: {list(spot_colors.items())[:5]}")
    params = load_parameters()
    # print(f"[DEBUG] Loaded parameters: {params}")
    spot_filter = set(str(s) for s in params.get('spot_numbers', [])) if params.get('spot_numbers') else None
    run_filter = set(str(r) for r in params.get('run_id', [])) if params.get('run_id') else None
    pallette_filter = set(str(p) for p in params.get('pallette_number', [])) if params.get('pallette_number') else None

    # Apply filters
    # print(f"[DEBUG] Data before filter: {df.shape[0]} rows")
    if spot_filter:
        df = df[df['SpotNumber'].isin(spot_filter)]
        # print(f"[DEBUG] After spot_number filter: {df.shape[0]} rows")
    if run_filter:
        df = df[df['run_id'].isin(run_filter)]
        # print(f"[DEBUG] After run_id filter: {df.shape[0]} rows")
    if pallette_filter:
        df = df[df['pallette_number'].isin(pallette_filter)]
        # print(f"[DEBUG] After pallette_number filter: {df.shape[0]} rows")

    # After filtering, get unique spot numbers
    unique_spots = sorted(df['SpotNumber'].unique(), key=lambda x: int(x))
    n_spots = len(unique_spots)
    import numpy as np
    import matplotlib.colors as mcolors
    import matplotlib.cm as cm
    # Hand-picked, ordered high-contrast colors for up to 12 spots (maximal mutual contrast)
    # Removed black since we'll use it for the high density circle
    high_contrast_colors = [
        '#FFD700',  # yellow
        '#FF0000',  # red
        '#00FFFF',  # cyan
        '#0000FF',  # blue
        '#00FF00',  # lime
        '#FF00FF',  # magenta
        '#FFA500',  # orange
        '#008000',  # green
        '#FFC0CB',  # pink
        '#800080',  # purple
        '#A52A2A',  # brown
        '#FF6347',  # tomato (added to replace black)
    ]
    if n_spots <= len(high_contrast_colors):
        color_list = high_contrast_colors[:n_spots]
        # Assign in order for maximum group contrast
        spot_colors = {spot: color for spot, color in zip(unique_spots, color_list)}
    else:
        # For more than 12, use HSV with high saturation and value for vividness
        color_indices = np.linspace(0, 1, n_spots, endpoint=False)
        np.random.shuffle(color_indices)
        spot_colors = {spot: mcolors.to_hex(mcolors.hsv_to_rgb([idx, 0.95, 0.95])) for spot, idx in zip(unique_spots, color_indices)}

    # Prepare output
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output', 'charts'))
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, 'case_02_grid.html' if grid else 'case_02.html')

    # Axis limits (centered, same for all)
    # x_min, x_max = df['XOffset'].min(), df['XOffset'].max()
    # y_min, y_max = df['YOffset'].min(), df['YOffset'].max()
    # print(f"[DEBUG] XOffset range: {x_min} to {x_max}, YOffset range: {y_min} to {y_max}")
    # x_c = (x_max + x_min) / 2
    # y_c = (y_max + y_min) / 2
    # x_range = max(abs(x_max - x_c), abs(x_min - x_c))
    # y_range = max(abs(y_max - y_c), abs(y_min - y_c))
    # axis_lim = max(x_range, y_range)
    # xlim = (x_c - axis_lim, x_c + axis_lim)
    # ylim = (y_c - axis_lim, y_c + axis_lim)
    xlim = (-0.3, 0.3)
    ylim = (-0.3, 0.3)
    # print(f"[DEBUG] Axis limits: xlim={xlim}, ylim={ylim}")

    # Grouping
    runs = sorted(df['run_id'].unique(), key=safe_int_sort_key)
    pallettes = sorted(df['pallette_number'].unique(), key=lambda x: int(x))
    spots = sorted(df['SpotNumber'].unique(), key=lambda x: int(x))
    # print(f"[DEBUG] Runs: {runs}")
    # print(f"[DEBUG] Pallettes: {pallettes}")
    # print(f"[DEBUG] Spots: {spots}")

    # Build HTML legend for all spot numbers/colors
    legend_html = '<div style="margin-bottom:10px;"><b>Spot Color Legend:</b><br>'
    for spot in spots:
        color = spot_colors.get(spot, '#000000')
        legend_html += f'<span style="display:inline-block;width:16px;height:16px;background:{color};margin-right:4px;"></span> {spot} '
    legend_html += '</div>'

    html = ['<html><head><title>Case 02 Charts</title></head><body>']
    # Add visual legend for circles
    html.append('<div style="margin-bottom:15px; padding:10px; background:#f9f9f9; border:1px solid #ddd;">')
    html.append('<div style="margin-bottom:5px;"><span style="display:inline-block; width:20px; height:3px; background:black; margin-right:8px; vertical-align:middle;"></span><b>Black circle:</b> Density area (86% of data points)</div>')
    html.append('<div><span style="display:inline-block; width:20px; height:2px; background:blue; border-top:2px dotted blue; margin-right:8px; vertical-align:middle;"></span><b>Blue dotted line:</b> Tolerance area</div>')
    html.append('</div>')
    html.append(legend_html)
    if grid:
        html.append('<h1>Case 02 Grid Layout</h1>')
        html.append('<table border="1" style="border-collapse:collapse;"><tr><th></th>')
        for run in runs:
            html.append(f'<th>Run {run}</th>')
        html.append('</tr>')
        for pallette in pallettes:
            html.append(f'<tr><td>Pallette {pallette}</td>')
            for run in runs:
                subdf = df[(df['run_id'] == run) & (df['pallette_number'] == pallette)]
                # print(f"[DEBUG] Plotting grid: run {run}, pallette {pallette}, {subdf.shape[0]} points")
                fig, ax = plt.subplots(figsize=(2,2))
                for spot in spots:
                    spotdf = subdf[subdf['SpotNumber'] == spot]
                    if not spotdf.empty:
                        ax.scatter(spotdf['XOffset'], spotdf['YOffset'], color=spot_colors.get(spot, '#000000'), s=1)
                ax.set_xlim(xlim)
                ax.set_ylim(ylim)
                ax.set_title("")
                # ax.set_xlabel('XOffset')
                # ax.set_ylabel('YOffset')
                ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.8)
                ax.axvline(x=0, color='gray', linestyle='--', linewidth=0.8)
                ax.set_aspect('equal')
                plt.tight_layout()
                buf = BytesIO()
                plt.savefig(buf, format='png')
                plt.close(fig)
                img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                html.append(f'<td><img src="data:image/png;base64,{img_b64}"/></td>')
            html.append('</tr>')
        html.append('</table>')
    else:
        html.append('<h1>Case 02</h1>')
        for run in runs:
            run_html = []
            run_html.append(f'<h2>Run {run}</h2>')
            pallette_std_radii = {}
            run_spread_values = []  # Collect all spread values for this run
            for pallette in pallettes:
                subdf = df[(df['run_id'] == run) & (df['pallette_number'] == pallette)]
                if subdf.empty:
                    continue
                fig, ax = plt.subplots(figsize=(3,3))
                all_radii = []
                for spot in spots:
                    spotdf = subdf[subdf['SpotNumber'] == spot]
                    if not spotdf.empty:
                        ax.scatter(spotdf['XOffset'], spotdf['YOffset'], color=spot_colors.get(spot, '#000000'), s=1)
                        radii = (spotdf['XOffset']**2 + spotdf['YOffset']**2)**0.5
                        all_radii.extend(radii.tolist())
                # Use measure_spread for this pallette/run (std_radius)
                spread_value = measure_spread(subdf['XOffset'], subdf['YOffset'], method=spread_method, percentile=percentile)
                circle_radius = 2 * spread_value
                pallette_std_radii[pallette] = pallette_std_radii.get(pallette, []) + [spread_value]
                run_spread_values.append(spread_value)  # Add to run's list
                if not subdf.empty:
                    from matplotlib.patches import Circle as MplCircle
                    # Draw tolerance circle at radius 0.2 (blue dotted)
                    tolerance_circle = plt.Circle((0, 0), 0.2, color='blue', fill=False, linestyle=':', linewidth=1.2, alpha=0.7)
                    ax.add_patch(tolerance_circle)
                    # Draw black solid line for high density circle (on top)
                    circle = plt.Circle((0, 0), circle_radius, color='black', fill=False, linestyle='-', linewidth=3, alpha=1.0)
                    ax.add_patch(circle)
                    metric_text = f"Std Radius: {spread_value:.4f} (2σ circle)"
                else:
                    metric_text = "No data"
                ax.set_xlim(xlim)
                ax.set_ylim(ylim)
                ax.set_title(f'Pallette {pallette}\n{metric_text}')
                # ax.set_xlabel('XOffset')
                # ax.set_ylabel('YOffset')
                ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.8)
                ax.axvline(x=0, color='gray', linestyle='--', linewidth=0.8)
                ax.set_aspect('equal')
                plt.tight_layout(pad=0.1)
                buf = BytesIO()
                plt.savefig(buf, format='png')
                plt.close(fig)
                img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                run_html.append(f'<div style="display:inline-block;margin:5px;"><img src="data:image/png;base64,{img_b64}"/></div>')
            # After all pallettes for this run, show average spread value for the run right below the run title
            if run_spread_values:
                avg_spread = sum(run_spread_values) / len(run_spread_values)
                method_label = spread_method.replace('_', ' ')
                run_html.insert(1, f'<div><b>Run {run} average {method_label}: {avg_spread:.4f}</b></div>')
            run_html.append('<hr/>')
            html.extend(run_html)
    html.append('</body></html>')
    # print(f"[DEBUG] Saving HTML to {out_file}")
    with open(out_file, 'w') as f:
        f.write('\n'.join(html))
    print(f"Charts saved to {out_file}")

def create_chart_case_03(grid=False, spread_method='std_radius', percentile=95):
    """
    Create scatterplot(s) for XOffset vs YOffset from data/views/view_case_03.csv.
    Features:
    - For each run_id (columns), for each pallette_number (rows), plot all row numbers in the same chart, colored by row number.
    - Use a dynamically generated, maximally distinct color palette for each run's filtered set of row numbers:
        - For up to 12 row numbers, assign a fixed, ordered set of high-contrast colors (black, yellow, red, cyan, blue, lime, magenta, orange, green, pink, purple, brown) for maximum mutual contrast.
        - For more than 12, generate vivid HSV colors.
        - The color mapping is consistent for all charts and the legend within the report.
        - Add a color legend at the top of the report, showing the color assigned to each row number.
        - Apply filters from parameters.yaml (row_number, run_id, cassette_number and spot_number).
        - Keep axis centered and fixed at [-0.3, 0.3] for both X and Y axes for all charts.
        - Draw cross axes at (0,0) for all charts.
        - Draw a black solid circle at 2× the standard deviation of the radius (2σ) for each chart, and display the value in the chart title.
        - Draw a blue dotted circle at radius 0.2 to represent the tolerance area.
        - Display the average std radius for each run below the run title.
        - Add a global legend at the top explaining the 2σ circle (black solid), the tolerance circle (blue dotted), and their statistical meaning.
        - Output: HTML file in output/charts/ (grid or non-grid layout).

        """
    
    # Load data
    data_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'views', 'view_case_03.csv')) # Adjusted for case_03.csv
    df = pd.read_csv(data_file, dtype=str)
    df['XOffset'] = pd.to_numeric(df['XOffset'], errors='coerce')
    df['YOffset'] = pd.to_numeric(df['YOffset'], errors='coerce')

    # Ensure 'SpotNumber' column exists
    if 'SpotNumber' in df.columns:
        df['SpotNumber'] = df['SpotNumber'].astype(str)
    else:
        df['SpotNumber'] = df['spot_number'].astype(str)
    df['run_id'] = df['run_id'].astype(str)
    df['pallette_number'] = df['pallette_number'].astype(str)

    # Remove outlier/placeholder values (e.g., 999.0)
    mask = (df['XOffset'] != 999.0) & (df['YOffset'] != 999.0)
    df = df[mask]

    # Load color mapping and parameters
    spot_colors = load_spotnumber_colors()

    # Load parameters
    params = load_parameters()

    # Setup filters from parameters.yaml
    spot_filter = set(str(s) for s in params.get('spot_numbers', [])) if params.get('spot_numbers') else None # Adjusted to 'spot_numbers'
    run_filter = set(str(r) for r in params.get('run_id', [])) if params.get('run_id') else None # Adjusted to 'run_id'
    row_filter = set(str(r) for r in params.get('row_numbers', [])) if params.get('row_numbers') else None # New filter for 'row_numbers'
    cassette_filter = set(str(c) for c in params.get('cassette_numbers', [])) if params.get('cassette_numbers') else None # New filter for 'cassette_numbers'

    # print(f"[DEBUG] Before filtering: {df.shape[0]} rows")

    # Apply filters and build filter summary
    filter_parts = []
    if spot_filter:
        df = df[df['SpotNumber'].isin(spot_filter)]
        filter_parts.append(f"Spot = [{', '.join(sorted(spot_filter))}]")
    if run_filter:
        df = df[df['run_id'].isin(run_filter)]
        filter_parts.append(f"Run = [{', '.join(sorted(run_filter))}]")
    if row_filter and 'RowNumber' in df.columns:
        df = df[df['RowNumber'].astype(str).isin(row_filter)]
        filter_parts.append(f"Row = [{', '.join(sorted(row_filter))}]")
    if cassette_filter and 'cassette_number' in df.columns:
        df = df[df['cassette_number'].astype(str).isin(cassette_filter)]
        filter_parts.append(f"Cassette = [{', '.join(sorted(cassette_filter))}]")
    if filter_parts:
        filter_summary_html = f'<div style="margin-bottom:10px; font-weight:bold;">Filters applied: {"; ".join(filter_parts)}</div>'
    else:
        filter_summary_html = ''    

       
    # print(f"[DEBUG] After filtering: {df.shape[0]} rows")
    # print(f"[DEBUG] First 5 rows after filtering:\n{df.head()}")

    # After filtering, get unique row numbers to create color mapping
    unique_rows = sorted(df['RowNumber'].unique(), key=lambda x: int(x))
    n_rows = len(unique_rows)
    unique_row_numbers = df['RowNumber'].unique() if 'RowNumber' in df.columns else []
    # print(f"[DEBUG] Unique row numbers after filtering: {unique_row_numbers}")

    # Generate color mapping for row numbers
    high_contrast_colors = [
        '#0000FF',  # blue        
        '#FF0000',  # red
        '#00FFFF',  # cyan
        '#FFD700',  # yellow
        '#00FF00',  # lime
        '#FF00FF',  # magenta
        '#FFA500',  # orange
        '#008000',  # green
        '#FFC0CB',  # pink
        '#800080',  # purple
        '#A52A2A',  # brown
        '#FF6347',  # tomato (added to replace black)
    ]

    if n_rows <= len(high_contrast_colors):
        color_list = high_contrast_colors[:n_rows]
        # Assign in order for maximum group contrast
        row_colors = {row: color for row, color in zip(unique_rows, color_list)} 
    else:                
        color_indices = np.linspace(0, 1, n_rows, endpoint=False)
        np.random.shuffle(color_indices)
        row_colors = {row: mcolors.to_hex(mcolors.hsv_to_rgb([idx, 0.95, 0.95])) for row, idx in zip(unique_rows, color_indices)}

    # Prepare output
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output', 'charts'))
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, 'case_03_grid.html' if grid else 'case_03.html')

    #set axis limits (centered, same for all)
    xlim = (-0.3, 0.3)
    ylim = (-0.3, 0.3)  

    # Grouping
    runs = sorted(df['run_id'].unique(), key=safe_int_sort_key) # New line to flag runs with letters
    pallettes = sorted(df['pallette_number'].unique(), key=lambda x: int(x)) # New line to flag pallettes with letters
    rows = sorted(df['RowNumber'].unique(), key=lambda x: int(x)) if 'RowNumber' in df.columns else [] # New line to flag rows with letters     

    # Build HTML legend for all row numbers/colors
    legend_html = '<div style="margin-bottom:10px;"><b>Row Color Legend:</b><br>'
    for row in unique_rows:
        color = row_colors.get(row, '#000000') 
        legend_html += f'<span style="display:inline-block;width:16px;height:16px;background:{color};margin-right:4px;"></span> {row} '
    legend_html += '</div>'
    html = ['<html><head><title>Case 03 Charts</title></head><body>']
    
    # Add visual legend for circles
    html.append('<div style="margin-bottom:15px; padding:10px; background:#f9f9f9; border:1px solid #ddd;">')
    html.append('<div style="margin-bottom:5px;"><span style="display:inline-block; width:20px; height:3px; background:black; margin-right:8px; vertical-align:middle;"></span><b>Black circle:</b> Density area (86% of data points)</div>')
    html.append('<div><span style="display:inline-block; width:20px; height:2px; background:blue; border-top:2px dotted blue; margin-right:8px; vertical-align:middle;"></span><b>Blue dotted line:</b> Tolerance area</div>')
    html.append('</div>')
    html.append(legend_html)    

    # Insert filter summary at the top (after <body> and before legends)
    if filter_summary_html:
        html.insert(1, filter_summary_html) # Insert after <body> tag

    if grid:
        html.append('<h1>Case 03 Grid Layout</h1>')
        html.append('<table border="1" style="border-collapse:collapse;"><tr><th></th>')
        for run in runs:
            html.append(f'<th>Run {run}</th>')
        html.append('</tr>')
        for pallette in pallettes:
            html.append(f'<tr><td>Pallette {pallette}</td>')
            for run in runs:
                subdf = df[(df['run_id'] == run) & (df['pallette_number'] == pallette)]
                fig, ax = plt.subplots(figsize=(2,2))
                for row in rows:
                    rowdf = subdf[subdf['RowNumber'] == row] if 'RowNumber' in subdf.columns else pd.DataFrame()
                    if not rowdf.empty:
                        ax.scatter(rowdf['XOffset'], rowdf['YOffset'], color=row_colors.get(row, '#000000'), s=1)
                ax.set_xlim(xlim)
                ax.set_ylim(ylim)
                ax.set_title("")
                ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.8)
                ax.axvline(x=0, color='gray', linestyle='--', linewidth=0.8)
                ax.set_aspect('equal')
                plt.tight_layout()
                buf = BytesIO()
                plt.savefig(buf, format='png')
                plt.close(fig)
                img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                html.append(f'<td><img src="data:image/png;base64,{img_b64}"/></td>')
            html.append('</tr>')
        html.append('</table>')
    else: 
        html.append('<h1>Case 03</h1>')
        for run in runs:
            run_html = []
            run_html.append(f'<h2>Run {run}</h2>')
            pallette_std_radii = {}
            run_spread_values = []  # Collect all spread values for this run
            for pallette in pallettes:
                subdf = df[(df['run_id'] == run) & (df['pallette_number'] == pallette)]
                
                # Count data points for each row (including zero)
                row_counts = {}
                for row in rows:
                    if 'RowNumber' in subdf.columns:
                        count = subdf[subdf['RowNumber'] == row].shape[0]
                    else:
                        count = 0
                    row_counts[row] = count
                # Build summary string
                count_summary = ', '.join([f'Row {row}: {row_counts[row]}' for row in rows])                
                
                if subdf.empty:
                    continue                    
                fig, ax = plt.subplots(figsize=(3,3))
                all_radii = []
                for row in rows:
                    rowdf = subdf[subdf['RowNumber'] == row] if 'RowNumber' in subdf.columns else pd.DataFrame()
                    if not rowdf.empty:
                        ax.scatter(rowdf['XOffset'], rowdf['YOffset'], color=row_colors.get(row, '#000000'), s=1)
                        radii = (rowdf['XOffset']**2 + rowdf['YOffset']**2)**0.5
                        all_radii.extend(radii.tolist())
                # Use measure_spread for this pallette/run (std_radius)
                spread_value = measure_spread(subdf['XOffset'], subdf['YOffset'], method=spread_method, percentile=percentile)
                circle_radius = 2 * spread_value
                pallette_std_radii[pallette] = pallette_std_radii.get(pallette, []) + [spread_value]
                run_spread_values.append(spread_value)  # Add to run's list
                if not subdf.empty:                    
                    # Draw tolerance circle at radius 0.2 (blue dotted)
                    tolerance_circle = plt.Circle((0, 0), 0.2, color='blue', fill=False, linestyle=':', linewidth=1.2, alpha=0.7)
                    ax.add_patch(tolerance_circle)
                    # Draw black solid line for high density circle (on top)
                    circle = plt.Circle((0, 0), circle_radius, color='black', fill=False, linestyle='-', linewidth=3, alpha=1.0)
                    ax.add_patch(circle)
                    metric_text = f"Std Radius: {spread_value:.4f} (2σ circle)"
                else:
                    metric_text = "No data"

                # Build count summary string for plot title
                count_summary = ', '.join([f'Row {row}: {row_counts[row]}' for row in rows])                
                
                ax.set_title(f'Pallette {pallette}\n{metric_text}\nData point count (Row): {count_summary}')
                ax.set_xlim(xlim)
                ax.set_ylim(ylim)
                ax.set_title(f'Pallette {pallette}\n{metric_text}\nData point count: \n{count_summary}')
                ax.axhline(y=0, color='gray', linestyle='--', linewidth=0.8)
                ax.axvline(x=0, color='gray', linestyle='--', linewidth=0.8)
                ax.set_aspect('equal')
                plt.tight_layout(pad=0.1)
                buf = BytesIO()
                plt.savefig(buf, format='png')
                plt.close(fig)
                img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                run_html.append(f'<div style="display:inline-block;margin:5px;"><img src="data:image/png;base64,{img_b64}"/></div>')
            # After all pallettes for this run, show average spread value for the run right below the run title
            if run_spread_values:
                avg_spread = sum(run_spread_values) / len(run_spread_values)
                method_label = spread_method.replace('_', ' ')
                run_html.insert(1, f'<div><b>Run {run} average {method_label}: {avg_spread:.4f}</b></div>')
            run_html.append('<hr/>')
            html.extend(run_html)
    html.append('</body></html>')
    with open(out_file, 'w') as f:
        f.write('\n'.join(html))
    print(f"Charts saved to {out_file}")    

               
            


def main():
    # Generate spotnumber color mapping if needed
    # if not os.path.exists(os.path.join(os.path.dirname(__file__), 'spotnumber_colors.csv')):
    #     generate_spotnumber_colors()
    create_chart_case_01()
    create_chart_case_02()
    create_chart_case_03()


if __name__ == "__main__":
    main()
