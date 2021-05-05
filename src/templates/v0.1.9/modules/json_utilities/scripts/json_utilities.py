"""json_utilities.py.

Generates a `Documents` object with methods for accessing the contents of 
project's `json` folder.

Last update: 2021-01-29
"""


# Python imports
import json
import os
import operator
import re
import shutil
import tempfile
import ipywidgets
import pandas as pd
import qgrid
from IPython.display import clear_output, display, HTML
from ipywidgets import HBox, IntProgress, Label
from natsort import natsorted
from time import time

# Constants
OPERATORS = {
    "<": operator.lt,
    "<=": operator.le,
    "=": operator.eq,
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "contains": operator.contains,
    "regex": None
}

# Qgrid options
qgrid_options = {
    # SlickGrid options
    'fullWidthRows': True,
    'syncColumnCellResize': True,
    'forceFitColumns': False,
    'defaultColumnWidth': 110,
    'rowHeight': 28,
    'enableColumnReorder': True,
    'enableTextSelectionOnCells': False,
    'editable': False,
    'autoEdit': False,
    'explicitInitialization': True,
    # Qgrid options
    'maxVisibleRows': 15,
    'minVisibleRows': 8,
    'sortable': True,
    'filterable': True,
    'highlightSelectedCell': False,
    'highlightSelectedRow': True
}

# Functions
def make_archive(source, destination):
    base_name = '.'.join(destination.split('.')[:-1])
    format = destination.split('.')[-1]
    root_dir = os.path.dirname(source)
    base_dir = os.path.basename(source.strip(os.sep))
    shutil.make_archive(base_name, format, root_dir, base_dir)
    
def regex_match(doc_field, filter_val):
    """Match a regex pattern and return a Boolean."""
    return bool(re.search(re.compile(filter_val), str(doc_field)))

# Classes
class Documents():
    """Search class."""

    def __init__(self, project_dir, data_dir='project_data', json_dir='json'):
        """Initialise a search."""
        self.project_dir = project_dir
        self.data_dir = os.path.join(self.project_dir, data_dir)
        self.json_dir = os.path.join(self.data_dir, json_dir)
        self.count = self.count_docs()

    # Private methods            
    def _match_filter(self, doc, query, lower_case=False):
        """Test a field for a value using a filter and return a Boolean."""
        if query[0] in doc:
            doc_field = doc[query[0]]
            if lower_case == True and isinstance(doc_field, str):
                doc_field = doc_field.lower()
            op = query[1]
            filter_val = query[2]
            if op == 'regex':
                result = regex_match(doc_field, filter_val)
            else:
                result = OPERATORS[op](doc_field, filter_val)
            return result
        else:
            self._show_error('The supplied field name' + str(query[0]) + ' does not exist in ' + doc['name'] + '.')

    def _perform_queries(self, doc, filename, queries, lower_case=False):
        """Iterate through a list of queries.

        Returns a list of doc names that match all the queries.
        """
        hits = []
        for query in queries:
            if isinstance(query, tuple):
                result = self._match_filter(doc, query, lower_case=lower_case)
                if result == True:
                    hits.append(filename)
            elif isinstance(query, dict):
                bool_op = list(query.keys())[0].lower()
                evals = []
                for subquery in list(query.values())[0]:
                    result = self._match_filter(doc, subquery, lower_case=lower_case)
                    evals.append(result)
                if bool_op == 'or' and True in evals:
                    hits.append(filename)
                elif bool_op == 'and' and False not in evals:
                    hits.append(filename)
        return list(set(hits))

    def _show_error(self, msg):
        """Show an error."""
        display(HTML('<p style="color: red;">' + msg + '</p>'))

    # Public methods
    def count_docs(self, file_list=None):
        """Count the number of files in a file list."""
        if file_list is None:
            return len(self.get_file_list())
        else:
            return len(file_list)

    def export(self, docs, zip_filepath='export.zip', text_only=False):
        """Create a zip archive of a list of documents."""
        clear_output()
        timer = Timer()
        # Set up the progress bar
        step = 0
        export_pbar = IntProgress(min=0, max=100) # instantiate the progress bar
        export_percent = ipywidgets.HTML(value='0%')
        display(HBox([Label('Progress:'), export_pbar, export_percent]))
        with tempfile.TemporaryDirectory() as temp_dir:
            for file in docs:
                if text_only == True:
                    with open(os.path.join(self.json_dir, file), 'r') as f:
                        doc = json.loads(f.read())
                    with open(os.path.join(temp_dir, file.replace('.json', '.txt')), 'w') as f:
                        f.write(doc['content'])
                else:
                    shutil.copy(os.path.join(self.json_dir, file), os.path.join(temp_dir, file))
                # Keep track of progress
                export_progress = int(100. * step/len(docs))
                export_pbar.value = export_progress
                export_percent.value = '{0}%'.format(export_progress)
                step = step + 1
            destination_dir = os.path.split(zip_filepath)[0]
            if destination_dir != '' and not os.path.exists(destination_dir):
                os.makedirs(destination_dir)
            make_archive(temp_dir, zip_filepath)
        export_pbar.value = 100
        export_percent.value = '{0}%'.format(100)
        display(HTML('<p style="color: green;">Export complete.</p>'))
        print('Time elapsed: %s' % timer.get_time_elapsed())
        
    def find(self, docs, query, lower_case=False):
        """Iterate through the document list and return query results."""
        clear_output()
        hits = []
        if not isinstance(query, list):
            query = [query]
        # Set up the progress bar
        step = 1
        pbar = IntProgress(min=0, max=100) # instantiate the progress bar
        percent = ipywidgets.HTML(value='0%')
        display(HBox([Label('Progress:'), pbar, percent]))
        for filename in docs:
            doc = self.read(filename)
            for result in self._perform_queries(doc, filename, query):
                hits.append(result)
            # Keep track of progress
            progress = int(100. * step/len(docs))
            pbar.value = progress
            percent.value = '{0}%'.format(progress)
            step = step + 1
        result = list(set(hits))
        if len(result) == 0:
            self._show_error('Your query returned no results.')
        else:
            return result

    def get_file_list(self, start=0, end=None):
        """Get a list of files from the json_dir."""
        return [file for file in os.listdir(self.json_dir) if file.endswith('json')][start:end]
    
    def get_table(self, docs, columns):
        """Iterate through the document list and return docs in a dataframe."""
        clear_output()
        df = pd.DataFrame(columns=columns)
        # Set up the progress bar
        step = 1
        pbar = IntProgress(min=0, max=100) # instantiate the progress bar
        percent = ipywidgets.HTML(value='0%')
        display(HBox([Label('Progress:'), pbar, percent]))
        for filename in docs:
            doc = self.read(filename)
            dict_fields = {k: v for k, v in doc.items() if k in columns}
            df = df.append(dict_fields, ignore_index=True)
            # Keep track of progress
            progress = int(100. * step/len(docs))
            pbar.value = progress
            percent.value = '{0}%'.format(progress)
            step = step + 1
        df.fillna('', inplace=True)
        qgrid_widget = qgrid.show_grid(df, grid_options=qgrid_options, show_toolbar=False)
        if df.shape[0] > 0:
            return qgrid_widget
        else:
            self._show_error('There was an error or none of the documents contain the specified field names.')
        
    def read(self, filename):
        """Load a doc file into a dict."""
        try:
            with open(os.path.join(self.json_dir, filename), 'r') as f:
                doc = json.loads(f.read())
            return doc
        except IOError:
            display(HTML('<p style="color: red;">Could not find the file. Make sure that you have provided a correct filename in the <code>doc = docs.read()</code> line above.</p>'))
            return {'content': 'File not found.'}

    def get_metadata_keys(self, start=0, end=None, file_list=None):
        """Get the keys for every doc in a list of files."""
        clear_output()
        # Set up the progress bar
        step = 1
        pbar = IntProgress(min=0, max=100) # instantiate the progress bar
        percent = ipywidgets.HTML(value='0%')
        display(HBox([Label('Progress:'), pbar, percent]))
        if file_list is None:
            file_list = self.get_file_list(start, end)
        else:
            file_list = file_list[start:end]
        keys = set()
        for filename in file_list:
            with open(os.path.join(self.json_dir, filename), 'r') as f:
                doc = json.loads(f.read())
            for key in list(doc.keys()):
                keys.add(key)
            # Keep track of progress
            progress = int(100. * step/len(file_list))
            pbar.value = progress
            percent.value = '{0}%'.format(progress)
            step = step + 1
        return natsorted(list(keys))

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
