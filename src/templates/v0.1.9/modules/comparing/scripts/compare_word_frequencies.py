"""compare_word_frequencies.py.

Compare two datasets to one another using a Wilcoxon rank sum test.

For use with compare_word_frequencies.ipynb v 2.0.

Last update: 2021-02-16
"""

from scipy.stats import mannwhitneyu
from scipy.stats import ranksums
import os
import csv
import json
import collections
from collections import Counter
from collections import defaultdict
import pandas as pd
import statistics
import random
from IPython.display import display, HTML

def get_bags(filenames, docterms_original, docterms_selected):
    """Check filenames against the doc-terms file and grab doc bags where filenames match.
    
    Accepts a list of filenames and returns a new doc-terms file including only selected documents.
    """
    # define variables
    filenames_list = []
    # open provided list of filenames and add to python list
    with open(filenames) as f1:
        for row in f1:
            row = row.strip()
            filenames_list.append(row)
    # create new file including only selected documents
    with open(docterms_selected, 'w') as f2:
        # open up file with all bags of words for the collection ("docterms_original" file)
        # if a filename in this file matches one in the list of filenames,
        # grab the bag of words for that filename to print to new doc-terms file
        with open(docterms_original) as f3:
            for row in f3:
                row2 = row.strip()
                row2 = row2.split(' ')
                filename = row2[0]
                for x in filenames_list:
                    if x == filename:
                        f2.write(row)
    display(HTML('<p style="color: green;">New doc-terms file created at <code>' + docterms_selected + '</code>.</p>'))

def get_random_sample(selection, docterms_original, docterms_selected):
    """Randomly select a selected number of docs from a doc-terms file.
    
    @selection: the number of documents to return.
    @docterms_original: the full doc-terms file.
    
    Returns a `docterms_sample` file containing the random sample of documents from `docterms_original`.
    """ 
    # define variables
    filenames_list = []
    # open up docterms_original and grab the filename
    # add each filename to a list
    with open(docterms_original) as f1:
        for row in f1:
            row2 = row.strip()
            row2 = row2.split(' ')
            filename = row2[0]
            filenames_list.append(filename)
    # take a random sample of the filenames list
    sample = random.sample(filenames_list, selection)
    # create new doc-terms file that will include only randomly selected documents
    with open(docterms_selected, 'w') as f2, open(docterms_original) as f3:
        for row in f3:
            row2 = row.strip()
            row2 = row2.split(' ')
            filename = row2[0]
            for x in sample:
                if x == filename:
                    f2.write(row)
    display(HTML('<p style="color: green;">New doc-terms file created at <code>' + docterms_selected + '</code>.</p>'))
    
def findFreq(bags):
    """Converts a doc-terms file into dataframes containing the document's raw word counts and relative word frequencies.
    
    Code adapted from https://github.com/rbudac/Text-Analysis-Notebooks/blob/master/Mann-Whitney.ipynb for we1s data.
    """
    # define variables
    texts = []
    docs_relative = {}
    docs_freqs = {}
    num_words = 0
    counts = defaultdict(int)    
    num_words = 0
    with open(bags) as f:
        # grab filename and bag of words for every document in txt file.
        for row in f:
            row = row.strip()
            row = row.split(' ')
            filename = row[0]
            x = len(row)
            words = row[2:x]
            # add each word in each doc to a dict of dicts and count raw frequencies
            for word in words:
                counts[word] += 1
            num_words += len(words)
            # create dicts for relative frequencies and for raw frequencies of each word in each doc
            relativefreqs = {}
            freqs = {}
            # add words and frequencies to dictionaries
            for word, rawCount in counts.items():
                relativefreqs[word] = rawCount / float(num_words)
                freqs[word] = rawCount
                # reset counts to use for the next doc
                counts[word] = 0
            # add relative and raw freqs for each doc to overall dictionary for all docs, filenames are keys
            docs_relative[filename] = relativefreqs
            docs_freqs[filename] = freqs
    # convert dicts to pandas dataframes and return dataframes.
    # the dataframes we are creating here are sparse matrices of EVERY word in EVERY doc in the input file.
    # as a result, they can get huge very quickly.
    # loading anything over ~4000 documents and handling via pandas can cause memory problems bc of the large 
    # vocabulary size. this code is therefore not extensible to large datasets.
    # this is why this notebook encourages users to work with small samples of their data. 
    # for large datasets, we recommend rewriting our code to take advantage of the parquet file format 
    # (for more on pandas integration with parquet, see https://pandas.pydata.org/pandas-docs/version/0.21/io.html#io-parquet)
    # or using numpy arrays. Sorry we didn't do this ourselves.
    df_relative = pd.DataFrame(docs_relative)
    df_freqs = pd.DataFrame(docs_freqs)
    return df_relative, df_freqs

def edit_freq_dataframes(df1_relative, df1_freqs, df2_relative, df2_freqs):
    """Prepare datadrames produced by findFreqs(), including replacing NA with 0, counting totals, and sorting.
    
    Also returns average number of times any word occurs in each dataset.
    
    The operations could be added to findFreqs() but are separated out because of memory use issues.
    """
    # fill na values with 0's
    # freqs = x
    df1_freqs = df1_freqs.fillna(0)
    df1_relative = df1_relative.fillna(0)
    df2_freqs = df2_freqs.fillna(0)
    df2_relative = df2_relative.fillna(0)
    # add total_count columns that count of # of times each word occurs across all docs in each dataset
    df1_freqs['total_count'] = df1_freqs.sum(axis=1)
    df2_freqs['total_count'] = df2_freqs.sum(axis=1)
    # sort dataframes in descending order by total_count column
    df1_freqs = df1_freqs.sort_values(by=['total_count'], ascending = False)
    df2_freqs = df2_freqs.sort_values(by=['total_count'], ascending = False)
    # obtaining average total word counts for each dataset
    counts_c1 = list(df1_freqs['total_count'])
    average_c1 = statistics.mean(counts_c1)
    counts_c2 = list(df2_freqs['total_count'])
    average_c2 = statistics.mean(counts_c2)
    # print results as cell output
    display(HTML('<p><strong>Average total word count for dataset 1:</strong> ' + str(average_c1) + '</p>'))
    display(HTML('<p><strong>Average total word count for dataset 2:</strong> ' + str(average_c2) + '</p>'))
    return df1_relative, df1_freqs, df2_relative, df2_freqs

def match_dataframes_and_save(threshold, df1_freqs, df1_relative, df2_freqs, df2_relative, c1_relative_csv, c2_relative_csv, c1_raw_csv, c2_raw_csv):
    """Create relative frequency dataframes.
    
    Uses raw and relative frequency dataframes obtained via edit_freq_dataframes() to create 
    new dataframes of relative frequency data, including only those words that occur at least
    x number of times (where x = threshold).
    
    Saves these dataframes to csv files so code doesn't have to be re-run, and also returns
    them as df1 and df2. Does the same for dataframes of raw counts data. Also returns lists
    of words in each dataset for use in the get_vocablist function below. Again, this function
    will produce 2 dataframes of relative (not raw) frequency data that are limited to words
    that occur at least x number of times. We need the relative frequency dataframes for
    performing the actual Wilcoxon test, so this is why we do this matching.
    """
    # if no threshold is set by user, just rename some variables so it all turns out right in the end
    if threshold == False:
        df1_raw = df1_freqs
        df2_raw = df2_freqs
    # otherwise, only grab documents from df1_freqs and df2_freqs dataframes that meet or exceed threshold
    else:
        df1_raw = df1_freqs[df1_freqs.total_count >= threshold]
        df2_raw = df2_freqs[df2_freqs.total_count >= threshold]
    # create lists of words in each new dataframe to use in matching
    words_c1 = list(df1_raw.index)
    words_c2 = list(df2_raw.index)
    # then create new dataframe consisting of relative frequencies only for words that are included in each list
    df1 = df1_relative[df1_relative.index.isin(words_c1)]
    df2 = df2_relative[df2_relative.index.isin(words_c2)]
    display(HTML('<p><strong>Words in dataset 1:</strong> ' + str(len(df1)) + '</p>'))
    display(HTML('<p><strong>Words in dataset 2:</strong> ' + str(len(df2)) + '</p>'))
    display(HTML('<p style="color: green;">Dataframes created. Saving files...<br>'))
    # create csv files
    df1.to_csv(c1_relative_csv)
    display(HTML('<code>' + c1_relative_csv + '</code><br>'))
    df2.to_csv(c2_relative_csv)
    display(HTML('<code>' + c2_relative_csv + '</code><br>'))
    df1_raw.to_csv(c1_raw_csv)
    display(HTML('<code>' + c1_raw_csv + '</code><br>'))
    df2_raw.to_csv(c2_raw_csv)
    display(HTML('<code>' + c2_raw_csv + '</code></p>'))
    return df1, df2, words_c1, words_c2

def get_vocablist(df1, df2, words_c1, words_c2, vocablist):
    """Create a list of all of the unique words across both datasets.
    
    Saves to disk as a plain-text file where each word is its own row.
    """
    # create vocab list
    words_c1 = list(df1.index)
    words_c2 = list(df2.index)
    words_total = words_c1 + words_c2
    words = set(words_total)
    with open(vocablist, 'w') as fout:
        for word in words:
            fout.write(word + '\n')
    display(HTML('<p style="color: green;">Vocab list created and saved to <code>' + vocablist + '</code>.</p>'))

def wrs_test(c1_relative_csv, c1_raw_csv, c2_relative_csv, c2_raw_csv, vocablist, results_csv):
    """Perform the Wilcoxon Rank Sum test.
    
    Requires csv files of 2 datasets for comparison (created in section 2 of
    compare_word_frequencies notebook), dataframes of raw counts of these datasets
    (also created in section 2 of the notebook), a list of the unique words across
    both datasets, and the name of a csv file to save the output to. Performs a
    Wilcoxon rank sums test on 2 datasets of relative word frequencies.
    
    Outputs a csv that lists the raw count of each word in each dataset, the difference
    between those counts, the percentage change in counts from dataset 1 to dataset 2,
    and the Wilcoxon statistic and p-value for each comparison.
    
    Code adapted from https://github.com/rbudac/Text-Analysis-Notebooks/blob/master/Mann-Whitney.ipynb
    and modified for we1s data. Also inspired by Andrew Piper's code from chapter 4 of Enumerations.
    See https://github.com/piperandrew/enumerations/blob/master/04_Fictionality/chap4_Fictionality.R.
    """
    # define needed variables
    missingInCorpus1 = []
    missingInCorpus2 = []
    # read in csvs
    df1 = pd.read_csv(c1_relative_csv, index_col=0) 
    df1 = df1.fillna(0) # replace NaNs with zeroes if not already done.
    df1_raw = pd.read_csv(c1_raw_csv, index_col=0)
    df1_raw = df1_raw.fillna(0)
    df2 = pd.read_csv(c2_relative_csv, index_col=0) 
    df2 = df2.fillna(0) # replace NaNs with zeroes if not already done.
    df2_raw = pd.read_csv(c2_raw_csv, index_col=0)
    df2_raw = df2_raw.fillna(0)
    #Make "dummy" rows of all zeroes for any words that only appear in one corpus and not the other
    for i in range(0, df1.shape[1]):
        missingInCorpus1.append(0) 
    for i in range(0, df2.shape[1]):
        missingInCorpus2.append(0)
    # perform the test and create the output csv file
    with open(results_csv, 'w', newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['word', 'c1 total count', 'c2 total count', 'difference c1 - c2', '% change', 'wilcoxon statistic', 'wilcoxon p-value'])
        # open vocablist
        with open(vocablist, 'r', encoding="utf-8") as f:
            for word in f:
                word = word.strip()
                # check if the word is in df1. if it is, grab the relative freq.
                # grab total count for word in corresponding df1_restrict dataframe.
                # if not, set counts to 0.
                if (word in df1.index):
                    countsInCorpus1 = df1.loc[word].values
                    c1_count = df1_raw.loc[word, 'total_count']
                else:
                    countsInCorpus1 = missingInCorpus1
                    c1_count = 0
                # repeat, checking df2 and df2_restrict
                if (word in df2.index):
                    countsInCorpus2 = df2.loc[word].values
                    c2_count = df2_raw.loc[word, 'total_count']
                else:
                    countsInCorpus2 = missingInCorpus2
                    c2_count = 0
                # now do wilcoxon test by comparing rel freqs of word in c1 to rel freqs of word in c2
                # grab metrics we want to save to results_csv
                try:
                    wrs = ranksums(countsInCorpus1, countsInCorpus2)
                    wrsStat = wrs.statistic
                    wrsP = wrs.pvalue  
                    diff = c1_count - c2_count
                    if c2_count == 0:
                        change = 'NaN'
                    else:
                        change = (diff/c2_count) * 100
                except ValueError: # Was having problems with this earlier, so this is mainly for debugging reasons
                    wrsStat = -1
                    wrsP = -1
                writer.writerow([word, c1_count, c2_count, diff, change, wrsStat, wrsP])
    display(HTML('<p style="color: green;"><strong>Test complete. Check the <code>results</code> folder for the csv file.</strong></p>'))

