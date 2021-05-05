"""diagnostics.py.


Last update: 2021-02-17
"""

# Python imports
import os
import re
import shutil
from IPython.display import display, HTML
from natsort import natsorted
from pathlib import Path

def create_vis(model_dir, current_dir, PORT):
    """Create diagnostics visualisations."""
    # Populate the select menus with the model options and the plots to show in the comparison tool
    topics = natsorted([x.replace('topics', '') for x in os.listdir(model_dir) if x.startswith('topics')])
    options = ''
    for topic in topics:
        options += '<option value="' + str(topic) + '">' + str(topic) + '</option>'
    with open('scripts/index_template.html', 'r') as f:
        html = f.read()
    html = html.replace('OPTIONS HERE', options)
    default_topic = 100
    if 100 not in topics:
        default_topic = topics[0]
    html = html.replace("'topics', '100'", "'topics', '" + str(default_topic) + "'")
    with open('index.html', 'w') as f:
        f.write(html)
    model_plots = []
    for topic in topics:
        model_plots.append('xml/diagnostics' + str(topic) + '.xml')
    with open('scripts/comparison_template.html', 'r') as f:
        html = f.read()
    html = html.replace('XML FILES HERE', str(model_plots))
    with open('comparison.html', 'w') as f:
        f.write(html)

    # Copy the xml files from the data directory to the current directory
    for subdir in os.listdir(model_dir):
        if subdir.startswith('topics'):
            subdir_path = os.path.join(model_dir, subdir)
            xml_file = [file for file in os.listdir(subdir_path) if file.endswith('.xml')][0]
            shutil.copy(os.path.join(subdir_path, xml_file), current_dir + '/xml/' + xml_file)

    current_reldir = current_dir.split("/write/")[1]
    if PORT != '' and PORT is not None:
        private_index_path = ':' + PORT + '/' + current_reldir + '/index.html'
    else:
        private_index_path = '/' + current_reldir + '/index.html'
    link = '<a target="_blank" href="#" onmouseover="event.srcElement.href = \'http://\' + window.location.hostname + \'' + private_index_path + '\';">diagnostics index page</a>'
    output = '<p>Your diagnostics visualizations can be accessed from the ' + link + '.</p>'
    display(HTML(output))
    
def get_project_directory():
    """Get the project directory from the current directory."""
    return str(Path(os.getcwd()).parent.parent)

