"""add_metadata.py.

Adds metadata values to json files in an existing project using a csv.

The csv must have a filename column referencing files in the json folder.
If this does not exist, the script will look for a name column, append
'.json', and attempt to use it as a filename.

Last update: 2021-02-17.
"""

# Python imports
import json
import os
import pandas as pd
import ipywidgets
from IPython.display import display, HTML
from ipywidgets import HBox, IntProgress, Label

class Metadata():
    """Metadata object which can be used to update json files."""

    def __init__(self, filepath, json_dir):
        """Initialise the object."""
        self.filepath = filepath
        self.json_dir = json_dir
        self.no_filename = []
        self.no_corresponding_file = []
        self.pbar = IntProgress(min=0, max=100) # instantiate the progress bar
        self.percent = ipywidgets.HTML(value='0%')
        self.metadata = self._load_metadata_file()
        display(HTML('<p style-"green;">Metadata file loaded.</p>'))

    def _get_filename(self, row, filename=None):
        """Get the filename referenced in the row.

        Tries to find a json file, then tries to construct one from the name.
        """
        if 'filename' in row:
            filename = row['filename']
        elif 'name' in row:
            filename = row['name'] + '.json'
        return filename

    def _load_metadata_file(self):
        """Load the metadata file."""
        if self.filepath.endswith('.csv'):
            return pd.read_csv(self.filepath)
        else:
            return pd.read_json(self.filepath)

    def _read_json(self, filepath):
        """Read the json file."""
        try:
            with open(os.path.join(self.json_dir, filepath), 'r') as f:
                doc = json.loads(f.read())
            return doc
        except IOError:
            self.no_corresponding_file.append(filepath)
            return None

    def _save_json(self, filename, doc):
        """Save the updated json file."""
        with open(os.path.join(self.json_dir, filename), 'w') as f:
            f.write(json.dumps(doc))

    def add(self):
        """Add the new metadata."""
        hbox = HBox([Label('Getting records...'), self.pbar, self.percent])
        display(hbox)
        records = self.metadata.to_dict(orient='records')
        hbox.children = [Label('Adding records...'), self.pbar, self.percent]
        num_records = len(records)
        num_added = 0
        for i, row in enumerate(records):
            this_iter = i + 1
            filename = self._get_filename(row)
            if filename is not None:
                doc = self._read_json(filename)
                if doc is not None:
                    for k, v in row.items():
                        doc[k] = v
                    self._save_json(filename, doc)
                    num_added += 1
                else:
                    self.no_corresponding_file.append(filename)
            else:
                self.no_filename.append(row)
            progress = int(100. * this_iter/num_records)
            self.pbar.value = progress
            self.percent.value = '{0}%'.format(progress)
        display(HTML('<p style="color:green;">' + str(num_added) + ' records have been added.</p>'))
        if len(self.no_filename) > 0:
            display(HTML('<p style="color:red;">A filename could not be found for the following records:</p>'))
            out = '<ul>'
            for item in sorted(list(set(self.no_filename))):
                out+= '<li>' + str(item) + '</li>'
            out += '</ul>'
            display(HTML(out))
        if len(self.no_corresponding_file) > 0:
            display(HTML('<p style="color:red;">The following filenames in your metadata did not have a corresponding file in the json folder:</p>'))
            out = '<ul>'
            for item in sorted(list(set(self.no_corresponding_file))):
                out+= '<li>' + str(item) + '</li>'
            out += '</ul>'
            display(HTML(out))

