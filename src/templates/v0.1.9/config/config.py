"""config.py.

Constants commonly used by all modules and paths to default project resources.
"""

# Server
WRITE_DIR           = '/home/jovyan/write'
PORT                = '10001'
MONGODB_CLIENT      = 'mongodb://localhost:27017'

# Project Root Files
PROJECT_ROOT_FILES  = ['datapackage.json', 'getting_started.md', 'README.md']

# Config Files
CONFIG_FILES        = ['config.py']

# Project Data Directory
DATA_DIR            = 'project_data'

# Modules
MODULES             = [
    {
        'comparing': [
            'results',
            'scripts',
            'scripts/compare_word_frequencies.py',
            'scripts/compare-word-frequencies.ipynb',
            'README.md'
        ]
    },
    {
        'counting': [
            'scripts',
            'scripts/count_docs.py',
            'scripts/count_tokens.py',
            'scripts/tokenizer.py',
            'scripts/vocab.py',
            'collocation.ipynb',
            'count_documents.ipynb',
            'docs_by_search_term.ipynb',
            'frequency.ipynb',
            'README.md',
            'tfidf.ipynb',
            'tokenize.ipynb',
            'vocab.ipynb'
        ]
    },
    {
        'dendrogram': [
            'partials',
            'scripts',
            'scripts/batch_cluster.py',
            'scripts/index_template.html',
            'scripts/model.py',
            'scripts/standalone.py',
            'batch_dendrogram.ipynb',
            'create_dendrogram.ipynb',
            'README.md'
        ]
    },
    {
        'dfr_browser': [
            'scripts',
            'scripts/create_dfrbrowser.py',
            'scripts/zip.py',
            'dfrb_scripts',
            'dfrb_scripts/bin',
            'dfrb_scripts/bin/prepare-data',
            'dfrb_scripts/bin/server',
            'dfrb_scripts/css',
            'dfrb_scripts/css/bootstrap-theme.min.css',
            'dfrb_scripts/css/bootstrap.min.css',
            'dfrb_scripts/css/index.css',
            'dfrb_scripts/font',
            'dfrb_scripts/fonts/glyphicons-halflings-regular.eot',
            'dfrb_scripts/fonts/glyphicons-halflings-regular.svg',
            'dfrb_scripts/fonts/glyphicons-halflings-regular.ttf',
            'dfrb_scripts/fonts/glyphicons-halflings-regular.woff',
            'dfrb_scripts/img',
            'dfrb_scripts/img/loading.gif',
            'dfrb_scripts/js',
            'dfrb_scripts/js/d3-mouse-event.js',
            'dfrb_scripts/js/dfb.min.js.custom',
            'dfrb_scripts/js/utils.min.js',
            'dfrb_scripts/js/worker.min.js',
            'dfrb_scripts/lib',
            'dfrb_scripts/lib/bootstrap.min.js',
            'dfrb_scripts/lib/d3.min.js',
            'dfrb_scripts/lib/jquery-1.11.0.min.js',
            'dfrb_scripts/lib/jszip.min.js',
            'dfrb_scripts/index.html',
            'dfrb_scripts/LICENSE',
            'create_dfrbrowser.ipynb',
            'customize_dfrbrowser.ipynb',
            'README.md'
        ]
    },
    {
        'diagnostics': [
            'css',
            'css/bootstrap.min.css',
            'css/all.min.css',
            'css/styles.css',
            'css/bootstrap.min.css',
            'js',
            'js/bootstrap.min.js',
            'js/d3.v3.min.js',
            'js/jquery-3.4.1.slim.min.js',
            'js/popper.min.js',
            'scripts',
            'scripts/comparison_template.html',
            'scripts/diagnostics.py',
            'scripts/index_template.html',
            'scripts/zip.py',
            'webfonts',
            'webfonts/fa-solid-900.woff2',
            'webfonts/fa-solid-900.woff',
            'webfonts/fa-solid-900.ttf',
            'webfonts/fa-solid-900.svg',
            'webfonts/fa-solid-900.eot',
            'webfonts/fa-regular-400.woff2',
            'webfonts/fa-regular-400.woff',
            'webfonts/fa-regular-400.ttf',
            'webfonts/fa-regular-400.svg',
            'webfonts/fa-regular-400.eot',
            'webfonts/fa-brands-400.woff2',
            'webfonts/fa-brands-400.woff',
            'webfonts/fa-brands-400.ttf',
            'webfonts/fa-brands-400.svg',
            'webfonts/fa-brands-400.eot',
            'xml',
            'README.md',
            'visualize_diagnostics.ipynb'
        ]
    },
    {
        'export': [
            'scripts',
            'scripts/export_package.py',
            'scripts/json_to_txt_csv.py',
            'export_project.ipynb',
            'json_to_txt_csv.ipynb',
            'README.md'
        ]
    },
    {
        'import': [
            'scripts',
            'scripts/import.py',
            'scripts/import_tokenizer.py',
            'scripts/timer.py',
            'query-builder',
            'query-builder/assets',
            'query-builder/assets/config',
            'query-builder/assets/config/schema.js',
            'query-builder/assets/css',
            'query-builder/assets/css/query-builder.default.min.css',
            'query-builder/assets/css/styles.css',
            'query-builder/assets/js',
            'query-builder/assets/js/query-builder.standalone.min.js',
            'query-builder/assets/js/builder.js',
            'query-builder/index.html',
            'query-builder/README.md',
            'query-builder-bundle.zip',
            'import.ipynb',
            'README.md'
        ]
    },
    {
        'json_utilities': [
            'scripts',
            'scripts/json_utilities.py',
            'json_utilities.ipynb',
            'remove_fields.ipynb',
            'README.md'
        ]
    },
    {
        'metadata': [
            'data',
            'scripts',
            'scripts/add_metadata.py',
            'scripts/scattertext.py',
            'scripts/topic_stats.py',
            'add_metadata.ipynb',
            'README.md',
            'scattertext.ipynb',
            'topic_statistics_by_metadata.ipynb'
        ]
    },
    {
        'pyldavis': [
            'scripts',
            'scripts/PyLDAvis.py',
            'scripts/PyLDAvis_custom.js',
            'scripts/zip.py',
            'create_pyldavis.ipynb',
            'README.md'
        ]
    },
    {
        'topic_bubbles': [
            'scripts',
            'scripts/lib',
            'scripts/lib/create_dfrbrowser.py',
            'scripts/lib/create_topic_bubbles.py',
            'scripts/lib/zip.py',
            'tb_scripts',
            'tb_scripts/css',
            'tb_scripts/css/style.css',
            'tb_scripts/data',
            'tb_scripts/data/config.json',
            'tb_scripts/img',
            'tb_scripts/img/screenshot.png',
            'tb_scripts/img/we1s_logo.png',
            'tb_scripts/js',
            'tb_scripts/js/d3-mouse-event.js',
            'tb_scripts/js/script.js',
            'tb_scripts/js/utils.min.js',
            'tb_scripts/js/worker.min.js',
            'tb_scripts/lib',
            'tb_scripts/lib/index.html',
            'tb_scripts/lib/LICENSE',
            'tb_scripts/lib/README.md',
            'create_topic_bubbles.ipynb',
            'README.md'
        ]
    },
    {
        'topic_modeling': [
            'scripts',
            'scripts/scale_topics.py',
            'scripts/timer.py',
            'scripts/mallet.py',
            'scripts/prepare_mallet_import.py',
            'scripts/slow.py',
            'scripts/timer.py',
            'scripts/we1s_standard_stoplist.txt',
            'model_topics.ipynb',
            'README.md'
        ]
    },
    {
        'utilities': [
            'scripts',
            'scripts/clear_caches.py',
            'clear_caches.ipynb',
            'README.md',
            'zip_folder.ipynb'
        ]
    }
]
