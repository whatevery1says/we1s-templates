# Topic Modeling

## Info

Authors: Dan Baciu, Jeremy Douglass, Scott Kleinman, Lindsay Thomas
Copyright: copyright 2019, The WE1S Project
License: MIT
Version: 2.0
Email: lindsaythomas@miami.edu
Last Update: 2021-02-17


## About This Module

This module uses MALLET to topic model project data. Prior to modelling, the notebooks extract word vectors from the project's JSON files into a single `doc_terms.txt` file, which is then imported into MALLET. Stop words are stripped at this stage. By default, the WE1S Standard Stoplist contained in the `scripts` folder is used for this process. After modelling is complete, there is an option to create a scaled data file for use in visualisations such as `dfr-browser` and `pyLDAvis`.

## Notebooks

- `model_topics.ipynb`: Main notebook for performing topic modelling.

## User Guide
 
This notebook performs topic modelling with MALLET by providing an easy-to-configure interface for the two basic steps, importing your data to MALLET and training your topics. The WE1S project performs a preprocessing step (creating the file to input to MALLET) before the import step and a post-processing step (scaling) after training. These steps are explained below. Both the preprocessing and the postprocessing steps are optional.

These instructions provide a step-by-step guide to using the notebook, once cell at a time. Each cell is referenced here by its title.

Note that when importing data to MALLET or creating topic models, files with the same name will be over-written. If you use different filenames, files from any previous runs will not be deleted.

### Settings

The purpose of this cell is to load some external Python code and define some commonly used file paths. If you encounter errors in any of the subsequent cells, it is worth re-running the **Settings** cell to check that all variables have been defined and all external code has been loaded.

In general, you can run this cell without changing anything. You are most likely to want to customise the following settings: `log_file`, `language_model`, `stoplist_file`. The `log_file` is a text file that lists errors generated when you run the **Create File for Importing to MALLET** cell. By default, it is saved to your `models` directory, but you can save it elsewhere if you wish. The `language_model` is the spaCy language model to use when tokenising your text if you run **Create File for Importing to MALLET** without a pre-tokenised collection of documents. More information on this is given in the instructions for **Create File for Importing to MALLET** below. The `stoplist_file` is the full path to the file containing stop words (words to be omitted from your model). The default setting points to a copy of the WE1S Standard Stoplist stored in the module's `scripts` folder. If you wish to use a different stoplist, set `stoplist_file` to the full path to your stoplist's location (including the filename).

### Create File for Importing to MALLET

MALLET has two methods of importing data: from a flat directory of plain text files or a single file with one document per line. By default, the WE1S project uses the latter method. **Create File for Importing to MALLET** is a preprocessing step that collects data from your project's JSON files and assembles it into a doc_terms file, which is saved as `models/doc_terms.txt` in you project folder.

**If you are running a model on a directory of plain text documents and you want to process them purely with MALLET, you can skip this cell.**

Note that the file that is produced is a plain-text file containing 1 document in the corpus per line. To produce what we call the doc_terms file, each term in a document is counted, and the term is then written however many times it occurs in the document to the document's row in the doc_terms file. For example, if the word "humanities" occurs twice in a document, the row in the doc_terms file will read "humanities humanites". The document's row in the doc_terms file is a string of repeated terms like this, separated by spaces (what is sometimes called a bag of words).

The prepare MALLET import script (`scripts/prepare_mallet_import.py`) creates a `PrepareMalletImport` object that handles the creation of a text file to be imported by MALLET. Although a `PrepareMalletImport` object can be created on a document with `mimport=PrepareMalletImport(0, 'manifest_path.json', 'mallet_import.txt', model='en_core_web_sm', stoplist='we1s_standard_stoplist.txt')`, it will typically be used with a directory of json files. This function loops through a sorted list of json files in the directory, creates a `MalletImport` object from each one, and saves its bag of words as a row in the `doc_terms.txt` file. This is the file that will be imported by MALLET.

If stop words are to be filtered prior to topic modelling, the `prepare_data()` function in `prepare_mallet_import.py` should be fed a stoplist file. If you do not want to strip stop words, give it an empty file.

`prepare_mallet_import.py` first looks for a `bag_of_words` field in your JSON files. A `bag_of_words` is a pre-packaged set of words already counted. If the field is not present, it will next look for a `features` field, extract the tokens from that field, and generate a bag of words. In both cases, the tokens are assumed to have been previously tokenised using the WE1S preprocessor.

If neither the `bag_of_words` nor `features` field is present, the script will attempt to tokenise the text in the `content` field on the fly using a slimmed-down version of the WE1S preprocessor. Note that this process will necessarily be slower and can take a long time for large projects. Tokenisation uses the Python spaCy package, which predicts linguistic features based on a language model. If spaCy is called to do the tokenisation, it will use the language model your designated in **Settings** in most cases, `en_core_web_sm` will be sufficient. Note that the language model must be installed in your environment for this process to work.

Normally you will run **Create File for Importing to MALLET** without changing any of the settings. When it finishes, you will see a preview of the beginning of the `doc_terms.txt` file. By default, five rows will be displayed, with each row clipped at 200 characters. You can change these settings in the final line of the cell, or remove them if you wish to display the whole file (not recommended in a Jupyter notebook). You can also navigate to `models/doc_terms.txt` and download or open the file to inspect it. Each row in the `doc_terms.txt` file is one document in your corpus, and each row lists the document's filename, its index number, and its bag of words. 

### Setup MALLET

In the first cell, you configure a list of models you wish to run. Models are listed by the number of topics you select. For instance, if you wish to run three models of 25, 50, and 100 topics each, you should set `num_topics = [25, 50, 100]`.

The second cell instantiates a `Mallet` object (referenced as `mallet` and creates subdirectories in your projects `models` folder for each model you listed. **Important:** The `Mallet` object is pre-configured with MALLET settings used by the WE1S project. These settings are given below.

- `import_file_path=import_file_path
- `import_sources='file'
- `num_iterations=1000`
- `optimize_interval=10`
- `use_random_seed=True`
- `random_seed=10`
- `keep_sequence=True`
- `preserve_case=False`
- `token_regex="\S+"
- `remove_stopwords=False`
- `extra_stopwords=None`
- `stoplist_file=None`
- `generate_diagnostics=True`

You can list the values for any of these settings with `print(mallet.import_file_path)`, `print(mallet.random_seed)`, etc.

The first two options set the data source to be a file read from the location of the `import_file_path` configured in **Settings**. If a setting is `False` or `None`, it is not used by MALLET for importing data or training the models. In addition, `random_seed` is ignored if `use_random_seed` is `False`. Because WE1S input is pre-tokenised and has stop words removed, `remove_stopwords` is set to `False` and the `token_regex` setting just splits the doc_terms file on whitespace between words.

Once you have run this cell, you are ready to begin importing your data to MALLET. However, you may need to adjust MALLET's configuration as described below.

### Custom Configuration

Once the setup is complete,  you can change any of the MALLET settings below with commands like `mallet.optimize_interval = 11` (this model goes to 11!). You can use most arguments available in MALLET on the command line (see <a href="http://mallet.cs.umass.edu/topics.php" target="_blank">MALLET's documentation</a>), but replace hyphens with underscores. For example, reference MALLET's `--num-iterations` argument in this notebook with `mallet.num_iterations`.

Set you custom configurations in the cell in this section. For instance, if you wish to change the `optimize_interval` setting to '11', add `mallet.optimize_interval = 11` (this model goes to 11!). Another example with `num_iterations = 1000`.

#### Importing Plain Text files

One common use case for custom configurations is if you wish to import data from a directory of plain text files. You can do this with `mallet.import_source='path_to_directory'`. You can also choose MALLET's default tokenisation and stop words instead of the WE1S tokenisation algorithm and stoplist using `mallet.token_regex=None` and `mallet.remove_stopwords=True`. These configurations are provided for convenience in the cell below. You just have to uncomment them and run the cell.

Note that using plain text files that just contain document contents (and not metadata) as your data source means that certain visualisation tools like Dfr-Browser and Topic Bubbles, which require metadata, will not be usable. Therefore, this method is not recommended. If you wish to generate these visualisations, it is best to use the **import** module to import your data into your project's `json` folder first.

### Import Data to MALLET

You can probably simply run this cell as is, and the import process will begin. It may take a long time if your collection is large.

By default, the topic list you supplied in **Setup MALLET** will be used. However, if, for instance, you wish to import data for only models 25 and 50, you can also provide a topic list here by typing `mallet.import_models([25, 50])`.

This cell generates a MALLET command and uses it to call MALLET. If you run into a problem and you wish to see the MALLET command, create a new cell and run `print(mallet.import_command)`.

Once the import process is complete, you are ready to begin training your models.

### Train Models

As with the previous cell, you can probably simply run this cell as is. Likewise, if you do not wish to train the models specified in **Setup MALLET**, you can supply a list of models here by typing `mallet.train_models([25, 50])`.

When the training begins, MALLET gives continuous feedback with each iteration of the modelling process. By default, this feedback is hidden, and a progress bar indicates how close the model is to completion. You may wish to change this behaviour with one of the following settings:

- `mallet.train_models(progress_bar=False)`: Display a plain text progress indicator every 10%.
- `mallet.train_models(capture_output=True)`: Capture the output and display it only when training is complete. This is useful for job that takes a long time because it allows you to close the window.
- `mallet.train_models(log_file='path_to_mallet_log.txt')`: Save the output to a log file at the path specified. This is useful if you wish to save a record of MALLET's feedback.

If you run into a problem, you can inspect the last MALLET command by creating a new cell and running `print(mallet.train_command)`.

### Scale Topics

This cell uses Multidimensional Scaling (MDS) to adjust the topic weights for use in visualisation tools such as Dfr-Browser, pyLDAvis, and Topic Bubbles. These modules will not work properly if you do not perform scaling by running this cell. The generated scaling information is stored as `topic_scaled.csv` in the model's directory.

By default, scaling files will be generated for the models you configured in **Setup MALLET** above. If you wish to specify which models to scale in this cell, replace `num_topics` with a list of topic desired topic numbers (e.g. `[50, 100]`) in the code below.

## Module Structure

📦02_MALLET
 ┣ 📂scripts
 ┃ ┣ 📜scale_topics.py
 ┃ ┣ 📜timer.py
 ┃ ┣ 📜mallet.py
 ┃ ┣ 📜prepare_mallet_import.py
 ┃ ┣ 📜slow.py
 ┃ ┣ 📜timer.py
 ┃ ┗ 📜we1s_standard_stoplist.txt
 ┣ 📜model_topics.ipynb
 ┣ 📜README.md
 