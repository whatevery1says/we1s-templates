# Metadata

## About This Module

The main notebook in this module, `topic_statistics_by_metadata.ipynb`, enables you to generate some basic statistics about document counts based on the metadata fields available in your project's JSON files.

There is also a notebook (`scattertext.ipynb`) for generating visualisations using the <a href="https://github.com/JasonKessler/scattertext" target="_blank">Scattertext</a> library.

Since these notebooks, and other tools in the Workspace, make use of document metadata, this module also provides a utility notebook (`add_metadata.ipynb`) for adding metadata fields to your project's JSON files after the data has been imported.

## User Guide

### `add_metadata.ipynb`

This notebook can be used to add metadata to project JSON files from a CSV file after they have been imported into the project.

The CSV file must have a `filename` column referencing files in the `json` folder. If this does not exist, the script will look for a `name` column, append `.json`, and attempt to use it as a filename.

#### Configuration

The only required configuration is the path to your metadata CSV file.

#### Load the Metadata

This cell loads the metadata file and performs other crucial setup functions. When it is finished, it displays the metadata in tabular format.

#### Add the Metadata to Project JSON files

This cell iterates through the metadata rows and adds the metadata field values to each file listed with a corresponding file in the JSON directory. If the metadata CSV does not have a filename listed, the notebook will attempt to create one from a `name` field. If a filename still cannot be found, the row will be skipped. Error messages are displayed if a filename could not be detected in the metadata CSV or if there is no corresponding file in the JSON folder.

### `scattertext.ipynb`

This notebook uses Jason Kessler's <a href="https://github.com/JasonKessler/scattertext" target="_blank">Scattertext</a> library to allow you to explore key terms in your corpus in relation to your documents' metadata. It does not require you to have topic modelled your data.

Because Scattertext is under active development and has many more functions than are made available through this notebook, WE1S does not distribute it as part of the Workspace. Instead, it is downloaded and intalled in your environment when you run the first cell. You may receive a warning that Scattertext is already installed if you run the cell again. You can safely ignore this warning.

Note that for the purpose of working with Scattertext, the original text is re-tokenized using slightly different rules from the WE1S preprocessor, so there may be some small discrepancies. By default, the WE1S standard stoplist in your project's MALLET module is applied.

#### Load Documents

This cell loads the json documents for the entire collection. Configuration also takes place in this cell, so be sure to set the configurations as detailed below before running it. If you have run this cell previously and wish to use the same settings, you can skip this cell. The next cell will load your Documents dataframe from a stored copy called `documents_df.parquet`. If you wish to save the settings, this fille will be overwritten with the new dataframe, so make a backup if you wish to keep the old one.

Loading can take a while, so, for experimentation, it is best to set `end` to a smaller number. This will limit the number of documents loaded. If you do not wish to start at the first document, set `start` to a higher number. Numbering is zero-indexed, so the first document is document 0.

By default, only your documents' content is loaded, but you can load other metadata from your JSON files using the the `extra_fields` setting, which takes a dictionary of key-value pairs. The value is the name of the field you wish to use from your JSON files. It will be referenced by the equivalent key in Scattertext. So, if you want to use your `pub_date` field and refer to it as `date` in Scattertext, the dictionary would be {'date': 'pub_date'}. Note that WE1S data contains specific tags with hierarchical filepath like formats. If these are found, they will be parsed automatically. Tags such as "media/news wires" and "media/news agency" cannot be resolved to a single table column, so only the last tag will appear. If you are not using WE1S data but you have a field called `tags` (the values of which must be a dictionary), open `scattertext.py` and delete or comment out line 118: `tags = tags_to_dict(doc)`.

If you wish to randomly sample a percentage of your corpus, set `random_sampling` to a number (without the "%" sign). If you do not wish to perform random sampling, set `random_sample=None`.

#### Save the Dataframe to CSV

By default, the output of the previous cell is a manipulatable dataframe. You can sort the columns by clicking on their labels or filter the table by clicking on the icons. If you wish to save the dataframe to a CSV file, configure a filename and then uncomment one of the lines below. The first will save the original dataframe and the second will save the dataframe after any sorting or filtering you have done.

#### Generate Document Counts Report

This cell provides a table of document counts for each field column beginning with the one configured for the `start_column` value. Each column provides the document counts for each metadata _field_ in the data. The rows provide the document counts by _value_. This information will be used for configuring the following cells.

#### Build a Corpus

When the corpus is built, each document is parsed using <a href="https://spacy.io/" target="_blank">spaCy</a>, so this can take a while. For that reason, it is a good idea to set the limit to around 2000 documents or smaller.

Before generating the corpus, the cell will automatically look for a previously-saved corpus file to speed loading time. If you have changed your `limit` or `field` settings, change the name of the `corpus_file` or set `from_file=False`. If you do not change the name of `corpus_file`, any previous corpus with that filename will be overwritten.

!!! important
    A Scattertext corpus requires a <code>field</code> category corresponding to one of the column headings in the Document Counts Report above. The column must contain at least two non-zero. If you get an error, you may not have chosen a valid field.</p>

Results seem to be improved by using lemmas rather than the original tokens, but this can be changed with `use_lemmas=False`. The other options are more unpredicatable. The `entity_types_to_use` and `tag_types_to_use` lists allow you to specify entity and part of speech categories that should be retained in the analysis. Tokens not belonging to the types you specify will be excluded from the corpus. A list of the category abbreviations can be found in the spaCy documentation for <a href="https://spacy.io/api/annotation#named-entities" target="_blank">named entities</a> and <a href="https://spacy.io/api/annotation#pos-universal" target="_blank">part of speech tags</a>. If you wish to use all the categories, set these values to `All`.

You can also "censor" certain types, which replaces the original token it entity or part of speech abbreviation. Lastly, periods at the ends of tokens can be stripped if they have escaped spaCy's tokenizer.

For convenience, here are lists of all entity and part of speech abbreviations, which you can use to copy and paste into the cell below.

!!! hint "Named Entities"
    "PERSON", "NORP", "FAC", "ORG", "GPE", "LOC", "PRODUCT", "EVENT", "WORK_OF_ART", "LAW", "DATE", "TIME", "PERCENT", "MONEY", "QUANTITY", "ORDINAL", "CARDINAL"

!!! hint "Parts of Speech"
    "$", "``", "''", ",", "-LRB-", "-RRB-", ".", ":", "ADD", "CC", "CD", "DT", "EX", "IN", "LS", "NFP", "NIL", "NNP", "NNPS", "PDT", "POS", "PRP", "PRP$", "RP", "SYM", "TO", "UH", "WDT", "WP", "WP$", "WRB"

You can perform quite a variety of configurations before generating your corpus:

- `limit`: A number less than or equal to the `end` value in **Load Documents**
- `field`: The metadata field you wish to explore
- `corpus_file`: The name of the corpus file (no file extension is necessary)
- `from_file`: If set to `True`, the notebook will look for a pre-existing corpus file before generating one from scratch.
- `stoplist_path`: Path to a custom stop word file
- `use_lemmas`: If set to `True`, the notebook will use lemmas (e.g. "go" for "going") instead of raw tokens. Lemmas are taken from spaCy's language model. The only modification is that the lemma of "humanities" is "humanities", not "humanity".
- `entity_types_to_use`: A list of the above entity types to use. If the value `None` is provided, all types are used.
- `entity_types_to_censor`: A list of entity types to "censor". This means that the tokens will be replaced by the entity label.
- `tag_types_to_use`: A list of the above tag types to use. If the value `None` is provided, all types are used.
- `tag_types_to_censor`: A list of tag types to "censor". This means that the tokens will be replaced by the tag label.
- `strip_final_period`: Removes periods (full stops) from the end of tokens if they have been missed by the tokenizer.

#### Generate terms that differentiate the collection from a general English corpus

This cell provides a list of terms in your corpus that make it distinct from a general English corpus. We _think_ that Scattertext uses the Brown University Standard Corpus of Present-Day American English (AKA the Brown Corpus) for comparison, but we have not been able to confirm this. As such, the results need to be interpreted with this uncertainty in mind.

The `limit` configuration controls the number of terms displayed in the output.

#### Generate terms associated with a field value

This cell provides a list of terms particularly associated with a particular metadata field value _within_ your corpus. For the `score_query` configuration, supply one of the row values in the **Generate Column Counts Report** cell. The `score_label` can be a more human-readable or descriptive label for the value.

#### Generate a Scattertext Visualization of Term Associations

This cell generates a Scattertext visualization, which provides a rich environment for exploring your corpus. The Scattertext visualization is saved as a single HTML file at the location you specify for `filename`. Be sure to set `limit` to the same number you used for generating the corpus.

The `field_name` value should be taken from one of the row values in the Counts Report above. In the graph, the axis for this field will be labelled with the value you provide for `field_label`. The other axis will be labelled by the value you provide for `non_field_label`. You can also modify the width of the graph and supply an extra metadata category, which will be the name of a column in the Documents table above. The values for that category will be displayed above sample documents in the graph.

The results can be filtered by minimum term frequency and pointwise mutual information (the higher the number the greater the requirement that terms co-occur in the same document).

!!! warning
    Scattertext HTML files are enormous and can take a very long time to load in your browser. A file generated from a corpus of 2000 documents will generally take about 15 minutes. So plan accordingly!</p>

### Topic Statistics by Metadata

This notebook extracts information form a model's `topic-docs.txt` file and combines it with the information in the documents' metadata fields to provide counts of the number of documents associated with specific metadata fields. Since MALLET automatically selects the top 100 documents in each topic, this is the basis for the data. The results can be viewed in pandas dataframes and saved to CSV files.

The results may be visualised in a static bar chart (stacked or unstacked) or an interactive plotly bar chart for any metadata field. The visusalisations may be saved to static PNG files.

#### Configuration

Select **one** model to explore. **Please run the next cell regardless of whether you change anything.**

If you are unsure of the name of your model, navigate to the `your_project_name/project_data/models` directory in your project, and choose the name of one of the subdirectories in that folder. Each subdirectory should be called `topicsn1`, where `n1` is the number of topics you chose to model, for example: `selection = 'topics100'`. Please follow this format exactly.

!!! info
    In most cases, you should not need to change the `data_path` and `from_file` configurations. The `data_path` variable specifies the folder where the notebook's assets will be saved. Some cells below attempt to load assets from this data folder so that you do not need to re-run procedures if you have already run the cell once. If for some reason you wish to bypass loading data from a saved file, set `from_file=False` in the cell's configuration section.

#### Read Topic-Docs File

This cell loads the `topic-docs.txt` file data into a pandas dataframe.

#### Export Data from Top Documents

Sometimes it can be useful to extract the text from the top documents in a topic in order to study them using a different tool. This cell allows you to export this content as plain text files save them as a zip archive. Before running the cell, configure the `save_path` with the path to the directory where you want to save the text files. If `topic_num` is set to `All`, the content of all documents will be exported. If you set it to a topic number, only the documents associated with that topic will be exported.

This cell is not required for running subsequent cells.

#### Gather Collection Metadata

This cell gathers metadata for a list of JSON fields from the documents in the collection.

In the dataframe output, tag attributes which exist but without subattributes have values of `1`; missing tag attributes have values of `0`. Tags with values like "funding/US private college" are represented on the table under the "funding" column with the value "US private colleges".

You can drag column boundaries to change their width or column labels to re-order the columns. To sort the columns, click the column label (and click again to sort in reverse order). Click the filter icon to filter your data by column values.

Note: This cell can take some time to run. If you have already run it once, it should read the metadata from a saved file. Set `from_file=False` to re-generate the data.

#### Save to CSV

If you wish to save a copy of the output of **Gather Collection Metadata** to a CSV file, set `save_path` to a filename to save the CSV to. In the sample below, `N` represents the topic number, which is recommended so that you do not overwrite a file from a different model.

By default, the CSV will reflect the table above _after_ any modifications you make by filtering or sorting. If you wish to use the original table, set `use_original=True`.

#### Get Counts by Field Values

This cell calculates document counts for each topic by field value using the `topic_docs_metadata` dataframe. In the configuration section, set `field` to the name of the metadata field you wish to calculate. Set `save_path` to a path to a CSV file if you wish to save the table. Set `use_original=True` if you wish the file to contain the original output. Otherwise, it will reflect any changes you make such as sorting and filtering.

#### Visualise Metadata with a Simple Bar Plot (Static Version)

This cell generates a simple bar plot for visualising the data generated by the notebook.

Set `fields` to a list of column headings in the `sums_and_means` dataframe. If you wish to display different names in the legend, provide a list of corresponding names for `legend_labels` (in the same order). You may adjust the `title`, `xlabel` (for the x-axis) and `ylabel` (for the y-axis) to describe the content of your data accurately.

Since plots can be very cramped, you may want to look at a limited range of topics. To do this, modify the `start_topic` and `end_topic` values. You can also save space by creating a stacked plot with `stacked=True`. (The interactive plot in the next cell provides another option with pan and zoom features.)

To save the plot a file, set `save_path` to a full file path, including the filename. The type of file is inferred from the extension. For instance, files ending in `.png` will be saved as PNG files and files ending in `.pdf` will be saved as PDF files. SVG format is also available.

#### Visualise Metadata with a Plotly Bar Plot (Interactive Version)

The interactive plot (using Plotly) takes the same settings as the static plot above, except the stacked mode is not available. However, because Plotly provides zoom and pan features, it is possible to display the entire range of topics in a single graph. Click and drag over the graph to zoom in on a location. Click the home icon in the Plotly toolbar to restore the default zoom level. Click on the boxes in the legend to show and hide specific categories. Double-click to restore the default display.

You can download the plot as PNG file by clicking the camera icon in the Plotly toolbar. If you wish to save the interactive plot as a standalone web page, set the `save_path` to a full file path, including the filename ending in `.html`.

#### Generate Topic-Doc Dictionary (Optional Utility)

This cell generates a dictionary with topic numbers as keys and a list of filenames in each topic as the values. Individual topics can be expected with `topic_docs_dict[1]`, where "1" is the desired topic number. The dictionary can be saved as a JSON file.

## Module Structure

:material-folder-outline: metadata<br>
 ┣ :material-folder-outline: data<br>
 ┣ :material-folder-outline: scripts<br>
 ┃ ┣ :material-language-python: add_metadata.py<br>
 ┃ ┣ :material-language-python: scattertext.py<br>
 ┃ ┗ :material-language-python: topic_stats.py<br>
 ┣ :jupyter-jupyter-logo: add_metadata.ipynb<br>
 ┣ :material-file-outline: README.md<br>
 ┣ :jupyter-jupyter-logo: scattertext.ipynb<br>
 ┗ :jupyter-jupyter-logo: topic_statistics_by_metadata.ipynb
