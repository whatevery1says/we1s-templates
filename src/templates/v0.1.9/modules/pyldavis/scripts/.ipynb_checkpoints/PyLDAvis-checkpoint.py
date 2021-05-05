"""pyldavis.py.

Generate a pyLDAvis visualisation from a MALLET topic model.

This script is based on Jeri Wieringa's blog post "Using pyLDAvis with Mallet" 
(http://jeriwieringa.com/2018/07/17/pyLDAviz-and-Mallet/) and has been slightly 
altered and commented. It can be used from the command line or in tandem with 
pyldavis.ipynb in the WhatEvery1Says Virtual Workspace environment.

v.2.0.1. Adds a timer, outputs filepaths to visualisations, and adds a function to update the config file.

v.2.0. Moves most of the work into a Python class. It also adds handling of 
multiple models and customisation of model labels.

v.1.2.1 Integrates the code by Dan C. Baciu, Yichen Li, and Junqing Sun to
generate visualisations based on metadata properties. Their code has been
slightly abstracted to contain more generic variable names, meet PEP8 standards,
and integrate with the rest of the script.

v.1.2.1 also substitues a local copy of ldavis.v1.0.0.js for the one loaded from CDN.

scott.kleinman@csun.edu

v2.0.1 2019-05-28
v2.0 2019-05-25
v1.2.1 2019-04-29
v1.2 2019-04-13
v1.1.1 2019-01-23
v1.1 2019-01-18
v1.0 2018-07-24
"""

# Python imports
import gzip
import json
import os
import pandas as pd
import pyLDAvis as vis
import re
import shutil
import sklearn.preprocessing
import time
from datetime import datetime
from IPython.display import display, HTML
from pathlib import Path

class PyLDAvis:
    """Model a pyLDAvis.

    Parameters:
    - model_dir: the path to the model directory
    - state_file: the name of the state file
    - output_dir: the name of the directory where the output file is saved
    - output_file: the name of the output file
    - metadata: the name of the metadata field if generating a metadata vis
    - json_dir: the name of the json directory if generating a metadata vis

    """

    def __init__(self, model_dir, state_file, output_dir, output_file, json_dir, metadata=None, ui_labels=None):
        """Initialize the object."""
        self.model_dir = model_dir
        self.state_file = state_file
        self.output_dir = output_dir
        self.output_file = output_file
        self.pyldavis_script_path = 'pyldavis_scripts' # Change if necessary
        self.javascript_file = 'pyldavis_custom.js' # Change if necessary
        self.ui_labels = ui_labels
        self.json_dir = json_dir
        self.metadata = metadata
        if self.metadata is not None:
            metadata_state_file = self.create_metadata_state()
            metadata_state_file = re.sub('\\\\+', '/', metadata_state_file) # Windows hack
            self.model_dir = os.path.split(metadata_state_file)[0]
            self.state_file = os.path.basename(os.path.normpath(metadata_state_file))
            # self.model_dir, self.state_file = metadata_state_file.split('/')
            self.output_file = self.output_file.strip('.html') + '-' + self.metadata + '.html'
        print('Processing ' + self.model_dir + '/' + self.state_file + '...')
        print('    Getting hyperparameters...')
        self.hyperparameters = self.get_hyperparameters()
        self.alpha = self.hyperparameters[0]
        self.beta = self.hyperparameters[1]
        print('    Creating dataframe...')
        self.df = self.state_to_df()
        print('    Getting document lengths...')
        self.docs = self.doc_lengths()
        print('    Getting term frequencies...')
        self.vocab = self.term_frequencies()
        print('    Getting topic-word-assignments...')
        self.phi_df = self.topic_word_assignments()
        self.phi = self.pivot_and_smooth(self.phi_df, self.beta, 'topic', 'type', 'token_count')
        print('    Getting topic-term-matrix...')
        self.theta_df = self.topic_term_matrix()
        self.theta = self.pivot_and_smooth(self.theta_df, self.alpha , '#doc', 'topic', 'topic_count')
        self.generate_vis()
        print('Done!')

    def extract_params(self):
        """Extract the alpha and beta values from the statefile.

        Args:
            state_file (str): Path to statefile produced by MALLET.
        Returns:
            tuple: alpha (list), beta
        
        """
        with gzip.open(os.path.join(self.model_dir, self.state_file), 'r') as state:
            params = [x.decode('utf8').strip() for x in state.readlines()[1:3]]
        return (list(params[0].split(":")[1].split(" ")), float(params[1].split(":")[1]))

    def state_to_df(self):
        """Transform state file into pandas dataframe.

        The MALLET statefile is tab-separated, and the first two rows contain the alpha and beta hypterparamters.
        
        Args:
            self.state_file (str): Path to statefile produced by MALLET.
        Returns:
            dataframe: topic assignment for each token in each document of the model

        """
        df = pd.read_csv(os.path.join(self.model_dir, self.state_file),
                        compression='gzip',
                        sep=' ',
                        skiprows=[1,2]
                        )
        df['type'] = df.type.astype(str)
        return df

    def get_hyperparameters(self):
        """Get the model hyperparameters."""
        params = self.extract_params()
        alpha = [float(x) for x in params[0][1:]]
        beta = params[1]
        return [alpha, beta]

    def doc_lengths(self):
        """Get the document lengths."""
        return self.df.groupby('#doc')['type'].count().reset_index(name ='doc_length')

    def term_frequencies(self):
        """Get the term frequencies."""
        vocab = self.df['type'].value_counts().reset_index()
        vocab.columns = ['type', 'term_freq']
        vocab = vocab.sort_values(by='type', ascending=True)
        return vocab

    def pivot_and_smooth(self, df, smooth_value, rows_variable, cols_variable, values_variable):
        """Turn the pandas dataframe into a data matrix.

        Args:
            df (dataframe): aggregated dataframe 
            smooth_value (float): value to add to the matrix to account for the priors.
            rows_variable (str): name of dataframe column to use as the rows in the matrix.
            cols_variable (str): name of dataframe column to use as the columns in the matrix.
            values_variable(str): name of the dataframe column to use as the values in the matrix.
        Returns:
            dataframe: pandas matrix that has been normalized on the rows.

        Derived from https://ldavis.cpsievert.me/reviews/reviews.html.

        """
        matrix = df.pivot(index=rows_variable, columns=cols_variable, values=values_variable).fillna(value=0)
        matrix = matrix.values + smooth_value        
        normed = sklearn.preprocessing.normalize(matrix, norm='l1', axis=1)
        return pd.DataFrame(normed)

    def topic_word_assignments(self):
        """Get topic-word assignments."""
        phi_df = self.df.groupby(['topic', 'type'])['type'].count().reset_index(name ='token_count')
        phi_df = phi_df.sort_values(by='type', ascending=True)
        return phi_df

    def topic_term_matrix(self):
        """Get topic-term matrix."""
        theta_df = self.df.groupby(['#doc', 'topic'])['topic'].count().reset_index(name ='topic_count')
        return theta_df

    def generate_vis(self, save=True):
        """Generate the visualisation."""
        data = {'topic_term_dists': self.phi, 
                'doc_topic_dists': self.theta,
                'doc_lengths': list(self.docs['doc_length']),
                'vocab': list(self.vocab['type']),
                'term_frequency': list(self.vocab['term_freq'])
        }
        # sort_topics=False preserves the original Mallet topic order
        vis_data = vis.prepare(**data, sort_topics=False)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        vis.save_html(vis_data, os.path.join(self.output_dir, self.output_file))
        self._tweak_layout()

    def _tweak_layout(self):
        """Add some layout tweaks."""
        if self.metadata == None:
            js_file = self.javascript_file
        else:
            js_file = self.javascript_file.strip('.js') + '-' + self.metadata + '.js'
        shutil.copy(os.path.join(self.pyldavis_script_path, self.javascript_file), os.path.join(self.output_dir, js_file))
        with open(os.path.join(self.output_dir, self.output_file), 'r') as f:
            html = f.read()
        html = html.replace('https://cdn.rawgit.com/bmabey/pyLDAvis/files/ldavis.v1.0.0.js', js_file)
        script1 = """<script
        src="http://code.jquery.com/jquery-3.4.0.min.js"
        integrity="sha256-BJeo0qm959uMBGb65z40ejJYGSgR7REI4+CW1fNKwOg="
        crossorigin="anonymous"></script>"""
        script2 = """
        <script>
        window.onload = function () {
          let id = $('body').children().first().attr('id')
          let barFreqs = id + '-bar-freqs'
          let labels = '#' + barFreqs + ' > text'
          let lengths = [] 
          $(labels).each(function () {
            lengths.push($(this).text().length)
          })
          maxLength = Math.max(...lengths)
          if (maxLength > 40) {
            let top = id + '-top'
            $('#' + top).css('width', '1460px')
            $('svg').attr('width', '1460')
            $('svg > g:eq(2)').attr('transform', 'translate(900,60)')
          }
        }
        </script>
        """
        html = script1 + html + script2
        with open(os.path.join(self.output_dir, self.output_file), 'w') as f:
            f.write(html)

    def _customize_labels(self):
        """Add custom labels to the visualisation.
        
        Args:
          - self.ui_labels: A list containing (in order):
            1. The title for the MDS display
            2. The item represented by the MDS bubbles
            3. The unit being in the bar graph
            4. The plural of the unit represented in the bar graph
            5. The unit represented in the percentage when Relevance is displayed
            The default is [
                'Intertopic Distance Map (via multidimensional scaling)',
                'topic',
                'term',
                'terms',
                'tokens'
            ]

        """
        print('custom labels called')
        # Lower case all but the first item in ui_labels
        for i, item in enumerate(self.ui_labels):
            if i is not 0:
                self.ui_labels[i] = item.lower()
        if self.metadata == None:
            js_file = self.javascript_file
        else:
            js_file = self.javascript_file.strip('.js') + '-' + self.metadata + '.js'
        with open(os.path.join(self.output_dir, js_file), 'r') as f:
            js = f.read()
            js = re.sub("var mdsTitle = \'.+\'", 'var mdsTitle = "' + self.ui_labels[0] + '"', js)
            js = re.sub("var selectionLabel = \'.+\'", 'var selectionLabel = "' + self.ui_labels[1] + '"', js)
            js = re.sub("var barUnitSingular = \'.+\'", 'var barUnitSingular = "' + self.ui_labels[2] + '"', js)
            js = re.sub("var barUnitPlural = \'.+\'", 'var barUnitPlural = "' + self.ui_labels[2] + '"', js)
            js = re.sub("var PCLabel = \'.+\'", 'var PCLabel = "' + self.ui_labels[4] + '"', js)
        with open(os.path.join(self.output_dir, js_file), 'w') as f:
            f.write(js)

    def get_sorted_metadata(self, doc_list, property_index, properties, ide):
        """Get sorted metadata properties."""
        for file in (doc_list):  
            if file.endswith('.json'):
                row = []
                file_nr = ide
                ide += 1 
                row.append(file_nr)
                with open(os.path.join(self.json_dir, file), 'r') as document_json:
                    document_values = json.loads(document_json.read())
                    if document_values[self.metadata] == None:
                        document_values[self.metadata] = 'unknown'
                    property_name = document_values[self.metadata].replace(' ', '_').replace("'", '-')
                    if property_name.startswith('_'):
                        property_name = property_name[1:]
                    row.append(property_name)
                    document_property = document_values[self.metadata]
                    if document_property not in property_index:
                        property_index.append(document_property)
                    row.append(property_index.index(document_property))
                properties.append(row)
        properties.sort()
        # print (len(properties))
        return properties

    def create_metadata_state(self):
        """Create metadata state file.
        
        Returns the path to a new topic-state-metadata.gz file,
        where "metadata" is the name of the supplied property.
        """
        print('Creating metadata state...')
        topic_state_orig = os.path.join(self.model_dir, self.state_file)
        topic_state_new = os.path.join(self.model_dir, 'topic-state-' + self.metadata + '.gz')
        metadata_index = []
        metadata_values = []
        ide = 0
        doc_list = os.listdir(self.json_dir)
        properties = self.get_sorted_metadata(doc_list, metadata_index, metadata_values, ide)
        # Reshape the property rows
        properties_a = []
        for row in properties:
                a_row = '\n0 0 0 ' + str(row[2]) + ' ' + row[1] + ' '
                properties_a.append(a_row)
        # Read and copy the original topic-state file 
        df = pd.read_csv(topic_state_orig, compression='gzip', delimiter=' ', skiprows=[0, 1, 2])
        # print('dataframe done')
        df5 = df
        # Get the headers of the original topic-state file as a string
        topic_state_properties = pd.read_csv(topic_state_orig, compression='gzip', sep=' ', nrows=2).to_csv(sep=' ', na_rep='')
        topic_state_properties = topic_state_properties[:-1]
        topic_state_properties = topic_state_properties[2:]
        ts = ''
        idx = 0
        for i in topic_state_properties:
            if i == '#':
                idx = 1
                ts += i
            else:
                if idx == 1:
                    ts += i 
        topic_state_properties = ts
        # Populate the matching property rows for each row in the original topic-state 
        list_0 = df['0'].tolist()
        list_l = df5.iloc[:,-1].tolist()
        # print(len(list_0))
        # print(len(list_l))
        i = 0
        for ie in list_0:
            rows = properties_a[ie]  
            topic_state_properties += rows + str(list_l[i])
            i += 1
        # Write a new topic-state file with the metadata suffix
        if os.path.isfile(topic_state_new):
            print('Warning: A previous version already exists and may corrupt the data from which your visualization is generated.')
        with gzip.GzipFile(topic_state_new, 'w+') as f:
                f.write(topic_state_properties.encode())
        # Return the name of the new topic-state file to the main script
        return topic_state_new

# Helper Methods
def get_models(model_dir, selection):
    """Automatically get all sub-directories and state files from the model_dir."""
    models = []
    if selection == None:
        subdir_list = []
        state_file_list = []
        for subdir in os.listdir(model_dir):
            if '.ipynb_checkpoints' not in subdir and '.txt' not in subdir:
                subdir_list.append(subdir)
                num = re.search(r'\d+', subdir).group()
                model_path = model_dir + '/' + subdir
                for file in os.listdir(model_path):
                    if file.endswith('.gz') and num in file:
                        state_file = model_path + '/' + file
                        state_file_list.append(state_file)
        msg = '<h2>Will create visualizations for all models in <code>models</code> directory: ' + str(subdir_list) +'</h2>' 
        display(HTML(msg))
        lsub = len(subdir_list)
        lstate = len(state_file_list)
        msg = '<h2>Found ' + str(lstate) + ' state files for ' + str(lsub) + ' models</h2>' 
        display(HTML(msg))
        if lsub > 0:
            msg = '<h2>Ready to generate visualization(s).</h2>'
            display(HTML(msg))
        else:
            msg = '<h2>Incorrect number of state files! Check your <code>model</code> directory</h2>'
            display(HTML(msg))
    else:
        state_file_list = []
        subdir_list = selection
        for subdir in subdir_list:
            num = re.search(r'\d+', subdir).group()
            model_path = model_dir + '/' + subdir
            for file in os.listdir(model_path):
                    if file.endswith('.gz') and num in file:
                        state_file = model_path + '/' + file
                        state_file_list.append(state_file)
        msg = '<h2>Will create visualizations for the following models: ' + str(subdir_list) +'</h2>' 
        display(HTML(msg))
        lsub = len(subdir_list)
        lstate = len(state_file_list)
        msg = '<h2><p>Found ' + str(lstate) + ' state files for ' + str(lsub) + ' models</h2>'  
        display(HTML(msg))
        if lsub > 0:
            msg = '<h2>Ready to generate visualization(s).</h2>'
            display(HTML(msg))
        else:
            msg = '<h2>Incorrect number of state files! Check your <code>model</code> directory</h2>'
            display(HTML(msg))
    for i, item in enumerate(subdir_list):
        d = {'model': item, 'state_file': state_file_list[i]}
        models.append(d)
    return models

def generate(model_path, models, output_path, output_file, json_dir):
    """Generate visualizations for multiple models."""
    # Start the timer
    start = time.time()
    
    vis_locations = []
    current_dir = os.getcwd()
    current_reldir = current_dir.split("/write/")[1]
    for item in models:
        pyldavis_path = 'http://harbor.english.ucsb.edu:10000/tree/write/' + current_reldir + '/' + item['model']         
        pyldavis_url = 'http://harbor.english.ucsb.edu:10001/' + current_reldir + '/' + item['model'] + '/index.html'         
        output_dict = {}
        output_dict['name'] = 'pyldavis-' + item['model'] # Vis name
        output_dict['model'] = item['model'] # Model name
        output_dict['path'] = pyldavis_path # Vis path
        output_dict['url'] = pyldavis_url # Vis url
        model_dir = os.path.join(model_path, item['model'])
        # Modify output_dict settings if metadata is configured
        if 'metadata' in item:
            metadata = item['metadata']
            output_dict['name'] = 'pyldavis-' + item['model'] + '-' + metadata # Vis name
            output_dict['url'] = output_dict['url'].replace('index.html', 'index-' + metadata + '.html')
            # Delete any previous topic-state-metadata files
            num = re.search(r'\d+', item['model']).group()
            meta_state = 'topic-state' + num + '-' + metadata +'.gz'
            topic_state_new = os.path.join(model_dir, meta_state)            
            if os.path.isfile(topic_state_new):
                os.remove(topic_state_new)
        else:
            metadata = None
            meta_state = None
        # Set ui_labels if configured
        if 'ui_labels' in item:
            ui_labels = item['ui_labels']
        else:
            ui_labels = None
        # Get the topic-state.gz file
        gzip_files = []
        model_short_path = model_path.split('/')[-2] + '/' + item['model']
        topic_state_file = ''
        for file in os.listdir(model_dir):
            if file.endswith('.gz'):
                gzip_files.append(file)
            if len(gzip_files) > 1:
                if meta_state is not None and file == meta_state:
                    topic_state_file = file
                else:
                    num = re.search(r'\d+', item['model']).group()
                    topic_state_file = 'topic-state' + num + '.gz'
        # If there are no .gz files
        if len(gzip_files) > 0:
            output_dir = os.path.join(output_path, item['model'])
            output_name = os.path.basename(output_dir)
            # Generate the pyLDAvis
            vis = PyLDAvis(model_dir, topic_state_file, output_dir, output_file, json_dir, metadata, ui_labels)
            vis_locations.append(output_dict)
        else:
            print('There are no topic-state.gz files in ' + model_dir + '. This directory will be skipped.')
    # Print time to completion
    end = time.time()
    t = end - start
    print('Time to completion: ' + str(t) + ' seconds.')
    return vis_locations

def prepare_vis_config(update_dict, vis_type):
    """Automatically get all sub-directories and state files from the model_dir.
    
    Parameters:
    - update_dict: A dict with the `name`, `model`, `path`, `url`.
    - The type of visualisation (e.g. "dfr-browser", "pyLDAvis", etc.)
    """
    # Make sure we know where the project directory and config files are
    current_pathobj = Path(os.getcwd())
    project_dir = str(current_pathobj.parent.parent)
    config_file = os.path.join(project_dir, 'config/config.json')
    
    # Open the config file and get the names of all the visualisations of the specified type
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.loads(f.read())
    vis_config_names = [item['name'] for item in config['visualizations'] if item['type'] == vis_type]
    
    # Loop through the update_dict and create a dict for each visualisation to be updated
    for vis in update_dict:
        name = vis['name']
        d = {
            'name': name,
            'model': vis['model'],
            'title': name.title(),
            'type': vis_type,
            'description': '',
            'path': vis['path'],
            'url': vis['url'],
            'public_url': '',
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # If the visualisation name is already in the configuration, update the value 
        if name in vis_config_names:
            index = [j for j, n in enumerate(vis_config_names) if n == name][0]
            config['visualizations'][index] = d
        # Otherwise, append the dict to the configuration
        else:
            config['visualizations'].append(d)
            
    return {'visualizations': config['visualizations']}
