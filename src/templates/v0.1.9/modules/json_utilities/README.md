# json_utilities

## Info

Authors: Scott Kleinman
Copyright: copyright 2020, The WE1S Project
License: MIT
Version: 1.0
Email: scott.kleinman@csun.edu
Last Update: 2021-03-08

## About This Module

This notebook provides a method of accessing the contents of a project's `json` folder. These folders can be quite large, and they will cause the browser to freeze if they are opened using the Jupyter notebook file browser. This notebook creates a `Documents` object with which you can call methods that list or read the contents of the files in the `json` folder. It also allows you to perform database-like queries on the contents to filter your results and to export the results to a zip archive.

## User Guide

The main notebook `json_utilities.ipynb` functions more like a tutorial than the notebooks of other modules. There are built-in examples, which you can work through and modify according to your data and research questions. You can also use `remove_fields.ipynb` to remove specific fields from json files.

### Setup

This cell imports Python libraries and scripts.

### View Metadata Fields (Optional)

If you wish to perform a query on your documents, it can be helpful to know what metadata fields are available. The cell below will read the first 100 documents and extract the keys for each metadata field. Note that listed keys may not be available in all documents. If you think that your metadata is very inconsistent, you may want to run `docs.get_metadata_keys()` without start and end values. However, this can take a long time, so it is not recommended unless you have reason to think that there are large discrepancies across your collection.

It is also possible to get the keys for a specific file with `docs.get_metadata_keys(filelist=['file1', 'file2', etc.])`. If you have already run something like `result = docs.get_file_list(0, 5)`, you can simply run `docs.get_metadata_keys(filelist=result)`.

In the second cell, you can generate a table of your documents with `get_table()`. It takes a list of files and a list of fields as its arguments, as in the example below. Columns can be re-ordered, sorted, and filtered. However, it is recommended that you only supply a small number of columns. The bigger the table, the longer the lag time when you scroll.

If you wish to save the table after you have sorted and/or filtered it, set the `filename` in the third cell and run the cell.

### Performing Queries

Although many questions about your data can be answered by working with the table above, sometimes you may need to perform more  sophisticated database-like queries to filter the data in your project's json folder. The cell below provide an interface for performing these queries.

A basic query is given in the form of a tuple with the syntax `(fieldname, operator, value)`. The `fieldname` is the name of the metadata field you wish to search. The `value` is the value you are looking for in the field, and the `operator` is the method by which you will evaluate the value. Here are the possible operators: `<`, `<=`, `=` (or `==`), `!=` (meaning "not equal to"), `>`, `>=`, `contains`. The last will match any value anywhere in the field. For greater power, you can use `regex` as the `operator` and a regex pattern as the `value`.

**Important:** The `fieldname` and `operator` must be enclosed in single quotes. The `value` must also be single quotes unless it is a number or Boolean (`True` or `False`).

The `find()` method takes three arguments: a list of filenames, a query, and, optionally, a Boolean `lower_case` value. If `lower_case=True` the `value` data will be converted to lower case before it is evaluated. The default is `False`.

In the cell below, we will get a list of the first 5 files (to keep things quick) and search for the ones that contain "Politics" in the document's `name` field.

Note: There is a built-in timer class that can be used to time queries of long file lists. Its use is illustrated in the cell below, but it can be used to time any of the methods.

### Performing Multiple Queries

You can pass multiple queries to the `find()` method by using a list of tuples. As you can see from the example below. The result will be every document that matches any of the queries in the list.

### Adding Boolean Logic

It is possible to add more complex Boolean logic by passing a dictionary as the query with `'and'` or `'or'` as the key. The value should be a list of one or more tuples, or a list of dictionaries as shown in the examples. 

### Exporting the Results of a Query

You can save the documents found by your query to a zip file with the `export()` method. It takes a list of filenames and a path where you wish to save the zip file. A filename is sufficient if you wish to save it in the current folder.

The `export()` method takes an optional `text_only` argument. Setting `text_only=True` will export only the `content` fields as plain text files.

Here is an example in which you create a `Documents` object, get a file list, find files in the list that match your query, and export the results to a zip archive.

The timer class is automatically applied to exports.

## Using `remove_fields.ipynb`

This notebook will remove specified field from all files in the `json` folder. It is intended primarily for creating sample data sets for testing, but we could consider documenting it fully and keeping it in the release version of the module.

### Configuration

Configure a list of fields to remove. By default, the folder containing the json files is the project's `json` directory, but you can configure another folder (relative to the project root). Errors will be logged to a file saved with the name you configure.

### Setup

This cell loads your configurations and instantiates your removal job.

### Remove Fields

This cell removes the fields from json files in the directory you have configured.

## Module Structure

📦import
 ┣ 📂scripts
 ┃ ┃ ┗ 📜json_utilities.py
 ┣ 📜json_utilities.ipynb
 ┣ 📜remove_fields.ipynb
 ┗ 📜README.md
