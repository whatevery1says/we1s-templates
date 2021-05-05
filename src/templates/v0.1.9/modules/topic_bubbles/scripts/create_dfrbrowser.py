"""create_dfrbrowser.py.

Creates files necessary to produce a dfr-browser visualization for exploring topic models. Dfr-browser code, stored in this module in `dfrb_scripts`, was written by Andrew Goldstone and adapted for WE1S use and data. See https://github.com/agoldst/dfr-browser for Goldstone's original code and documentation. Also see https://agoldst.github.io/dfr-browser/ for a version history of Goldstone's code. WE1S uses an older version of Goldstone's code (v0.5.1), and we use his prepare_data.py Python script to prepare the data files, NOT the R package. This script includes functions for preparing WE1S data for use with Goldstone's code and for creating dfr-browser visualizations.

For use with create_dfrbrowser.ipynb v 2.0.

Last update: 2021-02-18
"""

# Python imports
import csv
import os
import string
import unidecode
import json
import re
from pathlib import Path
import subprocess
from subprocess import STDOUT
import shutil
from IPython.display import display, HTML
from zipfile import ZipFile

def year_from_fpath(file):
    """Return the publication year of a document.

    Given a json filename (in WE1S format), return the publication year
    of the document using the document filename. For use when Lexis Nexis
    does not provide publication date information. Function depends on
    WE1S file format. Stamps files with obviously incorrect publication
    year of 1900 if all else fails.
    """
    # If the filename begins with a digit, grab the relevant publication year.
    # Otherwise, assign it a dummy date.
    year = ''
    if re.match(r'^\d', file):
        try:
            match = re.search(r'_(\d\d\d\d)-\d\d-\d\d', file)
            year = match.group(1)
        except AttributeError:
            year = '1900'
    # If the filename begins with `we1schomp` or `chomp`, grab the pub year.
    # Otherwise, assign it a dummy date.
    if re.match('^we1schomp_', file) or re.match('^chomp_', file):
        try:
            match = re.search(r'_(\d\d\d\d)\d\d\d\d_', file)
            year = match.group(1)
        except AttributeError:
            year = '1900'
    if year == '':
        year = '1900'
    return year

def dfrb_metadata(metadata_dir, metadata_csv_file, browser_meta_file_temp,
                  browser_meta_file, json_dir):
    """Produce dfr-browser metadata csvs.

    Takes directory of json files as input. Produces three different versions
    of dfr-browser metadata csvs. This function will delete existing metadata
    folder (`project_data/metadata`) if it exists and create a new metadata
    folder. Otherwise, it will just create a metadata folder in `project_data`.
    If you do not want to delete your metadata directory every time you run
    this code and your metadata folder already exists, comment out lines 76-80.
    """
    # MAP FIELDS FROM JSON TO DFRB METADATA
    # id, publication, pubdate, title, articlebody, author, docUrl, wordcount
    # idx       ->  id
    # title     ->  title
    #           ->  author
    # pub       ->  publication
    #           ->  docUrl
    # length    ->  wordcount
    # pub_date  ->  pubdate
    # content   ->  articlebody
    existing = os.path.exists(metadata_dir)
    if existing == True:
        shutil.rmtree(metadata_dir)
        os.makedirs(metadata_dir)
    else:
        os.makedirs(metadata_dir)
    csv.field_size_limit(100000000)
    # Original column order
    # 'id', 'publication', 'pubdate', 'title', 'articlebody', 'pagerange', 'author', 'docUrl', 'wordcount'
    # New column order
    # 'id', 'title', 'author', 'publication', 'docUrl', 'wordcount', 'pubdate', 'pagerange'
    with open(metadata_csv_file, 'w') as csvfile:
        row = ['id'] + ['title'] + ['author'] + ['journaltitle'] + ['volume'] + ['issue'] + ['pubdate'] + ['pagerange']
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(row)
        sorted_json = sorted(f for f in os.listdir(json_dir) if f.endswith('.json'))
        idx=0
        for filename in sorted_json:
            # log: preview the first and last files only to prevent log overflow
            if(idx < 5 or idx > len(sorted_json) - 5):
                print(idx, ':', filename, '\n')
            if(idx == 5 and len(sorted_json) > 10):
                print('...\n')
            with open(os.path.join(json_dir, filename)) as f:
                oe = False
                try:
                    j = json.loads(f.read())
                except:
                    oe = True
                    print(filename + ' could not be loaded.')
                if not 'pagerange' in j:
                    j['pagerange'] = 'no-pg'
                if not 'author' in j:
                    j['author'] = 'unknown'
                if not 'volume'in j:
                    j['volume'] = 'no-vol'
                if not 'issue' in j:
                    j['issue'] = 'no-issue'
                if not 'pub_date' in j:
                    try:
                        j['pub_date'] = j['pub_year'] + '-01-01'
                    except KeyError:
                        year = year_from_fpath(filename)
                        j['pub_date'] = year + '-01-01'
                if j['pub_date'] == '':
                    try:
                        j['pub_date'] = j['pub_year'] + '-01-01'
                    except KeyError:
                        year = year_from_fpath(filename)
                        j['pub_date'] = year + '-01-01'
                if not 'length' in j:
                    try:
                        # j['length'] = len(j['bag_of_words'].split())
                        j['length'] = len(j['bag_of_words'])
                    except KeyError:
                        try:
                            tokens = [feature[0] for feature in j['features'][1:]]
                            j['length'] = len(tokens)
                        except KeyError:
                            j['length'] = len(j['content'].split())
                # write article metadata to csv
                if oe == True:
                    testrow = ['json/' + filename] + [j['title']] + [j['author']] + [j['pub']] + [j['volume']] + [j['issue']] +[j['pub_date']] + [j['length']]
                    print(testrow)
                csvwriter.writerow(['json/' + filename] + [j['title']] + [j['author']] + [j['pub']] + [j['volume']] +
                                   [j['issue']] + [j['pub_date']] + [j['length']])
                oe = False
            idx = idx + 1
    # Spreadsheet manipulation and meddling to make it work with dfr-browser
    with open(metadata_csv_file, 'r') as csv_in:
        csvreader = csv.reader(csv_in, delimiter=',')
        next(csvreader)  # skip header row
        with open(browser_meta_file_temp, 'w') as csv_out:
            # enforce quoted fields
            csvwriter = csv.writer(csv_out, delimiter=',', quoting=csv.QUOTE_ALL)
            for row in csvreader:
                csvwriter.writerow(row)
    with open(browser_meta_file_temp, 'r') as fin:
        with open(browser_meta_file, 'w') as fout:
            for line in fin:
                fout.write(line.replace(',"",', ',NA,'))

def get_model_state(selection, model_dir):
    """Get model state.

    This function assumes your project folder is set up according to WE1S
    format (and was therefore created using our `new_project_from_archive`
    notebook). It looks for the models you have selected to create
    dfr-browsers for in your project's models directory and then grabs those
    models' state and scaled files, or, if it fails to find them, it alerts
    you to their absence. To produce dfr-browsers for all of your project's
    models, the selection variable should be set to 'None'. To run the
    create_dfrbrowser() you need lists of the names of the model subdirectories
    you want to create (in subdir_list), the state files from each of those
    models (in state_file_list), and the scaled files from each of those
    models (in scaled_file_list). You may set these values manually in the
    notebook.
    """
    # Define variables
    subdir_list = []
    state_file_list = []
    scaled_file_list = []
    # Set `selection` to `All` or `None` if you want to make dfr-browsers for ALL existing models
    if get_selection(selection) is None:
        # For each model subdirectory, add the model state file and model scaled file to a list
        for subdir in os.listdir(model_dir):
            subdir_path = model_dir + '/' + subdir
            if os.path.isdir(subdir_path) and '.ipynb_checkpoints' not in subdir_path:
                subdir_list.append(subdir)
                num = re.search(r'\d+', subdir).group()
                model_path = model_dir + '/' + subdir
                for file in os.listdir(model_path):
                    if file.endswith('.gz') and num in file:
                        state_file = model_path + '/' + file
                        state_file_list.append(state_file)
                    if file.endswith('.csv'):
                        scaled_file = model_path + '/' + file
                        scaled_file_list.append(scaled_file)
        # User feedback in the notebook
        msg = '<p>Visualizations will be created for all models in <code>models</code> directory: ' + str(subdir_list) + '.<p>'
        display(HTML(msg))
        lsub = len(subdir_list)
        lstate = len(state_file_list)
        lscaled = len(scaled_file_list)
        # Display how many state and scaled files were discovered for how many models
        msg = '<p>Found ' + str(lstate) + ' state files and ' + str(lscaled) + ' scaled files for ' + str(lsub) + ' models.</p>'
        display(HTML(msg))
        # If they all match, you are golden
        if lsub == lstate == lscaled:
            display(HTML('<p style="color: green;">Ready to create visualizations.</p>'))
        # If they don't all match, you need to check your `models` directory
        # to make sure each one contains a state and a scaled file.
        else:
            msg = '<p style="color: red;">Incorrect number of state or scaled files! Check your <code>model</code> directory.</p>'
            display(HTML(msg))    # If selection is not `None`, process selected models
    else:
        subdir_list = selection
        # For each selected model, add the model state and scaled files to a list
        for subdir in subdir_list:
            model_path = model_dir + '/' + subdir
            num = re.search(r'\d+', subdir).group()
            for file in os.listdir(model_path):
                if file.endswith('.gz') and num in file:
                    state_file = model_path + '/' + file
                    state_file_list.append(state_file)
                if file.endswith('.csv'):
                    scaled_file = model_path + '/' + file
                    scaled_file_list.append(scaled_file)
        # User feedback in the notebook
        msg = '<p>Visualizations will be created for the following models: ' + str(subdir_list) +'</p>'
        display(HTML(msg))
        lsub = len(subdir_list)
        lstate = len(state_file_list)
        lscaled = len(scaled_file_list)
        # Display how many state and scaled files were discovered for how many models
        msg = '<p>Found ' + str(lstate) + ' state files and ' + str(lscaled) + ' scaled files for ' + str(lsub) + 'model.s</p>'
        display(HTML(msg))
        # If they all match, you are golden
        if lsub == lstate == lscaled:
            display(HTML('<p style="color: green;">Ready to create visualizations.</p>'))
        # If they don't all match, you need to check your `models` directory to
        # make sure each one contains a state and a scaled file.
        else:
            msg = '<p style="color: red;">Incorrect number of state or scaled files! Check your <code>model</code> directory.</p>'
            display(HTML(msg))
    return subdir_list, state_file_list, scaled_file_list

def create_dfrbrowser(subdir_list, state_file_list, scaled_file_list,
                      browser_meta_file, project_data_rel, current_dir, project_dir):
    """Create a dfr-browser visualization.

    This notebook creates dfr-browser visualizations for all models selected
    via the `get_models()` function above. It is configured to work with
    multiple models at once organized in the WE1S default format. After
    moving a lot of data around to various appropriate subfolders, it uses
    Andrew Goldstone's prepare_data.py script to create the necessary files
    for a dfr-browser visualization (NOTE: WE1S does not use Goldstone's
    dfrbrowser R package, because we wanted to keep everything in Python).
    We've also included some small tweaks of the language in some dfr-browser
    files so that they accord with WE1S json data (and not JSTOR data).
    """
    # Take the lists of model subdirectories, state files, and scaled files
    # created via the get_models() function and iterate through each to
    # create the appropriate subdirectories for the dfrbrowser visualizations
    # within the dfr_browser module.
    for subdir, state, scaled in zip(subdir_list, state_file_list, scaled_file_list):
        num = re.search(r'\d+', subdir).group()
        browse_path = current_dir + '/topics' + num
        existing = os.path.exists(browse_path)
        if existing == True:
            shutil.rmtree(browse_path)
            os.makedirs(browse_path)
        else:
            os.makedirs(browse_path)
        # make browser subdirectory
        # sb_path = browse_path + '/topics'
        sb_path = browse_path
        existing = os.path.exists(sb_path)
        if existing == True:
            shutil.rmtree(sb_path)
        # copy dfrbrowser template from scripts to project browser folder
        dfrb_scripts = current_dir + '/dfrb_scripts'
        shutil.copytree(dfrb_scripts, sb_path)
        # move and rename customized js file
        min_js = sb_path + '/js/dfb.min.js.custom'
        min_js_new = sb_path + '/js/dfb.min.js'
        shutil.move(min_js, min_js_new)
        # make data dir
        bdata_dir = sb_path + '/data'
        os.makedirs(bdata_dir)
        # create dfr-browser files using python script
        prepare_data_script = sb_path + '/bin/prepare-data'
        tw = sb_path + '/data/tw.json'
        dt = sb_path +'/data/dt.json.zip'
        info = sb_path + '/data/info.json'
        # using check_output to preserve prepare_data.py output
        output = subprocess.check_output([prepare_data_script, 'convert-state', state, '--tw', tw, '--dt', dt],
                                         stderr=STDOUT,
                                         universal_newlines=True)
        print(output)
        output = subprocess.check_output([prepare_data_script, 'info-stub', '-o', info],
                                         stderr=STDOUT,
                                         universal_newlines=True)
        print(output)
        # copy scaled file into data dir
        shutil.copy(scaled, bdata_dir)
        # move metadata-dfrb to {sb_path}/data, zip up and rename, delete meta.csv copy
        meta_zip = bdata_dir + '/meta.csv.zip'
        existing = os.path.exists(meta_zip)
        if existing == True:
            os.remove(meta_zip)
        shutil.copy(browser_meta_file, bdata_dir)
        try:
            shutil.make_archive(os.path.join(bdata_dir, 'meta.csv'), 'zip', bdata_dir, 'meta.csv')
        except OSError as err:
            print('Error writing meta.csv.zip')
            print(err)
        # Tweak default index.html to link to JSON, not JSTOR
        fpath_html = sb_path + '/index.html'
        with open(fpath_html, 'r') as file:
            filedata = file.read()
        filedata = filedata.replace('on JSTOR', 'JSON')
        with open(fpath_html, 'w') as file:
            file.write(filedata)
        # Tweak js file to link to the project_data folder of whatever domain
        fpath_js = sb_path + '/js/dfb.min.js'
        with open(fpath_js, 'r') as file:
            filedata = file.read()
        pat = r't\.select\(\"#doc_remark a\.url\"\).attr\(\"href\", .+?\);'
        new_pat = r'var doc_url = document.URL.split("modules")[0] + "project_data"; t.select("#doc_remark a.url")'
        new_pat += r'.attr("href", doc_url + "/" + e.url);'
        filedata = re.sub(pat, new_pat, filedata)
        with open(fpath_js, 'w') as file:
            file.write(filedata)

def display_links(project_dir, item_list, WRITE_DIR, PORT):
    """Display links to visualisations."""
    out = '<h4>Your Topic Bubbles visualizations are now available at the following locations:</h4>'
    out += '<ul>'
    for item in item_list:
        num = re.search(r'\d+', item).group()
        index_path = project_dir.replace(WRITE_DIR, '') + '/modules/topic_bubbles/' + item + '/index.html'
        if PORT != '' and PORT is not None:
            index_path = ':' + PORT + index_path
        javascript = 'event.srcElement.href = \'http://\' + window.location.hostname + \'' + index_path + '\';'
        link = '<a target="_blank" href="#" onfocus="' + javascript + '">Topic Bubbles for ' + str(num) + ' topics</a>'
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
        
