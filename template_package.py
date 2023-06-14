"""template_package.py.

This script creates a TemplatePackage object which can be used to
create a `.tar.gz` archive of a template folder or extract an already
packaged archive to a destination folder such as a project directory.

The script can be run from the command line or imported to a Jupyter notebook.

Author: Scott Kleinman
Version: 0.9.0
Date: 2021-02-13
"""

# Python imports
import os
import re
import requests
import shutil
import tarfile
from argparse import ArgumentParser, SUPPRESS
from datapackage import Package
from datetime import datetime
from pathlib import Path

# Classes
class TemplatePackage():
    """Class for template packages."""

    def __init__(self, name=None, version=None, author=None):
        """Initialise the object."""
        self.name = name
        self.version = version
        self.author = author
        self.datapackage = None
        self.readme = """# README

        Name: {{name}}
        Version: {{version}}
        Author: {{author}}
        Date: {{date}}"""

    def create_datapackage(self, template_source):
        """Create a datapackage and README file inside the template folder.

        @template_source (str): The path to the folder containing the templates to be packaged.
        """
        fields = {'name': self.name, 'version': self.version, 'author': self.author}
        fields['date'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        if not os.path.exists(os.path.join(template_source, 'README.md')):
            for k, v in fields.items():
                self.readme = self.readme.replace('{{' + k + '}}', v)
            with open(os.path.join(template_source, 'README.md'), 'w') as f:
                f.write(self.readme)
        self.package = Package(fields, unsafe=True)
        self.infer_resources(template_source)
        self.package.save(os.path.join(template_source, 'datapackage.json'))

    def extract(self, archive_file, destination_dir, remove_package=True, datapackage=True):
        """Extract tar archive to a destination folder.

        @archive_file (str): The path to the archive file to be extracted.
        @destination_dir (str): The path to the directory where the archive will be extracted.
        @remove_package (bool): Whether to delete the package from the destination_dir after extraction (default is `True`).
        @datapackage (bool): Whether to create a `datapackage.json` file (default is `True`). This is set to `False` 
                             in `make_template_folder.ipynb`.

        Automatically loads the data package and README into the TemplatePackage object.

        An additional operation to bring the extracted folders to the destination root may be necessary.
        """
        # Strip GitHub's ?raw=true
        archive_file = archive_file.replace('.tar.gz?raw=true', '.tar.gz')
        # Extract the archive file
        tar = tarfile.open(archive_file)
        tar.extractall(destination_dir)
        tar.close()
        if remove_package == True:
            os.remove(archive_file)
        # Bring templates up to the project root level
        if datapackage:
            root = [x for x in os.listdir(destination_dir) if os.path.isdir(os.path.join(destination_dir, x))][0]
            for filename in os.listdir(os.path.join(destination_dir, root)):
                shutil.move(os.path.join(destination_dir + '/' + root, filename), os.path.join(destination_dir, filename))
            os.rmdir(os.path.join(destination_dir, root))
            self.datapackage = Package(os.path.join(destination_dir, 'datapackage.json'))
            with open(os.path.join(destination_dir, 'README.md'), 'r') as f:
                self.readme = f.read()
        print('Template archive extracted.')

    def infer_resources(self, template_source):
        """."""
        ignore = re.compile('\.DS_Store|\.gitignore|__pycache__|.ipynb_checkpoints')
        filepaths = [str(f) for f in Path(template_source).glob('**/*.*') if f.is_file()]
        filepaths = [f for f in filepaths if f != template_source + '/.ipynb' and not re.search(ignore, f)]
        for path in filepaths:
            self.package.add_resource({'path': path})
        for index, resource in enumerate(self.package.resources):
            descriptor = resource.infer()
            self.package.descriptor['resources'][index] = descriptor

    def load(self, template_source, destination_dir):
        """Load a template archive from a source location.

        @template_source (str): The filepath or url to the template archive file.
        @destination_dir (str): The path to the folder where the template archive file should be copied.
        """
        # Make sure a destination exists
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
        if template_source == 'latest':
            latest = 'https://api.github.com/repos/whatevery1says/workspace_templates/releases/latest'
            response = requests.get(latest, stream=True)
            tarball_url = response.json()['tarball_url']
            destination_file = os.path.join(destination_dir, tarball_url.split('/')[-1])
            response = requests.get(tarball_url, stream=True)
            with open(destination_file, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
        elif template_source.startswith('http'):
            # Get filename from url and strip GitHub's ?raw=true
            filename = template_source.split('/')[-1].replace('.tar.gz?raw=true', '.tar.gz')
            destination_file = os.path.join(destination_dir, filename)
            response = requests.get(template_source, stream=True)
            with open(destination_file, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
        else:
            shutil.copy(template_source, destination_dir)

    def make_archive(self, template_source, archive_file):
        """Make a tar archive of the template folder.

        @template_source (str): The root folder of the templates to be archived.
        @archive_file (str): The path to the filename of the output archive (with or without the `.tar.gz` extension).
        """
        # Strip GitHub's ?raw=true
        archive_file = archive_file.replace('.tar.gz?raw=true', '.tar.gz')
        archive_file = re.sub('.tar.gz', '', archive_file)
        with tarfile.open(archive_file + '.tar.gz', mode='w:gz') as archive:
            archive.add(template_source, recursive=True)
        print('Template archive created.')

def cli_make(args):
    """Make a template archive from the command line."""
    required = ['name', 'version', 'author', 'template_source', 'archive_file']
    for value in required:
        if value not in vars(args):
            argument = value.replace('template_', '')
            argument = argument.replace('_', '-')
            raise('You must supply a value for ' + argument + ' to make an archive.')
    package = TemplatePackage(args.name, args.version, args.author)
    package.create_datapackage(args.template_source)
    package.make_archive(args.template_source, args.archive_file)

def cli_extract(args):
    """Extract a template archive from the command line."""
    required = ['template_source', 'destination_dir']
    for value in required:
        if value not in vars(args):
            argument = value.replace('template_', '')
            argument = argument.replace('_', '-')
            raise('You must supply a value for ' + value + ' to extract an archive.')
    package = TemplatePackage()
    # Copy the template package from its source to a destination_dir
    package.load(args.template_source, args.destination_dir)
    archive_filename = str(Path(args.template_source).name)
    archive_filepath = os.path.join(args.destination_dir, archive_filename)
    # Extract the archive to the destination_dir with option to remove
    package.extract(archive_filepath, args.destination_dir, remove_package=args.remove_package)

if __name__ == '__main__':
    usage = """For making a template archive:

    `python template_package.py [--action] make [--name] template_name [--version] 1.0.0 [--author] "John Smith" [--source] template_source_directory [--archive-file] path_to_output_file`

    For extracting a template archive:

    `python template_package.py [--action] extract [--source] archive_file_path [--destination-dir] destination_directory`

    or

    `python template_package.py [--action] extract [--source] archive_file_url [--destination-dir] destination_directory`"""
    # Parse the command line
    parser = ArgumentParser(prog='TemplatePackage',
                            description='Package workspace templates and load and extract packaged templates into a folder.',
                            usage=usage,
                            add_help=False)
    required = parser.add_argument_group('Required Arguments')
    optional = parser.add_argument_group('Optional Arguments')
    required.add_argument('--action', type=str, choices=['make', 'extract'], dest='action', help='Specify whether the desired action is to "make" or "extract" an archive.')
    optional.add_argument('-n', '--name', metavar='n', type=str, help='Specify the name of the template package. Required for making new packages.', dest='name')
    optional.add_argument('-v', '--version', metavar='v', type=str, help='Specify the semantic version of the template package. Required for making new packages.', dest='version')
    optional.add_argument('-a', '--author', metavar='a', type=str, help='Specify the author of the template package (not the templates). Required for making new packages.', dest='author')
    optional.add_argument('-s', '--source', metavar='s', type=str, help='If making an archive, specify the folder to be packaged, or, if extracting an archive, specify the filepath or url to the archive to be extracted.', dest='template_source', default=None)
    optional.add_argument('-f', '--archive-file', metavar='f', type=str, help='Specify the path and filename where the archive will be saved.', dest='archive_file', default=None)
    optional.add_argument('-d', '--destination-dir', metavar='d', type=str, help='Specify the directory where an archive will be extracted.', dest='destination_dir', default=None)
    optional.add_argument('-r', '--remove-package', metavar='d', type=str, help='Specify whether to delete the package after it is extracted. Default is `True`.', dest='remove_package', default=True)
    optional.add_argument('-h', '--help', action='help', default=SUPPRESS, help='Show this help message and exit.')
    args = parser.parse_args()
    # If run from the command line, call the pipeline based on the action
    if any(vars(args).values()):
        if args.action == 'make':
            cli_make(args)
        elif args.action == 'extract':
            cli_extract(args)
