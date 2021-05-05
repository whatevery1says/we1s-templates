# Dendrogram

## About This Module

This module performs hierarchical agglomerative clustering on the _topics_ of a topic model or multiple topic models in a project. Several distance metrics and linkage methods are available. The default settings will conform closely to the output of pyLDAvis and the scaled view of dfr-browser. Information on alternative distance metrics can be found <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.pdist.html#scipy.spatial.distance.pdist" target="_blank">here</a> and information on alternative linkage methods can be found <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html" target="_blank">here</a>.

As dendrograms typically become crowded and hard to read, the visualisations are generated with Plotly, so that they can be browsed interactively with its pan and zoom features.

### Module Organization

Plotly exports dendrograms as HTML `<div>` elements which can be inserted into web pages. These are stored in the `partials` folder as `.html` files. The `dendrogram` module functions can then access these elements by inserting them into web pages that load Plotly's Javascript functions off the internet. Because these web pages access the internet, they will only work in a server environment. The `dendrogram` module also allows you to combine the partials and Plotly Javascript in a single, standalone HTML file that will work without an server environment, but they can be very large (several megabytes).

The module consists of two notebooks, `create_dendrogram.ipynb`, which allows you to create single dendrograms, and `batch_dendrogram.ipynb`, which allows you to create multiple dendrograms at once. `batch_dendrogram.ipynb` also enables you to generate an html index file for swapping between visualisations.

## User Guide

### `create_dendrogram.ipynb`

#### Setup

Imports Python libaries and scripts to the notebook and defines important file paths.

#### Configuration

**To select the model you want to produce a dendrogram for:** Navigate to the `your_project_name/project_data/models` directory in your project. Note the name of each subdirectory in that folder. Each subdirectory should be called `topicsn1`, where `n1` is the number of topics you chose to model. You should see a subdirectory for each model you produced. To choose which model you would like to produce a dendrogram visualization for, change the value of `selection` in the cell below to the corresponding subdirectory. For example, if you wanted to produce a dendrogram for the 50-topic model you created, change the value of `selection` below to this:

`selection = 'topics50'`

Please follow this format exactly.

!!! note
    You can select only one model to produce a dendrogram for at a time.

The dendrogram will be saved to the name you set for the `filename` configuration. It should end in `.html`. The file will be saved to the module's `partials` folder. It is often useful to give files names like `topics25-euclidean-single.html` to indicate the number of topics, distance metric, and linkage method used for the cluster analysis. This is especially helpful if you want to run the **Create Index for Multiple Dendrograms** section below.

Set the distance metric to `euclidean` and `cosine`. The linkage method may be `single`, `complete`, `average`, or `ward`. Ward linkage requires that the distance metric be set to `euclidean`.

!!! important
    The default output will only work in a server environment. If you wish to create a standalone version that can be run on a local computer, set `standalone=True`. The disadvantage of this method is that the file will be large, about 3 MB.

#### Load Data from the MALLET State File

This cell instantiates a `Model` object and loads the model's data from the MALLET state file.

#### Cluster the Model

By default, the cluster wil be saved as an html `div` element in the `partials` folder.

#### Create Web Page for a Single Dendrogram

This cell generates a web page that displays a single dendrogram. This web page will not work without an internet connection. If you wish to download a copy that does not require an internet connection, set the `standalone` configuration to `True` in the **Configuration** section and re-run the cluster analysis.

If you have already produced multiple dendrograms and wish to publish them with an index page, skip to the next section.

#### Create Index Page for Multiple Dendrograms

This section will produce an index page allowing you to navigate between multiple dendrogram files, which you have already created. Make sure that you configure the settings as described below.

The `source_filenames` must be the same as dendrogram filenames in your `partials` folder.

The `menu_items` and `dendrogram_titles` lists should correspond to the order of the `source_filenames`. The former will appear as menu labels for navigating between dendrograms, and the latter will be titles for each dendrogram.

If you would like to save the index and dendrograms to a zip archive for export, set `zip=True`.

!!! important
    The default output will only work in a server environment.

#### Generate the Index Page

This cell will display a link to your index page.

### `batch_dendrogram.ipynb`

This notebook allows you to perform hierarchical cluster analysis on multiple models with multiple clustering options. The output is an HTML index file which allows you to display the generated cluster analyses as dendrograms.

The last (optional) cell in this notebook allows you to generate standalone HTML files for a list of already-generated dendrograms.

#### Setup

Imports Python libaries and scripts to the notebook and defines important file paths.

#### Configuration

Provide a list of all models you wish to cluster and the distance metrics and linkage methods you wish to apply to each of the models.

Set `models = []` if you wish to cluster all the models available in our project. Otherwise, provide a list of the folder names for each model you wish to cluster.

Available distance metrics are 'euclidean' and 'cosine'.

Available linkage methods are 'average', 'single', 'complete', and 'ward'.

You will most likely not need to adjust the advanced configuration options, but their use is described below:

`orientation` ('top', 'left', 'bottom', 'right'): The location of the dendrogram root
`height`: The height of the dendrogram in pixels
`width`: The width of the dendrogram in pixels
`hovertext`: A list of hovertext for constituent traces of dendrogram clusters
`truncate_mode`:  The dendrogram can be hard to read when the original observation matrix from which the linkage is derived is large. Truncation is used to condense the dendrogram. There are several modes: `None` (no truncation, the default), `lastp` (the last `p` non-singleton clusters formed in the linkage are the only non-leaf nodes in the linkage), 'level' (No more than `p` levels of the dendrogram tree are displayed).
`p`: The `p` parameter for `truncate_mode`
`color_threshold`: The value at which all descendent links below a cluster node will be given the same colour

For further details, see the <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.dendrogram.html" target="_blank">`scipy.cluster.hierarchy.dendrogram documentation`</a>

#### Cluster

This cell starts the cluster analysis and can be run without modification.

#### Create Standalone Dendrograms

Run the cells in this section if you wish to create standalone versions of any of the dendrograms you have already created. They will be saved into your project's `dendrogram` module folder. The dendrograms can be downloaded and will work locally, as long as you have an internet connection. You only need to configure the list of dendrogram names you wish to save.

## Module Structure

:material-folder-outline: dendrogram<br>
 ┣ :material-folder-outline: partials<br>
 ┣ :material-folder-outline: scripts<br>
 ┃ ┣ :material-language-python: batch_cluster.py<br>
 ┃ ┣ :fontawesome-brands-html5:index_template.html<br>
 ┃ ┣ :material-language-python: model.py<br>
 ┃ ┗ :material-language-python: standalone.py<br>
 ┣ :jupyter-jupyter-logo: batch_dendrogram.ipynb<br>
 ┣ :jupyter-jupyter-logo: create_dendrogram.ipynb<br>
 ┗ :material-file-outline: README.md
