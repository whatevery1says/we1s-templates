"""import.py.

Imports a collection of plain text files to a project directory or database.

For use with `import-2.0.0.ipynb` or the command line.
When using in a jupyter notebook, initialise with `environment='jupyter'`.

Last update: 2021-02-15
"""

# Python imports
import csv
import dateparser
import json
import os
import random
import shutil
import ipywidgets
import pandas as pd
import pymongo
import re
import sys
import zipfile
from chardet import detect
from datapackage import DataPackageException, Package
from datetime import datetime
from ftfy import fix_text
from IPython.display import clear_output, display, HTML
from ipywidgets import HBox, IntProgress, Label
from pathlib import Path
from pymongo import errors, MongoClient

from bson import BSON
from bson import Binary, json_util
from bson.objectid import ObjectId
JSON_UTIL = json_util.default

from timer import Timer

# Constants
LINEBREAK_REGEX = re.compile(r'((\r\n)|[\n\v])+')
NONBREAKING_SPACE_REGEX = re.compile(r'(?!\n)\s+')
IntProgress(
    description='Importing...'
)

# Import deduping libraries
sys.path.insert(0, '/home/jovyan/utils/preprocessing')
from libs.fuzzyhasher.fuzzyhasher import FuzzyHasher
from libs.deduper.deduper import LinkFilter

# Create FuzzyHasher and LinkFilter objects
fhr =  FuzzyHasher(source_field='content', prefilter='baggify, lower_alnum')
lf = LinkFilter()

# Setup message
def display_setup_message():
    """Display a message when the setup is complete."""
    display(HTML('<p>Setup complete.</p>'))
    msg = '<p>Use the <strong>Configuration</strong> cell below to configure your job, then skip to either <strong>Prepare Workspace for File Import</strong> or <strong>Import from MongoDB</strong> section as appropriate for your data source.</p>'
    display(HTML(msg))

# Deduping Functions
def deduplicate(json_dir):
    """Remove duplicates data files from the workflow.
    
    `add_new` and `update_old` can be disabled if data consists of prehashed json files
    in order to create a more efficient process. This is documented in the module
    README file, but there is not setting in the notebook in order to reduce the
    complexity of notebook configurations.
    """
    # Configurations for hashing function
    add_new = True
    update_old = True
    # Rename files with empty content fields
    rename_contentless_files(json_dir)
    # Deduplicate
    try:
        hash_jsons(json_dir, add_new, update_old)
        results = fhr.compare_files_in_dir(json_dir)
        result_list = [[str(item) for item in row] for row in results]
        if result_list:
            display(HTML('<p style="color: red;">Duplicate pair matches found: ' + str(len(result_list)) + '</p>'))
            with open(os.path.join(json_dir,'_duplicates.txt'), 'w') as dupefile:
                writer = csv.writer(dupefile, dialect='excel-tab')
                for result in result_list:
                    writer.writerow(result)
            # Create delete list
            lf.links = result_list
            deletes_list = lf.filter_nodes(source='components', filter='remove')
            # Update deletes file
            with open(os.path.join(json_dir, '_deletes.txt'), 'w') as delfile:
                for item in deletes_list:
                    delfile.write('%s\n' % item)
            # Remove deletes by renaming
            with open(os.path.join(json_dir, '_deletes.txt'), 'r') as delfile:
                for dfname in delfile:
                    newfname = dfname.rstrip().replace('.json', '.dupe')
                    os.rename(dfname.rstrip(), newfname)
        else:
            display(HTML('<p style="color: green;">No duplicates found.</p>'))
    except (json.decoder.JSONDecodeError, KeyError, PermissionError, ValueError) as err:
        display(HTML('<p style="color: red;">Error: ' + str(err) + '.</p>'))

def hash_jsons(json_dir, add_new, update_old):
    """Hash the jsons for deduping."""
    for file in os.listdir(json_dir):
        if file.endswith('.json'):
            fhr.add_hash_to_json_file(os.path.join(json_dir, file), add_new=add_new, update_old=update_old)

def rename_contentless_files(json_dir):
    """Rename files with empty content fields to '.empty'."""
    files = [file for file in os.listdir(json_dir) if file.endswith('.json')]
    for file in files:
        filepath = os.path.join(json_dir, file)
        # Open the file, check the content field, and rename if empty
        with open(filepath, 'r') as f:
            content = json.load(f)['content']
        if content == '' or content is None:
            newfilepath = filepath.replace('.json', '.empty')
            os.rename(filepath, newfilepath)

def undo_extension(current_ext='.dupe', new_ext='.json', data_dir='.'):
    """Rename all my `.dupe` files back to `.json` or `.empty` files or whatever.

    Takes `data_dir` e.g. `all_hands/myproject/project_data/json`.
    """
    checkfiles = [entry.path for entry in os.scandir(data_dir) if entry.path.endswith(current_ext)]
    print('found ', len(checkfiles), 'files with ext ', current_ext, ' to revert')
    for checkfile in checkfiles:
        newcheckfile = checkfile.replace(current_ext, new_ext)
        os.rename(checkfile, newcheckfile)
    
# Normalize Unicode
def normalize(text, unicode_normalization='NFC'):
    """Normalize whitespace and and bad unicode."""
    return fix_text(NONBREAKING_SPACE_REGEX.sub(' ', LINEBREAK_REGEX.sub(r'\n', text)).strip(),
                    normalization=unicode_normalization)

# Classes
class Import():
    """Import a collection of plain text files from zip archive and accompanying metadata CSV file."""

    def __init__(self, zip_file='import.zip', metadata='metadata.csv',
                 client=None, db=None, collection=None,
                 project_dir=None, json_dir=None, delete_imports_dir=True,
                 delete_text_dir=False, data_dirs=None,
                 title_field=None, author_field=None, pub_date_field=None, content_field=None,
                 dedupe=False, random_sample=None,
                 random_seed=1, required_phrase=None, save_mode='project',
                 logfile='import_log.txt', environment=''):
        """Initialise the Import object."""
        self.zip_file = zip_file # Path to the zipfile
        self.metadata_file = metadata # Path to the metadata csv file
        self.client = client # Database client
        self.db = db # Name of database
        self.collection = collection # Database collection
        self.project_dir = project_dir # Path to project directory
        self.json_dir = json_dir
        self.imports_dir = project_dir + '/project_data/imports'
        self.text_dir = project_dir + '/project_data/imported_text_files'
        self.data_dirs = data_dirs # List of directories in a zip archive or data package from which to extract data
        self.title_field = title_field
        self.author_field = author_field
        self.pub_date_field = pub_date_field
        self.content_field = content_field
        self.dedupe = dedupe
        self.random_sample = random_sample
        self.random_seed = random_seed
        self.required_phrase = required_phrase
        self.delete_count = 0
        self.delete_imports_dir = delete_imports_dir
        self.delete_text_dir = delete_text_dir
        self.save_mode = 'project'
        self.logfile = logfile
        self.environment = environment
        self.metadata = 'Metadata has not been loaded.'
        self.valid_headers = ['filename', 'pub_date', 'title', 'author']
        self.this_iter = 0
        self.total_docs = 0
        self.errors = {'file_not_found': [], 'invalid_manifest_file': [], 'database_error': [], 'bad_json': []}
        self.pbar = IntProgress(min=0, max=100) # instantiate the progress bar
        self.percent = ipywidgets.HTML(value='0%')


    def configure_db(self):
        """Configure the database."""
        self.client = MongoClient(self.client)
        self.db = self.client[self.db]
        self.collection = self.db[self.collection]

    def create_imports_dir(self):
        """Create the imports directory if it does not exist."""
        is_new = False
        if not os.path.exists(self.imports_dir):
            os.makedirs(self.imports_dir)
            is_new = True
        return is_new

    def create_manifests(self):
        """Create a manifest for each document."""
        # Iterate through the dataframe and create name properties
        doc_ids = []
        names = []
        for i, filename in enumerate(self.metadata.filename.values.tolist()):
            doc_ids.append(i)
            names.append(filename.lower().replace('.txt', ''))
        # Add the doc_id and name columns
        self.metadata.insert(0, 'doc_id', doc_ids)
        self.metadata.insert(1, 'name', names)
        self.docs = self.metadata.to_dict(orient='records')
        self.total_iters = len(self.docs)
        for i, doc in enumerate(self.docs):
            filename = doc['filename']
            if 'namespace' not in doc:
                doc['namespace'] = 'we1sv2.0'
            if 'metapath' not in doc:
                doc['metapath'] = ''
            if 'title' not in doc:
                doc['title'] = doc['name'].replace('_', ' ').title()
            if 'pub' not in doc:
                doc['pub'] = 'unknown'
            if 'pub_date' not in doc or doc['pub_date'] == '' or doc['pub_date'] == 'unknown':
                doc['pub_date'] = 'unknown'
            else:
                pub_date = dateparser.parse(str(doc['pub_date']))
                doc['pub_date'] = pub_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            if 'pub_year' not in doc:
                if doc['pub_date'] != 'unknown':
                    doc['pub_year'] = doc['pub_date'][0:5]
                else:
                    doc['pub_year'] = 'unknown'
            # Read the source file and copy the content to the manifest
            try:
                try:
                    with open(os.path.join(self.text_dir, filename), 'r') as f:
                        doc['content'] = normalize(f.read())
                except UnicodeDecodeError:
                    with open(os.path.join(self.text_dir, filename), 'rb') as f:
                        rawdata = f.read()
                    encoding = detect(rawdata)['encoding']
                    if encoding == 'Windows-1252':
                        encoding = 'cp1252'
                    doc['content'] = normalize(rawdata.decode(encoding).encode('utf-8').decode('utf-8'))
                doc['length'] = str(len(doc['content']))
                # Save the document
                if self.required_phrase is None:
                    self.save(doc, i)
                elif self.required_phrase is not None and self.required_phrase in doc['content']:
                    self.save(doc, i)
                else:
                    self.this_iter += 1
                    progress = int(100. * self.this_iter/self.total_iters)
                    self.pbar.value = progress
                    self.percent.value = '{0}%'.format(progress)
                    self.delete_count += 1    
            except IOError:
                self.errors['file_not_found'].append(filename)

    def create_text_dir(self):
        """Create the text directory if it does not exist.

        Pre-existing data is deleted
        """
        if os.path.exists(self.text_dir):
            shutil.rmtree(self.text_dir)
        os.makedirs(self.text_dir)

    def delete_dirs(self, mode):
        """Delete asset folders."""
        if self.delete_imports_dir and mode == 'imports':
            shutil.rmtree(self.imports_dir)
        if self.delete_text_dir and mode == 'text_dir':
            shutil.rmtree(self.text_dir)

    def detect_zip_structure(self, namelist, root_folder=None):
        root = []
        for path in namelist:
            path_tuple = (path, os.path.dirname(path))
            _, ext = os.path.splitext(path)
            if not ext:
                root.append(path_tuple)
        root = list(set([item[0].split('/')[0] for item in root]))
        if len(root) == 1:
            root_folder = root[0]
        return root_folder

    def generate_log(self):
        """Generate a log file if there are errors."""
        with open(self.logfile, 'a') as f:
            f.write('The following filenames in your metadata file could not be found in your zip file:\n')
            if len(self.errors['file_not_found']) > 0:
                for file in self.errors['file_not_found']:
                    f.write(file + '\n')
            if len(self.errors['invalid_manifest_file']) > 0:
                f.write('\n')
                for file in self.errors['invalid_manifest_file']:
                    f.write(file + '\n')
            if len(self.errors['database_error']) > 0:
                f.write('\n')
                for file in self.errors['database_error']:
                    f.write(file + '\n')
            if len(self.errors['bad_json']) > 0:
                f.write('\n')
                for file in self.errors['bad_json']:
                    f.write(file + '\n')
            if self.required_phrase is not None:
                f.write('\n')
                f.write(str(self.delete_count) + ' files without the required phrase were deleted.')

    def import_plain_text(self):
        """Import plain text."""
        timer = Timer()
        # Load the metadata
        if not isinstance(self.metadata, pd.DataFrame):
            try:
                self.metadata = self.load_metadata()
            except ValueError:
                pass
        # Unzip the archive to the text directory
        self.unpack_zipfile()
        # Delete temporary assets
        self.delete_dirs('imports')
        # Create json manifests
        if not isinstance(self.metadata, pd.DataFrame):
            self.errors['file_not_found'].append('Missing metadata file.')
            self.show_message('To import plain text files, a metadata file must be in the `project_data/imports` folder.', 'red', 4)
        else:
            self.create_manifests()
        if self.dedupe:
            deduplicate(self.json_dir)
        self.delete_dirs('text_dir')
        # Generate log
        if len(self.errors['file_not_found']) or len(self.errors['invalid_manifest_file']) or len(self.errors['database_error']) > 0:
            num_errors = str(len([v for _, v in self.errors.items() if len(v)> 0]))
            self.show_message(num_errors + ' files could not be imported. See the import log for more information.', 'red')
            self.generate_log()
        self.total_docs = len([file for file in os.listdir(self.json_dir) if file.endswith('.json')])
        self.show_message(str(self.total_docs) + ' files have been imported to the project workspace.', 'green', 4)
        if self.required_phrase is not None:
            self.show_message(str(self.delete_count) + ' files were not imported because they did not have the required phrase.', 'green', 4)
        self.show_message('Time elapsed: %s' % timer.get_time_elapsed())

    def is_valid_json(self, doc, filename):
        """Check whether a json file is valid for the WE1S Workspace.

        Other validation rules can be added, as necessary.
        """
        required_fields = ['pub_date', 'title', 'author']
        errors = 0
        for field in required_fields:
            if field not in doc:
                doc[field] = ''
        if errors > 0:
            self.errors['bad_json'] = filename
            return False
        else:
            return True

    def load_metadata(self):
        """Load the metadata file."""
        try:
            df = pd.read_csv(os.path.join(self.imports_dir, self.metadata_file))
            if self.random_sample is not None:
                df = df.sample(n=self.random_sample, random_state=self.random_seed)
        except IOError:
            display(HTML('<p style="color: red;">Error! Could not read the metadata file.</p>'))
            raise
        # Validate the metadata
        try:
            assert df.columns.values.tolist()[0:4] == self.valid_headers
            return df
        except AssertionError:
            self.show_message('Error! Your metadata file must have "filename", "pub_date", "title", and "author" as its first four headers.', 'red')
            raise

    def save(self, doc, i):
        """Save a doc to a database or a project."""
        self.this_iter = i + 1
        if self.save_mode == 'db':
            try:
                result = self.collection.insert_one(doc)
            except ValueError:
                self.errors['database_error'].append(doc['filename'])
        else:
            try:
                manifest_file = os.path.join(self.json_dir, doc['name'] + '.json')
                with open(manifest_file, 'w') as f:
                    f.write(json.dumps(doc))
            except IOError:
                self.errors['invalid_manifest_file'].append(manifest_file)
        progress = int(100. * self.this_iter/self.total_iters)
        self.pbar.value = progress
        self.percent.value = '{0}%'.format(progress)

    def set_save_mode(self):
        """Set the save_mode."""
        if self.project_dir is None:
            if self.client is None:
                raise('Please supply a database client.')
            elif self.db is None:
                raise('Please supply database name.')
            elif self.collection is None:
                raise('Please supply a collection name.')
            else:
                self.save_mode = 'db'
                self.configure_db()

        else:
            if self.client is not None or self.db is not None or self.collection is not None:
                self.show_message('Warning! You have configured the import for both a database and a project. Defaulting the project setting.', 'red')

    def setup(self):
        """Call the create_imports_dir() and create_text_dir() methods."""
        self.create_text_dir()
        is_new = self.create_imports_dir()
        link = self.imports_dir.replace('/home/jovyan/', '/tree/')
        if self.environment == 'jupyter':
            link = '<a href="' + link + '" target="_blank">' + link + '</a>'
            if is_new == False:
                msg = '<p>Your imports folder is at ' + link + '.</p>'
            else:
                msg = '<p>A new imports folder has been created at ' + link + '.</p>'
            msg += '<p>Be sure to upload your data zip archive and metadata file (for plain text files) to this location before continuing.</p>'
        else:
            if is_new == False:
                msg = 'Your imports folder is at ' + link + '.'
                msg += ' Be sure to upload your data zip archive and metadata file (for plain text files) to this location before continuing.'
            else:
                msg = 'A new imports folder has been created at ' + link + '.'
                msg += ' Be sure to upload your data zip archive and metadata file (for plain text files) to this location before continuing.'
        self.show_message(msg, 'green', 5)

    def show_message(self, msg, color='', size=None):
        """Show HTML or plain text output by mode."""
        if self.environment == 'jupyter':
            if size is None:
                start_tag = '<p style="color: ' + color + ';">'
                end_tag = '</p>'
            else:
                start_tag = '<h' + str(size) + ' style="color: ' + color + ';">'
                end_tag = '</h' + str(size) + '>'
            display(HTML(start_tag + msg + end_tag))
        else:
            print(msg)

    def start_import(self, remove_existing_json=False):
        """Start the import pipeline."""
        display(HBox([Label('Importing...'), self.pbar, self.percent]))
        if remove_existing_json == True and os.path.exists(self.json_dir):
            shutil.rmtree(self.json_dir)
        if not os.path.exists(self.json_dir):
            os.makedirs(self.json_dir)
        package = None
        self.zip_file = os.path.join(self.imports_dir, self.zip_file)
        try:
            package = Package(self.zip_file)
        except DataPackageException:
            pass
        if package is not None:
            self.unpack_datapackage(package)
        elif len([x for x in zipfile.ZipFile(self.zip_file).namelist() if x.endswith('.json')]) > 0:
            self.unpack_json_zipfile()
        else:
            self.import_plain_text()

    def unpack_datapackage(self, package):
        """Unzip and data package and copy json files in selected folders to the json directory."""
        timer = Timer()
        try:
            data_dirs = re.compile('.')
            if self.data_dirs is not None:
                if isinstance(self.data_dirs, str):
                    self.data_dirs = [self.data_dirs]
                data_dirs = re.compile('^' + '|^'.join(self.data_dirs)) # ^dir1|^dir2|^dir3
            if self.random_sample is not None:
                random.seed(self.random_seed)
                resources = random.sample(package.resources, self.random_sample)
            else:
                resources = package.resources
            # Detect root directory in zipfile
            root_folder = self.detect_zip_structure(zipfile.ZipFile(self.zip_file).namelist())  
            # Iterate through the resources
            for i, resource in enumerate(resources):
                self.this_iter = i
                resource_filepath = resource.descriptor['path']
                if root_folder is not None:
                    filepath = os.path.join(root_folder, resource_filepath)
                else:
                    filepath = resource_filepath
                filename = filepath.split('/')[-1]
                # Add the root folder path, if present, to the data_dirs
                if root_folder is not None and self.data_dirs:
                    dir_list = [root_folder + x for x in self.data_dirs]
                    data_dirs = re.compile('^' + '|^'.join(dir_list)) # ^root_folder/dir1|^root_folder/dir2|^root_folder/dir3
                # Ensure that the resource is in the data_dirs
                if re.search(data_dirs, filepath) and filepath.endswith('.json'):           
                    file = zipfile.ZipFile(self.zip_file, 'r')
                    file_str = file.read(filepath)
                    doc = json.loads(file_str)
                    if not 'name' in doc:
                        doc['name'] = resource.split('/')[-1] + '.json'
                    if not 'namespace' in doc:
                        doc['namespace'] = 'we1sv2.0'
                    if not 'metapath' in doc:
                        doc['metapath'] = 'Corpus,RawData'
                    if self.title_field is not None:
                        doc['title'] = doc[self.title_field]
                        doc.pop(self.title_field, None)
                    if self.author_field is not None:
                        doc['author'] = [self.author_field]
                        doc.pop(self.author_field, None)
                    if 'pub' not in doc:
                        doc['pub'] = 'unknown'
                    if self.pub_date_field is not None:
                        pub_date = dateparser.parse(str(doc[self.pub_date_field]))
                        doc.pop(self.pub_date_field, None)
                    if 'pub_date' not in doc or doc['pub_date'] == '' or doc['pub_date'] == 'unknown':
                        doc['pub_date'] = 'unknown'
                    else:
                        pub_date = dateparser.parse(str(doc['pub_date']))
                        doc['pub_date'] = pub_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                    if 'pub_year' not in doc:
                        if doc['pub_date'] != 'unknown':
                            doc['pub_year'] = pub_date[0:5]
                        else:
                            doc['pub_year'] = 'unknown'
                    if self.content_field is not None:
                        doc['content'] = self.content_field
                        doc.pop(self.content_field, None)
                    if self.is_valid_json(doc, filepath):
                        if self.required_phrase is None:
                            with open(os.path.join(self.json_dir, filename), 'w') as f:
                                f.write(json.dumps(doc))
                        elif self.required_phrase is not None and self.required_phrase in doc['content']:
                            with open(os.path.join(self.json_dir, filename), 'w') as f:
                                f.write(json.dumps(doc))
                        else:
                            self.this_iter += 1
                            progress = int(100. * self.this_iter/self.total_iters)
                            self.pbar.value = progress
                            self.percent.value = '{0}%'.format(progress)
                            self.delete_count += 1
                    else:
                        self.errors['invalid_manifest_file'].append(filename)
                progress = int(100. * self.this_iter/len(resources))
                self.pbar.value = progress
                self.percent.value = '{0}%'.format(progress)
                self.this_iter += 1
            if self.dedupe:
                self.this_iter += 1
                deduplicate(self.json_dir)
            progress = int(100. * self.this_iter/len(resources))
            self.pbar.value = progress
            self.percent.value = '{0}%'.format(progress)
        except IOError:
            self.show_message('Error! Could not unpack zipfile.', 'red')
        # Generate log
        if len(self.errors['file_not_found']) or len(self.errors['invalid_manifest_file']) or len(self.errors['database_error']) > 0:
            self.show_message('One or more files could not be imported. See the import log for more information.', 'red')
            self.generate_log()
        self.total_docs = len([file for file in os.listdir(self.json_dir) if file.endswith('.json')])
        self.show_message(str(self.total_docs) + ' have been imported to the project workspace.', 'green', 4)
        if self.required_phrase is not None:
            self.show_message(str(self.delete_count) + ' records were not imported because they did not have the required phrase.', 'green', 4)
        self.show_message('Time elapsed: %s' % timer.get_time_elapsed())

    def unpack_json_zipfile(self):
        """Unzip and flatten the archive to the json directory."""
        timer = Timer()
        try:
            # Detect root directory in zipfile
            root_folder = self.detect_zip_structure(zipfile.ZipFile(self.zip_file).namelist())
            if root_folder is not None:
                print('root folder is ' + root_folder)
            else:
                print('No root folder')           
            # Set the data_dirs pattern
            if self.data_dirs is not None:
                if isinstance(self.data_dirs, str):
                    self.data_dirs = [self.data_dirs]
                data_dirs = re.compile('^' + '|^'.join(self.data_dirs)) # ^dir1|^dir2|^dir3
            # Add the root folder path, if present, to the data_dirs
            data_dirs = None
            if root_folder is not None and self.data_dirs is not None:
                dir_list = [root_folder + '/' + x for x in self.data_dirs]
                data_dirs = re.compile('^' + '|^'.join(dir_list)) # ^root_folder/dir1|^root_folder/dir2|^root_folder/dir3
            self.this_iter = 0
            with zipfile.ZipFile(self.zip_file) as zip_file:
                if data_dirs is not None:
                    json_files = [file for file in zip_file.namelist() if file.endswith('.json') and re.search(data_dirs, file)]
                else:
                    json_files = [file for file in zip_file.namelist() if file.endswith('.json')]
                if self.random_sample is not None:
                    random.seed(self.random_seed)
                    json_files = random.sample(json_files, self.random_sample)
                for filepath in json_files:
                    filename = os.path.basename(filepath)
                    # Skip directories
                    if not filename:
                        continue
                    else:
                        # Copy file (taken from zipfile's extract)
                        source = zip_file.open(filepath).read()
                        doc = json.loads(source.decode())
                        if not 'name' in doc:
                            doc['name'] = filename.replace('.json', '')
                        if not 'namespace' in doc:
                            doc['namespace'] = 'we1sv2.0'
                        if not 'metapath' in doc:
                            doc['metapath'] = 'Corpus,RawData'
                        if self.title_field is not None:
                            doc['title'] = doc[self.title_field]
                            doc.pop(self.title_field, None)
                        if self.author_field is not None:
                            doc['author'] = doc[self.author_field]
                            doc.pop(self.author_field, None)
                        if self.content_field is not None:
                            doc['content'] = doc[self.content_field]
                            doc.pop(self.content_field, None)
                        if self.pub_date_field is not None:
                            pub_date = dateparser.parse(str(doc[self.pub_date_field]))
                            doc.pop(self.pub_date_field, None)
                        if 'pub_date' not in doc or doc['pub_date'] == '' or doc['pub_date'] == 'unknown':
                            doc['pub_date'] = 'unknown'
                        else:
                            pub_date = dateparser.parse(str(doc['pub_date']))
                            doc['pub_date'] = pub_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                        if 'pub_year' not in doc:
                            if doc['pub_date'] != 'unknown':
                                doc['pub_year'] = pub_date[0:5]
                            else:
                                doc['pub_year'] = 'unknown'
                        if self.is_valid_json(doc, filename):
                            if self.required_phrase is None:
                                with open(os.path.join(self.json_dir, filename), 'w') as f:
                                    f.write(json.dumps(doc))
                            elif self.required_phrase is not None and self.required_phrase in doc['content']:
                                with open(os.path.join(self.json_dir, filename), 'w') as f:
                                    f.write(json.dumps(doc))
                            else:
                                self.this_iter += 1
                                progress = int(100. * self.this_iter/self.total_iters)
                                self.pbar.value = progress
                                self.percent.value = '{0}%'.format(progress)
                                self.delete_count += 1
                        else:
                            self.errors['invalid_manifest_file'].append(filename)
                    progress = int(100. * self.this_iter/len(json_files))
                    self.pbar.value = progress
                    self.percent.value = '{0}%'.format(progress)
                    self.this_iter += 1
                    if self.dedupe:
                        self.this_iter += 1
                        deduplicate(self.json_dir)
                    progress = int(100. * self.this_iter/len(json_files))
                    self.pbar.value = progress
                    self.percent.value = '{0}%'.format(progress)
        except IOError:
            self.show_message('Error! Could not unpack zipfile.', 'red')
        # Generate log
        if len(self.errors['file_not_found']) or len(self.errors['invalid_manifest_file']) or len(self.errors['database_error']) > 0:
            self.show_message('One or more files could not be imported. See the import log for more information.', 'red')
            self.generate_log()
        self.total_docs = len([file for file in os.listdir(self.json_dir) if file.endswith('.json')])
        self.show_message(str(self.total_docs) + ' have been imported to the project workspace.', 'green', 4)
        if self.required_phrase is not None:
            self.show_message(str(self.delete_count) + ' records were not imported because they did not have the required phrase.', 'green', 4)
        self.show_message('Time elapsed: %s' % timer.get_time_elapsed())

    def unpack_zipfile(self):
        """Unzip and flatten the archive to the text directory."""
        try:
            zip_filepath = os.path.join(self.imports_dir, self.zip_file)
            with zipfile.ZipFile(zip_filepath) as zip_file:
                for filepath in zip_file.namelist():
                    filename = os.path.basename(filepath)
                    # Skip directories
                    if not filename:
                        continue
                    # Copy file (taken from zipfile's extract)
                    source = zip_file.open(filepath)
                    target = open(os.path.join(self.text_dir, filename), 'wb')
                    with source, target:
                        shutil.copyfileobj(source, target)
        except IOError:
            if not os.path.isfile(zip_filepath):
                self.show_message('Error! Could not find the zipfile. Make sure it is in the `project_data/imports` folder.', 'red')
            else:
                self.show_message('Error! Could not unpack zipfile.', 'red')

class MongoDBImport():
    """Import records from MongoDB."""

    def __init__(self, query, client=None, db=None, collection=None,
                 project_dir=None, json_dir=None, dedupe=False,
                 title_field=None, author_field=None, pub_date_field=None, content_field=None,
                 random_sample=None, random_seed=1,
                 required_phrase=None, logfile='import_log.txt',
                 environment=''):
        """Initialise the Import object."""
        if isinstance(query, str):
            self.query = json.loads(query)
        else:
            self.query = query
        self.client = MongoClient(client)
        self.db = self.client[db]
        self.collection = self.db[collection]
        self.project_dir = project_dir # Path to project directory
        self.json_dir = json_dir
        self.title_field = title_field
        self.author_field = author_field
        self.pub_date_field = pub_date_field
        self.content_field = content_field
        self.dedupe = dedupe
        self.random_sample = random_sample
        self.random_seed = random_seed
        self.required_phrase = required_phrase
        self.delete_count = 0
        self.saved_count = 0
        self.logfile = logfile
        self.environment = environment
        self.valid_headers = ['filename', 'pub_date', 'title', 'author']
        self.result = None
        self.result_count = 0
        self.errors = {'database_error': []}
        self.this_iter = 0
        self.pbar = IntProgress(min=0, max=100) # instantiate the progress bar
        self.percent = ipywidgets.HTML(value='0%')
        self.setup()

    def generate_log(self):
        """Generate a log file if there are errors."""
        with open(self.logfile, 'a') as f:
            if len(self.errors['database_error']) > 0:
                f.write('\n')
                for file in self.errors['database_error']:
                    f.write(file + '\n')
            if self.required_phrase is not None:
                f.write('\n')
                f.write(str(self.delete_count) + ' files without the required phrase were deleted.')

    def get_random_sample(self):
        """Use either MongoDB or Python (as needed) to return a random sample of the query data."""
        if self.random_seed is None:
            return self.sample_database()
        else:
            random.seed(self.random_seed)
            return random.sample(list(self.query_database()), self.random_sample)
        
    def start_import(self, remove_existing_json=False):
        """Start the import pipeline."""
        timer = Timer()
        display(HBox([Label('Importing...'), self.pbar, self.percent]))
        if remove_existing_json == True:
            shutil.rmtree(self.json_dir)
        if not os.path.exists(self.json_dir):
            os.makedirs(self.json_dir)
        if isinstance(self.query, dict) and self.random_sample is None:
            result = self.query_database()
        elif isinstance(self.query, dict) and isinstance(self.random_sample, int):
            result = self.get_random_sample()
        elif self.query is None and isinstance(self.random_sample, int):
            result = self.get_random_sample()
        else:
            self.query = {}
            result = self.query_database()
        if self.random_sample and isinstance(result, list):
            result_count = len(result)
        elif self.random_sample and not isinstance(result, list):
            result_count = len(list(result))
        else:
            result_count = result.count()
        self.result_count = result_count
        if result is not None:
            for doc in result:
                self.save(doc)
        if self.dedupe:
            deduplicate(self.json_dir)
            self.this_iter += 1
        progress = int(100. * self.this_iter/self.result_count)
        self.pbar.value = progress
        self.percent.value = '{0}%'.format(progress)
        # Generate log
        if len(self.errors['database_error']) > 0:
            self.show_message('One or more errors were encountered during the import process. See the import log for more information.', 'red')
            self.generate_log()
        self.show_message(str(self.saved_count) + ' records have been imported to the project workspace.', 'green', 4)
        if self.required_phrase is not None:
            self.show_message(str(self.delete_count) + ' records were not imported because they did not have the required phrase.', 'green', 4)
        self.show_message('Time elapsed: %s' % timer.get_time_elapsed())

    def query_database(self):
        """Query the database.

        Needs to handle multiple collections.
        """
        try:
            result = self.collection.find(self.query)
        except pymongo.errors.OperationFailure as e:
            print('error')
            self.errors['database'].append(e.code + ':' + e.details)
            result = None
        return result

    def sample_database(self):
        """Sample the database.

        Ignores self.query, uses sample aggregation.
        """
        try:
            result = self.collection.aggregate([{ '$sample': { 'size': self.random_sample } }])
            return list(result)
        except pymongo.errors.OperationFailure as e:
            self.errors['database_error'].append(str(e.code) + ':' + str(e.details))
            return None

    def save(self, doc):
        """Save a doc to a project."""
        # Ensure that the doc is valid before saving
        doc = self.validate(doc)
        if self.required_phrase is not None and self.required_phrase not in doc['content']:
            self.delete_count += 1
        else:
            try:
                savepath = os.path.join(self.project_dir, 'project_data/json')
                filepath = os.path.join(savepath, doc['name'] + '.json')
                with open(filepath, 'w') as f:
                    f.write(json.dumps(doc, sort_keys=False, default=JSON_UTIL))
                self.saved_count += 1
            except IOError:
                self.errors['invalid_manifest_file'].append(doc['name'] + '.json')
        self.this_iter += 1
        progress = int(100. * self.this_iter/self.result_count)
        self.pbar.value = progress
        self.percent.value = '{0}%'.format(progress)

    def setup(self):
        """Set up the task object."""
        # Make a fresh json directory
        if os.path.exists(os.path.join(self.project_dir, 'project_data/json')):
            shutil.rmtree(os.path.join(self.project_dir, 'project_data/json'))
        os.makedirs(os.path.join(self.project_dir, 'project_data/json'))
        display(HTML('<p>Project <code>json</code> directory created.</p>'))

    def show_message(self, msg, color='', size=None):
        """Show HTML or plain text output by mode."""
        if self.environment == 'jupyter':
            if size is None:
                start_tag = '<p style="color: ' + color + ';">'
                end_tag = '</p>'
            else:
                start_tag = '<h' + str(size) + ' style="color: ' + color + ';">'
                end_tag = '</h' + str(size) + '>'
            display(HTML(start_tag + msg + end_tag))
        else:
            print(msg)

    def validate(self, doc):
        """Validate a manifest before saving."""
        if self.title_field is not None:
            doc['title'] = self.title_field
        if self.author_field is not None:
            doc['author'] = self.author_field
        if self.content_field is not None:
            doc['content'] = self.content_field            
        if 'namespace' not in doc:
            doc['namespace'] = 'we1sv2.0'
        if 'metapath' not in doc:
            doc['metapath'] = ''
        if 'title' not in doc:
            if 'name' in doc:
                doc['name'] = str(doc['id'])
            doc['title'] = doc['name'].replace('_', ' ').title()
        if 'pub' not in doc:
            doc['pub'] = 'unknown'
        if self.pub_date_field is not None:
            pub_date = dateparser.parse(str(doc[self.pub_date_field]))
        if 'pub_date' not in doc or doc['pub_date'] == '':
            doc['pub_date'] = 'unknown'
        else:
            pub_date = dateparser.parse(str(doc['pub_date']))
            doc['pub_date'] = pub_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        if 'pub_year' not in doc:
            if doc['pub_date'] != 'unknown':
                doc['pub_year'] = pub_date[0:5]
            else:
                doc['pub_year'] = 'unknown'
        return doc
