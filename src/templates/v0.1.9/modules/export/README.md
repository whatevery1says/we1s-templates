# Export

## Info

Authors: Jeremy Douglass, Scott Kleinman, Lindsay Thomas
Copyright: copyright 2020, The WE1S Project
License: MIT
Version: 1.0
Email: scott.kleinman@csun.edu
Last Update: 2020-07-31

## About This Module

The `export` module provides utilities for exporting data from a project or a project as a whole to a compressed tar archive. The tar format is preferred to the zip format for entire projects because it preserves file permissions. This is less important for exports of the data itself.

## Notebooks

- `export_project.ipynb`: The notebook for exporting an entire project.
- `json_to_txt_csv.ipynb`: A utility for exporting files from the project `json` folder to a directory of plain text files with an accompanying metadata CSV file.

## User Guide

### Export Project

This notebook provides the ability to export an entire project to a single file in the form of a .tar.gz archive. File size can be reduced by setting a list of folders for exclusion. Once the archive has been created, its location can optionally be recorded in a MongoDB database. (Eventually it will be possible to store the archive in the database, but this feature is not yet available.

#### Configuration

The notebook expects the following values in the **Configuration** cell:

- `name`: The name of the project archive
- `author`: The name of the author of the archive
- `version`: The version number
- `save_path`: The filepath where the archive will be save (including filename)
- `exclude` (optional): List of folder paths to ignore. Paths should be relative to the project folder without a leading '/'.
- `client` (optional): The url of the MongoDB client
- `database` (optional): The name of a MongoDB database
- `collection` (optional): The name of a MongoDB database

If you are not working with MongoDB, leave these the `client`, `database`, and `collection` set to `None`.

#### Build Data Package

This cell instantiates the `ExportPackage` object and builds a <a href="https://frictionlessdata.io/" target="_blank">Frictionless Data</a> data package detailing the project's resources. If the project directory contains a `datapackage.json` and/or `README.md`, a datetime stamp will be added; otherwise, these files will be created.

Once the data package is built, it is possible to access it with `export_package.datapackage`, and the `README` text can be accessed with `export_package.readme`.

#### Make Archive

This cell creates the archive file. It can be run without modification.

#### Extract Archive

The last two cells can be used to extract an existing project archive file to a project folder. 

Before running the last cell set the following configurations:

`archive_file`: The path the archive file to be extracted
`destination_dir`: The path to the project folder where the project will be extracted. If the folder does not exist, it will be created.
`remove_archive`: By default, the archive file copied to the project folder (not the original one) will be deleted after it is extracted. If you wish to retain it, set `remove_archive=False`.


### json_to_txt_csv

The WE1S workflows use JSON format internally for manipulating data. However, you may wish to export JSON data from a project to plain text files with a CSV metadata file for use with other external tools.

This notebook uses JSON project data to export a collection of plain txt files &mdash; one per JSON document &mdash; containing only the document contents field or bag of words. Each file is named with the name of the JSON document and a `.txt` extension.

It also produces a `metadata.csv` file. This file contains a header and one row per document with the document filename plus required fields.

Output from this notebook can be imported using the import module by copying the `txt.zip` and `metadata.csv` from `project_data/txt` to `project_data/import`. However, it is generally not recommended to export and then reimport data, as you may lose metadata in the process.

#### Configuration

The default configuration assumes:

1. There are JSON files in `project_data/json`.
2. Each JSON has the required fields `pub_date`, `title`, `author`.
3. Each JSON file has either:
   - a `content` field, or
   - a `bag_of_words` field created using the `import` module tokenizer.

The following configurations are accepted:

- `limit`: The number of files to export. Set to `0` to export all files.
- `txt_dir`: The path to the directory where text files will be saved.
- `metafile`: The path to the metadata CSV file (including filename) that will be saved.
- `zipfile`: The path to the zip archive (including filename) that will be saved if `zip_output=True`.
- `zip_output`: Whether or not to create a zip archive the exported plain text files. This option automatically deletes the plain text files after they are zipped.
- `clear_cache`: If set to `True`, previous export contents in the `txt` directory, including metadata and zip files will be deleted before an export is started.
- `txt_content_fields`: A list of JSON fields to be checked in order for data content. The first field encountered in a document will be used for the data export. Documents with no listed field will be excluded from export.
- `csv_export_fields`: A list of JSON fields to be exported to the metadata file. Fields in this list will become the columns in the CSV file.

#### Export

This cell starts the export. It can be run without modification.

#### Export Features Tables

If your data contains features tables (lists of lists containing linguistic features), you can use this cell to export features tables as CSV files for each document in your JSON folder. Set the `save_path` to a directory where you wish to save the CSV files.

## Module Structure

📦export
 ┣ 📂scripts
 ┃ ┃ ┣ 📜export_package.py
 ┃ ┃ ┗ 📜json_to_txt_csv.py
 ┣ 📜export_project.ipynb
 ┣ 📜json_to_txt_csv.ipynb
 ┗ 📜README.md
