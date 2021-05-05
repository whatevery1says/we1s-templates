"""topic_weights.py.

Functions supporting `topic_statistics_by_metadata.ipynb`.

Last update: 2020-07-29
"""

# Python imports
import ipywidgets
import json
import os
import re
import shutil
import tempfile
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import qgrid
from collections import Counter, defaultdict
from datetime import datetime
from IPython.display import display, HTML
from ipywidgets import HBox, IntProgress, Label

# plotly standard imports
import plotly.graph_objs as go
import chart_studio.plotly as py

# Cufflinks wrapper on plotly
import cufflinks

# Display all cell outputs
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = 'all'

# Import plotly offline
from plotly.offline import iplot
cufflinks.go_offline()

# Set global cufflinks theme
cufflinks.set_config_file(world_readable=True, theme='pearl')

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
    'maxVisibleRows': 10,
    'minVisibleRows': 5,
    'sortable': True,
    'filterable': True,
    'highlightSelectedCell': False,
    'highlightSelectedRow': True
}

# Functions

def bar_plot(df, start, end, columns, title, xlabel, ylabel, legend_labels, stacked=False, save_path=None):
    """Plot a bar plot with matplotlib."""
    start = start - 1
    query = [i for i in df.columns.values.tolist() if i in columns]
    tmp_df = df[query][start:end]
    tmp_df.columns = legend_labels
    tmp_df = tmp_df.astype('float')
    ax = tmp_df.plot(kind='bar', title=title, figsize=(15, 10), legend=True, fontsize=12, stacked=stacked)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_xticklabels([str(int(item.get_text())) for item in ax.get_xticklabels()])
    if save_path is not None:
        plt.savefig(save_path)
        
def export_top_docs_as_text(df, json_dir, save_path=''):
    """Export the `content` fields of the top documents to text files."""
    unique_files = list(set(df.name.values.tolist()))
    bad_json = []
    saved_files = 0
    if save_path == None:
        save_path = ''
    if save_path != '' and not os.path.exists(save_path):
        os.makedirs(save_path)
    display(HTML('<p>Exporting ' + str(len(unique_files)) + ' files ...</p>'))
    pbar = IntProgress(min=0, max=100) # instantiate the progress bar
    percent = ipywidgets.HTML(value='0%')
    display(HBox([Label('Progress'), pbar, percent]))
    temp_dir = tempfile.mkdtemp()
    for i, filename in enumerate(unique_files):
        j = i + 1
        filepath = os.path.join(json_dir, filename)
        try:
            with open(filepath, 'r') as f:
                doc = json.loads(f.read())
            if 'content' not in doc or doc['content'] == '':
                bad_json.append(filename)
            else:
                filepath = os.path.join(temp_dir, re.sub('.json$', '.txt', filename))
                with open(filepath, 'w') as f:
                    f.write(doc['content'])
            saved_files += 1
        except IOError:
            bad_json.append(filename)
        progress = int(100. * j/len(unique_files))
        pbar.value = progress
        percent.value = '{0}%'.format(progress)
    display(HTML('<p>Creating zip archive...</p>'))
    zip_location = os.path.join(save_path, datetime.now().strftime('export_%Y%m%d%H%M%S.zip'))
    make_archive(temp_dir, zip_location)
    display(HTML('<p style="color:green;">' + str(saved_files) + ' text files were exported to ' + zip_location + '.</p>'))
    shutil.rmtree(temp_dir)
    if len(bad_json) > 0:
        display(HTML('<p style="color:red;">The following json files could not be read.</p></ul>'))
        ul = ''
        for filename in bad_json:
            ul += '<li>' + filename + '</li>'
        display(HTML(ul))

def filter_df(df, filter_column, by, save_path=None):
    """Implement a general dataframe filter method."""
    df = df[df[filter_column].str.contains(by, na=False)]
    if save_path is not None:
        df.to_csv(save_path)
    return df

def generate_topic_doc_dict(df, save_path=None):
    """Get top documents by topic."""
    topic_docs_dict = {}
    table = df.groupby('#topic', as_index=False)
    table = df.groupby('#topic').agg(lambda g: dict([(k, g[k].tolist()) for k in g]))
    table = table[['name']].copy()
    for i, row in enumerate(table.index):
        filenames = table.iloc[0].values.tolist()[0]
        topic_docs_dict[i + 1] = filenames
    if save_path is not None:
        with open(save_path, 'w') as f:
            f.write(json.dumps(topic_dict, indent=2))
    return topic_docs_dict

def get_counts(df, field, save_path=None):
    """Get the topic counts by a particular field"""
    counts_df = df[['#topic', field, 'doc']].copy()    
    counts = counts_df.groupby(['#topic', field]).count()
    counts.rename(columns={'doc': 'Number of Docs'}, inplace=True)
    counts = counts.unstack(fill_value=0)
    counts.columns = counts.columns.get_level_values(1)
    counts.columns.name = ''
    counts.index.name = ''
    if save_path is not None:
        counts.to_csv(save_path)
    return counts

def make_archive(source, destination):
    base_name = '.'.join(destination.split('.')[:-1])
    format = destination.split('.')[-1]
    root_dir = os.path.dirname(source)
    base_dir = os.path.basename(source.strip(os.sep))
    shutil.make_archive(base_name, format, root_dir, base_dir)

def get_metadata(df, fields, selection, json_dir, from_file=False, data_path='data', save_path=None, preview=5):
    """Gather the collection metadata from the filenames in a dataframe."""
    num_topics = selection.replace('topics', '')
    if from_file == True and os.path.exists(os.path.join(data_path, 'topic_docs_metadata' + num_topics + '.parquet')):
        metadata_df = pd.read_parquet(os.path.join(data_path, 'topic_docs_metadata' + num_topics + '.parquet'))
    else:
        files = df.name.values.tolist()
        bad_json = []
        file_rows =[]
        for filename in files:
            try:
                with open(os.path.join(json_dir, filename), 'r') as f:
                    doc = f.read()
                try:
                    doc = json.loads(doc)
                    try:
                        field_vals = {}
                        for field in fields:
                            if field == 'tags':
                                for k, v in tags_to_dict(doc).items():
                                    field_vals[k] = v
                            else:
                                field_vals[field] = doc[field]
                        file_rows.append(field_vals)
                    except ValueError:
                        if filename not in bad_json:
                            bad_json.append(filename)
                except ValueError as err:
                    if filename not in bad_json:
                        bad_json.append(filename)
            except IOError:
                if filename not in bad_json:
                    bad_json.append(filename)
        if len(bad_json) > 0:
            display(HTML('<p style="color:red;">The following json files could not be read.</p><ul>'))
            ul = ''
            for filename in bad_json:
                ul += '<li>' + filename + '</li>'
            display(HTML(ul))
        metadata_df = pd.DataFrame(file_rows)
        metadata_df.to_parquet(os.path.join(data_path, 'topic_docs_metadata' + num_topics + '.parquet'))
    if save_path is not None:
        metadata_df.to_csv(save_path)
    return metadata_df

def plotly_bar_plot(df, start, end, columns, title, xlabel, ylabel, legend_labels, save_path=None):
    start = start-1
    num_topics = df.shape[0]
    query = [i for i in df.columns.values.tolist() if i in columns]
    df = df[query][start:end]
    df.columns = legend_labels
    df = df.astype('float')
    tickvals = [i for i in range(0, num_topics + 1)]
    ticktext = [str(i) for i in tickvals]
    layout = go.Layout(
        title=title,
        xaxis=go.layout.XAxis(
        showticklabels=True,
        linewidth=1,
        tickmode='array',
        tickvals=tickvals,
        ticktext=ticktext
    ))
    if save_path is not None:
        save_path = save_path.replace('.html', '')
        fig = df.iplot(
            kind='bar',
            xTitle=xlabel,
            yTitle=ylabel,
            linecolor='black',
            sortbars=True,
            layout=layout,
            filename=save_path,
            asPlot=True)
        save_file = save_path + '.html'
        msg = '<h4>Plot saved.</h4><p>View it at <a href="' + save_file + '" target="_blank">' + save_file + '</a></p>'
        display(HTML(msg))
    else:
        display(HTML('<h4>To view a larger version in a saved file, use the <code>save_path</code> setting.</h4>'))
        df.iplot(
            kind='bar',
            barmode='relative',
            xTitle=xlabel,
            yTitle=ylabel,
            linecolor='black',
            sortbars=True,
            layout=layout)
        
def save_to_csv(source, save_path, use_original=False):
    try:
        if not isinstance(source, pd.DataFrame) and use_original == False:
            source = source.get_changed_df()
        elif not isinstance(source, pd.DataFrame) and use_original == True:
            source = source.df
        source.to_csv(save_path)
        display(HTML('<p style="color: green;">Done!</p>'))
    except IOError:
        msg = 'The file could not be saved. Check that your source is a pandas dataframe or qgrid widget and that you have supplied a valid filepath.'
        display(HTML('<p style="color: red;">' + msg + '</p>'))

def start_export(df, json_dir, topic_num='all', save_path=None):
    """Check the topic_num configuration and then start the export."""
    if isinstance(topic_num, str):
        if topic_num.isdigit():
            topic_num = int(topic_num)
        else:
            topic_num = topic_num.lower()
    if isinstance(topic_num, int):
        df = df[df['#topic'] == topic_num]
    export_top_docs_as_text(df, json_dir, save_path=save_path)

def tags_to_dict(doc):
    """Process the tags from a single document and return a dict.

    Assumes a tag schema with the fields in `fields`. Boolean values are represented as '0' and '1'.
    Also retrieves the `country` and `language` fields as tags if they are present in the document.
    """
    # Initialise dict with all fields
    d = {'education': '0'}
    fields = ['affiliation', 'demographic', 'emphasis', 'funding', 'identity', 'institution', 'media', 'perspective', 'politics', 'reach', 'region', 'religion']
    for prop in fields:
        d[prop] = '0'
    # Add country and language if available
    if 'country' in doc:
        d['country'] = doc['country']
    if 'language' in doc:
        d['language'] = doc['language']
    # If the doc contains tags...
    if 'tags' in doc:
        # Iterate through the doc tags
        for tag in doc['tags']:
            # Set education to True if the education tag is detected
            if re.search('^education', tag):
                d['education'] = '1'
                tag = re.sub('^education/', '', tag)
            # Find all subtags and get the penult as the key
            subtag_properties = '^demographic|^emphasis|^funding|^identity|^institution|^media|^politics|^reach|^region|^religion'
            subtags = re.findall(subtag_properties, tag)
            if len(subtags) > 0:
                tail = tag.split('/')
                head = tail.pop(0)
                tail = '/'.join(tail)
                if tail.startswith('demographic/religion/'):
                    head = 'religion'
                    tail = tail.replace('demographic/religion/', '')
                if head.startswith('demographic'):
                    head = 'demographic'
                    tail = tail.replace('demographic/', '')
                if head.startswith('affiliation'):
                    head = 'affiliation'
                    tail = tail.replace('affiliation/', '')
                if head.startswith('institution'):
                    head = 'institution'
                    tail = tail.replace('institution/', '')
                if head.startswith('funding'):
                    head = 'funding'
                    tail = tail.replace('funding/', '')
                if head.startswith('emphasis'):
                    head = 'emphasis'
                    tail = tail.replace('emphasis/', '')
                if tail.startswith('religion'):
                    head = 'religion'
                    tail = tail.replace('religion/', '')
                # Combine UK and US with the rest of the tag
                tail = re.sub('^UK/', 'UK-', tail)
                tail = re.sub('^US/', 'US-', tail)
                # Set the new dict key and value
                d[head] = tail
    # Return the dict
    return d

def to_qgrid(df):
    """Display a dataframe as a qgrid."""
    return qgrid.show_grid(df, grid_options=qgrid_options, show_toolbar=False)    
