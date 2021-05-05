# pyLDAvis

## About This Module

<a href="https://github.com/bmabey/pyLDAvis" target="_blank">pyLDAvis</a> is a port of the R LDAvis package for interactive topic model visualization by Carson Sievert and Kenny Shirley.

pyLDAvis is designed to help users interpret the topics in a topic model by examining the relevance and salience of terms in topics. Once a pyLDAvis object has been generated, many of its properties can be inspected as in tabular form as a way to examine the model. However, the main output is a visualization of the relevance and salience of key terms to the topics.

pyLDAvis is not designed to use MALLET data out of the box. This notebook transforms the MALLET state file into the appropriate data formats before generating the visualization. The code is based on Jeri Wieringa's blog post <a href="http://jeriwieringa.com/2018/07/17/pyLDAviz-and-Mallet/" target="_blank">Using pyLDAvis with Mallet</a> and has been slightly altered and commented.

The main module for this notebook is `create_pyldavis.ipynb`.

## User Guide

### Settings

The **Settings** cell defines paths and important variables used to create the pyLDAVis visualizations. The default settings will create a folder inside the pyLDAvis module for each topic model in your project (you can select specific models in the **Configuration** cell below). In most case, you will not need to change the default settings.

### Configuration

Select models to create pyLDAvis visualizations for. **Please run the next cell regardless of whether you change anything.**

By default, this notebook is set to create a pyLDAvis for all of the models in your project `models` directory. If you would like to select only certain models to produce a pyLDAvis for, make those selections in the next cell (see next paragraph). Otherwise leave the value for `selection` as `All`, which is the default.

**To produce pyLDAvis for a selection of the models you created, but not all:** Navigate to the `your_project_name/project_data/models` directory in your project. Note the name of each subdirectory in that folder. Each subdirectory should be called `topicsn1`, where `n1` is the number of topics you chose to model. You should see a subdirectory for each model you produced. To choose which subdirectory/ies you would like to produce browsers for, change the value of `selection` in the cell below to a list of subdirectory names. For example, if you wanted to produce browsers for only the 50- and 75-topic models you created, change the value of `selection` below to this:

Example:

`selection = ['topics50','topics75']`

Once you have configured your topic models, run the next cell in the section to ensure that all of the models you selected are detectable by the pyLDAvis module.

### Add Metadata and Labels for the User Interface

This section is option and is for more advanced users. Skip this cell if you want to generate a basic pyLDAvis plot.

The pyLDAvis plot can be customized to display metadata information in your project's json files. To do this, identify the index number for each model in the list displayed by the second **Configuration** cell and add the necessary information using the following lines in the next cell.

```python
models[0]['metadata'] = 'pub'
models[0]['ui_labels'] = [
                'Intertopic Distance Map (via multidimensional scaling)',
                'topic',
                'publication',
                'publications',
                'tokens'
            ]
```
Remember that the first model is `models[0]`. Additional models would be `models[1]`, `models[2]`, etc.

For the `metadata` line, enter the json field you would like to use. For instance, a basic pyLDAvis displays your model's documents. If you wish to display, publications, you could use the `pub` field.

The `ui_labels` must be given in the following order:

1. The title of the multidimensional scaling graph
2. The type of unit represented by the graph circles
3. The singular form of the unit represented in the bar graphs on the right
4. The plural form of the unit represented in the bar graph on the right.
5. The unit represented by the percentage in the Relevance display.

The example above indicates that the model will represent a map of intertopic distances in which each topic will show the distribution of publications, as represented by the percentage of topic tokens in the publication.

!!! hint
    If you are unsure what to put, you do not have to assign `ui_labels`. A visualization will still be generated but may not have appropriate labels for the type of metadata you are using.

### Generate Visualizations

This cell generates the pyLDAvis visualizations for all selected topic models. The output is a set of links to all pyLDAvis visualizations in your project folder. See the next cell if you wish to make them public.

Since this cell can take some time to run, the output is captured instead of shown as the script is processing. Run the following `output.show()` cell when it is finished to check that everything ran as expected.

### Create Zipped Copies of your Visualizations for Export

This section allows you to create zip archives of your pyLDAvis visualizations for export. By default, visualizations for all available models will be zipped. If you wish to zip only one model, change the `models` setting to indicate the name of the model folder (e.g. `'topics25'`). If you wish to zip more than one model, but not all, provide a list in square brackets (e.g. `['topics25', 'topics50']`).

## Access pyLDAvis Data Attributes (Optional)

pyLDAvis generates a number of useful variables which it can be helpful for understanding the data underlying the visualization or for use in other applications. These variables can be accessed via the `vis` object created in **Generate the Visualizations** section. You can view the data by calling `show_attribute()` with the appropriate attribute configured. Possible attributes are `model_state` (a matrix o the models state file), `hyperparameters`, `alpha`, `beta`, `doc_lengths` (document lengths), `phi` (the matrix of topic-term distributions), `phi_df` (a pivoted dataframe of phi), `theta` (the matrix of document-topic), `theta_df` (a pivoted dataframe of theta), `vocab` (a matrix of term frequencies). Further information about these attributes can be found in the discussion of Jeri Wieringa's blog post <a href="http://jeriwieringa.com/2018/07/17/pyLDAviz-and-Mallet/" target="_blank">Using pyLDAvis with Mallet</a>.

You can restrict the number of lines shown by modifying the `start` and `end` settings. If you wish to save the result to a file, set the `save_path`. Tabular data should be saved to a csv file; everything else can be plain text.

## Module Structure

:material-folder-outline: pyldavis<br>
 ┣ :material-folder-outline: scripts<br>
 ┃ ┣ :material-language-python: PyLDAvis.py<br>
 ┃ ┣ :material-language-python: PyLDAvis_custom.js<br>
 ┃ ┗ :material-language-python: zip.py<br>
 ┣ jupyter-jupyter-logo: create_pyldavis.ipynb<br>
 ┗ :material-file-outline: README.md
