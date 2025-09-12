def chart_substrate_by_spotnumber():
    """
    This function generates a scatter plot chart comparing the X and Y offsets of a substrate barcode across different spot numbers.
    It uses the parameters defined in the parameters.yaml file to filter the data and create the chart. 
    The chart is saved as HTML page in the output folder.
    This file should contain one chart per substrate barcode, with the X and Y offsets plotted against each other for each spot number.
    """
    import pandas as pd
    import yaml
    import os
    import random
    import plotly.express as px

    # Load parameters from the YAML file
    with open('parameters.yaml', 'r') as file:
        params = yaml.safe_load(file)

    # Read the view data file
    view_file_path = os.path.join('..', 'data', 'views', 'view_data.csv')
    df = pd.read_csv(view_file_path, dtype={'run_id': str})

    # Inclusion filters
    if 'spot_numbers' in params and params['spot_numbers']:
        df = df[df['SpotNumber'].isin(params['spot_numbers'])]
    if 'run_id' in params and params['run_id']:
        run_ids = [str(r).zfill(3) for r in params['run_id']]
        df = df[df['run_id'].isin(run_ids)]
    # Exclusion filters
    if 'filter_out' in params and params['filter_out']:
        for filt in params['filter_out']:
            for col, val in filt.items():
                df = df[df[col] != val]
    if df.empty:
        print('Warning: Filtered DataFrame is empty! No data to plot.')

    spot_numbers = params['spot_numbers']
    def random_color():
        return '#{:06x}'.format(random.randint(0, 0xFFFFFF))
    color_map = {str(spot): random_color() for spot in spot_numbers}

    # Ensure SpotNumber is string for mapping
    df['SpotNumber'] = df['SpotNumber'].astype(str)

    # Helper to generate a scatter plot for a given substrate barcode
    def make_scatter(sub_barcode, filtered_df, color_map, include_plotlyjs):
        fig = px.scatter(
            filtered_df,
            x='XOffset',
            y='YOffset',
            color='SpotNumber',
            color_discrete_map=color_map,
            title=f"Substrate Barcode: {sub_barcode} - Spot Numbers: {params['spot_numbers']}",
            labels={'XOffset': 'X Offset', 'YOffset': 'Y Offset', 'SpotNumber': 'Spot Number'}
        )
        return fig.to_html(full_html=False, include_plotlyjs=include_plotlyjs)

    # If substrate_barcode is not in params, plot for each substrate
    all_substrates = df['TaskName2'].dropna().unique()
    html_parts = []
    for i, sub_barcode in enumerate(all_substrates):
        sub_df = df[df['TaskName2'] == sub_barcode]
        if sub_df.empty:
            continue
        color_map = {str(spot): '#{:06x}'.format(random.randint(0, 0xFFFFFF)) for spot in params['spot_numbers']}
        html = make_scatter(sub_barcode, sub_df, color_map, include_plotlyjs=(i==0))
        html_parts.append(html)
    # Save all charts in one HTML file
    output_file_path = os.path.join('..', 'output', 'charts', 'all_substrate_charts.html')
    with open(output_file_path, 'w') as f:
        f.write('<html><head><script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script></head><body>')
        for part in html_parts:
            f.write(part)
        f.write('</body></html>')
    print(f"All substrate charts saved to {output_file_path}")


    """
    For each run_id, then for each pallette (cassette_code), generate a scatterplot (XOffset vs YOffset).
    Each spot number is colored randomly and a legend is shown. All charts are saved in a single HTML file.
    Applies filters from parameters.yaml.
    """
    

   

    """
    Minimal example using Matplotlib: For the first run_id and first spot number, plot a scatterplot of XOffset vs YOffset.
    Save the output as a PNG and also embed it in a simple HTML file.
    """
    import pandas as pd
    import os
    import yaml
    import matplotlib.pyplot as plt
    import base64
    from io import BytesIO

    # Read the view data file (absolute path for robustness)
    view_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'views', 'view_data.csv'))
    df = pd.read_csv(view_file_path)

    # Load parameters.yaml (absolute path)
    param_path = os.path.join(os.path.dirname(__file__), 'parameters.yaml')
    with open(param_path, 'r') as file:
        params = yaml.safe_load(file)

    # Ensure run_id is string and zero-padded
    df['run_id'] = df['run_id'].astype(str).str.zfill(3)
    df['SpotNumber'] = pd.to_numeric(df['SpotNumber'], errors='coerce').astype('Int64')

    # Apply spot number filter
    if 'spot_numbers' in params and params['spot_numbers']:
        spot_numbers = [int(s) for s in params['spot_numbers']]
        df = df[df['SpotNumber'].isin(spot_numbers)]
    else:
        spot_numbers = sorted(df['SpotNumber'].dropna().unique())

    # Apply run_id filter
    if 'run_id' in params and params['run_id']:
        run_ids = [str(r).zfill(3) for r in params['run_id']]
        df = df[df['run_id'].isin(run_ids)]
    else:
        run_ids = df['run_id'].unique()

    # Minimal: only first run_id and first spot number
    if len(run_ids) > 0 and len(spot_numbers) > 0:
        run_id = run_ids[0]
        spot = spot_numbers[0]
        run_df = df[df['run_id'] == run_id]
        spot_df = run_df[run_df['SpotNumber'] == spot]
        print(f'run_id: {run_id}, spot: {spot}, spot_df length: {len(spot_df)}')
        # Ensure XOffset and YOffset are numeric
        spot_df['XOffset'] = pd.to_numeric(spot_df['XOffset'], errors='coerce')
        spot_df['YOffset'] = pd.to_numeric(spot_df['YOffset'], errors='coerce')
        spot_df = spot_df.dropna(subset=['XOffset', 'YOffset'])
        # Plot with matplotlib
        plt.figure(figsize=(8, 6))
        plt.scatter(spot_df['XOffset'], spot_df['YOffset'], alpha=0.6)
        plt.title(f'Run ID: {run_id} - Spot Number: {spot} - XOffset vs YOffset')
        plt.xlabel('XOffset')
        plt.ylabel('YOffset')
        plt.grid(True)
        # Save as PNG
        png_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output', 'charts', 'debug_minimal_matplotlib.png'))
        plt.savefig(png_path)
        print(f"Matplotlib PNG saved to {png_path}")
        # Save as HTML with embedded image
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        html_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output', 'charts', 'debug_minimal_matplotlib.html'))
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(f'<html><body><h2>Run ID: {run_id} - Spot Number: {spot} - XOffset vs YOffset</h2>')
            f.write(f'<img src="data:image/png;base64,{img_base64}"/></body></html>')
        print(f"Matplotlib HTML with embedded image saved to {html_path}")
        plt.close()

def chart_spot_scatter_by_runid_matplotlib():
    """
    For each run_id and each spot number, plot a scatterplot of XOffset vs YOffset using Matplotlib.
    Use parameters.yaml for filtering. Save all charts in a single HTML file in the charts folder, with headings for each chart.
    Warnings are suppressed by using low_memory=False and .copy() for DataFrame slices.
    """
    import pandas as pd
    import os
    import yaml
    import matplotlib.pyplot as plt
    import base64
    from io import BytesIO

    # Read the view data file (absolute path for robustness)
    view_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'views', 'view_data.csv'))
    df = pd.read_csv(view_file_path, low_memory=False)

    # Load parameters.yaml (absolute path)
    param_path = os.path.join(os.path.dirname(__file__), 'parameters.yaml')
    with open(param_path, 'r') as file:
        params = yaml.safe_load(file)

    # Ensure run_id is string and zero-padded
    df['run_id'] = df['run_id'].astype(str).str.zfill(3)
    df['SpotNumber'] = pd.to_numeric(df['SpotNumber'], errors='coerce').astype('Int64')

    # Apply spot number filter
    if 'spot_numbers' in params and params['spot_numbers']:
        spot_numbers = [int(s) for s in params['spot_numbers']]
        df = df[df['SpotNumber'].isin(spot_numbers)]
    else:
        spot_numbers = sorted(df['SpotNumber'].dropna().unique())

    # Apply run_id filter
    if 'run_id' in params and params['run_id']:
        run_ids = [str(r).zfill(3) for r in params['run_id']]
        df = df[df['run_id'].isin(run_ids)]
    else:
        run_ids = df['run_id'].unique()

    html_parts = []
    for run_id in run_ids:
        run_df = df[df['run_id'] == run_id]
        for spot in spot_numbers:
            spot_df = run_df[run_df['SpotNumber'] == spot].copy()
            # Ensure XOffset and YOffset are numeric
            spot_df['XOffset'] = pd.to_numeric(spot_df['XOffset'], errors='coerce')
            spot_df['YOffset'] = pd.to_numeric(spot_df['YOffset'], errors='coerce')
            spot_df = spot_df.dropna(subset=['XOffset', 'YOffset'])
            if len(spot_df) == 0:
                continue
            plt.figure(figsize=(8, 6))
            plt.scatter(spot_df['XOffset'], spot_df['YOffset'], alpha=0.6)
            plt.title(f'Run ID: {run_id} - Spot Number: {spot} - XOffset vs YOffset')
            plt.xlabel('XOffset')
            plt.ylabel('YOffset')
            plt.grid(True)
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            html_parts.append(f'<h3>Run ID: {run_id} - Spot Number: {spot}</h3>')
            html_parts.append(f'<img src="data:image/png;base64,{img_base64}"/><br>')

    stitched_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output', 'charts', 'matplotlib_grouped_by_runid_spot.html'))
    with open(stitched_path, 'w', encoding='utf-8') as f:
        f.write('<html><body>')
        for part in html_parts:
            f.write(part)
        f.write('</body></html>')
    print(f"All grouped Matplotlib charts saved to {stitched_path}")

def chart_substrate_by_spotnumber_matplotlib():
    """
    This function generates a scatter plot chart comparing the X and Y offsets of a substrate barcode across different spot numbers using Matplotlib.
    It uses the parameters defined in the parameters.yaml file to filter the data and create the chart.
    The chart is saved as an HTML page in the output folder.
    This file should contain one chart per substrate barcode, with the X and Y offsets plotted against each other for each spot number.
    """
    import pandas as pd
    import yaml
    import os
    import matplotlib.pyplot as plt
    import base64
    from io import BytesIO

    # Load parameters from the YAML file
    param_path = os.path.join(os.path.dirname(__file__), 'parameters.yaml')
    with open(param_path, 'r') as file:
        params = yaml.safe_load(file)

    # Read the view data file
    view_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'views', 'view_data.csv'))
    df = pd.read_csv(view_file_path, low_memory=False)

    # Inclusion filters
    if 'spot_numbers' in params and params['spot_numbers']:
        df['SpotNumber'] = pd.to_numeric(df['SpotNumber'], errors='coerce').astype('Int64')
        spot_numbers = [int(s) for s in params['spot_numbers']]
        df = df[df['SpotNumber'].isin(spot_numbers)]
    else:
        spot_numbers = sorted(df['SpotNumber'].dropna().unique())
    if 'run_id' in params and params['run_id']:
        df['run_id'] = df['run_id'].astype(str).str.zfill(3)
        run_ids = [str(r).zfill(3) for r in params['run_id']]
        df = df[df['run_id'].isin(run_ids)]
    else:
        run_ids = df['run_id'].unique()
    # Exclusion filters
    if 'filter_out' in params and params['filter_out']:
        for filt in params['filter_out']:
            for col, val in filt.items():
                df = df[df[col] != val]
    if df.empty:
        print('Warning: Filtered DataFrame is empty! No data to plot.')
        return

    all_substrates = df['TaskName2'].dropna().unique()
    html_parts = []
    for sub_barcode in all_substrates:
        sub_df = df[df['TaskName2'] == sub_barcode].copy()
        if sub_df.empty:
            continue
        plt.figure(figsize=(8, 6))
        for spot in spot_numbers:
            spot_df = sub_df[sub_df['SpotNumber'] == spot]
            if spot_df.empty:
                continue
            plt.scatter(spot_df['XOffset'], spot_df['YOffset'], alpha=0.6, label=f'Spot {spot}')
        plt.title(f'Substrate Barcode: {sub_barcode} - Spot Numbers: {spot_numbers}')
        plt.xlabel('X Offset')
        plt.ylabel('Y Offset')
        plt.legend()
        plt.grid(True)
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        html_parts.append(f'<h3>Substrate Barcode: {sub_barcode}</h3>')
        html_parts.append(f'<img src="data:image/png;base64,{img_base64}"/><br>')
    output_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output', 'charts', 'all_substrate_charts_matplotlib.html'))
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write('<html><body>')
        for part in html_parts:
            f.write(part)
        f.write('</body></html>')
    print(f"All substrate charts (Matplotlib) saved to {output_file_path}")

def chart_substrate_by_pallette_matplotlib(grid: bool = False):
    """
    For each run_id, then for each pallette (cassette_code), generate a scatterplot (XOffset vs YOffset) using Matplotlib.
    Each spot number is colored randomly and a legend is shown. All charts are saved in a single HTML file.
    If grid=True, format as a table (run_ids as columns, cassette_codes as rows). If grid=False, display charts sequentially.
    Applies filters from parameters.yaml.
    """
    import pandas as pd
    import yaml
    import os
    import matplotlib.pyplot as plt
    import base64
    from io import BytesIO
    import random

    # Load parameters from the YAML file
    param_path = os.path.join(os.path.dirname(__file__), 'parameters.yaml')
    with open(param_path, 'r') as file:
        params = yaml.safe_load(file)

    # Read the view data file
    view_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'views', 'view_data.csv'))
    df = pd.read_csv(view_file_path, low_memory=False)

    # Inclusion filters
    if 'spot_numbers' in params and params['spot_numbers']:
        df['SpotNumber'] = pd.to_numeric(df['SpotNumber'], errors='coerce').astype('Int64')
        spot_numbers = [int(s) for s in params['spot_numbers']]
        df = df[df['SpotNumber'].isin(spot_numbers)]
    else:
        spot_numbers = sorted(df['SpotNumber'].dropna().unique())
    if 'run_id' in params and params['run_id']:
        df['run_id'] = df['run_id'].astype(str).str.zfill(3)
        run_ids = [str(r).zfill(3) for r in params['run_id']]
        df = df[df['run_id'].isin(run_ids)]
    else:
        run_ids = df['run_id'].unique()
    # Exclusion filters
    if 'filter_out' in params and params['filter_out']:
        for filt in params['filter_out']:
            for col, val in filt.items():
                df = df[df[col] != val]
    if df.empty:
        print('Warning: Filtered DataFrame is empty! No data to plot.')
        return

    cassette_codes = sorted(df['cassette_code'].dropna().unique())
    chart_dict = {(cassette, run_id): None for cassette in cassette_codes for run_id in run_ids}
    chart_list = []

    for run_id in run_ids:
        run_df = df[df['run_id'] == run_id]
        for cassette in cassette_codes:
            cassette_df = run_df[run_df['cassette_code'] == cassette].copy()
            if cassette_df.empty:
                continue
            plt.figure(figsize=(8, 6))
            color_map = {spot: f'#{random.randint(0, 0xFFFFFF):06x}' for spot in spot_numbers}
            for spot in spot_numbers:
                spot_df = cassette_df[cassette_df['SpotNumber'] == spot]
                if spot_df.empty:
                    continue
                plt.scatter(spot_df['XOffset'], spot_df['YOffset'], alpha=0.6, label=f'Spot {spot}', color=color_map[spot])
            plt.title(f'Run ID: {run_id} - Cassette: {cassette} - XOffset vs YOffset')
            plt.xlabel('X Offset')
            plt.ylabel('Y Offset')
            plt.legend()
            plt.grid(True)
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            chart_html = f'<img src="data:image/png;base64,{img_base64}" style="max-width:100%;height:auto;"/>'
            chart_dict[(cassette, run_id)] = chart_html
            chart_list.append((run_id, cassette, chart_html))

    output_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output', 'charts', 'all_pallette_charts_matplotlib.html'))
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write('<html><body>')
        if grid:
            f.write('<table border="1" style="border-collapse:collapse;text-align:center;">')
            f.write('<tr><th>Cassette \\ Run ID</th>')
            for run_id in run_ids:
                f.write(f'<th>{run_id}</th>')
            f.write('</tr>')
            for cassette in cassette_codes:
                f.write(f'<tr><td><b>{cassette}</b></td>')
                for run_id in run_ids:
                    chart_html = chart_dict.get((cassette, run_id))
                    if chart_html:
                        f.write(f'<td>{chart_html}</td>')
                    else:
                        f.write('<td></td>')
                f.write('</tr>')
            f.write('</table>')
        else:
            for run_id, cassette, chart_html in chart_list:
                f.write(f'<h3>Run ID: {run_id} - Cassette: {cassette}</h3>')
                f.write(chart_html)
                f.write('<br>')
        f.write('</body></html>')
    print(f"All pallette charts (Matplotlib) saved to {output_file_path}")

def ensure_data_files_exist():
    """
    Check if unified_data.csv and view_data.csv exist. If not, run processing.py to generate them.
    """
    import os
    import subprocess
    base_dir = os.path.dirname(__file__)
    unified_path = os.path.abspath(os.path.join(base_dir, '..', 'data', 'source_data', 'unified_data.csv'))
    view_path = os.path.abspath(os.path.join(base_dir, '..', 'data', 'views', 'view_data.csv'))
    missing = []
    if not os.path.exists(unified_path):
        missing.append('unified_data.csv')
    if not os.path.exists(view_path):
        missing.append('view_data.csv')
    if missing:
        print(f"Missing files: {', '.join(missing)}. Running processing.py to generate them...")
        script_path = os.path.abspath(os.path.join(base_dir, 'processing.py'))
        result = subprocess.run(['python3', script_path], capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
        if not os.path.exists(unified_path) or not os.path.exists(view_path):
            raise RuntimeError("Failed to generate required data files. Please check processing.py.")
    else:
        print("All required data files exist.")

# Minimal chart test for debugging
if __name__ == "__main__":
    ensure_data_files_exist()
    chart_substrate_by_spotnumber_matplotlib()
    chart_substrate_by_pallette_matplotlib()
    chart_spot_scatter_by_runid_matplotlib()
    print("Chart generation completed successfully.")
