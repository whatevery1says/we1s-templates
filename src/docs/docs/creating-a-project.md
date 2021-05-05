# Creating a Project

Begin by double-clicking on the `new_project.ipynb` notebook. Follow the instructions to create a new project, and then click the link to navigate to the project folder.

!!! note "Note"
    It is good practice to close and halt the `new_project.ipynb` notebook after you have opened the project folder in a new browser tab.

A project is a folder containing copies of the WE1S project template files and folders. Here is a brief description of each part of the project:

## The `README.md` File

This is a Markdown file containing details about the version of the WE1S template used to create the project and any metadata about the project which you added in `new_project.ipynb`. It is meant to be a human-readable guide to the content of the project.

## The `datapackage.json` File

The `datapackage.json` file is a manifest of your project's resources which is compliant with the WE1S manifest schema and the <a href="https://frictionlessdata.io/" target="_blank">Frictionless Data project</a> specification. The purpose of this file is to enable easier interoperability between your data and tools outside the WE1S Workspace. The `datapackage.json` file is is a JSON file containing metadata about the project and a complete list of the file paths to all resources in the project. If you export your project, the `export` module will detect any files you have added and add their paths to `datapackage.json`.

## The `config.py` File

The `config.py` file inside the `config` folder is a Python file that contains information about the Workspace's server environment and the resources installed with the project template. It is used to restore the project to a virgin state if you run the `models/clear_caches.ipynb` notebook.

## The `modules` Folder

The `modules` folder contains all the project's Jupyter notebooks (and supporting scripts and files). Each module focuses on a particular task: e.g., creating a topic model or visualizing it. Some modules can be used at any point in your workflow. Others need to be implemented in a certain order. For instance, the `dfr_browser`, `topic_bubbles`, and `pyldavis` modules create visualizations of topic models, so they will naturally not work until you have run the `topic_modeling` module.

## The `project_data` Folder

The `project_data` contains all your project's primary data. It is empty when the project is first created until you import your data using the `import` module.

!!! note "Note"
    Sample projects providing example of the contents of each of these components of the Workspace can be found in the <a href="#" onclick="alert('This is just a dummy link until we create the examples folder on GitHub.');">examples</a> folder on GitHub.

## Importing Data to Your Project

Before you do anything else, you must import some data to your project. The WE1S accepts data in four formats:

1. A zip archive of plain text (`.txt`) files accompanied by a CSV file containing metadata.
2. A zip archive of JSON files combining the textual content and metadata.
3. A Frictionless Data data package containing paths to all your data files.
4. A query of records in a MongoDB database.

To import your data, navigate to `modules/import/import.ipynb`. This notebook creates a new folder, `project_data/json` and copies your data from its source into this folder, converting it into JSON format, if necessary.

!!! important "Important"
    Most tools in the WE1S Workspace use the JSON files in the `project_data/json` folder. These tools assume that the files are compliant with the WE1S manifest schema. The `import` module provides some functions for converting your metadata fields to the expected format; however, it cannot cover every scenario. You may need to perform some preprocessing on your data prior to import.

!!! note "Note"
    The `import` module automatically coerces your textual data to <a href="https://www.w3.org/International/questions/qa-choosing-encodings" target="_blank">UTF-8 character encoding</a>.

## What Next?

Once you have imported your data, you can perform a number of procedures with the other modules. The WE1S project primarily employs topic modeling in its research methodlogy, so this technique is prominent in the Workspace in its current version. Many of the modules depend on your first having run a topic model on your data. This makes the `topic_modeling` module a good place to start. The `metadata` module contains some analysis and visualization tools that do not require a pre-existing topic model.
