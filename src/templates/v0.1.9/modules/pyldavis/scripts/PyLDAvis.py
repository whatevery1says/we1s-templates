"""pyldavis.py.

Generate a pyLDAvis visualisation from a MALLET topic model.

This script is based on Jeri Wieringa's blog post "Using pyLDAvis with Mallet" 
(http://jeriwieringa.com/2018/07/17/pyLDAviz-and-Mallet/) and has been slightly 
altered and commented. It can be used from the command line or in tandem with 
pyldavis.ipynb in the WhatEvery1Says Virtual Workspace environment.


v.2.0.4. Adds Timer class.

v.2.0.3. Exposes pyLDAvis class methods for use in the final cell.

v.2.0.1. Adds a timer, outputs filepaths to visualisations, and adds a function to update the config file.

v.2.0. Moves most of the work into a Python class. It also adds handling of 
multiple models and customisation of model labels.

v.1.2.1 Integrates the code by Dan C. Baciu, Yichen Li, and Junqing Sun to
generate visualisations based on metadata properties. Their code has been
slightly abstracted to contain more generic variable names, meet PEP8 standards,
and integrate with the rest of the script.

v.1.2.1 also substitues a local copy of ldavis.v1.0.0.js for the one loaded from CDN.

scott.kleinman@csun.edu

v2.0.3 2020-07-09
v2.0.3 2019-10-30
v2.0.2 2019-06-13 # Bug fix
v2.0.1 2019-05-28
v2.0 2019-05-25
v1.2.1 2019-04-29
v1.2 2019-04-13
v1.1.1 2019-01-23
v1.1 2019-01-18
v1.0 2018-07-24

Lsst update: 2021-02-19.
"""

# Python imports
import gzip
import json
import os
import pandas as pd
import pyLDAvis as vis
import re
import shutil
import sys
import ipywidgets
import sklearn.preprocessing
from datetime import datetime
from IPython.display import display, HTML
from ipywidgets import HBox, IntProgress, Label
from pathlib import Path
from time import time

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
        self.pyldavis_script_path = 'scripts' # Change if necessary
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
        display(HTML('<p>Processing ' + self.model_dir.split('/')[-1] + '...</p>'))
        display(HTML('<code>    Getting hyperparameters...</code>'))
        self.hyperparameters = self.get_hyperparameters()
        self.alpha = self.hyperparameters[0]
        self.beta = self.hyperparameters[1]
        display(HTML('<code>    Creating dataframe...</code>'))
        self.df = self.state_to_df()
        display(HTML('<code>    Getting document lengths...</code>'))
        self.docs = self.doc_lengths()
        display(HTML('<code>    Getting term frequencies...</code>'))
        self.vocab = self.term_frequencies()
        display(HTML('<code>    Getting topic-word assignments...</code>'))
        self.phi_df = self.topic_word_assignments()
        self.phi = self.pivot_and_smooth(self.phi_df, self.beta, 'topic', 'type', 'token_count')
        display(HTML('<code>    Getting topic-term-matrix. This can take a long time, so please be patient.</code>'))
        self.theta_df = self.topic_term_matrix()
        self.theta = self.pivot_and_smooth(self.theta_df, self.alpha , '#doc', 'topic', 'topic_count')
        try:
            self.generate_vis()
        except BaseException:
            sys.exit('Could not generate vis.')
        display(HTML('<p style="color: green;">Done!</p>'))

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
        try:
            df = pd.read_csv(os.path.join(self.model_dir, self.state_file),
                            compression='gzip',
                            sep=' ',
                            skiprows=[1,2]
                            )
            df['type'] = df.type.astype(str)
            return df
        except BaseException:
            sys.exit('Could not get topic state file.')

    def get_hyperparameters(self):
        """Get the model hyperparameters."""
        try:
            params = self.extract_params()
            alpha = [float(x) for x in params[0][1:]]
            beta = params[1]
            return [alpha, beta]
        except BaseException:
            sys.exit('Could not get hyperparameters.')


    def doc_lengths(self):
        """Get the document lengths."""
        try:
            return self.df.groupby('#doc')['type'].count().reset_index(name ='doc_length')
        except BaseException:
            sys.exit('Could not get document lengths.')

    def term_frequencies(self):
        """Get the term frequencies."""
        try:
            vocab = self.df['type'].value_counts().reset_index()
            vocab.columns = ['type', 'term_freq']
            vocab = vocab.sort_values(by='type', ascending=True)
            return vocab
        except BaseException:
            sys.exit('Could not get term frequencies.')

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
        try:
            phi_df = self.df.groupby(['topic', 'type'])['type'].count().reset_index(name ='token_count')
            phi_df = phi_df.sort_values(by='type', ascending=True)
            return phi_df
        except BaseException:
            sys.exit('Could not get topic-word assignments.')

    def topic_term_matrix(self):
        """Get topic-term matrix."""
        try:
            theta_df = self.df.groupby(['#doc', 'topic'])['topic'].count().reset_index(name ='topic_count')
            return theta_df
        except BaseException:
            sys.exit('Could not get topic-term matrix.')

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
        try:
            vis.save_html(vis_data, os.path.join(self.output_dir, self.output_file))
        except BaseException:
            print('Could not save html')
        try:
            self._tweak_layout()
        except BaseException:
            print('Could not tweak layout.')
        if self.ui_labels is not None:
            try:
                self._customize_labels()
            except BaseException:
                print('Could not customize labels.')
            

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
        js = re.sub("mdsTitle = \'.+\'", "mdsTitle = '{0}'".format(self.ui_labels[0]), js)
        js = re.sub("selectionLabel = \'.+\'", "selectionLabel = '{0}'".format(self.ui_labels[1]), js)
        js = re.sub("barUnitSingular = \'.+\'", "barUnitSingular = '{0}'".format(self.ui_labels[2]), js)
        js = re.sub("barUnitPlural = \'.+\'", "barUnitPlural = '{0}'".format(self.ui_labels[3]), js)
        js = re.sub("PCLabel = \'.+\'", "PCLabel = '{0}'".format(self.ui_labels[4]), js)
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
            msg = 'Process aborted! A previous version already exists and may corrupt the data from which your visualization is generated.'
            sys.exit(msg)
        with gzip.GzipFile(topic_state_new, 'w+') as f:
                f.write(topic_state_properties.encode())
        # Return the name of the new topic-state file to the main script
        return topic_state_new

# Helper Methods
def get_models(model_dir, selection):
    """Automatically get all sub-directories and state files from the model_dir."""
    models = []
    if selection == None or (isinstance(selection, str) and selection.lower() == 'all'):
        subdir_list = []
        state_file_list = []
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
        msg = '<p>Visualizations will be created for all models in <code>models</code> directory: ' + ', '.join(subdir_list) + '.</p>' 
        display(HTML(msg))
        lsub = len(subdir_list)
        lstate = len(state_file_list)
        msg = '<p>Found ' + str(lstate) + ' state files for ' + str(lsub) + ' models.</p>' 
        display(HTML(msg))
        if lsub > 0:
            msg = '<p style="color: green;">Ready to generate visualization(s).</p2>'
            display(HTML(msg))
        else:
            msg = '<p style="color: red;">Incorrect number of state files! Check your <code>model</code> directory.</p>'
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
        msg = '<p>Visualizations will be created for the following models: ' + ', '.join(subdir_list) + '.</p>' 
        display(HTML(msg))
        lsub = len(subdir_list)
        lstate = len(state_file_list)
        msg = '<p>Found ' + str(lstate) + ' state files for ' + str(lsub) + ' models.</p>'  
        display(HTML(msg))
        if lsub > 0:
            msg = '<p style="color:green;">Ready to generate visualization(s).</p>'
            display(HTML(msg))
        else:
            msg = '<p style="color:red;">Incorrect number of state files! Check your <code>model</code> directory.</p>'
            display(HTML(msg))
    for i, item in enumerate(subdir_list):
        d = {'model': item, 'state_file': state_file_list[i]}
        models.append(d)
    return models

def generate(model_path, models, output_path, output_file, json_dir):
    """Generate visualizations for multiple models.
    
    Insert project_dir
    """
    # Start the timer
    vis_locations = []
    current_dir = os.getcwd()
    current_reldir = current_dir.split("/write/")[1]
    for i, item in enumerate(models):
        timer = Timer()
#         pyldavis_path = 'http://harbor.english.ucsb.edu:10000/tree/write/' + current_reldir + '/' + item['model']         
#         pyldavis_url = 'http://harbor.english.ucsb.edu:10001/' + current_reldir + '/' + item['model'] + '/index.html'         

#         pyldavis_path = project_dir + '/' + item['model']         
#         pyldavis_url = 'http://harbor.english.ucsb.edu:10001/' + current_reldir + '/' + item['model'] + '/index.html'         
        output_dict = {}
        output_dict['name'] = 'pyldavis-' + item['model'] # Vis name
        output_dict['model'] = item['model'] # Model name
#         output_dict['path'] = pyldavis_path # Vis path
#         output_dict['url'] = pyldavis_url # Vis url
        model_dir = os.path.join(model_path, item['model'])
        # Modify output_dict settings if metadata is configured
        if 'metadata' in item:
            metadata = item['metadata']
            output_dict['name'] = 'pyldavis-' + item['model'] + '-' + metadata # Vis name
#             output_dict['url'] = output_dict['url'].replace('index.html', 'index-' + metadata + '.html')
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
        if len(gzip_files) > 0:
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
            display(HTML('<p style="color: red;">There are no topic-state.gz files in ' + model_dir + '. This directory will be skipped.</p>'))            
        # Print time to completion
        print('Time elapsed: %s' % timer.get_time_elapsed())
    return vis_locations, vis

def display_links(project_dir, models, WRITE_DIR, PORT):
    """Display links to visualisations."""
    out = '<p style="color: green;">Your pyLDAvis visualizations are now available at the following locations:</p></h4>'
    out += '<ul>'   
    for model in models:
        num = re.search(r'\d+', model['model']).group()
        model_name = model['model']
        index = 'index'
        if 'metadata' in model:
            index = index + '-' + model['metadata']
        index_path = project_dir.replace(WRITE_DIR, '') + '/modules/pyldavis/' + model['model'] + '/' + index + '.html'
        if PORT != '' and PORT is not None:
            index_path = ':' + PORT + index_path
        javascript = 'event.srcElement.href = \'http://\' + window.location.hostname + \'' + index_path + '\';'
        link = '<a target="_blank" href="#" onfocus="' + javascript + '">pyLDAvis for ' + str(num) + ' topics</a>'
        out += '<li>' + link + '</li>'
    out += '</ul>'
    display(HTML(out))

class Timer:
    """Create a timer object."""

    def __init__(self):
        """Initialise the timer object."""
        self.start = time()

    def restart(self):
        """Restart the timer."""
        self.start = time()

    def get_time_elapsed(self):
        """Get the elapsed time and format it as hours, minutes, and seconds."""
        end = time()
        m, s = divmod(end - self.start, 60)
        h, m = divmod(m, 60)
        time_str = "%02d:%02d:%02d" % (h, m, s)
        return time_str

