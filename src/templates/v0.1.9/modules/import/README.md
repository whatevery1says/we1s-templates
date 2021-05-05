# Import

## Info

Authors: Jeremy Douglass, Scott Kleinman, Lindsay Thomas
Copyright: copyright 2020, The WE1S Project
License: MIT
Version: 1.3
Email: scott.kleinman@csun.edu
Last Update: 2021-02-15

## About This Module

The `import` module is main starting point for using the WE1S Workspace project. Use this module to import data into your project. Imported data is stored in the `project_data` folder. The import pipeline attempts to massage all data into a collection of JSON files, stored in the `project_data/json` folder. These JSON files contain both data and metadata as a series of key-value pairs that conform to the <a href="https://en.wikipedia.org/wiki/JSON" target="_blank">JSON</a> file format. The names of the keys (also called "fields") conform to the WE1S manifest schema _and_ certain metadata required by the tools in the WE1S Workspace. After import, the text content of your data will be stored in the JSON files' `content` field. JSON files are human-readable text files, which you can open and inspect. However, it is very easy to corrupt their format. If you ever suspect that this may have happened, you can paste the text into a JSON validator like <a href="https://jsonlint.com/" target="_blank">jsonlint.com</a> to check for errors.

The import notebook requires either a zip archive of your data or a connection to a MongoDB database where the data is stored. Zip archives may take one of the following forms:

1. A zip archive containing plain text data _and_ an accompanying CSV file with relevant metadata.
2. A zip archive containing data already in JSON format.
3. A zip archive of a <a href="https://frictionlessdata.io/" target="_blank">Frictionless Data</a> data package containing data already in JSON format.

If your metadata does not contain the field names required by the WE1S workspace, the import module allows to map your metadata's field names onto the WE1S field names.


## Notebooks

- `import.ipynb`: The main notebook for this module.

## User Guide

### Setup

This cell imports various Python modules and defines paths that will be used by the module. In most cases, you will not need to change the default settings.

### Configuration

Configuration options are explained briefly below.

- `zip_file`: The name of the zip archive containing your data. By default, the archive is called `import.zip`, but you can modify the filename. If the data is in plain text format, you must also prepare a `metadata.csv` file. Does not apply when importing from MongoDB (you can set it to `None`).
- `metadata.csv`: The name of your metadata file if you are importing plain text data. By default, it is called `metadata.csv`, but you can change the name. <span style="color:red;">Important:</span> The metadata file must have `filename`, `pub_date`, `title`, and `author` as its first four headers. You can include additional metadata fields _after_ the `author` field. Does not apply when importing directly from JSON files or from MongoDB (you can set it to `None`).
- `remove_existing_json`: Empty the json folder before importing. The default is `False`, so it is possible to add additional data on multiple runs.
- `delete_imports_dir`: If set to `True`, the folder containing your `zip_file` and `metadata.csv` file will be deleted when the import is complete. Does not apply when importing from MongoDB (you can set it to `None`).
- `delete_text_dir`: If set to `True`, the folder containing your imported plain text files will be deleted after they are converted to json format. Does not apply when importing directly from JSON files or from MongoDB (you can set it to `None`).
- `data_dirs`: If you are importing data already in json format, you can specify a list of paths in your zip archive or Frictionless Data data package where the json files are located. Does not apply when importing from MongoDB (you can set it to `None`).
- `title_field`: If you are importing data already in json format that does not contain a field named `title` you can map an existing field to this key by providing the name of the existing field here.
- `author_field`: If you are importing data already in json format that does not contain a field named `author` you can map an existing field to this key by providing the name of the existing field here.
- `pub_date_field`: If you are importing data already in json format that does not contain a field named `pub_date` you can map an existing field to this key by providing the name of the existing field here.
- `content_field`: If you are importing data already in json format that does not contain a field named `content` you can map an existing field to this key by providing the name of the existing field here.
- `dedupe`: If set to `True`, the script will check for duplicate files within the project that may have been created by importing data from multiple zip archives. Duplicate files will be given the extension `.dupe`. This option also changes the extension of json files containing empty `content` fields to `.empty`. <span style="color:red;">Warning:</span> For very large projects (~100,000 or more documents), duplicate detection may take up to several hours to run and, depending on other traffic on the server, may cause a server error.
- `random_sample`: If you wish to import a random sample of the data in your `zip_file`, specify the number of documents you wish to import.
- `random_seed`: Specify a number to initialize the random sampling. This ensures reproducibility if you have to run the import multiple times. In most cases, the setting can be left as `1`.
- `required_phrase`: A word or phrase which will be used to filter the imported data. Only documents that contain the `required_phrase` value will be imported to your project.
- `log_file`: The path to the file where errors and deduping results are logged. The default is `import_log.txt` in the same folder as this notebook.

If you are importing your data directly to MongoDB, rather than a project folder, configure your MongoDB `client`, your database as `db`, and the name of your `collection`. For the `client` setting you can simply enter `MONGODB_CLIENT` to use your project's configuration. If importing from MongoDB, the `query` setting should be a valid MongoDB query. Since MongoDB syntax can be difficult &mdash; especially for complex queries &mdash; you may wish to use the <a href="query-builder/index.html" target="_blank">WE1S QueryBuilder</a> to construct your query and then paste it into the configuration cell. For information on using the Query Builder with your data, see on **Using the QueryBuilder** below.

### Prepare the Workspace for File Import

**You should use this cell only if you are importing from a zip archive.**

This cell sets up an import task based on the configuration you have supplied in the previous cell. When you run this cell, it will indicate whether the setup process was successful. Once the task is set up, instructions are displayed for uploading your data and metadata files to the Workspace.

### Perform the Import

This cell starts the import process. A progress bar indicates the percentage of files imported. You may also receive error messages if there was a problem importing specific files. A log file will be generated, and you can inspect this file to see the nature of the errors. When the process is finished, instructions for tokenize the data are displayed. See the **Tokenize the Data** section below.

### MongoDB

This cell starts the import process directly from MongoDB. Assuming that the client, database, and collection have been configured correctly in the **Configuration** section, it should work automatically. A progress bar indicates the percentage of files imported. You may also receive error messages if there was a problem importing specific files. A log file will be generated, and you can inspect this file to see the nature of the errors. When the process is finished, instructions for tokenize the data are displayed. See the **Tokenize the Data** section below.

For help with constructing MongoDB queries, you may wish to use the <a href="query-builder/index.html" target="_blank">WE1S QueryBuilder</a> to construct your query and then paste it into the configuration cell. For information on using the Query Builder with your data, see on **Using the QueryBuilder** below.

### Tokenize the Data

This cell is optional, but it can save time when performing tasks in other tools. Normally text analysis tools have to divide a text into countable "tokens" (most frequently words). This process is called tokenization. This cell allows you to pre-tokenize your data so that other tools do not need to take this step. It generates a dictionary of token-count pairs such as `{"cat": 3, "dog": 2}` for each of your JSON files. This dictionary is appended to the JSON file in the `bag_of_words` field.

The import tokenizer offers two tokenization methods. The default method is strips all non-alphanumeric characters and then divides the text into tokens on white space. Alternatively, you can use the <a href="https://spacy.io/" target="_blank">spaCy</a> Natural Language Processing library to tokenize based on spaCy's language model. spaCy extracts linguistic `features` from your text, not only tokens but parts of speech and named entities. This is instrinsically slower and may require a lot of memory for large texts. To use WE1S's custom spaCy tokenizer, set `method='we1s'`. If your text has been previously processed by spaCy and there is a `features` table in your JSON file, the tokenizer will attempt to use it to build the `bag_of_words` dictionary. If you do not have a `features` table but would like to save one to your JSON files, configure `save_features_table=True`.

### Using the QueryBuilder

The QueryBuilder is a simple web-based form that allows you to select metadata field names, operators such as "is equal to" or "contains", and values to match in the database. It can be used to generate very complex queries that are difficult to write by hand. To launch the QueryBuilder, open `query-builder/index.html`, configure a query in the form, and click "Get Query to display the query you have configured. You can then copy the one-line query string into the import notebook's `query` setting.

The QueryBuilder may not work if you open the web page on a sandboxed server. If you try to use it in this setting, you will receive a warning with the suggestion to download the `query-builder-bundle.zip` file. Download and extract this file to your local computer, and you can open `index.html` to run the QueryBuilder locally.

By default, the QueryBuilder is configured to display common fields in the WE1S manifest schema. However, you may have metadata fields in your JSON files that are not part of the schema and will therefore not appear in the dropdown menu. If this is the case, you can easily configure the QueryBuilder for metadata fields since its configuration file is also in JSON format. Just open `query-builder/assets/config.js`. Copy a section between curly braces and rename the the `id` and `label` to your desired field name. The `type` should be "string", "integer", "boolean", or "date", depending on the type of value that occurs in that metadata category. There are a couple of examples that perform validation (such as for date format) that can be used as models for your own fields. The QueryBuilder is based on <a href="https://querybuilder.js.org/" target="_blank">jQuery QueryBuilder</a>. See its documentation for more sophisticated forms of customization. We recommend that you make a backup of the `schema.js` file before modifying it. If find that you have corrupted the format of the format, you can paste it into a JSON validator like <a href="https://jsonlint.com/" target="_blank">jsonlint.com</a> (omitting the `var schema =` at the beginning) to check for errors.

## Module Structure

📦import
 ┣ 📂scripts
 ┃ ┃ ┣ 📜import.py
 ┃ ┃ ┣ 📜import_tokenizer.py
 ┃ ┃ ┗ 📜timer.py
 ┣ 📂query-builder
 ┃ ┣ 📂assets
 ┃ ┃ ┣ 📂config
 ┃ ┃ ┃ ┣ 📜schema.js
 ┃ ┃ ┣ 📂css
 ┃ ┃ ┃ ┣ 📜query-builder.default.min.css
 ┃ ┃ ┃ ┗ 📜styles.css
 ┃ ┃ ┣ 📂js
 ┃ ┃ ┃ ┣ 📜query-builder.standalone.min.js
 ┃ ┃ ┃ ┗ 📜builder.js
 ┃ ┣ 📜index.html
 ┃ ┗ 📜README.md
 ┣ 📜import.ipynb
 ┣ 📜query-builder-bundle.zip
 ┗ 📜README.md
