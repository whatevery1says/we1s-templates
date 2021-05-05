"""create_topic_bubbles.py.

Creates files necessary to produce a topic bubbles visualization for exploring
topic models. Topic bubbles code, stored in this module in `tb_scripts`, was
written by WE1S researcher Sihwa Park. See https://github.com/sihwapark/topic-bubbles
for Park's original code and documentation. Topic bubbles also relies on data
files produced for Andrew Goldstone's dfrbrowser visualization. See
https://github.com/agoldst/dfr-browser for Goldstone's original code and
documentation. Also see https://agoldst.github.io/dfr-browser/ for a version
history of Goldstone's code. WE1S is using an older version of Goldstone's
code (v0.5.1), and we use his prepare_data.py Python script to prepare the
data files, NOT the R package. This script includes functions for preparing
WE1S data for use with Park's code and for creating topic bubbles visualizations.

For use with create_topic_bubbles.ipynb v 2.0.

Last update: 2021-02-18
"""

## Python imports
import os
import pathlib
import re
import csv
import json
import shutil
import subprocess
from subprocess import STDOUT
from IPython.display import display, HTML


def create_topicbubbles_dfrbrowser(selection, current_dir, dfrbrowser_dir,
                                   tb_scripts_dir):
    """Create topic bubbles from Dfr-Browser metadata files.

    Uses files created for already existing dfr-browser visualizations of
    selected models to create topic bubbles visualizations. Needs to be
    told which models to create visualizations for, to be pointed to the
    current directory (top level of the topic bubbles module, to be pointed
    to the dfr-browser directory in the module, and to be pointed to the topic
    bubbles script directory (all of these variables are configured in the
    notebook). Returns a list of the model subdirectories topic bubbles
    visualizations were created for (for use in the notebook for WE1S
    researchers). This script will delete existing topic bubbles visualization
    subdirectories you have created for selected models in this project.
    """
    # Generate visualizations for all models in the project
    if get_selection(selection) is None:
        subdir_list = []
        # For each dfrbrowser subdirectory in the dfrbrowser module, add the files
        # needed for topic bubbles from the `/data` to subdirectories in the
        # topic bubbles module.
        for subdir in os.listdir(dfrbrowser_dir):
            # check to make sure you're looking in the right place
            if subdir.startswith('topics'):
                # add subdirectory to a list
                subdir_list.append(subdir)
                # create the path
                subdir_path = dfrbrowser_dir + '/' + subdir
                # grab the topic number from subdir
                num = re.search(r'\d+', subdir).group()
                # get all of the files you need
                tb_path = current_dir + '/topics' + num
                tb_path_data = tb_path + '/data'
                sb_path_data = subdir_path + '/data'
                # check to see if topic bubbles subdirectory already exists
                existing = os.path.exists(tb_path)
                # if it exists, delete it
                if existing == True:
                    shutil.rmtree(tb_path)
                # copy files from topic bubbles script directory to new topic bubbles viz subdirectory
                shutil.copytree(tb_scripts_dir, tb_path)
                # copy files from dfr-browser viz subdirectories
                for item in os.listdir(sb_path_data):
                    item_path = sb_path_data + '/' + item
                    shutil.copy(item_path, tb_path_data)
    # Otherwise, add files only for selected models
    else:
        for subdir in selection:
            subdir_list = selection
            subdir_path = dfrbrowser_dir + '/' + subdir
            num = re.search(r'\d+', subdir).group()
            tb_path = current_dir + '/topics' + num
            tb_path_data = tb_path + '/data'
            sb_path_data = subdir_path + '/data'
            existing = os.path.exists(tb_path)
            if existing == True:
                shutil.rmtree(tb_path)
            shutil.copytree(tb_scripts_dir, tb_path)
            for item in os.listdir(sb_path_data):
                item_path = sb_path_data + '/' + item
                shutil.copy(item_path, tb_path_data)
    return subdir_list


def create_topic_bubbles(subdir_list, state_file_list, scaled_file_list,
                         current_dir, tb_scripts_dir, prepare_data_script,
                         browser_meta_file):
    """Create topic bubbles visualizations.

    This function creates topic bubble visualizations for all models
    selected via the `get_models()` function in the `create_dfrbrowser.py`
    script. It is configured to work with multiple models at once organized
    in the WE1S default format. Requires lists of model subdirectories,
    model state files, and model scaled files, as well as other variables
    configured via the `create_topic_bubbles.ipynb` notebook. Does not
    require a dfr-browser visualization of any model to already exist.
    After moving a lot of data around to various appropriate subfolders,
    it uses Andrew Goldstone's prepare_data.py script to create the
    necessary files for a dfr-browser visualization (NOTE: WE1S does not
    use Goldstone's dfrbrowser R package, because we wanted to keep
    everything in Python), which are also used in topic bubbles
    visualizations. This script will delete existing topic bubbles
    visualization subdirectories you have created for selected models
    in this project.
    """
    # Iterate through lists of model subdirectories, state files,
    # and scaled files created via the get_models() function (in
    # create_drbrowser.py script) function and create the appropriate
    # subdirectories for the topic bubbles visualizations within
    # the topic bubbles module.
    for subdir, state, scaled in zip(subdir_list, state_file_list, scaled_file_list):
        # grab number of topics
        num = re.search(r'\d+', subdir).group()
        # topic bubbles viz subdirectory
        tb_path = current_dir + '/topics' + num
        # check if it already exists
        existing = os.path.exists(tb_path)
        # if it does, delete it
        if existing == True:
            shutil.rmtree(tb_path)
        # copy scripts from the scripts directory to subdirectories for each model
        shutil.copytree(tb_scripts_dir, tb_path)
        # create paths to dfrbrowser data files needed for topic bubbles
        tb_data_dir = tb_path + '/data'
        tw = tb_data_dir + '/tw.json'
        dt = tb_data_dir +'/dt.json.zip'
        info = tb_data_dir + '/info.json'
        # Create dfrbrowser files needed for topic bubbles using Goldstone's
        # prepare_data.py script using check_output to preserve prepare_data.py
        # output.
        output = subprocess.check_output([prepare_data_script, 'convert-state', state, '--tw', tw, '--dt', dt],
                                         stderr=STDOUT,
                                         universal_newlines=True)
        print(output)
        output = subprocess.check_output([prepare_data_script, 'info-stub', '-o', info],
                                         stderr=STDOUT,
                                         universal_newlines=True)
        print(output)
        # copy model scaled file into data dir
        shutil.copy(scaled, tb_data_dir)
        # path to dfrbrowser metadata file
        meta_zip = tb_data_dir + '/meta.csv.zip'
        # see if if exists
        existing = os.path.exists
        # if it does, delete it
        if existing == True:
            os.remove(meta_zip)
        # copy to topic bubbles viz subdirectories
        shutil.copy(browser_meta_file, tb_data_dir)
        # zip up the metadata file
        try:
            shutil.make_archive(os.path.join(tb_data_dir, 'meta.csv'),
                                'zip', tb_data_dir,
                                'meta.csv')
        except OSError as err:
            display(HTML('<p style="color: red;">Error writing <code>meta.csv.zip</code>: ' + str(err) + '.</p>'))
    
def display_links(project_dir, item_list, WRITE_DIR, PORT):
    """Display links to visualisations."""
    out = '<h4>Your topic bubbles visualizations are now available at the following locations:</h4>'
    out += '<ul>'
    for item in item_list:
        num = re.search(r'\d+', item).group()
        index_path = project_dir.replace(WRITE_DIR, '') + '/modules/dfr_browser/' + item + '/index.html'
        if PORT != '' and PORT is not None:
            index_path = ':' + PORT + index_path
        javascript = 'event.srcElement.href = \'http://\' + window.location.hostname + \'' + index_path + '\';'
        link = '<a target="_blank" href="#" onfocus="' + javascript + '">Browser for ' + str(num) + ' topics</a>'
        out += '<li>' + link + '</li>'
    out += '</ul>'
    display(HTML(out))

def get_selection(selection):
    """Return a valid model selection."""
    if not isinstance(selection, str) and not isinstance(selection, list):
        raise TypeError('The selection setting must be a string or a list.')
    if isinstance(selection, str):
        if selection.lower() == 'all' or selection == '':
            selection = None
        elif selection.startswith('topics'):
            selection = [selection]
    return selection
        
