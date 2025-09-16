import subprocess
import logging
import os
from datetime import datetime
import subprocess
import logging
import os
from datetime import datetime

# Setup logging

log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'one_click_vas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

logger = logging.getLogger('one_click_vas')

logger.setLevel(logging.DEBUG)

# File handler (DEBUG level)
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Console handler (INFO level)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

def run_script(script_name):
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    logger.info(f'Running {script_name}...')
    logger.debug(f'Executing: python {script_path}')
    try:
        result = subprocess.run(['python', script_path], capture_output=True, text=True)
        logger.debug(f'STDOUT for {script_name}:\n{result.stdout}')
        logger.debug(f'STDERR for {script_name}:\n{result.stderr}')
        if result.returncode == 0:
            logger.info(f'{script_name} completed successfully.')
        else:
            logger.error(f'{script_name} failed with exit code {result.returncode}. See logs for details.')
    except Exception as e:
        logger.error(f'Error running {script_name}: {e}')

def main():
    logger.info('--- VAS One-Click Pipeline Started ---')
    run_script('processing.py')
    run_script('create_charts.py')
    logger.info('--- All tasks completed. Reports are up to date. ---')

if __name__ == '__main__':
    main()
