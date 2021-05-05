"""standalone.py.

Last update: 2021-02-19
"""

## Python Imports

import os
import re
from IPython.display import display, HTML
from shutil import copy, copytree, rmtree

def create_standalone(dendrograms, partials_path, model_dir, file_prefix='standalone_'):
    """Create standalone dendrograms."""
    dendrograms = ['dendrogram-' + d + '.html' for d in dendrograms]
    output_cache = []

    for filename in dendrograms:
        # Open the dendrogram div file and inject some html, css, and javascript code
        source_filepath = os.path.join(partials_path, filename)
        prefix, title, distance, linkage = filename.split('-')
        distance = distance.strip('.html')
        linkage = linkage.strip('.html')
        title = title.title() + ' with ' + distance.title() + ' Distance and ' + linkage.title() + ' Linkage'
        with open(source_filepath, 'r') as f:
            html = f.read()    
        head = '<html><head><meta charset="utf-8"><title>' + title + '</title>'
        head2 = """<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <script
          src="https://code.jquery.com/jquery-3.4.1.slim.min.js"
          integrity="sha256-pasqAKBDmFT4eHoN2ndd6lN370kFiGUFyTiUHWhU7k8="
          crossorigin="anonymous"></script>
            <script type="text/javascript">window.PlotlyConfig = {MathJaxConfig: 'local'};</script>
            <style type="text/css">
                #cluster_graph {
                    width: 1200px;
                    margin: auto;
                    margin-left: 100px;
                    height: 600px;
                }
                #topic-keys-div {
                  margin: auto;
                  margin-left: 100px;

                }
                .xaxislayer-above, x.tick {
                  cursor: pointer;
                  pointer-events: all;
                }
            </style>
        </head>
        <body>"""
        head += head2
        head += '<h3 class=text-center>' + title + '</h3><div id="cluster_graph">'
        html = head + html + '</div><div id="topic-keys-div"><span id="topic-keys-label" style="font-weight: bold;">Hover over Topic Labels to View Topic Keywords</span> <span id="topic-keys"></span></div></div></body></html>'

        # Get topic keywords
        model_name = filename.split('-')[1]
        model_path = model_dir + '/' + model_name
        for file in os.listdir(model_path):
            if 'keys' in file:
                keys_filepath = model_path + '/' + file
        # Add the topic keywords and hover behaviour
        with open(keys_filepath, 'r') as f:
            keys = f.read().split('\n')
        keys = [re.sub('.+\t', '', line) for line in keys]
        keywords = {}
        for i, line in enumerate(keys):
            k = 'Topic' + str(i + 1)
            keywords[k] = line
        script = """<script>
                $(document).on('mouseenter', '.xtick', function() {
                    var keywords = []
                    $('#topic-keys-label').html($(this).children().eq(0).text() + ':')
                    $('#topic-keys').html(keywords[$(this).children().eq(0).text()])
                })
            </script>"""
        html = html.replace('</style>', '</style>\n' + script)
        html = html.replace('var keywords = []', 'var keywords = ' + str(keywords))

        # Save the file
        if file_prefix is not None and file_prefix != 'None':
            filename = file_prefix + filename
        output_filepath = os.path.join(os.getcwd(), filename)
        with open(output_filepath, 'w') as f:
            f.write(html)

        output_cache.append('<a target="_blank" href="' + filename + '">' + filename + '</a>')

    # Display the output links
    output = '<p style="color: green;">Done! Dendrogram pages can be viewed at</p>'
    output += '<ul>'
    for item in output_cache:
        output += '<li>' + item + '</li>'
    output += '</ul>'
    display(HTML(output))