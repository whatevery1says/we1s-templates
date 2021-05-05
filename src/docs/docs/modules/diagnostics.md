# Diagnostics

## About This Module

This notebook produces a modified version of the <a href="http://mallet.cs.umass.edu/diagnostics.php" target="_blank">diagnostics visualisation</a> on the MALLET website. A single model will be viewable as a web page called `index.html`. The notebook also produces a comparative visualisation file for multiple models called `comparison.html`. The main notebook for this module is `visualize_diagnostics.ipynb`.

## User Guide

This module assembles the MALLET diagnostics xml filse together with assets for a web-based visualization of the contents. Because it does not generate any information itself, it simply outputs a link to the visualization index file.

### Create Diagnostics Visualizations

This cell copies all of the diagnostics xml files from the diagnostics module directory and generates two web pages called `index.html` and `comparison.html`. Opening `index.html` on the public visualization port (a link is created by the notebook) launches the visualizations. Instructions for using the visualizations can be viewed by clicking "About This Tool" in the menu. The "Model Comparison Tool" menu item switches to the comparison view, from which the "Individual Model Tool" will take you back to the single-model visualization.

!!! important
    In the Model Comparison Tool, one or two scatterplots may sometimes fail to load due to other browser activity. Usually doing a hard refresh of the page will allow them to load.

### Zip Diagnostics

This optional cell The second cell optionally creates a zip archive of the visualization, which is suitable for export, in the module directory.

## Module Structure

:material-folder-outline: diagnostics<br>
 ┣ :material-folder-outline: css<br>
 ┃ ┃ :material-language-css3: bootstrap.min.css<br>
 ┃ ┃ :material-language-css3: all.min.css<br>
 ┃ ┃ :material-language-css3: styles.css<br>
 ┃ ┗ :material-language-css3: bootstrap.min.css<br>
 ┣ :material-folder-outline: js<br>
 ┃ ┣ :material-language-javascript: bootstrap.min.js<br>
 ┃ ┣ :material-language-javascript: d3.v3.min.js<br>
 ┃ ┣ :material-language-javascript: jquery-3.4.1.slim.min.js<br>
 ┃ ┗ :material-language-javascript: popper.min.js<br>
 ┣ :material-folder-outline: scripts<br>
 ┃ ┣ :fontawesome-brands-html5: comparison_template.html<br>
 ┃ ┣ :material-language-python: diagnostics.py<br>
 ┃ ┣ :fontawesome-brands-html5: index_template.html<br>
 ┃ ┣ :material-language-python: zip.py<br>
 ┣ :material-folder-outline: webfonts<br>
 ┃ ┣ :fontawesome-solid-font: fa-solid-900.woff2<br>
 ┃ ┣ :fontawesome-solid-font: fa-solid-900.woff<br>
 ┃ ┣ :fontawesome-solid-font: fa-solid-900.ttf<br>
 ┃ ┣ :fontawesome-solid-font: fa-solid-900.svg<br>
 ┃ ┣ :fontawesome-solid-font: fa-solid-900.eot<br>
 ┃ ┣ :fontawesome-solid-font: fa-regular-400.woff2<br>
 ┃ ┣ :fontawesome-solid-font: fa-regular-400.woff<br>
 ┃ ┣ :fontawesome-solid-font: fa-regular-400.ttf<br>
 ┃ ┣ :fontawesome-solid-font: fa-regular-400.svg<br>
 ┃ ┣ :fontawesome-solid-font: fa-regular-400.eot<br>
 ┃ ┣ :fontawesome-solid-font: fa-brands-400.woff2<br>
 ┃ ┣ :fontawesome-solid-font: fa-brands-400.woff<br>
 ┃ ┣ :fontawesome-solid-font: fa-brands-400.ttf<br>
 ┃ ┣ :fontawesome-solid-font: fa-brands-400.svg<br>
 ┃ ┗ :fontawesome-solid-font: fa-brands-400.eot<br>
 ┣ :material-folder-outline: xml<br>
 ┣ :material-file-outline: README.md<br>
 ┗ :jupyter-jupyter-logo: visualize_diagnostics.ipynb
