"""mallet.py.

Generates a Mallet object with WE1S settings for MALLET topic modelling.
MALLET settings can be adjusted with commands like`Mallet.num_iterations = 500`.
`Mallet.import_models()` imports data to MALLET and `Mallet.train_models()`
trains the models.

For use with 02_model_topics.ipynb v 2.0.

Last update: 2020-07-06
"""

import json
import os
import re
import shlex
import shutil
import signal
import ipywidgets
from IPython.display import display, HTML
from ipywidgets import HBox, IntProgress, Label
from subprocess import check_output, CalledProcessError, PIPE, Popen, STDOUT

from timer import Timer

IntProgress(
    description='Processing:',
)

class Mallet:
    """Create a MALLET class object."""

    def __init__(self, num_topics, model_dir, import_file_path, import_source='file', num_iterations=1000,
                 optimize_interval=10, use_random_seed=True, random_seed=10, keep_sequence=True,
                 preserve_case=False, token_regex='"\S+"', remove_stopwords=False, extra_stopwords=None,
                 stoplist_file=None, generate_diagnostics=True):
        """Initialise the object."""
        self.num_topics = num_topics # List of integers
        self.model_dir = model_dir
        self.import_file_path = import_file_path
        self.import_source = import_source
        self.num_iterations = num_iterations
        self.optimize_interval = optimize_interval
        self.use_random_seed = use_random_seed
        self.random_seed = random_seed
        self.keep_sequence = keep_sequence
        self.preserve_case = preserve_case
        self.token_regex = token_regex
        self.remove_stopwords = remove_stopwords
        self.extra_stopwords = extra_stopwords
        self.stoplist_file = stoplist_file
        self.generate_diagnostics = generate_diagnostics
        self.model_vars = {}
        self.import_command = ''
        self.train_command = ''
        try:
            self.build_subdirs()
            display(HTML('<h4>Setup complete.</h4>'))
        except RuntimeError:
            display(HTML('<h4 style="color:red;">There was an error setting up your model directories.</h4>'))
        
    def build_subdirs(self, delete_existing=False):
        """Create subdirectories for each model and a dict to store variables for use with each model.
        
        Parameters:
        - delete_existing (Bool): Delete existing model subdirectories before building the model_vars dict.
        """
        for topic in self.num_topics:
            model_num_topics = str(topic)
            subdir = self.model_dir + '/topics' + model_num_topics
            if delete_existing == True:
                if os.path.exists(subdir):
                    shutil.rmtree(subdir)
                os.makedirs(subdir)
            else:
                if not os.path.exists(subdir):
                    os.makedirs(subdir)
            self.model_vars[model_num_topics] = {
                'model_file': 'topics' + model_num_topics + '.mallet',
                'model_state': 'topic-state' + model_num_topics + '.gz',
                'model_keys': 'keys' + model_num_topics + '.txt',
                'model_composition': 'composition' + model_num_topics + '.txt',
                'model_counts': 'topic_counts' + model_num_topics + '.txt',
                'diagnostics_file': 'diagnostics' + model_num_topics + '.xml',
                'model_topic_docs':'topic-docs' + model_num_topics + '.txt'
            }

    def import_data(self, num_topics):
        """Import doc-terms data to MALLET for a single model.
        
        Parameters:
        - num_topics (str): The number of topics in the model. 
        """
        timer = Timer()
        # Define model variables
        model_vars = self.model_vars[num_topics]
        subdir = self.model_dir + '/topics' + num_topics
        output_path = subdir + '/' + model_vars['model_file']        
        # Add arguments
        args = []
        if self.keep_sequence == True:
            args.append('--keep-sequence')
        if self.preserve_case == True:
            args.append('--preserve-case')
        if self.remove_stopwords == True:
            args.append('--remove-stopwords')
        if self.extra_stopwords == True:
            args.append('--exta-stopwords')
        if self.token_regex is not None:
            args.append('--token-regex ' + self.token_regex)
        if self.stoplist_file is not None:
            args.append('--stoplist-file ' + self.stoplist-file)
        args = ' '.join(args)
        mallet_import_args = '--input ' + self.import_file_path + ' --output ' + output_path + ' ' + args
        self.import_command = 'mallet import-' + self.import_source + ' ' + mallet_import_args
        # Perform the import
        try:
            # shell=True required to handle backslashes in token-regex
            output = check_output(self.import_command, stderr=STDOUT, shell=True, universal_newlines=True)
            display(HTML('<h4>Import for topics' + num_topics + ' complete!</h4>'))
            print('Time elapsed: %s' % timer.get_time_elapsed())
            return True
        except CalledProcessError as e:
            output = e.output.decode()
            display(HTML('<p style="color: red;">' + output + '</p>'))
            print('Time elapsed: %s' % timer.get_time_elapsed())
            return False

    def import_models(self, models=None):
        """Import doc_terms data to MALLET from multiple models.
        
        Parameters:
        - models (list): A list of model numbers to be imported. By default this is the number given when the object was initialised. 
        """
        if models is None:
            models = self.num_topics
        for topic_num in models:
            try:
                result = self.import_data(str(topic_num))
            except RuntimeError:
                display(HTML('<p style="color: red;">Import failed for topics' + str(topic_num) + '. Training will be skipped for this model.</p>'))

    def train(self, num_topics, display_output=False, capture_output=False, progress_bar=True, log_file=None):
        """Train a single topic model.
        
        Parameters:
        - num_topics (str): The number of topics in the model.
        
        Progress monitor borrowed from TETHNE: https://diging.github.io/tethne/_modules/tethne/model/corpus/mallet.html
        """
        # Define model variables
        timer = Timer()
        model_vars = self.model_vars[num_topics]
        subdir = self.model_dir + '/topics' + num_topics
        mallet_file = subdir + '/' + model_vars['model_file']        
        ll = []
        num_iters = 0
        prog = re.compile(u'\<([^\)]+)\>')
        ll_prog = re.compile(r'(\d+)')
        command = [
            'mallet',
            'train-topics',
            '--input', mallet_file,
            '--num-topics', str(num_topics),
            '--num-iterations', str(self.num_iterations),
            '--optimize-interval', str(self.optimize_interval),
            '--output-state', subdir + '/' + model_vars['model_state'],
            '--output-topic-keys', subdir + '/' + model_vars['model_keys'],
            '--output-doc-topics', subdir + '/' + model_vars['model_composition'],
            '--word-topic-counts-file', subdir + '/' + model_vars['model_counts'],
            '--output-topic-docs', subdir + '/' + model_vars['model_topic_docs']
        ]
        if self.use_random_seed == True:
            command = command + ['--random-seed', str(self.random_seed)]
        if self.generate_diagnostics == True:
            command = command + ['--diagnostics-file', subdir + '/' + model_vars['diagnostics_file']]
        self.train_command = ' '.join(command)
        command = shlex.split(self.train_command)
        # Simply capture the output and print it at the end
        if capture_output == True:
            output = check_output(command, stderr=STDOUT)
            print(output.decode())
            if log_file is not None:
                with open(log_file, 'w') as f:
                    f.write(output.decode())
        # Otherwise, monitor the MALLET output in real time
        else:
            if progress_bar is not False and display_output == False:
                pbar = IntProgress(min=0, max=100) # instantiate the progress bar
                percent = ipywidgets.HTML(value='0%')
                display(HBox([Label('topics' + str(num_topics)), pbar, percent]))
            p = Popen(command, stdout=PIPE, stderr=STDOUT)
            while p.poll() is None:
                l = p.stdout.readline().decode()
                if display_output == True:
                    print(l, end='')
                if log_file is not None:
                    with open(log_file, 'a') as f:
                        f.write(l)
                # Keep track of LL/topic.
                try:
                    this_ll = float(re.findall('([-+]\d+\.\d+)', l)[0])
                    ll.append(this_ll)
                except IndexError:  # Not every line will match.
                    pass
                # Keep track of modeling progress
                try:
                    this_iter = float(prog.match(l).groups()[0])
                    progress = int(100. * this_iter/self.num_iterations)
                    if progress_bar is not False and display_output == False:
                        pbar.value = progress
                        percent.value = '{0}%'.format(progress)
                    else:
                        if progress % 10 == 0:
                            print('Modeling progress: {0}%.\r'.format(progress)),
                except AttributeError:  # Not every line will match.
                    pass
            num_iters += self.num_iterations
        display(HTML('<h4>Training of topics' + num_topics + ' complete.</h4>'))
        print('Time elapsed: %s' % timer.get_time_elapsed())

    def train_models(self, models=None, display_output=False, capture_output=False, progress_bar=True, log_file=None):
        """Train imported data for multiple models.
        
        Parameters:
        - models (list): A list of model numbers to be imported. By default this is the number given when the object was initialised.       
        """
        if models is None:
            models = self.num_topics
        for topic_num in models:
            display(HTML('<h4>Training topics' + str(topic_num) + '...</h4>'))
            try:
                result = self.train(str(topic_num),
                                    display_output,
                                    capture_output=capture_output,
                                    progress_bar=progress_bar,
                                    log_file=log_file)
            except RuntimeError:
                display(HTML('<p style="color: red;">Error! Training failed for topics' + str(topic_num) + '.</p>'))
