"""export_package.py.

This script creates an ExportPackage object which can be used to
create a `.tar.gz` archive of an entire project folder or extract
an already packaged archive to a destination folder.

The script can be run from the command line or imported to a Jupyter notebook.

Author: Scott Kleinman
Version: 0.9.0
Date: 2020-07-29

export_package = ExportPackage(name, version, author)
export_package.build_datapackage(project_dir)
export_package.make_archive(project_dir)
"""

# Python imports
import json
import os
import re
import requests
import shutil
import tarfile
from argparse import ArgumentParser, SUPPRESS
from datapackage import Package
from datetime import datetime
from IPython.display import display, HTML
from pathlib import Path
import pymongo
from pymongo import MongoClient

# Classes
class ExportPackage():
    """Class for export packages."""

    def __init__(self, name=None, title=None, version=None, author=None):
        """Initialise the object."""
        self.name = name
        if title is None and name is not None:
            self.title = self.name.title()
        else:
            self.title = title
        self.version = version
        self.author = author
        self.datapackage = None
        self.readme = """# README

        Name: {{name}}
        Title: {{name}}
        Version: {{version}}
        Author: {{author}}
        Date: {{date}}"""

    def build_datapackage(self, project_dir, exclude=None):
        """Create or update a datapackage and README file in the project directory.

        @project_dir (str): The path to the project directory to be packaged.
        """
        now = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        # Modify project data package or create a new one if this fails
        try:
            with open(os.path.join(project_dir, 'datapackage.json'), 'r') as f:
                doc = json.loads(f.read())
            doc['archived'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            with open(os.path.join(project_dir, 'datapackage.json'), 'w') as f:
                f.write(json.dumps(doc))
        except IOError:
            doc = {'name': self.name, 'title': self.title, 'version': self.version, 'author': self.author}
            doc['archived'] = now
        if not 'title' in doc:
            doc['title'] = self.title
        # Modify exsting README or create a new on this fails
        try:
            with open(os.path.join(project_dir, 'README.md'), 'r') as f:
                text = f.read()
                text = text + '\n\nArchived: ' + now
            with open(os.path.join(project_dir, 'README.md'), 'w') as f:
                f.write(text)
        except IOError:
            for k, v in doc.items():
                self.readme = self.readme.replace('{{' + k + '}}', v)
            with open(os.path.join(project_dir, 'README.md'), 'w') as f:
                f.write(self.readme)
        # Read the data package into a Package object
        self.datapackage = Package(doc)
        # Infer the resources in the project directory
        self.infer_resources(project_dir, exclude=exclude)
        # Save the data package
        self.datapackage.save(os.path.join(project_dir, 'datapackage.json'))

    def db_add(self, archive_file, client, db, collection):
        """Upsert metadata for a project archive in MongoDB.
        @archive_file (str): The path to the filename of the output archive (with or without the `.tar.gz` extension).
        @client (str): The url of a MongoDB client.
        @db (str): The name of a MongoDB database.
        @collection (str): The name of a MongoDB collection.
        """
        metapath = ','.join(['db', 'collection'])
        client = MongoClient(client)
        db = client['db']
        collection = db['collection']
        manifest = {
            'name': self.datapackage['name'],
            'namespace': self.datapackage['we1sv2.0'],
            'metapath': metapath,
            'title': self.datapackage['title'],
            'version': self.datapackage['version'],
            'author': self.datapackage['author'],
            'archived': self.datapackage['archived'],
            'location': archive_file
        }
        result = collection.find_({'name': manifest['name']})
        collection.update_one({'_id': result['_id']}, manifest, upsert=True)

    def extract(self, archive_file, destination_dir, remove_archive=True):
        """Extract tar archive to a destination folder.

        @archive_file (str): The path to the archive file to be extracted.
        @destination_dir (str): The path to the directory where the archive will be extracted.
        @remove_archive (bool): Whether to delete the archive file from the destination_dir after extraction (default is `True`).

        Automatically loads the data package and README into the ExportPackage object.

        An additional operation to bring the extracted folders to the destination root may be necessary.
        """
        # Extract the archive file
        tar = tarfile.open(archive_file)
        tar.extractall(destination_dir)
        tar.close()
        # Remove the tar file
        if remove_archive == True:
            os.remove(archive_file)
        # Bring templates up to the project root level
        root = os.listdir(destination_dir)[0]
        for filename in os.listdir(os.path.join(destination_dir, root)):
            shutil.move(os.path.join(destination_dir + '/' + root, filename), os.path.join(destination_dir, filename))
        os.rmdir(os.path.join(destination_dir, root))
        # Read the data package and README into the ExportPackage object
        self.datapackage = Package(os.path.join(destination_dir, 'datapackage.json'))
        with open(os.path.join(destination_dir, 'README.md'), 'r') as f:
            self.readme = f.read()
        print('Template archive extracted.')

    def infer_resources(self, project_dir, exclude=None):
        """Infer the resources in the project directory.

        Ignoring things like .ipynb_checkpoints is probably not appropriate,
        but the code can serve as the basis for a configuration to ignore
        folders.
        """
        if exclude is None:
            exclude = []
        if not isinstance(exclude, list):
            display(HTML('<p style="color: red;">Your <code>exclude</code> parameter must be a list or <code>None</code>/</p>'))
        else:
            filepaths = [str(f) for f in Path(project_dir).glob('**/*.*') if f.is_file()]
            for path in filepaths:
                if str(Path(path).parent) not in exclude:
                    self.datapackage.add_resource({'path': path})
            for index, resource in enumerate(self.datapackage.resources):
                descriptor = resource.infer()
                self.datapackage.descriptor['resources'][index] = descriptor

    def load(self, archive_file, destination_dir):
        """Load a project archive from a source location.

        @archive_file (str): The filepath or url to the project archive file.
        @destination_dir (str): The path to the folder where the project archive file should be copied.
        """
        # Make sure a destination exists
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
        # Load the archive from a url
        if archive_file.startswith('http'):
            response = requests.get(archive_file, stream=True)
            with open(destination_dir, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
        # Load the archive from a file path
        else:
            shutil.copy(archive_file, destination_dir)

    def make_archive(self, project_dir, archive_file, client=None, db=None, collection=None):
        """Make a tar archive of the project directory.

        @project_dir (str): The path to the project directory to be archived.
        @archive_file (str): The path to the filename of the output archive (with or without the `.tar.gz` extension).
        @client (str): The url of a MongoDB client.
        @db (str): The name of a MongoDB database.
        @collection (str): The name of a MongoDB collection.
        """
        archive_file = re.sub('.tar.gz', '', archive_file) + '.tar.gz'
        with tarfile.open(archive_file, mode='w:gz') as archive:
            for resource in self.datapackage.descriptor['resources']:
                archive.add(resource, recursive=False)
        display(HTML('<p style="color: green;">Project archive created.</p>'))
        # If the user wants to add the project to a database
        if client is not None or db is not None or collection is not None:
            missing = []
            if client is None:
                missing.append('client')
            elif db is None:
                missing.append('db')
            elif collection is None:
                missing.append('collection')
            if len(missing) > 0:
                for item in missing:
                    display(HTML('<p style="color:red;">Please configure a value for the ' + item + ' setting.</p>'))
            else:
                self.db_add(archive_file, client, db, collection)

def cli_make(args):
    """Make a project archive from the command line."""
    required = ['name', 'version', 'author', 'project_dir', 'archive_file']
    for value in required:
        if value not in vars(args):
            argument = value.replace('export_', '')
            argument = argument.replace('_', '-')
            raise('You must supply a value for ' + argument + ' to make an archive.')
    export_package = ExportPackage(args.name, args.version, args.author)
    export_package.build_datapackage(args.project_dir)
    export_package.make_archive(args.project_dir, args.archive_file)

def cli_extract(args):
    """Extract a project archive from the command line."""
    required = ['project_dir', 'destination_dir']
    for value in required:
        if value not in vars(args):
            argument = value.replace('export', '')
            argument = argument.replace('_', '-')
            raise('You must supply a value for ' + value + ' to extract an archive.')
    export_package = ExportPackage()
    # Copy the export package from its source to a destination_dir
    export_package.load(args.project_dir, args.destination_dir)
    archive_filename = str(Path(args.project_dir).name)
    archive_filepath = os.path.join(args.destination_dir, archive_filename)
    # Extract the archive to the destination_dir with option to remove
    export_package.extract(archive_filepath, args.destination_dir, remove_archive=args.remove_archive)

if __name__ == '__main__':
    usage = """For making a project archive:

    `python export_package.py [--action] make [--name] project_name [--version] 1.0.0 [--author] "John Smith" [--source] project_dir [--archive-file] path_to_output_file`

    For extracting a project archive:

    `python export_package.py [--action] extract [--source] archive_file_path [--destination-dir] project_dir`

    or

    `python export_package.py [--action] extract [--source] archive_file_url [--destination-dir] project_dir`"""
    # Parse the command line
    parser = ArgumentParser(prog='ExportPackage',
                            description='Package WE1S project folder and load and extract a packaged project into a folder.',
                            usage=usage,
                            add_help=False)
    required = parser.add_argument_group('Required Arguments')
    optional = parser.add_argument_group('Optional Arguments')
    required.add_argument('--action', type=str, choices=['make', 'extract'], dest='action', help='Specify whether the desired action is to "make" or "extract" an archive.')
    optional.add_argument('-n', '--name', metavar='n', type=str, help='Specify the name of the project package. Required for making new packages.', dest='name')
    optional.add_argument('-v', '--version', metavar='v', type=str, help='Specify the semantic version of the project package. Required for making new packages.', dest='version')
    optional.add_argument('-a', '--author', metavar='a', type=str, help='Specify the author of the project package (not necessarily the same as the project itself). Required for making new packages.', dest='author')
    optional.add_argument('-s', '--source', metavar='s', type=str, help='If making an archive, specify the folder to be packaged, or, if extracting an archive, specify the filepath or url to the archive to be extracted.', dest='project_dir', default=None)
    optional.add_argument('-f', '--archive-file', metavar='f', type=str, help='Specify the path and filename where the archive will be saved.', dest='archive_file', default=None)
    optional.add_argument('-d', '--destination-dir', metavar='d', type=str, help='Specify the directory where an archive will be extracted.', dest='destination_dir', default=None)
    optional.add_argument('-r', '--remove-archive', metavar='d', type=str, help='Specify whether to delete the archive file after it is extracted. Default is `True`.', dest='remove_archive', default=True)
    optional.add_argument('-h', '--help', action='help', default=SUPPRESS, help='Show this help message and exit.')
    args = parser.parse_args()
    # If run from the command line, call the pipeline based on the action
    if any(vars(args).values()):
        if args.action == 'make':
            cli_make(args)
        elif args.action == 'extract':
            cli_extract(args)
