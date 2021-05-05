"""model.py.

Last update: 2021-02-19.
"""

# Python imports
import gzip
import numpy as np
import os
import pandas as pd
import re
import shutil
import tempfile
import sklearn.preprocessing
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup as bs
from IPython.display import display, HTML
from pathlib import Path
from time import time
from scipy.cluster.hierarchy import linkage, dendrogram, average, single, complete, ward
from scipy.spatial.distance import pdist
import plotly.offline as py
import plotly.graph_objs as go
import plotly.figure_factory as FF

# Adjust the height and width of inline dengrograms
plt.rcParams['figure.figsize']  = [15, 15]

# Functions
def create_index_file(index_filename, selection, model_dir, page_title, source_filenames, menu_items,
                      dendrogram_titles, PORT=None, zip=False):
    """Create the index file."""
    try:
        # Open the index template file
        with open('scripts/index_template.html', 'r') as f:
            html = f.read()
        # Inject some html, css, and javascript
        html = html.replace('<title></title>', '<title>' + page_title +'</title>')
        titles = {}
        list_items = '<li class="nav-item active"><a class="nav-link" href="' + source_filenames[0] + '">' + menu_items[0] + ' <span class="sr-only">(current)</span></a></li>\n'
        for i, item in enumerate(source_filenames):
            titles[source_filenames[i]] = dendrogram_titles[i]
            if i is not 0:
                list_items += '<li class="nav-item"><a class="nav-link" href="' + source_filenames[i] + '">' + menu_items[i] + '</a></li>\n'
        html = html.replace('<a class="navbar-brand" href="#"></a>', '<a class="navbar-brand" href="#">' + page_title + '</a>')
        html = html.replace('<ul class="navbar-nav"></ul>', '<ul class="navbar-nav">' + list_items + '</ul>')
        html = html.replace('var titles = {}', 'var titles = ' + str(titles))
        html = html.replace('<h3 id="title" class="text-center" style="display: none;"></h3>', '<h3 id="title" class="text-center" style="display: none;">' + dendrogram_titles[0] + '</h3>')
        html = html.replace("url='.html'", "url='" + source_filenames[0] + "'")
        # Get topic state and keys files
        topic_state_file, keys_filepath = get_model_data(selection, model_dir)
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
        with open(index_filename, 'w') as f:
            f.write(html)
        current_reldir = os.getcwd().split("/write/")[1]
        if zip == True:
            zip_filename = index_filename.replace('.html', '')
            with tempfile.TemporaryDirectory() as temp_dir:
                shutil.copy(index_filename, os.path.join(temp_dir, index_filename))
                shutil.copytree(os.getcwd() + '/partials', temp_dir + '/partials')
                shutil.make_archive(os.getcwd() + '/' + zip_filename, 'zip', temp_dir)
        if PORT is not None and PORT != '':
            vis_path = ':' + PORT + '/' + current_reldir + '/' + index_filename
        else:
            vis_path = current_reldir + '/' + index_filename
        link = '<a target="_blank" href="#" onmouseover="event.srcElement.href = \'http://\' + window.location.hostname + \'' + vis_path + '\';">View Private Dendrogram Index</a>'
        display(HTML('<p style="color: green;">Done! ' + link + '</p>'))
    except Exception:
        msg = '<p style="color: red;">Something wrong! Your dendrogram files could not be published.</p>'
        display(HTML(msg))

def get_model_data(model, model_dir):
    """Get topic state and keys files for a model."""
    model_num = model.replace('topics', '')
    keys_file_path = model_dir + '/' + model + '/keys' + model_num + '.txt'
    state_file_path = model_dir + '/' + model + '/topic-state' + model_num + '.gz'
    return state_file_path, keys_file_path

def make_partials_path(partials_path):
    """Create the partials folder, if necessary."""
    if not os.path.exists(partials_path):
        os.makedirs(partials_path)


# Clasess
class Model():
    """Convert Mallet state to a Python object.

    @statefile (str): The path to mallet state file.
    """
    def __init__(self, statefile, keys_filepath, partials_path, title=None, current_dir=os.getcwd(), WRITE_DIR=None, PORT=None):
        """Initialize the object."""
        timer = Timer()
        self.statefile = statefile
        self.keys_filepath = keys_filepath
        self.partials_path = partials_path
        self.title = title
        self.current_dir = current_dir
        self.project_dir = str(Path(current_dir).parent.parent)
        self.WRITE_DIR = WRITE_DIR
        self.PORT = PORT
        self.df = self._state_to_df()
        self.alpha = self._extract_params()[0]
        self.beta = self._extract_params()[1]
        self.vocab = self._get_vocab()
        self.topic_state_format = self.topic_state_format()
        self.word_topic_assignments = self.word_topic_assignments()
        self.smoothed_word_topic_assignments = self.smoothed_word_topic_assignments()
        self.topic_term_matrix = self.topic_term_matrix()
        display(HTML('<p style="color:green;">Model loaded.</p>'))
        print('Time elapsed: %s' % timer.get_time_elapsed())

    def cluster(self, distance_metric='euclidean', linkage_method='average', filename=None, height=600,
                width=1200, smoothed=True, orientation='bottom', truncate_mode=None, p=None,
                leaf_font_size=12, hovertext=None, color_threshold=None, standalone=False, save=True):
        """Perform a cluster analysis.
        
        @distance_metric (str): 'euclidean' or 'cosine'
        @linkage_method (str): 'single', 'complete', 'average', 'ward'
        @filename (str): The name of the dendrogram file to save
        @height (int): The height of the dendrogram in pixels
        @width (int): The width of the dendrogram in pixels
        @smoothed (bool): Whether or not the values are smoothed
        @orientation (str): 'top', 'left', 'bottom', or 'right'
        @truncate_mode ():
        @p ():
        @leaf_font_size (int): The size of the leaf font in pxels
        @hovertext ():
        @color_threshold ():
        """
        if filename is None or os.path.isdir(filename) or filename == '':
            display(HTML('<p style="color:red;">Please add a filename to the configuration settings.</p>'))
        else:
            # Make sure the filename has an .html extension
            filepath=os.path.join(self.partials_path, os.path.splitext(filename)[0] + '.html')
            display(HTML('<p>Clustering topics...</p>'))
            timer = Timer()
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
            distfun = lambda x: pdist(ttm, distance_metric)
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
            display(HTML('<p style="color:green;">Clustering is complete.</p>'))
            print('Time elapsed: %s' % timer.get_time_elapsed())

    def _extract_params(self):
        """Extract the alpha and beta values from the statefile.

        @statefile (str): Path to statefile produced by MALLET.

        Returns a tuple: alpha (list), beta
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
        
        @statefile (str): Path to statefile produced by MALLET.
        
        Returns a dataframe with the topic assignment for each token in each document of the model
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
        
        @df (dataframe): aggregated dataframe 
        @smooth_value (float): value to add to the matrix to account for the priors
        @rows_variable (str): name of dataframe column to use as the rows in the matrix
        @cols_variable (str): name of dataframe column to use as the columns in the matrix
        @values_variable(str): name of the dataframe column to use as the values in the matrix
        
        Returns a dataframe: pandas matrix that has been normalized on the rows.
        """
        matrix = df.pivot(index=rows_variable, columns=cols_variable, values=values_variable).fillna(value=0)
        matrix = matrix.values + smooth_value        
        normed = sklearn.preprocessing.normalize(matrix, norm='l1', axis=1)
        return pd.DataFrame(normed)
    
    def save(self, partials_path, filename, save_path=None):
        """Save the dendrogram file."""
        filename = os.path.splitext(filename)[0] + '.html'
        try:
            # Open the dendrogram div file and inject some html, css, and javascript code
            with open(os.path.join(partials_path, filename), 'r') as f:
                html = f.read()    
            head = '<html><head><meta charset="utf-8"><title>' + self.title + '</title>'
            head2 = """<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <script
              src="https://code.jquery.com/jquery-3.4.1.slim.min.js"
              integrity="sha256-pasqAKBDmFT4eHoN2ndd6lN370kFiGUFyTiUHWhU7k8="
              crossorigin="anonymous"></script>
                <script type="text/javascript">window.PlotlyConfig = {MathJaxConfig: 'local'};</script>
                <style type="text/css">
                    #cluster_graph {
                        width: 1200px;
                        margin: auto;
                        margin-left: 100px;
                        height: 600px;
                    }
                    #topic-keys-div {
                      margin: auto;
                      margin-left: 100px;

                    }
                    .xaxislayer-above, x.tick {
                      cursor: pointer;
                      pointer-events: all;
                    }
                </style>
            </head>
            <body>"""
            head += head2
            head += '<h3 class=text-center>' + self.title + '</h3><div id="cluster_graph">'
            html = head + html + '</div><div id="topic-keys-div"><span id="topic-keys-label" style="font-weight: bold;">Hover over Topic Labels to View Topic Keywords</span> <span id="topic-keys"></span></div></div></body></html>'
            # Add the topic keywords and hover behaviour
            with open(self.keys_filepath, 'r') as f:
                keys = f.read().split('\n')
            keys = [re.sub('.+\t', '', line) for line in keys]
            keywords = {}
            for i, line in enumerate(keys):
                k = 'Topic' + str(i + 1)
                keywords[k] = line
            script = """<script>
                    $(document).on('mouseenter', '.xtick', function() {
                        var keywords = []
                        $('#topic-keys-label').html($(this).children().eq(0).text() + ':')
                        $('#topic-keys').html(keywords[$(this).children().eq(0).text()])
                    })
                </script>"""
            html = html.replace('</style>', '</style>\n' + script)
            html = html.replace('var keywords = []', 'var keywords = ' + str(keywords))
            # Save the file
            if save_path is None:
                save_path = os.getcwd()
            with open(os.path.join(save_path, filename), 'w') as f:
                f.write(html)
            current_reldir = self.current_dir.split("/write/")[1]
            if self.PORT is not None and self.PORT != '':
                vis_path = ':' + self.PORT + '/' + current_reldir + '/' + filename
                link = '<a target="_blank" href="#" onmouseover="event.srcElement.href = \'http://\' + window.location.hostname + \'' + vis_path + '\';">View Dendrogram</a>'
                display(HTML('<p style="color: green;">Done! ' + link + '</p>'))
        except Exception:
            display(HTML('<p style="color: red;">Error! The dendrogram file could not be generated.</p>'))

    def smoothed_word_topic_assignments(self):
        """Get a smoothed version of the word-topic assignments from the state file.
        
        Returns a datafrapme phi.
        """
        return self._pivot_and_smooth(self.word_topic_assignments, self.beta, 'topic', 'type', 'token_count')

    def topic_term_matrix(self):
        """Get the document-topic matrix."""
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

    def word_topic_assignments(self, sort_by='topic', ascending=True):
        """Get the word-topic assignments from the state file."""
        phi_df = self.df.groupby(['topic', 'type'])['type'].count().reset_index(name ='token_count')
        return phi_df.sort_values(by=sort_by, ascending=ascending)
                

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
