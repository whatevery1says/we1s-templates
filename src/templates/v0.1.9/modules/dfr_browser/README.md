# Dfr-Browser

## Info

Authors: Jeremy Douglass, Scott Kleinman, Lindsay Thomas
Copyright: copyright 2019, The WE1S Project
License: MIT
Version: 1.2.1
Email: scott.kleinman@csun.edu
Last Update: 2021-02-18

## About This Module

The notebooks in this module implement the creation and customization of Andrew Goldstone's <a href="https://github.com/agoldst/dfr-browser" target="_blank">dfr-browser</a> from a topic model produced with MALLET. Dfr-browser code, stored in this module in `dfrb_scripts`, was written by Andrew Goldstone and adapted for WE1S use and data. WE1S uses an older version of Goldstone's code (v0.5.1); see https://agoldst.github.io/dfr-browser/ for a version history of Goldstone's code. WE1S uses Goldstone's prepare_data.py Python script to prepare the data files, NOT the R package.

## Notebooks

- `create_dfrbrowser.ipynb`: Notebook for creating a dfr-browser.
- `customize_dfrbrowser.ipynb`: Notebook for customizing the dfr-browser's display.

## User Guide -- create_dfrbrowser.ipynb notebook

### Settings

The **Settings** cell defines paths and important variables used to create a Dfr-Browser visualization. The default settings will create a folder inside the dfr_browser module for each topic model in your project or for a selection of models. In most cases, you will not need to change the default settings.

### Create Dfr-Browser Metadata Files from JSON Files

The `dfrb_metadata()` function opens up each json in your project's json directory and grabs the metadata information dfr-browser needs. It creates both the `metadata_csv_file` file and the `browser_meta_file_temp` file.

### Create Browser: Create files needed for dfr-browser

By default, this notebook is set to create Dfr-browsers for all of the models you produced using the `topic_modeling` module. If you would like to select only certain models to produce Dfr-browsers for, make those selections in the next cell (see next paragraph). Otherwise leave the value in the next cell set to `All`, which is the default.

To produce browsers for a selection of the models you created, but not all: Navigate to the `your_project_name/project_data/models` directory in your project. Note the name of each subdirectory in that folder. Each subdirectory should be called `topicsn1`, where `n1` is the number of topics you chose to model. You should see a subdirectory for each model you produced. To choose which subdirectory/ies you would like to produce browsers for, change the value of selection in the cell below to a list of subdirectory names. For example, if you wanted to produce browsers for only the 50- and 75-topic models you created, change the value of selection below to to `selection = ['topics50','topics75']`.

The `get_model_state()` function grabs the filepaths of model subdirectories in order to visualize and their state and scaled files. Optionally, you can instead set values for `subdir_list`, `state_file_list`, and `scaled_file_list` manually in the second cell.

The `create_dfrbrowser()` function creates the files needed for Dfr-browser, using the model state and scaled files for all selected models. It prints output from Goldstone's `prepare_data.py` script to the notebook cell. Once your Dfr-browser(s) have been created, the `display_links()` function displays links to open the Dfr-browser(s) in a tab in your web browser. 


### Create Zipped Copies of Your Visualizations (Optional)

This section zips up your dfr-browser visualizations for serving on a different machine or server. By default, browsers for all available models will be zipped. If you wish to zip only one model, change the `models` setting to indicate the name of the model folder (e.g. `'topics25'`). If you wish to zip more than one model, but not all, provide a list in square brackets (e.g. `['topics25', 'topics50']`). This section also includes instructions for downloading and running your dfrbrowser visualization(s) on a different machine (i.e., outside of the WE1S container system).

## User Guide -- customize_dfrbrowser.ipynb notebook

The `customize_dfrbrowser.ipynb` notebook allows you to customize certain Dfr-browser settings. You can only customize 1 topic model at a time. You can customize the title, names and contact info for contributors, a description of the model, a list of custom metadata fields, the number of words to display in topic bubbles, the font size of topic labels, the number of documents to display in Topic View, and the topic labels. This notebook edits your Dfr-browser's `info.json` file. You can also just edit this file manually to make these customizations. For more information on how to do this, see Goldstone's documentation here: https://github.com/agoldst/dfr-browser#tune-the-visualization-parameters.

## Module Structure

📦dfr_browser
 ┣ 📂scripts
 ┃ ┃ ┣ 📜create_dfrbrowser.py
 ┃ ┃ ┗ 📜zip.py
 ┣ 📂dfrb_scripts
 ┃ ┣ 📂bin
 ┃ ┃ ┣ 📜prepare-data
 ┃ ┃ ┗ 📜server
 ┃ ┣ 📂css
 ┃ ┃ ┣ 📜bootstrap-theme.min.css
 ┃ ┃ ┣ 📜bootstrap.min.css
 ┃ ┃ ┗ 📜index.css
 ┃ ┣ 📂fonts
 ┃ ┃ ┣ 📜glyphicons-halflings-regular.eot
 ┃ ┃ ┣ 📜glyphicons-halflings-regular.svg
 ┃ ┃ ┣ 📜glyphicons-halflings-regular.ttf
 ┃ ┃ ┗ 📜glyphicons-halflings-regular.woff
 ┃ ┣ 📂img
 ┃ ┃ ┗ 📜loading.gif
 ┃ ┣ 📂js
 ┃ ┃ ┣ 📜d3-mouse-event.js
 ┃ ┃ ┣ 📜dfb.min.js.custom
 ┃ ┃ ┣ 📜utils.min.js
 ┃ ┃ ┗ 📜worker.min.js
 ┃ ┣ 📂lib
 ┃ ┃ ┣ 📜bootstrap.min.js
 ┃ ┃ ┣ 📜d3.min.js
 ┃ ┃ ┣ 📜jquery-1.11.0.min.js
 ┃ ┃ ┗ 📜jszip.min.js
 ┃ ┣ 📜index.html
 ┃ ┗ 📜LICENSE
 ┣ 📜create_dfrbrowser.ipynb
 ┣ 📜customize_dfrbrowser.ipynb
 ┗ 📜README.md
