# Topic Bubbles

## Info

Authors: Sihwa Park, Jeremy Douglass, Scott Kleinman, Lindsay Thomas
Copyright: copyright 2019, The WE1S Project
License: MIT
Version: 1.2.1
Email: lindsaythomas@miami.edu
Last Update: 2021-02-18

## About This Module

This module creates a topic bubbles visualization from dfr-browser data generated in the dfr-browser notebook or from model data generated in the topic modeling notebook. This module uses scripts originally written by Sihwa Park for the WE1S project. For more information on Park's script, see <a href="https://github.com/sihwapark/topic-bubbles" target="_blank">Park's topic bubbles Github repo</a> and the `README.md` located in this module's `tb_scripts` folder.

## Notebooks

`create_topic_bubbles.ipynb`: The main notebook for the module. Notebook for creating a topic bubbles visualization.

## User Guide

### Settings

The **Settings** cell defines paths and important variables used to create a topic bubbles visualization. The default settings will create a folder inside the topic_bubbles module for each topic model in your project or for a selection of models. In most cases, you will not need to change the default settings.

### Create Topic Bubbles Using Dfr-Browser Metadata

If you ran the `dfr-browser` module to create dfr-browser visualizations for your models, the next cells will import data produced via that module into the `topic_bubbles` module.

If you did not run the `dfr_browser` module, skip to the next section: **Create Topic Bubbles without Dfr-Browser Metadata**.

By default, this notebook is set to create Topic Bubbles visualizations the same models you produced Dfr-browsers for in the `dfr_browser` module. This means that the `selection` variable below is set to its default value of `All` (`selection = 'All'`). If you would like to select only certain models to produce Topic Bubbles visualizations, make those selections in the next cell. Otherwise leave the value in the next cell set to `All`. **You must run this cell regardless of whether you change anything.**

**To produce topic bubbles for a selection of models:** Navigate to the `modules/dfr_browser` directory and look for subdirectories titled `topicsn1`, where `n1` is the number of topics you chose to model. You should see a subdirectory for each browser you produced. To choose which subdirectory/ies you would like to produce, change the value of `selection` in the cell below to a list of subdirectory names. For example, if you wanted to produce browsers for only the 50- and 75-topic models you created, change the value of `selection` below to `selection = ['topics50', 'topics75']`.

### Create Topic Bubbles without Dfr-Browser Metadata

If you have not yet created Dfr-browsers for this project, run the following cells to create your Topic Bubbles visualization.

By default, this notebook is set to create Topic Bubbles visualizations the same models you produced Dfr-browsers for in the `dfr_browser` module. This means that the `selection` variable below is set to its default value of `All` (`selection = 'All'`). If you would like to select only certain models to produce Topic Bubbles visualizations, make those selections in the next cell. Otherwise leave the value in the next cell set to `All`. **You must run this cell regardless of whether you change anything.**

**To produce topic bubbles for a selection of models:** Navigate to the `modules/dfr_browser` directory and look for subdirectories titled `topicsn1`, where `n1` is the number of topics you chose to model. You should see a subdirectory for each browser you produced. To choose which subdirectory/ies you would like to produce, change the value of `selection` in the cell below to a list of subdirectory names. For example, if you wanted to produce browsers for only the 50- and 75-topic models you created, change the value of `selection` below to `selection = ['topics50', 'topics75']`.

### Create Files Needed for Topic Bubbles


### Select Models for Which You Would Like to Create Visualizations

By default, this notebook is set to create Topic Bubbles visualizations the same models you produced Dfr-browsers for in the `dfr_browser` module. This means that the `selection` variable below is set to its default value of `All` (`selection = 'All'`). If you would like to select only certain models to produce Topic Bubbles visualizations, make those selections in the next cell. Otherwise leave the value in the next cell set to `All`. **You must run this cell regardless of whether you change anything.**

**To produce topic bubbles for a selection of models:** Navigate to the `modules/dfr_browser` directory and look for subdirectories titled `topicsn1`, where `n1` is the number of topics you chose to model. You should see a subdirectory for each browser you produced. To choose which subdirectory/ies you would like to produce, change the value of `selection` in the cell below to a list of subdirectory names. For example, if you wanted to produce browsers for only the 50- and 75-topic models you created, change the value of `selection` below to `selection = ['topics50', 'topics75']`.

The `get_model_state()` function in the second cell grabs the filepaths of model subdirectories in order to visualize and their state and scaled files. Optionally, you can instead set values for `subdir_list`, `state_file_list`, and `scaled_file_list` manually in the third cell.

The `create_topicbubbles()` function creates the files needed for topic bubbles, using the model state and scaled files for all selected modelsand Goldstone's prepare_data.py script (to produce the dfr-browser files needed for topic bubbles). It prints output from Goldstone's prepare_data.py script to the notebook cell. 

### Create Zipped Copies of Your Visualizations (Optional)

This section zips up your topic bubbles visualizations for serving on a different machine or server. By default, browsers for all available models will be zipped. If you wish to zip only one model, change the `models` setting to indicate the name of the model folder (e.g. `'topics25'`). If you wish to zip more than one model, but not all, provide a list in square brackets (e.g. `['topics25', 'topics50']`). This section also includes instructions for downloading and running your topic bubble visualization(s) on a different machine (i.e., outside of the WE1S container system).

## Module Structure

📦topic_bubbles
 ┣ 📂scripts
 ┃ ┣ 📜create_dfrbrowser.py
 ┃ ┣ 📜create_topic_bubbles.py
 ┃ ┣ 📜zip.py
 ┣ 📂tb_scripts
 ┃ ┣ 📂css
 ┃ ┃ ┗ 📜style.css
 ┃ ┣ 📂data
 ┃ ┃ ┗ 📜config.json
 ┃ ┣ 📂img
 ┃ ┃ ┣ 📜screenshot.png
 ┃ ┃ ┗ 📜we1s_logo.png
 ┃ ┣ 📂js
 ┃ ┃ ┣ 📜d3-mouse-event.js
 ┃ ┃ ┣ 📜script.js
 ┃ ┃ ┣ 📜utils.min.js
 ┃ ┃ ┗ 📜worker.min.js
 ┃ ┣ 📂lib
 ┃ ┣ 📜index.html
 ┃ ┣ 📜LICENSE
 ┃ ┗ 📜README.md
 ┣ 📜create_topic_bubbles.ipynb
 ┗ 📜README.md
