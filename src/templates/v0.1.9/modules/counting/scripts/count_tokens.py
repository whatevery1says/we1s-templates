"""count_tokens.py.

Count the number of documents in a project containing a specific word or phrase; obtain uni-, bi-, and trigram frequency counts and relative frequencies; obtain tf-idf scores for specific words; and utilize some basic collocation metrics for determining the relationships between words in a project.

For use with count_tokens.ipynb v 2.0.

Last update: 2020-07-01
"""

import os
import json
import re
import csv
import shutil
import nltk
nltk.download('punkt')
from nltk import word_tokenize, sent_tokenize
from nltk import ngrams, FreqDist
import nltk.collocations
import nltk.corpus
from nltk.data import load
import collections
from pymongo import MongoClient 
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
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

def get_we1s_stopwords(stopword_file):
    '''Returns a list of we1s stopwords, taken from the multiple_topics_template.'''
    # Create a list to store stopwords in
    stopword_list = []
    # open up the stopwords file in the template and add each word to the list
    with open(stopword_file, 'r') as f:
        for row in f:
            stopword_list.append(row.strip())
    return stopword_list

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

def tokenize_single_file(json_content, content_field, set_length, set_stopwords, stopword_file, punctuations):
    '''Uses NLTK's tokenizer, with some custom tweaks, to tokenize a single document as unigrams, bigrams, or trigrams.
    For use within the overall_count and frequency_single_file functions below. Takes the content field of a json file as input,     NOT a json document itself (i.e., you must read in the json document and grab its content field before calling this     
    function). Bigram and trigram tokenization capability is only available with full-text data (i.e., content_field = 
    'content').'''
    # set needed variable
    finder = None
    # lower case it
    lower_text = json_content.lower()
    # if we're doing unigrams, and/or stopwords, tokenize accordingly
    if set_length == 'unigram':
        if set_stopwords == True:
            stopword_list = get_we1s_stopwords(stopword_file)
            contractions = ["n't", "nt", "'re", "re","'ll", "ll", "d", "'d", "t.", "l.", "'s", "s", "b.", "m.", "p."]
            for contraction in contractions:
                stopword_list.append(contraction)
            json_tokens = [token for token in nltk.word_tokenize(lower_text) if token not in stopword_list]
            json_tokens_final = [token for token in json_tokens if token not in punctuations]
        else:
            json_tokens_final = [token for token in nltk.word_tokenize(lower_text) if token not in punctuations]
    # if we're doing bigrams, and/or stopwords, tokenize accordingly.
    # we use both nltk.bigrams and nltk's BigramCollocationFinder class to tokenize here and for trigrams. 
    # this is rather silly, but it's because of how each method stores its resulting data, and how we manipulate 
    # and view that data later on in the count_tokens notebook.
    # basically, i couldn't figure out how to make things work by only using one tokenization method here.
    elif set_length == 'bigram' and content_field == 'content':
        if set_stopwords == True:
            stopword_list = get_we1s_stopwords(stopword_file)
            contractions = ["n't", "nt", "'re", "re","'ll", "ll", "d", "'d", "t.", "l.", "'s", "s", "b."]
            for contraction in contractions:
                stopword_list.append(contraction)
            json_tokens = [token for token in nltk.word_tokenize(lower_text) if token not in stopword_list]
            json_tokens = [token for token in json_tokens if token not in punctuations]
            json_tokens_final = list(nltk.bigrams(json_tokens))
            finder = nltk.collocations.BigramCollocationFinder.from_words(json_tokens)
        else:
            json_tokens = [token for token in nltk.word_tokenize(lower_text) if token not in punctuations]
            json_tokens_final = list(nltk.bigrams(json_tokens))
            finder = nltk.collocations.BigramCollocationFinder.from_words(json_tokens)
    # if we're doing trigrams, and/or stopwords, tokenize accordingly.
    elif set_length == 'trigram' and content_field == 'content':
        if set_stopwords == True:
            stopword_list = get_we1s_stopwords(stopword_file)
            contractions = ["n't", "nt", "'re", "re","'ll", "ll", "d", "'d", "t.", "l.", "'s", "s", "b."]
            for contraction in contractions:
                stopword_list.append(contraction)
            json_tokens = [token for token in nltk.word_tokenize(lower_text) if token not in stopword_list]
            json_tokens = [token for token in json_tokens if token not in punctuations]
            json_tokens_final = list(nltk.trigrams(json_tokens))
            finder = nltk.collocations.TrigramCollocationFinder.from_words(json_tokens)
        else:
            json_tokens = [token for token in nltk.word_tokenize(lower_text) if token not in punctuations]
            json_tokens_final = list(nltk.trigrams(json_tokens))
            finder = nltk.collocations.TrigramCollocationFinder.from_words(json_tokens)
    elif (set_length == 'trigram' and (content_field == 'bag_of_words' or content_field == 'features')) or (set_length == 
                                                                                                              'bigram' and 
                                                                                                            (content_field == 
                                                                                                             'bag_of_words' or 
                                                                                                             content_field == 
                                                                                                             'features')):
        print('This notebook is not configured to detect ' + set_length + 's using the ' + content_field + ' field!')
        json_tokens_final = None
        finder = None
    return json_tokens_final, finder

def docs_by_search_term(json_dir, content_field, required_phrase, set_stopwords, source_set, set_length, punctuations, stopword_file):
    '''Counts the number of documents that contain a specific word or phrase. Returns a list containing filenames for
    easy downloading, and a dictionary containing bibliographic information for each document containing the word or
    phrase, as well as the number of times the word appears in each document.'''
    # set needed variables
    source_dict = {}
    source_dict['Filename'] = []
    source_dict['Author'] = []
    source_dict['Title'] = []
    source_dict['Source Name'] = []
    source_dict['Publication Date'] = []
    source_dict['Count'] = []
    file_list = []
    bad_jsons = []
    json_author = ''
    json_title = ''
    json_pub = ''
    json_date = ''
    # start with a directory
    for file in os.listdir(json_dir):
        # json check!
        if file.endswith('.json'):
            # take one file at a time
            fpath = os.path.join(json_dir, file)
            with open(fpath) as f:
                # read that file and load its content field
                try:
                    json_decoded = json.loads(f.read())
                except ValueError as err:
                    bad_jsons.append(fpath)
                    continue
                # grab the content from whatever field the user has selected
                if content_field == 'content':
                    json_content = json_decoded['content']
                    # lower case the content field
                    lower_text = json_content.lower()
                if content_field == 'features':
                    features = [feature[0] for feature in json_decoded['features']]
                    json_content = ' '
                    json_content = json_content.join(features)
                    lower_text = json_content.lower()
                if content_field == 'bag_of_words':
                    bow = json_decoded['bag_of_words']
                    features = []
                    for k,v in bow.items():
                        features.append(k)
                    json_content = ' '
                    json_content = json_content.join(features)   
                    lower_text = json_content.lower()
                # lower case required phrase
                required_phrase = required_phrase.lower()
                # if the content field contains the required word or phrase, do the rest.
                if re.search(required_phrase, json_content, re.IGNORECASE):
                    # set count to 0 for each file
                    count = 0
                    # add the file to a list of file names for downloading later
                    file_list.append(file)
                    # now try grabbing various bibliographic info; default to 'Unknown'
                    try:
                        json_title = json_decoded['title']
                    except KeyError as err:
                        json_title = 'Unknown'
                    if json_title == '':
                        json_title = 'Unknown'
                    try:
                        json_author = json_decoded['author']
                    except KeyError as err:
                        json_author = 'Unknown'
                    if json_author == '':
                        json_author = 'Unknown'
                    # can use source field or not. default is to not use it.
                    if source_set == True:
                        try:
                            json_pub = json_decoded['source']
                        except KeyError as err:
                            try:
                                json_pub = json_decoded['pub']
                            except KeyError as err:
                                json_pub = 'Unknown'
                    elif source_set == False:
                        try:
                            json_pub = json_decoded['pub']
                        except KeyError as err:
                            json_pub = 'Unknown'
                    if json_pub == '':
                        json_pub = 'Unknown'
                    try:
                        json_date = json_decoded['pub_date']
                    except KeyError as err:
                        try:
                            json_date = json_decoded['pub_year']
                        except KeyError as err:
                            json_date = year_from_fpath(file)
                    if json_date == '':
                        json_date = year_from_fpath(file)
                    # if we are removing stopwords, grab the stopwords and then tokenize accordingly.
                    # custom tokenizer
                    json_tokens_final, finder = tokenize_single_file(json_content, content_field, set_length, set_stopwords, 
                                                                     stopword_file, punctuations)
                    if json_tokens_final == None and finder == None:
                        file_list = None
                        df = None
                        bad_jsons = None
                        print('Please reconfigure.')
                        return file_list, df, bad_jsons
                    # frequency distribution method 1 (only one used in this function)
                    freq = FreqDist(json_tokens_final)
                    # save frequency count for the required word or phrase depending on type of word or phrase.
                    if set_length == 'unigram':
                        for k,v in freq.items():
                            if k == required_phrase:
                                count = v 
                    elif set_length == 'bigram':
                        token1 = required_phrase.split()[0]
                        token2 = required_phrase.split()[1]
                        token_bi = (token1, token2)
                        for k,v in freq.items():
                            if k == token_bi:
                                count = v
                    elif set_length == 'trigram':
                        token1 = required_phrase.split()[0]
                        token2 = required_phrase.split()[1]
                        token3 = required_phrase.split()[2]
                        token_tri = (token1, token2, token3)
                        for k,v in freq.items():
                            if k == token_tri:
                                count = v
                    # add to overall count dictionary
                    source_dict['Filename'].append(fpath)
                    source_dict['Author'].append(json_author)
                    source_dict['Title'].append(json_title)
                    source_dict['Source Name'].append(json_pub)
                    source_dict['Publication Date'].append(json_date)
                    source_dict['Count'].append(count)
    df = pd.DataFrame(source_dict)
    return file_list, df, bad_jsons

def zip_json(zip_path, file_list, json_dir):
    ''' Copy json files containing search ngram (those listed in file_list) to separate folder and zip folder up for easy downloading.'''
    # If folder that will be zipped already exists, delete; make if doesn't already exist
    if os.path.exists(zip_path) == True:
        shutil.rmtree(zip_path)
        os.mkdir(zip_path)
    else:
        os.mkdir(zip_path)
    # Copy documents containing search ngram to folder created above
    for file in file_list:
        fpath = json_dir + '/' + file
        shutil.copy(fpath, zip_path)
    # Zip up the folder
    zpath_json = zip_path + '.zip'
    if os.path.exists(zpath_json) == True:
        shutil.rmtree(zpath_json)
        shutil.make_archive(zip_path, 'zip', zip_path)
    else:
        shutil.make_archive(zip_path, 'zip', zip_path)
    # Remove the directory (but not the zip file)
    shutil.rmtree(zip_path)
    
def zip_txt(txt_path, file_list, json_dir, content_field):
    '''Copy content field from json files containing search ngram (those listed in file_list) to separate folder and zip folder up for easy downloading.'''
    # If folder that will be zipped already exists, delete; make if doesn't already exist
    if os.path.exists(txt_path) == True:
        shutil.rmtree(txt_path)
        os.mkdir(txt_path)
    else:
        os.mkdir(txt_path)
    # Copy content field of documents containing search ngram to folder created above
    for file in file_list:
        fpath = json_dir + '/' + file
        slug = file.split('.')[0]
        txtpath = txt_path + '/' + slug + '.txt'
        with open(fpath) as fin:
            json_data = json.loads(fin.read())
            json_content = json_data[content_field]
        with open(txtpath, 'w') as fout:
            fout.write(json_content)
    # Make it a zip file
    zpath_txt = txt_path + '.zip'
    if os.path.exists(zpath_txt) == True:
        shutil.rmtree(zpath_txt)
        shutil.make_archive(txt_path, 'zip', txt_path)
    else:
        shutil.make_archive(txt_path, 'zip', txt_path)
    # Remove the directory (but not the zip file)
    shutil.rmtree(txt_path)

def frequency_single_file(fpath, content_field, set_stopwords, punctuations, set_length, stopword_file):
    '''Produces an nltk frequency count dictionary for a single json file using 2 different methods.'''
    # set needed variable
    finder = None
    # just working with a single file here, error handling
    try:
        with open(fpath) as f:
            json_decoded = json.loads(f.read())
    except FileNotFoundError:
        display(HTML('<p style="color: red;">This file does not exist. Please check file path.</p>'))
        finder_freq = None
        freq = None
        return finder_freq, freq
        # grab the content from whatever field the user has selected
    if content_field == 'content':
        try:
            json_content = json_decoded['content']
        except KeyError:
            display(HTML('<p style="color: red;">Selected content field not found. Please check file.</p>'))
            finder_freq = None
            freq = None
            return finder_freq, freq
    if content_field == 'features':
        try:
            features = [feature[0] for feature in json_decoded['features']]
            json_content = ' '
            json_content = json_content.join(features)
        except KeyError:
            display(HTML('<p style="color: red;">Selected content field not found. Please check file.</p>'))
            finder_freq = None
            freq = None
            return finder_freq, freq 
    if content_field == 'bag_of_words':
        try:
            bow = json_decoded['bag_of_words']
            features = []
            for k,v in bow.items():
                features.append(k)
            json_content = ' '
            json_content = json_content.join(features) 
        except KeyError:
            display(HTML('<p style="color: red;">Selected content field not found. Please check file.</p>'))
            finder_freq = None
            freq = None
            return finder_freq, freq
    # custom tokenizer
    json_tokens_final, finder = tokenize_single_file(json_content, content_field, set_length, set_stopwords, stopword_file, 
                                                     punctuations)
    if json_tokens_final == None and finder == None:
        finder_freq = None
        freq = None
        display(HTML('<p style="color:red;">Frequency calculation failed. Please check file.</p>'))
        return finder_freq, freq
    # frequency distribution method 1
    freq = FreqDist(json_tokens_final)
    # frequency distribution method 2
    # not needed for unigrams so hence the if clause here
    if finder == None:
        finder_freq = None
    else:
        finder_freq = finder.ngram_fd.items()
    display(HTML('<p style="color: green;">Frequency counts complete. View and explore results by running the cells below.</p>'))
    return finder_freq, freq

def frequency_dir(json_dir, content_field, set_stopwords, punctuations, set_length, stopword_file):
    '''Produces an nltk frequency count dictionary for all documents in a project using 2 different methods.
    Also returns a list of the NLTK tokenizer finders for each document for use in association metrics.'''
    # set needed variables
    finder = None
    all_tokens = []
    all_finders_freq = {}
    all_finders_list = []
    bad_jsons = []
    # we are working with a directory here so start there
    for file in os.listdir(json_dir):
        # json check!
        if file.endswith('.json'):
            # open up each document and load its content
            fpath = os.path.join(json_dir, file)
            with open(fpath) as f:
                try:
                    json_decoded = json.loads(f.read())
                except ValueError as err:
                    bad_jsons.append(fpath)
                    continue
                # grab content from whatever content_field the user has selected
                try:
                    if content_field == 'content':
                        json_content = json_decoded['content']
                except KeyError:
                    bad_jsons.append(fpath)
                    continue
                try:
                    if content_field == 'features':
                        features = [feature[0] for feature in json_decoded['features']]
                        json_content = ' '
                        json_content = json_content.join(features)
                except KeyError:
                    bad_jsons.append(fpath)
                    continue
                try:
                    if content_field == 'bag_of_words':
                        bow = json_decoded['bag_of_words']
                        features = []
                        for k,v in bow.items():
                            features.append(k)
                        json_content = ' '
                        json_content = json_content.join(features) 
                except KeyError:
                    bad_jsons.append(fpath)
                    continue
                # custom tokenizer
                json_tokens_final, finder = tokenize_single_file(json_content, content_field, set_length, set_stopwords, 
                                                                 stopword_file, punctuations)
                # ok now put all of the tokens obtained through tokenization method 1 into a big list that will
                # eventually contain all of the tokens for the whole project.
                for item in json_tokens_final:
                    all_tokens.append(item)
                # frequency distribution method 2
                if finder == None:
                    finder_freq = None
                else:
                    finder_freq = finder.ngram_fd.items()
                    # put each bi- or trigram frequency into big dictionary so that frequencies for the whole project 
                    # will exist in one data structure by the end (like freq, obtained below).
                    # presumably it would be better to use nltk's CorpusReader class to handle this, but it was much
                    # easier just to do it this way and we don't require all of the functionality of the CorpusReader 
                    # class anyway. 
                    all_finders_freq.update(finder_freq)
                    # put the finder for each document into a list for use in later analyses.
                    all_finders_list.append(finder)
    # frequency distribution method 1 using all_tokens list
    freq = FreqDist(all_tokens)
    return all_finders_freq, all_finders_list, freq, bad_jsons

def dummy_fun(tokens):
    '''Dummy function for use in tfidf_dir function below. This function exists so we can use the custom tokenization functions 
    defined earlier in this script, and don't have to rely on scikitlearn's tokenizer.'''
    return tokens

def freq_df(freq_type, freq):
    '''Calculate raw or relative frequency values from a freq object. Produce a dataframe of values.'''
    if freq_type == 'raw':
        df = pd.Series(freq, name='Raw Frequency')
        df.index.name = 'Token'
        df = df.reset_index()
        df = df.sort_values('Raw Frequency', ascending=False)
        freq_dist = None
        display(HTML('<p style="color:green;">Dataframe of raw frequency counts created. View dataframe below.</p>'))
    if freq_type == 'relative':
        # obtain the total number of tokens in the document
        norm = freq.N()
        # make a copy of the freq object 
        freq_dist = freq.copy()
        # replace raw frequency counts with relative frequency values
        for key in freq_dist.keys():
            freq_dist[key] = float(freq_dist[key]) / norm
        # create and format dataframe
        df = pd.Series(freq_dist, name='Relative Frequency')
        df.index.name = 'Token'
        df = df.reset_index()
        df = df.sort_values('Relative Frequency', ascending=False)
        display(HTML('<p style="color:green;">Dataframe of relative frequency values created. View dataframe below.</p>'))
    return df, freq_dist

def freq_token(token, set_length, freq_type, freq, freq_dist):
    '''Calculate the frequency of a specific token in the project as a whole or in a single file.'''
    if set_length == 'unigram':
        if freq_type == 'raw':
            x = freq[token]
        if freq_type == 'relative':
            x = freq_dist[token]
        display(HTML('<p><strong>' + token + ':</strong> ' + str(x)))
    if set_length == 'bigram':
        token1 = token.split()[0]
        token2 = token.split()[1]
        if freq_type == 'raw':
            x = freq[token1, token2]
        if freq_type == 'relative':
            x = freq_dist[token1, token2]
        display(HTML('<p><strong>' + token + ':</strong> ' + str(x)))
    if set_length == 'trigram':
        token1 = token.split()[0]
        token2 = token.split()[1]
        token3 = token.split()[2]
        if freq_type == 'raw':
            x = freq[token1, token2, token3]
        if freq_type == 'relative':
            x = freq_dist[token1, token2, token3]
        display(HTML('<p><strong>' + token + ':</strong> ' + str(x)))

def tfidf_dir(json_dir, content_field, set_stopwords, punctuations, set_length, stopword_file):
    '''Use scikitlearn's tfidf vectorizer to obtain tf-idf scores for documents in a given directory. Returns a 
    dataframe of all tokens and tf-idf values for each document, vectors, feature_names, and a list of file names of 
    documents in the project.'''
    # set needed variables
    token_dict = {}
    bad_jsons = []
    # we are working with a directory here so start there
    for file in os.listdir(json_dir):
        # json check!
        if file.endswith('.json'):
            # open up each document and load its content
            fpath = os.path.join(json_dir, file)
            with open(fpath) as f:
                try:
                    json_decoded = json.loads(f.read())
                except ValueError as err:
                    bad_jsons.append(fpath)
                    continue
                # grab content from whatever content_field the user has selected
                if content_field == 'content':
                    json_content = json_decoded['content']
                if content_field == 'features':
                    features = [feature[0] for feature in json_decoded['features']]
                    json_content = ' '
                    json_content = json_content.join(features)
                if content_field == 'bag_of_words':
                    bow = json_decoded['bag_of_words']
                    features = []
                    for k,v in bow.items():
                        features.append(k)
                    json_content = ' '
                    json_content = json_content.join(features)  
                # tokenize the file
                json_tokens_final, finder = tokenize_single_file(json_content, content_field, set_length, set_stopwords, 
                                                                 stopword_file, punctuations)
                # put the contents in a dictionary with the key as the filepath and the value as the tokens
                token_dict[fpath] = json_tokens_final
    # once you've done that for every file, grab just the values (content) of the dictionary
    tokens = token_dict.values()
    # grab the keys (filepaths)
    file_list = list(token_dict.keys())
    # use scikitlearn's tfidf vectorizer
    tfidf = TfidfVectorizer(tokenizer=dummy_fun, preprocessor=dummy_fun, token_pattern=None)
    # fit and transform
    vectors = tfidf.fit_transform(tokens)
    # put the individual tokens and their tfidf values into a dataframe
    feature_names = tfidf.get_feature_names()
    dense = vectors.todense()
    denselist = dense.tolist()
    df_tfidf = pd.DataFrame(denselist, columns=feature_names, index=file_list)
    return df_tfidf, vectors, feature_names, file_list, bad_jsons

def tfidf_token(set_length, token, df_tfidf):
    '''Calculate the tf-idf value of a specific ngram in each project document.'''
    if set_length == 'unigram':
        try:
            df_tfidf_token = df_tfidf[[token]]
            df_tfidf_token = df_tfidf_token.loc[df_tfidf_token[token] > 0]
        except KeyError as err:
            msg = token + ' not in project'
            display(HTML('<p style="color:red;">' + msg + '</p>'))
            df_tfidf_token = None
            return df_tfidf_token
    if set_length == 'bigram':
        token1 = token.split()[0]
        token2 = token.split()[1]
        token_tuple = (token1, token2)
        try: 
            df_tfidf_token = df_tfidf[[token_tuple]]
            df_tfidf_token = df_tfidf_token.loc[df_tfidf_token[token_tuple] > 0]
        except KeyError as err:
            msg = token + ' not in project'
            display(HTML('<p style="color:red;">' + msg + '</p>'))
            df_tfidf_token = None
            return df_tfidf_token
    if set_length == 'trigram':
        token1 = token.split()[0]
        token2 = token.split()[1]
        token3 = token.split()[2]
        token_tuple = (token1, token2, token3)
        try:
            df_tfidf_token = df_tfidf[[token_tuple]]
            df_tfidf_token = df_tfidf_token.loc[df_tfidf_token[token_tuple] > 0]
        except KeyError as err:
            msg = token + ' not in project'
            display(HTML('<p style="color:red;">' + msg + '</p>'))
            df_tfidf_token = None
            return df_tfidf_token
    display(HTML('<p style="color:green;">Calculations complete. View results in the next cell.'))
    return df_tfidf_token

# Next 3 functions are taken from https://buhrmann.github.io/tfidf-analysis.html
def top_tfidf_feats(row, feature_names, top_n):
    ''' Get top n tfidf values in df_tfidf row and return them with their corresponding feature names.'''
    topn_ids = np.argsort(row)[::-1][:top_n]
    top_feats = [(feature_names[i], row[i]) for i in topn_ids]
    df = pd.DataFrame(top_feats)
    df.columns = ['token', 'tfidf']
    display(HTML('<p style="color:green;">Calculations complete. View results in next cell.</p>'))
    return df

def top_feats_in_doc(vectors, feature_names, row_id, top_n):
    ''' Top tfidf features in specific document (df_tfidf row) '''
    row = np.squeeze(vectors[row_id].toarray())
    return top_tfidf_feats(row, feature_names, top_n)

def top_mean_feats(vectors, feature_names, top_n, grp_ids=None, min_tfidf=0.1):
    ''' Return the top n features that on average are most important among documents in rows
        indentified by indices in grp_ids. '''
    if grp_ids:
        D = vectors[grp_ids].toarray()
    else:
        D = vectors.toarray()

    D[D < min_tfidf] = 0
    tfidf_means = np.mean(D, axis=0)
    return top_tfidf_feats(tfidf_means, feature_names, top_n)

# Collocation metric functions
def collocation_metric(set_length, all_finders_list, metric, freq_filter=None):
    '''Use NLTK collocation metrics to return various association metric scores for all tokens in the project. Returns a 
    dataframe with association metrics for each token. Only works with one association metric at a time.'''
    # define variable -- need a dict to store scores
    all_scores = {}
    # use NLTK association metrics for bigrams or trigrams, depending on what the user has selected
    if set_length == 'bigram':
        association_metrics = nltk.collocations.BigramAssocMeasures()
    if set_length == 'trigram':
        association_metrics = nltk.collocations.TrigramAssocMeasures()
    # use the finders list, obtained via the frequency_dir function, to gather different association metrics
    for item in all_finders_list:
        # log-likelihood ratio
        if metric == 'likelihood':
            likelihood = item.score_ngrams(association_metrics.likelihood_ratio)
            all_scores.update(likelihood)
            ScoreTable = pd.DataFrame(list(all_scores.items()), 
                                  columns=['token','likelihood ratio']).sort_values(by='likelihood ratio', ascending=False)
        # mutual information score
        if metric == 'mi':
            if freq_filter:
                item.apply_freq_filter(freq_filter)
            MI = item.score_ngrams(association_metrics.mi_like)  
            all_scores.update(MI)
            ScoreTable = pd.DataFrame(list(all_scores.items()), columns=['token','MI']).sort_values(by='MI',        
                                                                                                           ascending=False)
        # pointwise mutual information score
        if metric == 'pmi':
            if freq_filter:
                item.apply_freq_filter(freq_filter)
            PMI = item.score_ngrams(association_metrics.pmi)  
            all_scores.update(PMI)
            ScoreTable = pd.DataFrame(list(all_scores.items()), columns=['token','PMI']).sort_values(by='PMI', 
                                                                                                             ascending=False)
        # student's t-test
        if metric == 't-test':
            TTest = item.score_ngrams(association_metrics.student_t)
            all_scores.update(TTest)
            ScoreTable = pd.DataFrame(list(all_scores.items()), columns=['token','t-test']).sort_values(by='t-test', 
                                                                                                              ascending=False)
        # chi-squared test
        if metric == 'chi-square':
            chisq = item.score_ngrams(association_metrics.chi_sq)
            all_scores.update(chisq)
            ScoreTable = pd.DataFrame(list(all_scores.items()), columns=['token','chi-sq']).sort_values(by='chi-sq', 
                                                                                                                ascending=False)
    return ScoreTable, all_scores

def order_collocation_scores(all_scores, token, save_csv=False, csv_file=None):
    '''Given a token, returns all collocation metric scores that include that token. I.e., if you would like to see
    the specific scores for words that co-occur with "science," this is how you display and save those results. Can only be run 
    after running collocation_metric function above, because it requires the all_scores dict returned by that function. Returns a 
    list of tuples ordered from highest to lowest scores. If save_csv option is turned on and csv_file set, saves a csv file of  
    results. Csv file will not be ordered (that would be too simple! [i.e., couldn't figure that out]).'''
    # define variable -- need a dict of lists
    prefix_keys = collections.defaultdict(list)
    # iterate through the all_scores returned via the collocation_metric function
    # add the token the user has selected along with other words it occurs with (in bi- or trigram) as key, scores as value
    for key,scores in all_scores.items():
        prefix_keys[key[0]].append((key[1], scores))
    # sort this defaultdict by bi- or trigrams with highest scores
    for key in prefix_keys:
        prefix_keys[key].sort(key = lambda x: -x[1])
    # grab all scores for token of interest for inspection by user
    token_scores = prefix_keys[token]
    # if save_csv is turned on, save results to a csv file
    if save_csv == True:
        with open(csv_file, 'w') as fin:
            writer = csv.writer(fin, delimiter = ',')
            writer.writerow(['token', 'score'])
            for k,v in all_scores.items():
                if token in k:
                    row = (k,v)
                    writer.writerow(row)
    return token_scores


