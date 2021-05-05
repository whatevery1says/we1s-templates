"""zip.py.

Zips a Diagnostics visualisation for export.

Last update: 2020-07-25
"""

# Python imports
import os
import shutil
import tempfile
from IPython.display import display, HTML

# Zip functions
def copy_assets(dirs, current_dir, temp_dir):
    """Copy the asset directories to the temporary directory."""
    for dir in dirs:
        shutil.copytree(os.path.join(current_dir, dir), os.path.join(temp_dir, dir))
        
def copy_html(files, current_dir, temp_dir):
    """Copy the html files to the temporary directory."""
    for file in files:
        shutil.copy(os.path.join(current_dir, file), os.path.join(temp_dir, file))
        
def zip():
    """Zip diagnostics visualisations to the current directory."""
    current_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as temp_dir:
        copy_html(['index.html', 'comparison.html'], current_dir, temp_dir)
        copy_assets(['css', 'js', 'webfonts', 'xml'], current_dir, temp_dir)
        shutil.make_archive(os.path.join(current_dir, 'diagnostics'), 'zip', temp_dir)
    display(HTML('<p style="color:green;">Done!</p>'))
