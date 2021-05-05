"""clear_caches.py.

Perform various cleanup operations on a project directory, such as deleting
files and directories, as well as resetting notebooks.

Last update: 2021-02-06
"""

# Python imports
import glob
import os
import shutil
import subprocess
import sys
from IPython.display import display, HTML
from pathlib import Path

# Functions
def get_paths():
    """Get the project and project data directories."""
    project_dir = str(Path(os.getcwd()).parent.parent)
    project_datadir   = project_dir + '/project_data'
    return project_dir, project_datadir
    
    
def show_feedback(processed, errors, msg=None):
    """Display feedback."""
    if len(errors) == 0:
        if msg is not None:
            msg = msg.replace('{processed}', str(processed))
            display(HTML('<p style="color: green;">{0}</p>'.format(msg)))
        else:
            display(HTML('<p style="color: green;">Done!</p>'))
    else:
        num_errors = len(errors)
        display(HTML('<p style="color: red;">{0} items could not be processed:</p>'.format(num_errors)))
        error_list = '<ul>'
        for error in errors:
            error_list += '<li>' + error + '</li>'
        error_list += '</ul>'
        display(HTML(error_list))
        

def clear_folders(project_dir, folder_paths, delete_folders=False, show_feedback=True):
    """Clear specific folders from a list of folder paths with an option to delete the folders."""
    processed = 0
    errors = []
    if delete_folders:
        msg = '{processed} folders were deleted.'
    else:
        msg = '{processed} folders were emptied.'
    folder_paths = [os.path.join(project_dir, path) for path in folder_paths]
    for folder in folder_paths:
        try:
            shutil.rmtree(folder)
            if not delete_folders:
                os.makedirs(folder)
            processed += 1
        except IOError:
            errors.append(folder)
    if show_feedback:
        show_feedback(processed, errors, msg)
            
def clear_module(module_path, resource_paths):
    """Delete all files in a specific module folder that are not part of the templates."""
    deleted = 0
    errors = []
    for item in glob.glob(module_path + '/**'):
        if item in resource_paths:
            pass
        else:
            try:
                os.remove(item)
                deleted += 1
            except IOError:
                errors.append(item)
    return deleted, errors                

def clear_module_folders(project_dir, modules=None, clear_notebooks=True, show_feedback=True):
    """Delete all non-template files in the module folders.
    
    By default, all modules will be cleared, but a list of folders can be supplied.
    """
    if modules is not None and not isinstance(modules, list):
        error_msg = "Please supply the names of modules as a Python list (e.g. <code>['counting', 'topic_modeling']</code>."
        display(HTML('<p style="color:red;">' + error_msg + '</p>'))
    else:
        # If no module list is supplied, get a list of all modules
        if modules is None:
            modules = []
            for module in config.MODULES:
                module_name = list(module.keys())[0]
                modules.append(module_name)
        # Iterate through the modules
        log = {}
        for module in modules:
            # Get the module's path and resources
            deleted = 0
            errors = []
            module_path = os.path.join(project_dir + '/modules', module)
            module_resources = next((item for item in config.MODULES if list(item.keys())[0] == module), None)[module]
            resource_paths = [os.path.join(module_path, item) for item in module_resources]
            # Call clear_module() to clear the module's files
            deleted, errors = clear_module(module_path, resource_paths)
            log[module] = {'deleted': deleted, 'errors': errors, 'notebooks_cleared': 0}
            if show_feedback:
                msg = '{processed} files in "' + module + '" were deleted.'
                show_feedback(deleted, errors, msg)
            # If specified, clear the notebooks in the module
            if clear_notebooks:
                notebook_paths = [path for path in resource_paths if path.endswith('.ipynb')]
                notebooks_cleard = 0
                for notebook in notebook_paths:
                    if not notebook.endswith('modules/utilities/clear_caches.ipynb'):
                        subprocess.call('nbstripout ' + notebook, shell=True)
                        log[module]['notebooks_cleared'] += 1
        return log
                
def clear_notebooks(project_dir, notebook_paths):
    """Clear specific notebooks from a list of paths to notebook files."""
    notebook_paths = [os.path.join(project_dir, path) for path in notebook_paths]
    for notebook in notebook_paths:
        subprocess.call('nbstripout ' + notebook, shell=True)
        display(HTML('<p style="color: green"><code>' + notebook + '</code> reset.</p>'))

def clear_project_data(project_datadir, show_feedback=True):
    """Delete and recreate the project data folder."""
    try:
        shutil.rmtree(project_datadir)
        os.makedirs(project_datadir)
        msg = '<p style="color: green">Done!</p>'
        result = '<p style="color: green">The project data directory was deleted.</p>'
    except IOError:
        msg = '<p style="color: red">An unknown error occurred. Please check that the project data directory exists.</p>'
        result = '<p style="color: red">An unknown error occurred. The project data directory could not be deleted.</p>'
    if show_feedback:
        display(HTML(msg))
    else:
        return result
    
def delete_files(project_dir, file_paths):
    """Delete specific files from a list of file paths."""
    deleted = 0
    errors = []
    file_paths = [os.path.join(project_dir, path) for path in file_paths]
    for file in file_paths:
        try:
            os.remove(file)
            deleted += 1
        except IOError:
            errors.append(file)
    show_feedback(deleted, errors, '{processed} files were deleted.')
            
def clear_root_dir(project_dir, project_datadir):
    """Delete non-template files and directories in the root dir."""
    deleted = 0
    errors = []
    project_datadirname = project_datadir.split('/')[-1]
    exceptions = config.PROJECT_ROOT_FILES + ['__pycache__', 'config', 'modules', project_datadirname] + config.CONFIG_FILES
    file_paths = os.listdir(project_dir)
    file_paths = [path for path in file_paths if path not in exceptions]
    for file in file_paths:
        try:
            if os.path.isdir(os.path.join(project_dir, file)):
                shutil.rmtree(file)
            else:
                os.remove(os.path.join(project_dir, file))
            deleted += 1
        except IOError:
            errors.append(file)
    # Delete empty directories, except for the project_datadir
    empty_dirs = [x for x in os.listdir(project_dir) if os.path.isdir(x)]
    for dir in empty_dirs:
        if dir != project_datadir and dir != '.ipynb_checkpoints':
            shutil.rmtree(dir)
    show_feedback(deleted, errors, '{processed} files were deleted.')
    
def reset_project(project_dir, project_datadir):
    """Delete project and module data and reset notebooks."""
    try:
        result = clear_project_data(project_datadir, show_feedback=False)
        display(HTML('<h4 style="color: green; font-weight: strong;">' + result + '</h4>'))
        display(HTML('<h4 style="color: green; font-weight: strong;">Project Root Folder</h4>'))
        clear_root_dir(project_dir, project_datadir)
        display(HTML('<h4 style="color: green; font-weight: strong;">Checking Modules...</h4>'))
        log = clear_module_folders(project_dir, show_feedback=False)
        for module, entries in log.items():
            display(HTML('<h4 style="color: green; font-weight: strong;">Module: ' + module + '</h4>'))
            display(HTML('<p style="color: green;">' + str(entries['deleted']) + ' files deleted.</p>'))
            if len(entries['errors']) > 0:
                display(HTML('<p style="color: red">Errors:</p><ul>'))
                for error in entries['errors']:
                   display(HTML('<li style="color: red">' + error + '</li>'))
                display(HTML('</ul>'))
            if (entries['notebooks_cleared']) > 0:
                display(HTML('<p style="color: green">' + str(entries['notebooks_cleared']) + ' notebooks cleared.</p>'))
        display(HTML('<h4 style="color: green">Done!</h4>'))
    except RuntimeError:
        display(HTML('<p style="color: red">An unknown error occurred. Please check your settings.</p>'))

# Define paths
project_dir, project_datadir = get_paths()

# Import config
sys.path.insert(0, project_dir)
from config import config
