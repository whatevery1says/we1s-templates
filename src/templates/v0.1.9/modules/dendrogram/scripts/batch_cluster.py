"""batch_cluster.py.

Last update: 2020-07-31
"""

# Python Imports
import gzip
import numpy as np
import os
import pandas as pd
import re
import time
import sklearn.preprocessing
import matplotlib.pyplot as plt
import numpy as np
from bs4 import BeautifulSoup as bs
from IPython.display import display, HTML
from natsort import natsorted
from operator import itemgetter
from pathlib import Path
from shutil import copy, copytree, rmtree
from scipy.cluster.hierarchy import linkage, dendrogram, average, single, complete, ward
from scipy.spatial.distance import pdist
import plotly.offline as py
import plotly.graph_objs as go
import plotly.figure_factory as FF
from time import time

# BatchCluster class
class BatchCluster():
    """BatchCluster class.
    
    Reads and clusters the topic state file for each model and saves the cluster divs
    to the partials folder.
    """

    def __init__(self, models, project_dir, model_dir, partials_path, distance_metrics,
                  linkage_methods, orientation='top', height=600, width=1200,
                  truncate_mode=None, p=None, leaf_font_size=None, hovertext=None,
                  color_threshold=None, smoothed=True, standalone=False,
                  WRITE_DIR=None, PORT=None):
        """Initialise a batch cluster."""
        timer = Timer()
        self.models = models
        self.project_dir = project_dir
        self.model_dir = model_dir
        self.partials_path = partials_path
        self.distance_metrics = distance_metrics
        self.linkage_methods = linkage_methods
        self.orientation = orientation
        self.height = height
        self.width = width
        self.truncate_mode = truncate_mode
        self.p = p
        self.leaf_font_size = leaf_font_size
        self.hovertext = hovertext
        self.color_threshold = color_threshold
        self.smoothed = True
        self.standalone = False
        self.WRITE_DIR = WRITE_DIR
        self.PORT = PORT
        self.meta = self._get_model_meta()
        self._build_cluster_settings()
        self._add_cluster_settings()
        self._make_partials_folder()
        self._cluster_models()
        output_cache = self._create_index_files()
        display(HTML('<h4>Index pages can be viewed at</h4>'))
        project_dirname = os.path.basename(self.project_dir)
        output = '<ul>'
        project_path = project_dir.replace(self.WRITE_DIR, '')
        for filename in output_cache:
            if self.PORT is not None:
                index_path = ':' + self.PORT + '/' + project_path + '/modules/dendrogram/' + filename
            else:
                index_path = '/' + project_path + '/modules/dendrogram/' + filename
            link = '<a target="_blank" href="#" onmouseover="event.srcElement.href = \'http://\' + window.location.hostname + \'' + index_path + '\';">' + filename + '</a>'
            output += '<li>' + link + '</li>'
        output += '</ul>'
        display(HTML(output))
        # Correct url: http://harbor.english.ucsb.edu:10001/dev/20200723_2335_import2dfb-test/modules/dendrogram/dendrogram-topics50-index.html
        # Generated url: http://harbor.english.ucsb.edu:10001/20200723_2335_import2dfb-test/dendrogram/dendrogram-topics50-index.html
        print('Time elapsed: %s' % timer.get_time_elapsed())

    def _add_cluster_settings(self):
        """Add the cluster settings."""
        models_with_duplicates = []
        for i, _ in enumerate(self.cluster_settings):
            result = [dict(item, **self.cluster_settings[i]) for item in self.meta]
            models_with_duplicates.append(result)
        all_models = []
        for model in models_with_duplicates:
            all_models += model
        self.all_models = sorted(all_models, key=itemgetter('model'), reverse=True)

    def _build_cluster_settings(self):
        """Build cluster settings."""
        self.cluster_settings = []
        if 'euclidean' in self.distance_metrics:
            for linkage_method in self.linkage_methods:
                self.cluster_settings.append({'distance_metric': 'euclidean', 'linkage_method': linkage_method})
        if 'cosine' in self.distance_metrics:
            self.cluster_settings.append({'distance_metric': 'cosine', 'linkage_method': linkage_method})

    def _cluster_models(self):
        """Iterate through the models, get their states, and cluster them."""
        prev_model = None
        source_filenames = []
        self.all_models = natsorted(self.all_models, key=lambda k: k['model'])
        for model in self.all_models:
            state_path = model['state_path']
            model_name = model['model']
            if model_name is not prev_model:
                display(HTML('Loading state file for ' + model_name + '...'))
                object_exists = False
                try:
                    # Instantiate the topic-state object only if it does not already exist for the model
                    topic_state = State(state_path)
                    object_exists = True
                    message = HTML('The topic-state object has been created. Performing cluster analysis...')
                    display(message)
                except:
                    display(HTML('<p style="color:red;">Error: Could not instantiate the topic-state object for ' + state_path + '. Skipping...</p>'))
            if object_exists:
                try:
                    distance_metric = model['distance_metric']
                    linkage_method = model['linkage_method']
                    file_meta = ['dendrogram', model_name, distance_metric, linkage_method, 'index.html']
                    file_path =  self.partials_path + '/' + '-'.join(file_meta).replace('-index.html', '.html')
                    source_filenames.append(file_path)
                    topic_state.cluster(distance_metric, linkage_method, filepath=file_path,
                                        height=self.height, width=self.width, smoothed=self.smoothed, orientation=self.orientation,
                                        truncate_mode=self.truncate_mode, p=self.p, leaf_font_size=self.leaf_font_size,
                                        hovertext=self.hovertext, color_threshold=self.color_threshold)
                    print('Dendrogram successfully created for ' + model_name + ' with ' + distance_metric + ' distance and ' + linkage_method + ' linkage.')
                except:
                    display(HTML('<p style="color:red;">Error: Could not perform the cluster analysis for ' + model_name + ' with ' + distance_metric + ' distance and ' + linkage_method + ' linkage. Skipping...</p>'))
            prev_model = model_name

    def _create_index_files(self):
        """Save the dendrogram index files to the private module directory.
        
        Returns a cache of filenames to the main batch_cluster() function.
        """
        display(HTML('Creating index files...'))
        # Configure web page settings
        model_names = natsorted(list(set([model['model'] for model in self.all_models])))
        index_filenames = natsorted(list(set(['dendrogram-' + model['model'] + '-index.html' for model in self.all_models])))
        index_titles  = natsorted(list(set([model['model'].replace('topics', ' Topics') for model in self.all_models])))
        menu_items = np.unique([model['distance_metric'].title() + ' ' + model['linkage_method'].title() for model in self.all_models])
        dendrogram_titles = np.unique([model['distance_metric'].title() + ' Distance with ' + model['linkage_method'].title() + ' Linkage' for model in self.all_models])
        idx = []
        titles = {}
        for i, item in enumerate(index_filenames):
            d = {'name': model_names[i], 'filename': item, 'title': index_titles[i], 'menu_items': [], 'dendrogram_titles': []}
            for li in menu_items:
                d['menu_items'].append(li)
                d['dendrogram_titles'] = dendrogram_titles
            idx.append(d)
        output_cache = []
        # Inject some html, css, and javascript into the template file
        settings = [x.lower().replace(' ', '-') for x in menu_items] 
        for item in idx:
            display(HTML('Building ' + item['filename'] + '...'))
            with open('scripts/index_template.html', 'r') as f:
                html = f.read()
            html = html.replace('<title></title>', '<title>' + item['title'] +'</title>')
            # Build the menu
            filename = item['filename']
            source_filename = filename.replace('index.html', settings[0] + '.html')
            list_items = '<li class="nav-item active"><a class="nav-link" href="' + source_filename + '">' + menu_items[0] + ' <span class="sr-only">(current)</span></a></li>\n'
            titles = {}
            titles[source_filename] = dendrogram_titles[0]
            for i, li in enumerate(menu_items):
                if i > 0:
                    source_filename = filename.replace('index.html', settings[i] + '.html')
                    titles[source_filename] = dendrogram_titles[i]
                    list_items += '<li class="nav-item"><a class="nav-link" href="' + source_filename + '">' + menu_items[i] + '</a></li>\n' 
            html = html.replace('<a class="navbar-brand" href="#"></a>', '<a class="navbar-brand" href="#">' + item['title'] + '</a>')
            html = html.replace('<ul class="navbar-nav"></ul>', '<ul class="navbar-nav">' + list_items + '</ul>')
            html = html.replace('var titles = {}', 'var titles = ' + str(titles))
            html = html.replace('<h3 id="title" class="text-center" style="display: none;"></h3>', '<h3 id="title" class="text-center" style="display: none;">' + dendrogram_titles[0] + '</h3>')
            html = html.replace("url='.html'", "url='" + source_filename + "'")
            # Get topic keywords
            model_path = self.model_dir + '/' + item['name']
            model_dirs = os.listdir(model_path)
            model_dirs = [dir for dir in model_dirs if not dir.endswith('.txt') and not dir.endswith('.mallet')]
            for file in os.listdir(model_path):
                if 'keys' in file:
                    keys_filepath = model_path + '/' + file
            # Add the topic keywords
            with open(keys_filepath, 'r') as f:
                keys = f.read().split('\n')
            keys = [re.sub('.+\t', '', line) for line in keys]
            keywords = {}
            for i, line in enumerate(keys):
                k = 'Topic' + str(i + 1)
                keywords[k] = line
            html = html.replace('var keywords = []', 'var keywords = ' + str(keywords))
            # Save the file
            with open(filename, 'w') as f:
                f.write(html)
            print('Saved ' + filename + '.')
            output_cache.append(filename)
        return output_cache

    def _get_model_meta(self):
        """Get a list of dicts with state paths and key paths for all models."""
        meta = []
        if self.models == []:
            self.models = [model for model in os.listdir(self.model_dir) if model.startswith('topics')]
        for model in self.models:
            model_num = model.replace('topics', '')
            meta.append(
                {'model': model,
                'state_path': self.model_dir + '/' + model + '/topic-state' + model_num + '.gz',
                'keys_path': self.model_dir + '/' + model + '/keys' + model_num + '.txt'
                })
        return meta

    def _make_partials_folder(self):
        """Make the partials folder if necessary."""
        if not os.path.exists(self.partials_path):
            os.makedirs(self.partials_path)

# State File Class
class State():
    """Convert Mallet state to a Python object.

    Parameters:
    - statefile: The path to mallet state file.
    """
    def __init__(self, statefile):
        """Initialize the object."""
        self.statefile = statefile
        self.df = self._state_to_df()
        self.alpha = self._extract_params()[0]
        self.beta = self._extract_params()[1]
        self.vocab = self._get_vocab()
        self.topic_state_format = self.topic_state_format()
        self.word_topic_assignments = self.word_topic_assignments()
        self.smoothed_word_topic_assignments = self.smoothed_word_topic_assignments()
        self.topic_term_matrix = self.topic_term_matrix()
        
    def _extract_params(self):
        """Extract the alpha and beta values from the statefile.

        Args:
            statefile (str): Path to statefile produced by MALLET.
        Returns:
            tuple: alpha (list), beta    
        """
        with gzip.open(self. statefile, 'r') as state:
            temp_params = [x.decode('utf8').strip() for x in state.readlines()[1:3]]
            params = (list(temp_params[0].split(":")[1].split(" ")), float(temp_params[1].split(":")[1]))
            alpha = [float(x) for x in params[0][1:]]
            beta = params[1]
        return (alpha, beta)

    def _state_to_df(self):
        """Transform state file into pandas dataframe.
        The MALLET statefile is tab-separated, and the first two rows contain the alpha and beta hypterparamters.
        
        Args:
            statefile (str): Path to statefile produced by MALLET.
        Returns:
            dataframe: topic assignment for each token in each document of the model
        """
        return pd.read_csv(self.statefile, compression='gzip', sep=' ', skiprows=[1,2])

    def topic_state_format(self):
        """Get Topic-State Format."""
        self.df['type'] = self.df.type.astype(str)
        return self.df

    def _get_vocab(self, sort_by='term_freq', ascending=False):
        """Get the vocabulary and term frequencies from the state file."""
        vocab = self.df['type'].value_counts().reset_index()
        vocab.columns = ['type', 'term_freq']
        return vocab.sort_values(by=sort_by, ascending=ascending)

    def _pivot_and_smooth(self, df, smooth_value, rows_variable, cols_variable, values_variable):
        """
        Turn the pandas dataframe into a data matrix.
        Args:
            df (dataframe): aggregated dataframe 
            smooth_value (float): value to add to the matrix to account for the priors
            rows_variable (str): name of dataframe column to use as the rows in the matrix
            cols_variable (str): name of dataframe column to use as the columns in the matrix
            values_variable(str): name of the dataframe column to use as the values in the matrix
        Returns:
            dataframe: pandas matrix that has been normalized on the rows.
        """
        matrix = df.pivot(index=rows_variable, columns=cols_variable, values=values_variable).fillna(value=0)
        matrix = matrix.values + smooth_value        
        normed = sklearn.preprocessing.normalize(matrix, norm='l1', axis=1)
        return pd.DataFrame(normed)

    def word_topic_assignments(self, sort_by='topic', ascending=True):
        """Get the word-topic assignments from the state file."""
        phi_df = self.df.groupby(['topic', 'type'])['type'].count().reset_index(name ='token_count')
        return phi_df.sort_values(by=sort_by, ascending=ascending)

    def smoothed_word_topic_assignments(self):
        """Get a smoothed version of the word-topic assignments from the state file.
        
        This returns phi, which is what is submitted to pyLDAvis.
        """
        return self._pivot_and_smooth(self.word_topic_assignments, self.beta, 'topic', 'type', 'token_count')

    def topic_term_matrix(self):
        df = self.word_topic_assignments.sort_values(['topic', 'token_count'], ascending=[True, False]).values
        num_topics = max(list(self.df['topic'].values + 1))
        # Convert the word-topic assignments to a list of lists
        topics = []
        for topic_num in range(0, num_topics):
            row = [x[2] for x in df if x[0] == topic_num]
            topics.append(row)
        # Even the length of the rows and add 0 to empty rows
        length = max(map(len, topics))
        ttm = np.array([topic+[0]*(length-len(topic)) for topic in topics])
        ttm.astype(int)
        return ttm
    
    def cluster(self, distance_metric='euclidean', linkage_method='average', filepath=None, height=600,
                width=1200, smoothed=True, orientation='top', truncate_mode=None, p=None,
                leaf_font_size=12, hovertext=None, color_threshold=None, save=True, standalone=False):
        if smoothed == True:
            ttm = self.smoothed_word_topic_assignments
        else:
            ttm = self.topic_term_matrix
        num_topics = len(ttm)
        labels = []
        i = 0
        while i < num_topics:
            j = i + 1 # index from 1
            labels.append('Topic' + str(j)) 
            i = i + 1
        distfun = lambda x: pdist(ttm, metric=distance_metric)
        if linkage_method == 'single':
            linkagefun = lambda x: single(ttm)
        elif linkage_method == 'complete':
            linkagefun = lambda x: complete(ttm)
        elif linkage_method == 'ward':
            linkagefun = lambda x: ward(ttm)
        else:
            linkagefun = lambda x: average(ttm)
"""batch_cluster.py.

Last update: 2020-07-31
"""

# Python Imports
import gzip
import numpy as np
import os
import pandas as pd
import re
import time
import sklearn.preprocessing
import matplotlib.pyplot as plt
import numpy as np
from bs4 import BeautifulSoup as bs
from IPython.display import display, HTML
from natsort import natsorted
from operator import itemgetter
from pathlib import Path
from shutil import copy, copytree, rmtree
from scipy.cluster.hierarchy import linkage, dendrogram, average, single, complete, ward
from scipy.spatial.distance import pdist
import plotly.offline as py
import plotly.graph_objs as go
import plotly.figure_factory as FF
from time import time

# BatchCluster class
class BatchCluster():
    """BatchCluster class.
    
    Reads and clusters the topic state file for each model and saves the cluster divs
    to the partials folder.
    """

    def __init__(self, models, project_dir, model_dir, partials_path, distance_metrics,
                  linkage_methods, orientation='bottom', height=600, width=1200,
                  truncate_mode=None, p=None, leaf_font_size=None, hovertext=None,
                  color_threshold=None, smoothed=True, standalone=False,
                  WRITE_DIR=None, PORT=None):
        """Initialise a batch cluster."""
        timer = Timer()
        self.models = models
        self.project_dir = project_dir
        self.model_dir = model_dir
        self.partials_path = partials_path
        self.distance_metrics = distance_metrics
        self.linkage_methods = linkage_methods
        self.orientation = orientation
        self.height = height
        self.width = width
        self.truncate_mode = truncate_mode
        self.p = p
        self.leaf_font_size = leaf_font_size
        self.hovertext = hovertext
        self.color_threshold = color_threshold
        self.smoothed = True
        self.standalone = False
        self.WRITE_DIR = WRITE_DIR
        self.PORT = PORT
        self.meta = self._get_model_meta()
        self._build_cluster_settings()
        self._add_cluster_settings()
        self._make_partials_folder()
        self._cluster_models()
        output_cache = self._create_index_files()
        display(HTML('<h4>Index pages can be viewed at</h4>'))
        project_dirname = os.path.basename(self.project_dir)
        output = '<ul>'
        project_path = project_dir.replace(self.WRITE_DIR, '')
        for filename in output_cache:
            if self.PORT is not None:
                index_path = ':' + self.PORT + '/' + project_path + '/modules/dendrogram/' + filename
            else:
                index_path = '/' + project_path + '/modules/dendrogram/' + filename
            link = '<a target="_blank" href="#" onmouseover="event.srcElement.href = \'http://\' + window.location.hostname + \'' + index_path + '\';">' + filename + '</a>'
            output += '<li>' + link + '</li>'
        output += '</ul>'
        display(HTML(output))
        # Correct url: http://harbor.english.ucsb.edu:10001/dev/20200723_2335_import2dfb-test/modules/dendrogram/dendrogram-topics50-index.html
        # Generated url: http://harbor.english.ucsb.edu:10001/20200723_2335_import2dfb-test/dendrogram/dendrogram-topics50-index.html
        print('Time elapsed: %s' % timer.get_time_elapsed())

    def _add_cluster_settings(self):
        """Add the cluster settings."""
        models_with_duplicates = []
        for i, _ in enumerate(self.cluster_settings):
            result = [dict(item, **self.cluster_settings[i]) for item in self.meta]
            models_with_duplicates.append(result)
        all_models = []
        for model in models_with_duplicates:
            all_models += model
        self.all_models = sorted(all_models, key=itemgetter('model'), reverse=True)

    def _build_cluster_settings(self):
        """Build cluster settings."""
        self.cluster_settings = []
        if 'euclidean' in self.distance_metrics:
            for linkage_method in self.linkage_methods:
                self.cluster_settings.append({'distance_metric': 'euclidean', 'linkage_method': linkage_method})
        if 'cosine' in self.distance_metrics:
            self.cluster_settings.append({'distance_metric': 'cosine', 'linkage_method': linkage_method})

    def _cluster_models(self):
        """Iterate through the models, get their states, and cluster them."""
        prev_model = None
        source_filenames = []
        self.all_models = natsorted(self.all_models, key=lambda k: k['model'])
        for model in self.all_models:
            state_path = model['state_path']
            model_name = model['model']
            if model_name is not prev_model:
                display(HTML('Loading state file for ' + model_name + '...'))
                object_exists = False
                try:
                    # Instantiate the topic-state object only if it does not already exist for the model
                    topic_state = State(state_path)
                    object_exists = True
                    message = HTML('The topic-state object has been created. Performing cluster analysis...')
                    display(message)
                except:
                    display(HTML('<p style="color:red;">Error: Could not instantiate the topic-state object for ' + state_path + '. Skipping...</p>'))
            if object_exists:
                try:
                    distance_metric = model['distance_metric']
                    linkage_method = model['linkage_method']
                    file_meta = ['dendrogram', model_name, distance_metric, linkage_method, 'index.html']
                    file_path =  self.partials_path + '/' + '-'.join(file_meta).replace('-index.html', '.html')
                    source_filenames.append(file_path)
                    topic_state.cluster(distance_metric, linkage_method, filepath=file_path,
                                        height=self.height, width=self.width, smoothed=self.smoothed, orientation=self.orientation,
                                        truncate_mode=self.truncate_mode, p=self.p, leaf_font_size=self.leaf_font_size,
                                        hovertext=self.hovertext, color_threshold=self.color_threshold)
                    print('Dendrogram successfully created for ' + model_name + ' with ' + distance_metric + ' distance and ' + linkage_method + ' linkage.')
                except:
                    display(HTML('<p style="color:red;">Error: Could not perform the cluster analysis for ' + model_name + ' with ' + distance_metric + ' distance and ' + linkage_method + ' linkage. Skipping...</p>'))
            prev_model = model_name

    def _create_index_files(self):
        """Save the dendrogram index files to the private module directory.
        
        Returns a cache of filenames to the main batch_cluster() function.
        """
        display(HTML('Creating index files...'))
        # Configure web page settings
        model_names = natsorted(list(set([model['model'] for model in self.all_models])))
        index_filenames = natsorted(list(set(['dendrogram-' + model['model'] + '-index.html' for model in self.all_models])))
        index_titles  = natsorted(list(set([model['model'].replace('topics', ' Topics') for model in self.all_models])))
        menu_items = np.unique([model['distance_metric'].title() + ' ' + model['linkage_method'].title() for model in self.all_models])
        dendrogram_titles = np.unique([model['distance_metric'].title() + ' Distance with ' + model['linkage_method'].title() + ' Linkage' for model in self.all_models])
        idx = []
        titles = {}
        for i, item in enumerate(index_filenames):
            d = {'name': model_names[i], 'filename': item, 'title': index_titles[i], 'menu_items': [], 'dendrogram_titles': []}
            for li in menu_items:
                d['menu_items'].append(li)
                d['dendrogram_titles'] = dendrogram_titles
            idx.append(d)
        output_cache = []
        # Inject some html, css, and javascript into the template file
        settings = [x.lower().replace(' ', '-') for x in menu_items] 
        for item in idx:
            display(HTML('Building ' + item['filename'] + '...'))
            with open('scripts/index_template.html', 'r') as f:
                html = f.read()
            html = html.replace('<title></title>', '<title>' + item['title'] +'</title>')
            # Build the menu
            filename = item['filename']
            source_filename = filename.replace('index.html', settings[0] + '.html')
            list_items = '<li class="nav-item active"><a class="nav-link" href="' + source_filename + '">' + menu_items[0] + ' <span class="sr-only">(current)</span></a></li>\n'
            titles = {}
            titles[source_filename] = dendrogram_titles[0]
            for i, li in enumerate(menu_items):
                if i > 0:
                    source_filename = filename.replace('index.html', settings[i] + '.html')
                    titles[source_filename] = dendrogram_titles[i]
                    list_items += '<li class="nav-item"><a class="nav-link" href="' + source_filename + '">' + menu_items[i] + '</a></li>\n' 
            html = html.replace('<a class="navbar-brand" href="#"></a>', '<a class="navbar-brand" href="#">' + item['title'] + '</a>')
            html = html.replace('<ul class="navbar-nav"></ul>', '<ul class="navbar-nav">' + list_items + '</ul>')
            html = html.replace('var titles = {}', 'var titles = ' + str(titles))
            html = html.replace('<h3 id="title" class="text-center" style="display: none;"></h3>', '<h3 id="title" class="text-center" style="display: none;">' + dendrogram_titles[0] + '</h3>')
            html = html.replace("url='.html'", "url='" + source_filename + "'")
            # Get topic keywords
            model_path = self.model_dir + '/' + item['name']
            model_dirs = os.listdir(model_path)
            model_dirs = [dir for dir in model_dirs if not dir.endswith('.txt') and not dir.endswith('.mallet')]
            for file in os.listdir(model_path):
                if 'keys' in file:
                    keys_filepath = model_path + '/' + file
            # Add the topic keywords
            with open(keys_filepath, 'r') as f:
                keys = f.read().split('\n')
            keys = [re.sub('.+\t', '', line) for line in keys]
            keywords = {}
            for i, line in enumerate(keys):
                k = 'Topic' + str(i + 1)
                keywords[k] = line
            html = html.replace('var keywords = []', 'var keywords = ' + str(keywords))
            # Save the file
            with open(filename, 'w') as f:
                f.write(html)
            print('Saved ' + filename + '.')
            output_cache.append(filename)
        return output_cache

    def _get_model_meta(self):
        """Get a list of dicts with state paths and key paths for all models."""
        meta = []
        if self.models == []:
            self.models = [model for model in os.listdir(self.model_dir) if model.startswith('topics')]
        for model in self.models:
            model_num = model.replace('topics', '')
            meta.append(
                {'model': model,
                'state_path': self.model_dir + '/' + model + '/topic-state' + model_num + '.gz',
                'keys_path': self.model_dir + '/' + model + '/keys' + model_num + '.txt'
                })
        return meta

    def _make_partials_folder(self):
        """Make the partials folder if necessary."""
        if not os.path.exists(self.partials_path):
            os.makedirs(self.partials_path)

# State File Class
class State():
    """Convert Mallet state to a Python object.

    Parameters:
    - statefile: The path to mallet state file.
    """
    def __init__(self, statefile):
        """Initialize the object."""
        self.statefile = statefile
        self.df = self._state_to_df()
        self.alpha = self._extract_params()[0]
        self.beta = self._extract_params()[1]
        self.vocab = self._get_vocab()
        self.topic_state_format = self.topic_state_format()
        self.word_topic_assignments = self.word_topic_assignments()
        self.smoothed_word_topic_assignments = self.smoothed_word_topic_assignments()
        self.topic_term_matrix = self.topic_term_matrix()
        
    def _extract_params(self):
        """Extract the alpha and beta values from the statefile.

        Args:
            statefile (str): Path to statefile produced by MALLET.
        Returns:
            tuple: alpha (list), beta    
        """
        with gzip.open(self. statefile, 'r') as state:
            temp_params = [x.decode('utf8').strip() for x in state.readlines()[1:3]]
            params = (list(temp_params[0].split(":")[1].split(" ")), float(temp_params[1].split(":")[1]))
            alpha = [float(x) for x in params[0][1:]]
            beta = params[1]
        return (alpha, beta)

    def _state_to_df(self):
        """Transform state file into pandas dataframe.
        The MALLET statefile is tab-separated, and the first two rows contain the alpha and beta hypterparamters.
        
        Args:
            statefile (str): Path to statefile produced by MALLET.
        Returns:
            dataframe: topic assignment for each token in each document of the model
        """
        return pd.read_csv(self.statefile, compression='gzip', sep=' ', skiprows=[1,2])

    def topic_state_format(self):
        """Get Topic-State Format."""
        self.df['type'] = self.df.type.astype(str)
        return self.df

    def _get_vocab(self, sort_by='term_freq', ascending=False):
        """Get the vocabulary and term frequencies from the state file."""
        vocab = self.df['type'].value_counts().reset_index()
        vocab.columns = ['type', 'term_freq']
        return vocab.sort_values(by=sort_by, ascending=ascending)

    def _pivot_and_smooth(self, df, smooth_value, rows_variable, cols_variable, values_variable):
        """
        Turn the pandas dataframe into a data matrix.
        Args:
            df (dataframe): aggregated dataframe 
            smooth_value (float): value to add to the matrix to account for the priors
            rows_variable (str): name of dataframe column to use as the rows in the matrix
            cols_variable (str): name of dataframe column to use as the columns in the matrix
            values_variable(str): name of the dataframe column to use as the values in the matrix
        Returns:
            dataframe: pandas matrix that has been normalized on the rows.
        """
        matrix = df.pivot(index=rows_variable, columns=cols_variable, values=values_variable).fillna(value=0)
        matrix = matrix.values + smooth_value        
        normed = sklearn.preprocessing.normalize(matrix, norm='l1', axis=1)
        return pd.DataFrame(normed)

    def word_topic_assignments(self, sort_by='topic', ascending=True):
        """Get the word-topic assignments from the state file."""
        phi_df = self.df.groupby(['topic', 'type'])['type'].count().reset_index(name ='token_count')
        return phi_df.sort_values(by=sort_by, ascending=ascending)

    def smoothed_word_topic_assignments(self):
        """Get a smoothed version of the word-topic assignments from the state file.
        
        This returns phi, which is what is submitted to pyLDAvis.
        """
        return self._pivot_and_smooth(self.word_topic_assignments, self.beta, 'topic', 'type', 'token_count')

    def topic_term_matrix(self):
        df = self.word_topic_assignments.sort_values(['topic', 'token_count'], ascending=[True, False]).values
        num_topics = max(list(self.df['topic'].values + 1))
        # Convert the word-topic assignments to a list of lists
        topics = []
        for topic_num in range(0, num_topics):
            row = [x[2] for x in df if x[0] == topic_num]
            topics.append(row)
        # Even the length of the rows and add 0 to empty rows
        length = max(map(len, topics))
        ttm = np.array([topic+[0]*(length-len(topic)) for topic in topics])
        ttm.astype(int)
        return ttm
    
    def cluster(self, distance_metric='euclidean', linkage_method='average', filepath=None, height=600,
                width=1200, smoothed=True, orientation='top', truncate_mode=None, p=None,
                leaf_font_size=12, hovertext=None, color_threshold=None, save=True, standalone=False):
        if smoothed == True:
            ttm = self.smoothed_word_topic_assignments
        else:
            ttm = self.topic_term_matrix
        num_topics = len(ttm)
        labels = []
        i = 0
        while i < num_topics:
            j = i + 1 # index from 1
            labels.append('Topic' + str(j)) 
            i = i + 1
        distfun = lambda x: pdist(ttm, metric=distance_metric)
        if linkage_method == 'single':
            linkagefun = lambda x: single(ttm)
        elif linkage_method == 'complete':
            linkagefun = lambda x: complete(ttm)
        elif linkage_method == 'ward':
            linkagefun = lambda x: ward(ttm)
        else:
            linkagefun = lambda x: average(ttm)
        dendro = FF.create_dendrogram(ttm, orientation=orientation, labels=labels, distfun=distfun,
                                          linkagefun=linkagefun, hovertext=hovertext, color_threshold=color_threshold)
        dendro['layout'].update({'width': width, 'height': height})
        
        if save == False:
            py.iplot(dendro)
        if save == True and standalone == True:
            py.offline.plot(dendro, filename=filepath)
        if save == True and standalone == False:
            div = py.offline.plot(dendro, include_plotlyjs=False, output_type='div')
            with open(filepath, 'w') as f:
                f.write(div)

# Timer class              
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

        dendro['layout'].update({'width': width, 'height': height})
        
        if save == False:
            py.iplot(dendro)
        if save == True and standalone == True:
            py.offline.plot(dendro, filename=filepath)
        if save == True and standalone == False:
            div = py.offline.plot(dendro, include_plotlyjs=False, output_type='div')
            with open(filepath, 'w') as f:
                f.write(div)

# Timer class              
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
