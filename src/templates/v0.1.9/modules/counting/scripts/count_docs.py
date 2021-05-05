"""count_docs.py.

Count the number of documents per unique source per year in a given project.

For use with count_documents.ipynb v 2.0.

Last update: 2020-06-25
"""

import csv
import os
import string
import unidecode
import json
import re
import shutil
import collections
import operator
import pandas as pd
from collections import defaultdict
from pymongo import MongoClient 
import qgrid
from IPython.display import display, HTML

grid_options = {
    # SlickGrid options
    'fullWidthRows': True,
    'syncColumnCellResize': True,
    'forceFitColumns': False,
    'defaultColumnWidth': 110,
    'rowHeight': 28,
    'enableColumnReorder': True,
    'enableTextSelectionOnCells': False,
    'editable': False,
    'autoEdit': False,
    'explicitInitialization': True,
    # Qgrid options
    'maxVisibleRows': 15,
    'minVisibleRows': 8,
    'sortable': True,
    'filterable': True,
    'highlightSelectedCell': False,
    'highlightSelectedRow': True
}

def source_from_filename(row):
    '''Given a row from dfr-browser's metadata file (i.e., one document in the model), return the name of the source
    of the document using the document filename. For use when Lexis Nexis does not provide publication source 
    information.'''
    # Grab the filename.
    filename = row['id']
    # If the filename begins with a digit, look in specific place for the source name.
    if re.match("json/\d", filename):
        try:
            match = re.search("_\d+_([a-z]+)_", filename)
            title = match.group(1)
        except AttributeError as err:
            title = 'unknown'
    # If the filename begins with 'we1schomp' or 'chomp', look in another place.
    if re.match("json/we1schomp_", filename) or re.match("json/chomp_", filename):
        try:
            match = re.search("_([a-z]+)_", filename)
            title = match.group(1)
        except AttributeError as err:
            title = 'unknown'
    return title

def year_from_row(row):
    '''Given a row from dfr-browser's metadata file (i.e., one document in the model), return the publication year
    of the document using the document filename. For use when Lexis Nexis does not provide publication date
    information.'''
    # Grab the filename.
    filename = row['id']
    # If the filename begins with a digit, look in specific place for the publication year.
    if re.match("json/\d", filename):
        try:
            match = re.search("_(\d\d\d\d)-\d\d-\d\d", filename)
            year = match.group(1)
        # Use 'unknown' as publication year if we can't determine it.
        except AttributeError as err:
            year = 'unknown'
    # If the filename begins with 'we1schomp' or 'chomp', look in another place.
    if re.match("json/we1schomp_", filename) or re.match("json/chomp_", filename):
        try:
            match = re.search("_(\d\d\d\d)\d\d\d\d_", filename)
            year = match.group(1)
        # Use 'unknown' as publication year if we can't determine it.
        except AttributeError as err:
            year = 'unknown'
    return year

def year_from_fpath(file):
    '''Given a json filename, return the publication year of the document using the document filename. For use when Lexis Nexis       does not provide publication date information.'''
    # If the filename begins with a digit, grab the relevant publication year from filename.
    # If we can't do it, we assign it as 'unknown.'
    year = ''
    if re.match("^\d", file):
        try:
            match = re.search("_(\d\d\d\d)-\d\d-\d\d", file)
            year = match.group(1)
        except AttributeError as err:
            year = 'unknown'
    # If the filename begins with `we1schomp` or `chomp`, grab the pub year from filename.
    # If we can't do it, we assign it as 'unknown'.
    if re.match("^we1schomp_", file) or re.match("^chomp_", file):
        try:
            match = re.search("_(\d\d\d\d)\d\d\d\d_", file)
            year = match.group(1)
        except AttributeError as err:
            year = 'unknown'
    if year == '':
        year = 'unknown'
    return year

def year_from_pubdate(pubdate):
    '''Grab just the publication year from Lexis Nexis UTC pubdates.'''
    # Grab the first four digits of the given Lexis Nexis UTC pubdate.
    try:
        match = re.search('(\d\d\d\d)', pubdate)
        year = match.group(1)
    # If you can't do it, stamp year as 'unknown'
    except AttributeError as err:
        year = 'unknown'
    return year

def source_count_by_year(mode, md_file, json_dir, title_field, date_field):
    '''Count the number of articles per source and per publication year in a given project. 
    
    Can use dfr-browser's metadata file or a directory of json files. Returns a dataframe where each row is a unique source and 
    each column is a unique year.'''
    # Define variables.
    count_title = 0
    count_date = 0
    d = defaultdict(list)
    sourceyear_list = []
    year_list = []
    # Open up dfr-browser metadata file and read it in as csv.
    if mode == 'dfr-browser':
        try:
            with open(md_file) as mdf:
                mdreader = csv.DictReader(mdf)
                # Grab the source name and the pubdate from the metadata file.
                for row in mdreader:
                    source = row['journaltitle']
                    pubdate = row['pubdate']
                    # If there's not a source name, call source_from_filename function to find it.
                    if not source:
                        source = source_from_filename(row)
                    # Find the publication year, depending on the info we have.
                    # If all options fail, the below functions will stamp the pubdate as 'unknown'
                    if re.match('\d\d\d\d', pubdate):
                        year = year_from_pubdate(pubdate)
                    if not pubdate:
                        year = year_from_row(row)
                    if pubdate == '':
                        year = year_from_row(row)
                    if pubdate == 'none':
                        year = year_from_row(row)
                    if pubdate == 'unknown':
                        year = year_from_row(row)
                    if year == None:
                        year = 'unknown'
                    if year == '':
                        year = 'unknown'
                    # coerce into string
                    year = str(year)
                    # Add the publication year to a list of all publication years for counting purposes.
                    year_list.append(year)
                    # Create a source,year tuple.
                    syt = (source, year)
                    # Add the source,year tuple to a list of all source,year tuples.
                    sourceyear_list.append(syt)
        except FileNotFoundError:
            display(HTML('<p style="color:#FF0000";>Dfr-browser metadata file not found. Dfr-browser may not exist for this project. See `md_file` value under Settings. Use `json` mode instead.</p>'))
            return
            # Take all of the publication years from all of the documents and create a list where each unique year only appears 
            # once.
            unique_years = sorted(set(year_list))
            # Take the list of all source,year tuples and add them to a dictionary of dictionaries where the key is each source
            # and the value is the year.
            for k,v in sourceyear_list:
                d[k].append(v)
            # Then for each unique source, count the number of documents published in that source for each unique year.
            # Store this in the dictionary of dictionaries.
            for k, v in d.items():
                new_cols = []
                for year in unique_years:
                    num = v.count(year)
                    new_cols.append(num)
                    d[k] = new_cols
    if mode == 'json':
        # start with a directory
        for file in os.listdir(json_dir):
            # json check!
            if file.endswith('.json'):
                # take one file at a time
                fpath = os.path.join(json_dir, file)
                with open(fpath) as f:
                    # read that file and load its data
                    json_decoded = json.loads(f.read())
                    # try to grab the document's source
                    try:
                        source = json_decoded[title_field]
                    # if a document doesn't have the specified title_file, the source = unkown
                    except KeyError as err:
                        count_title += 1
                        source = 'unknown'
                    # if the source still isn't set, it's unknown
                    if source == '':
                        source = 'unknown'
                    # check to see if the document has the specified date field to grab the publication year
                    try:
                        json_date = json_decoded[date_field]
                    # if it doesn't, mark date as 'unknown'
                    except KeyError as err:
                        count_date += 1
                        json_date = 'unknown'
                    # check if date is already a 4-digit year:
                    result = isinstance(json_date, int)
                    if result == True:
                        year = json_date
                    # if not, try to derive the year of publication from the full publication UTC format date
                    else: 
                        if json_date is not None:
                            year = year_from_pubdate(json_date)
                        else:
                            year = 'unknown'
                    # if the date is unknown, try to get it from the filename (will probably only work with WE1S data)
                    if json_date == 'unknown' or year == None or year == 'unknown':   
                        year = year_from_fpath(file)
                    # last try (will only work if using WE1S data): if the publication year is listed as 'unknown', try to 
                    # get an accurate year from the `pub_date` field.
                    # if that doesn't work, keep it at 'unknown'
                    if year == 'unknown':
                        try:
                            pubdate = json_decoded['pub_date']
                            match = re.search('(\d\d\d\d)', pubdate)
                            year = match.group(1)        
                        except:
                            year = 'unknown'
                    if year == None:
                        year = 'unknown'
                    if year == '':
                        year = 'unknown'
                    # coerce into string
                    year = str(year)
                    # Add the publication year to a list of all publication years for counting purposes.
                    year_list.append(year)
                    # Create a source,year tuple.
                    syt = (source, year)
                    # Add the source,year tuple to a list of all source,year tuples.
                    sourceyear_list.append(syt)
        # Take all of the publication years from all of the documents and create a list where each unique year only appears once.
        unique_years = sorted(set(year_list))
        # Take the list of all source,year tuples and add them to a dictionary of dictionaries where the key is each source
        # and the value is the year.
        for k,v in sourceyear_list:
            d[k].append(v)
        # Then for each unique source, count the number of documents published in that source for each unique year.
        # Store this in the dictionary of dictionaries.
        for k, v in d.items():
            new_cols = []
            for year in unique_years:
                num = v.count(year)
                new_cols.append(num)
                d[k] = new_cols
    # Convert dict of dicts to a pandas dataframe for easy viewing in the notebook and create a 'Total' column that displays
    # the total number of documents for each unique source.
    df = pd.DataFrame.from_dict(d, orient='index', columns=unique_years)
    df = df.fillna('unknown')
    df['Total'] = df.sum(axis=1)
    if count_title > 0:
        display(HTML('<p style="color:#FF0000";>Check title_field variable. Specified title field does not exist in 1 or more documents.</p>'))
    if count_date > 0:
        display(HTML('<p style="color:#FF0000";>Check date_field variable. Specified date field does not exist in 1 or more documents.</p>'))
    return df

def docs_by_field(json_dir, field):
    '''Counts number of documents per given field. Returns a dataframe of counts by field and lists of docs that
    can't be opened or that don't contain the given field.'''
    # Define variables.
    bad_jsons = []
    no_field = []
    count = 0
    count_dict = {}
    df = 'did not count'
    forbidden = ['custom', 'vectors', 'speed', 'language_model', 'features', 'bag_of_words']
    # if the user enters a field this function isn't designed to use, print out statement and return values and stop.
    if field in forbidden:
        print("This function cannot count the values associated with this field. If you would like to count this field, talk to Lindsay.")
        return bad_jsons, no_field, df
    # otherwise, start with the json directory
    for file in os.listdir(json_dir):
        # json check!
        if file.endswith('.json'):
            # open each document in the directory
            fpath = os.path.join(json_dir, file)
            with open(fpath) as fin:
                # load that document's json data; if it can't be loaded, append filename to list of files that can't be opened.
                try:
                    json_data = json.loads(fin.read())
                except ValueError as err:
                    bad_jsons.append(file)
                    continue
                # see if the document has the field of interest. if it does, count. 
                try:
                    json_field = json_data[field]
                    if field == 'tags' or field == 'readability_scores':
                        for tag in json_field:
                            if tag in count_dict:
                                count_dict[tag] = count_dict[tag] + 1
                            else:
                                count_dict[tag] = 1 
                    else:  
                        if json_field in count_dict:
                             count_dict[json_field] = count_dict[json_field] + 1
                        else:
                             count_dict[json_field] = 1                        
                # if a document doesn't have that field, add it to the appropriate list and keep going.
                except KeyError as err:
                    no_field.append(file)
                    continue
    # calculate number of files in json directory
    json_dir_files = [file for file in os.listdir(json_dir) if file.endswith('.json')]
    json_length = len(json_dir_files)
    # turn counting dict into a pandas dataframe, define header and first row
    # first row is just number of total documents in json directory
    df = pd.DataFrame(list(count_dict.items()), columns= ['value', 'total number of docs'])
    row = pd.DataFrame([['total docs in project', json_length]], columns= ['value', 'total number of docs'])
    df = df.append(row)
    # sort dataframe by number of documents
    df = df.sort_values(by='total number of docs', ascending=False)
    return bad_jsons, no_field, df


def specific_value_count(json_dir, field, target_value):
    '''Counts number of documents with a specific value in a specific field. Returns a count variable and lists of 
    docs that can't be opened or that don't contain the given field.'''
    # Define variable.
    bad_jsons = []
    no_field = []
    value_count = 0
    # Start with the json directory
    for file in os.listdir(json_dir):
        # Json check!
        if file.endswith('.json'):
            # open each document in the directory
            fpath = os.path.join(json_dir, file)
            with open(fpath) as fin:
                # load that document's json data; if it can't be loaded, append filename to list of files that can't be opened.
                try:
                    json_data = json.loads(fin.read())
                except ValueError as err:
                    bad_jsons.append(file)
                    continue
                # see if the document has target field. if it does, count target values. 
                try:
                    json_field = json_data[field]
                    if field == 'tags' or field == 'readability_scores':
                        for tag in json_field:
                            if tag == target_value:
                                value_count += 1
                    else:
                        if json_field == target_value:
                            value_count += 1
                # if a document doesn't have that field, add it to the appropriate list and keep going.
                except KeyError as err:
                    no_tags.append(file)
                    continue
    return value_count
