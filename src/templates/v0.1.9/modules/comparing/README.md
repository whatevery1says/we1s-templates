# Comparing

## Info

Authors: Lindsay Thomas
Copyright: copyright 2020, The WE1S Project
License: MIT
Version: 2.0
Email: lindsaythomas@miami.edu
Last Update: 2021-03-08

## About This Module

This noteboook allows you to compare two sets of textual data to one another to discover how, and how much, they differ based on word frequency. The notebook performs this comparison using the Wilcoxon rank sum test, a statistical test that determines if two samples (i.e., the relative frequencies of a specific word in two different datasets) are taken from populations that are significantly different from one another (meaning, if they have different distributions). When used to compare word frequency data from two different datasets, it helps you to determine what the most "significant" words in each dataset are.

For details on the Wilcoxon rank sum test, see <a href="https://data.library.virginia.edu/the-wilcoxon-rank-sum-test/" target="_blank">this description</a> by the University of Virgina Library. For implementations of the Wilcoxon rank sum test in literary studies, see Andrew Piper and Eva Portelace's article <a href="http://post45.org/2016/05/how-cultural-capital-works-prizewinning-novels-bestsellers-and-the-time-of-reading/" target="_blank">How Cultural Capital Works: Prizewinning Novels, Bestsellers, and the Time of Reading</a> (<em>Post45</em>, 5.10.16)</A>, and chapter 4 "Fictionality" from Andrew Piper's book <em>Enumerations</em>.

## Notebooks

- `compare-word-frequencies.ipynb`: Main notebook for the module. Provides an interface to the code in `compare_word_frequencies.py` script.

## User Guide

Prior to beginning the workflow, you already must have two `doc-terms` files, one for each dataset you wish to compare. A `doc-terms` file is a text file representing the vocabulary in each document in the dataset. `doc-terms` files must contain rows of space-delimited columns beginning with the filename and index number (starting with 0), and then a list of every token in the document (with each instance of a token in its own column). Each row in each file should represent one document. A small example is given below:

```
sample_document1.json 0 21st a a a an an absolutely abyss academic addition advance afghanistan...
sample_document2.json 1 a a a an an an artificial artificial food food ingredients...
```

As you can see in the example above, the data in these files should already be tokenized and (ideally) stripped of stop words. If you have already prepared your data for topic modeling, there will be a `doc_terms.txt` file in your project's `project_data/models`, which you can use as an example of the format. This notebook does not include any processes for tokenizing or stripping stop words from document data.

**Important: The two doc-terms files you are comparing must not have overlapping filenames.**

The `compare_word_frequencies.ipynb` notebook provides 3 different methods to help users select data for this test: you can simply provide the filepaths to the `doc-terms` files you want to use; you can use a list of filenames to select only specific files from a given `doc-terms` file; and/or you can select a random sampling of files from a given `doc-terms` file. Each of these options is described in the notebook.

Once you have your `doc-terms` files ready, you can prepare your data for the test and then run the test. Please refer to the notebook for additional instructions about how to run the test.

## Module Structure

📦comparing
 ┣ 📂results
 ┣ 📂scripts
 ┃ ┣ 📜compare_word_frequencies.py
 ┣ 📜compare-word-frequencies.ipynb
 ┗ 📜README.md
