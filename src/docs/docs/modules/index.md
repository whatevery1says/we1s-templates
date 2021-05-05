# Modules

This section provides brief overviews of the individual modules in the Workspace. More information and a User Guide for each module can be found on the individual module pages and in the `README.md` files inside each module folder.

## `comparing`

The `comparing` module allows you to compare two sets of textual data to one another to discover how, and how much, they differ using the Wilcoxon rank sum test, a statistical test that determines if the relative frequencies of specific words in two populations are significantly different from one another (that is, they have different distributions). This helps you to determine what the most "significant" words in each dataset are.

For more on the Wilcoxon rank sum test in the context of corpus analytics, see [Jefrey Lijffijt, Terttu Nevalainen, Tanja Säily, Panagiotis Papapetrou, Kai Puolamäki, Heikki Mannila, "Significance testing of word frequencies in corpora", _Digital Scholarship in the Humanities_, Volume 31, Issue 2, June 2016, Pages 374–397.](https://doi-org.libproxy.csun.edu/10.1093/llc/fqu064){: target="_blank"}

## `counting`

The `counting` module contains notebooks for counting various aspects of project data. The notebooks allow you to count project documents (`count_documents.ipynb`), to count the number of documents containing a specific token (`docs_by_search_term.ipynb`), to calculate token frequencies (`frequency.ipynb`), to calculate tf-idf scores (`tfidf.ipynb`), to calculate various collocation metrics (`collocation.ipynb`), and to grab summary statistics of documents, tokens, etc in the project (`vocab.ipynb`). The `vocab.ipynb` notebook requires that your json data files contain a `bag_of_words` field with term counts. If you did not generate this field when you imported your data, you can do so using `tokenize.ipynb`, which leverages <a href="https://spacy.io" target="_blank">spaCy's</a> tokenizer. The `docs_by_search_term.ipynb`, `frequency.ipynb`, `tfidf.ipynb`, and `collocation.ipynb` notebooks use a custom tokenizer based on the tokenizer available in <a href="https://www.nltk.org/" target="_blank">NLTK</a>. This differs from the tokenizer WE1S uses in its preprocessing and topic modeling pipelines, which only tokenizes unigrams. As a result, some features of these notebooks will not work if you do not have access to full-text data.

## `dendrogram`

The `dendrogram` module performs hierarchical agglomerative clustering on the _topics_ of a topic model or multiple topic models in a project. Several distance metrics and linkage methods are available. The default settings will conform closely to the output of pyLDAvis and the scaled view of dfr-browser. Information on alternative distance metrics can be found <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.pdist.html#scipy.spatial.distance.pdist" target="_blank">here</a>, and information on alternative linkage methods can be found <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html" target="_blank">here</a>, in the documentation for the Python `scipy` package, which is used "under the hood".

As dendrograms typically become crowded and hard to read, the visualizations are generated with <a href="https://plotly.com/python/" target="_blank">Plotly</a>, which allows them to be browsed interactively with its pan and zoom features.

## `dfr_browser`

The `dfr_browser` module implements the creation and customization of Andrew Goldstone's <a href="https://github.com/agoldst/dfr-browser" target="_blank">dfr-browser</a> from a topic model produced with <a href="http://mallet.cs.umass.edu/topics.php" target="_blank">MALLET</a> (the output of the `topic_modeling` module). Dfr-browser code, stored in this module in `dfrb_scripts`, was written by Andrew Goldstone and adapted for WE1S use to provide an easy pipeline from data import to topic modeling to visualisation. WE1S uses an older version of Goldstone's code (v0.5.1) (see <a href="https://agoldst.github.io/dfr-browser/" target="_blank">https://agoldst.github.io/dfr-browser/</a> for a version history). WE1S uses Goldstone's `prepare_data.py` Python script to prepare the data files, not Goldstone's R package.

## `diagnostics`

The `diagnostics` module produces a modified version of the <a href="http://mallet.cs.umass.edu/diagnostics.php" target="_blank">diagnostics visualization</a> on the <a href="http://mallet.cs.umass.edu/topics.php" target="_blank">MALLET</a> website. This includes various metrics for analyzing the quality of topic models. Users can generate diagnostics to visualize a single model or a comparative visualisation for multiple models.

## `export`

The `export` module provides utilities for exporting data from a project or a project as a whole to a compressed `tar.gz` archive. The `tar` format is preferred to the `zip` format for entire projects because it preserves file permissions. This is less important for exports of the data itself.

## `import`

The `import` module is main starting point for using the WE1S Workspace project. Use this module to import data into your project. Imported data is stored in the `project_data` folder. The import pipeline attempts to massage all data into a collection of JSON files, stored in the `project_data/json` folder. These JSON files contain both data and metadata as a series of key-value pairs that conform to the <a href="https://en.wikipedia.org/wiki/JSON" target="_blank">JSON</a> file format. The names of the keys (also called "fields") conform to the WE1S manifest schema _and_ certain metadata required by the tools in the WE1S Workspace. After import, the text content of your data will be stored in the JSON files' `content` field. JSON files are human-readable text files, which you can open and inspect. However, it is very easy to corrupt their format. If you ever suspect that this may have happened, you can paste the text into a JSON validator like <a href="https://jsonlint.com/" target="_blank">jsonlint.com</a> to check for errors.

The import notebook requires either a zip archive of your data or a connection to a MongoDB database where the data is stored. Zip archives may take one of the following forms:

1. A zip archive containing plain text data _and_ an accompanying CSV file with relevant metadata.
2. A zip archive containing data already in JSON format.
3. A zip archive of a <a href="https://frictionlessdata.io/" target="_blank">Frictionless Data</a> data package containing data already in JSON format.

If your metadata does not contain the field names required by the WE1S workspace, the import module allows you to map your metadata's field names onto the WE1S field names that comply with the WE1S manifest schema. Most modules in the Workspace assume that your project's json files contain schema-compliant fields.

## `json_utilities`

This module provides helpful methods of accessing the contents of you project's `json` folder. This folder can be quite large, and may cause the browser to freeze if opened using the Jupyter notebook file browser. The `json_utilities.ipynb` notebook in this module provides methods for reading the contents of files in the `json` folder and for performing database-like queries on its contents to filter results.

The `remove_fields.ipynb` notebook will remove specified field from all files in the `json` folder. It is intended primarily for creating sample data sets for testing or for removing content that might be subject to intellectual property restrictions.

## `metadata`

The `metadata` module enables you to generate some basic statistics about document counts based on the metadata fields available in your project's json files. You can also use the `add_metada1 notebook to add custom metadata fields to your project's json files after the data has been imported.

This module also contains a notebook for generating visualizations based on project data using the <a href="https://github.com/JasonKessler/scattertext" target="_blank">Scattertext</a> library.

## `pyldavis`

This module allows you to produce pyLDAvis visualizations of topic models produced using <a href="http://mallet.cs.umass.edu/topics.php" target="_blank">MALLET</a> (the output of the `topic_modeling` module). <a href="https://github.com/bmabey/pyLDAvis" target="_blank">pyLDAvis</a> is a port of the R LDAvis package for interactive topic model visualization by Carson Sievert and Kenny Shirley.

pyLDAvis is designed to help users interpret the topics in a topic model by examining the relevance and salience of terms in topics. Once a pyLDAvis object has been generated, many of its properties can be inspected as in tabular form as a way to examine the model. However, the main output is a visualization of the relevance and salience of key terms to the topics.

pyLDAvis is not designed to use MALLET data out of the box. This notebook transforms the MALLET state file into the appropriate data formats before generating the visualization. The code is based on Jeri Wieringa's blog post <a href="http://jeriwieringa.com/2018/07/17/pyLDAviz-and-Mallet/" target="_blank">Using pyLDAvis with Mallet</a> and has been slightly altered and commented.

## `topic_bubbles`

This module creates a topic bubbles visualization from dfr-browser data generated in the dfr-browser notebook or from model data generated in the `topic_modeling` module. This module uses scripts originally written by Sihwa Park for the WE1S project. For more information on Park's script, see <a href="https://github.com/sihwapark/topic-bubbles" target="_blank">Park's topic bubbles Github repo</a> and the `README.md` located in this module's `tb_scripts` folder.

## `topic_modeling`

This module uses <a href="http://mallet.cs.umass.edu/topics.php" target="_blank">MALLET</a> to topic model project data. Prior to modeling, the notebooks extract word vectors from the project's json files into a single `doc_terms.txt` file, which is then imported into MALLET. Stop words are stripped at this stage. By default, the WE1S Standard Stoplist contained in the `scripts` folder is used for this process. After modeling is complete, there is an option to create a scaled data file for use in visualisations such as `dfr-browser` and `pyLDAvis`.

## `utilities`

This module is really a container for miscellaneous "helper" notebooks that can be used to interact with the data in the project. `clear_caches.ipynb` provides various methods for deleting data, clearing notebook outputs, or resetting a project folder to its original state.

`zip_folder.ipynb` provides code to save any folder as a zip archive so that it can be exported from the Workspace.
