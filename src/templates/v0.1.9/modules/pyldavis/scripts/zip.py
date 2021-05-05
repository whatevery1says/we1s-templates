"""zip.py.

Create zip archives of one or more dfr-browsers.

Last update: 2020-07-25
"""

# Python imports
import os
import re
import shutil
from IPython.display import display, HTML

# Zip function
def zip(models=None):
    """Zip pyLDAvis visualizations to the current directory.
    
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

