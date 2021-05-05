# Diagnostics

## Info

Authors: Scott Kleinman
Copyright: copyright 2020, The WE1S Project
License: MIT
Version: 1.0.0
Email: scott.kleinman@csun.edu
Last Update: 2020-07-25

## About This Module

This notebook produces a modified version of the <a href="http://mallet.cs.umass.edu/diagnostics.php" target="_blank">diagnostics visualisation</a> on the MALLET website. A single model will be viewable as a web page called `index.html`. The notebook also produces a comparative visualisation file for multiple models called `comparison.html`.

## Notebooks

- `visualize_diagnostics.ipynb`: The main notebook for this module.

## User Guide

This module assembles the MALLET diagnostics xml filse together with assets for a web-based visualization of the contents. Because it does not generate any information itself, it simply outputs a link to the visualization index file.


### Create Diagnostics Visualizations

This cell copies all of the diagnostics xml files from the diagnostics module directory and generates two web pages called `index.html` and `comparison.html`. Opening `index.html` on the public visualization port (a link is created by the notebook) launches the visualizations. Instructions for using the visualizations can be viewed by clicking "About This Tool" in the menu. The "Model Comparison Tool" menu item switches to the comparison view, from which the "Individual Model Tool" will take you back to the single-model visualization.

**Important:** In the Model Comparison Tool, one or two scatterplots may sometimes fail to load due to other browser activity. Usually doing a hard refresh of the page will allow them to load. 

 
### Zip Diagnostics

This optional cell The second cell optionally creates a zip archive of the visualization, which is suitable for export, in the module directory.

## Module Structure

📦diagnostics
 ┣ 📂css
 ┃ ┃ 📜bootstrap.min.css
 ┃ ┃ 📜all.min.css
 ┃ ┃ 📜styles.css
 ┃ ┗ 📜bootstrap.min.css
 ┣ 📂js
 ┃ ┣ 📜bootstrap.min.js
 ┃ ┣ 📜d3.v3.min.js
 ┃ ┣ 📜jquery-3.4.1.slim.min.js
 ┃ ┗ 📜popper.min.js
 ┣ 📂scripts
 ┃ ┣ 📜comparison_template.html
 ┃ ┣ 📜diagnostics.py
 ┃ ┣ 📜index_template.html
 ┃ ┣ 📜zip.py
 ┣ 📂webfonts
 ┃ ┣ 📜fa-solid-900.woff2
 ┃ ┣ 📜fa-solid-900.woff
 ┃ ┣ 📜fa-solid-900.ttf
 ┃ ┣ 📜fa-solid-900.svg
 ┃ ┣ 📜fa-solid-900.eot
 ┃ ┣ 📜fa-regular-400.woff2
 ┃ ┣ 📜fa-regular-400.woff
 ┃ ┣ 📜fa-regular-400.ttf
 ┃ ┣ 📜fa-regular-400.svg
 ┃ ┣ 📜fa-regular-400.eot
 ┃ ┣ 📜fa-brands-400.woff2
 ┃ ┣ 📜fa-brands-400.woff
 ┃ ┣ 📜fa-brands-400.ttf
 ┃ ┣ 📜fa-brands-400.svg
 ┃ ┗ 📜fa-brands-400.eot
 ┣ 📂xml
 ┣ 📜README.md
 ┗ 📜visualize_diagnostics.ipynb
 
