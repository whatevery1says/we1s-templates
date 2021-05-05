"""zip.py.

Create zip archives of one or more dfr-browsers.

Last update: 2021-02-18
"""

# Python imports
import os
import re
import shutil
from IPython.display import display, HTML

# Zip function
def zip(models=None):
    """Zip dfr-browsers to the current directory.
    
    The `models` parameter takes a string (e.g. 'topics25') or a list (e.g. ['topics25', 'topics50']).
    If left blank or set to `All` or `None`, all available models will be zipped.
    """
    current_dir = os.getcwd()
    if models == None or models.lower() == 'all':
        models = [model for model in os.listdir(current_dir) if os.path.isdir(model) and model.startswith('topics')]
    elif isinstance(models, str):
        models = [models]
    for model in models:
        print('Zipping ' + model  + '...')
        source = os.path.join(current_dir, model)
        temp = os.path.join(current_dir, model + '_temp')
        if os.path.exists(temp):
            shutil.rmtree(temp)
        shutil.copytree(source, temp)
        shutil.make_archive(model, 'zip', temp)
        shutil.rmtree(temp)
    display(HTML('<p style="color:green;">Done!</p>'))    
    msg = """
    <h2>Download</h2>
    <p>To download and view your browsers through a webserver hosted on your local machine:</p>
    <ol>
        <li>In the `dfr_browser` module directory, you should now see folders titled <code>browsern1</code>, <code>browsern2</code>, etc where <code>n</code> is the number of topics you modeled. There should be one browser folder for each browser you produced. The zipped version of each browser is in each of these directories. It is called <code>browser.zip</code>.</li>
        <li>Download your browser zips and save them on your local machine in an easily accessible place you will remember.</li>
        <li>Unzip the browser you want to view.</li>
        <li>Open a shell/terminal on your local machine, and navigate to the browser directory you just downloaded.</li>
        <li>On Linux / OSX, launch a local webserver by running:<br><code>./bin/server</code>.</li>
        <li>You can now view your dfr-browser using your machine's internet browser at <a href='http://localhost:8888/' target='_blank'>http://localhost:8888/</a>.</li>
        </ol>
    """
    output = HTML(msg)
    display(output)
