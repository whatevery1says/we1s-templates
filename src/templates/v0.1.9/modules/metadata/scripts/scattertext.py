# Python imports
import gzip
import joblib
import json
import os
import re
from collections import Counter
from random import choice
import ipywidgets
import pandas as pd
import qgrid
import spacy
import scattertext as st
from scattertext.features.FeatsFromSpacyDoc import FeatsFromSpacyDoc
from IPython.display import display, HTML

# Constants
SPACY_ENTITY_TYPES = ["PERSON", "NORP", "FAC", "ORG", "GPE", "LOC", "PRODUCT", "EVENT", "WORK_OF_ART", "LAW", "DATE", "TIME", "PERCENT", "MONEY", "QUANTITY", "ORDINAL", "CARDINAL"]
SPACY_TAG_TYPES = ["$", "``", "''", ",", "-LRB-", "-RRB-", ".", ":", "ADD", "CC", "CD", "DT", "EX", "IN", "LS", "NFP", "NIL", "NNP", "NNPS", "PDT", "POS", "PRP", "PRP$", "RP", "SYM", "TO", "UH", "WDT", "WP", "WP$", "WRB"]

# Qgrid options
qgrid_options = {
    # SlickGrid options
    'fullWidthRows': True,
    'syncColumnCellResize': True,
    'forceFitColumns': False,
    'defaultColumnWidth': 110,
    'rowHeight': 28,
    'enableColumnReorder': True,
    'enableTextSelectionOnCells': False,
    'editable': False,
    'autoEdit': False,
    'explicitInitialization': True,
    # Qgrid options
    'maxVisibleRows': 10,
    'minVisibleRows': 5,
    'sortable': True,
    'filterable': True,
    'highlightSelectedCell': False,
    'highlightSelectedRow': True
}

# Load language model
nlp = spacy.load('en_core_web_sm')

# Initialise variables
df        = None
corpus    = None
stoplist  = None

# Functions
class SpacyTagsEntities(FeatsFromSpacyDoc):
    """Class for removing entity and tag types."""
    def __init__(self,
                 use_lemmas=False,
                 entity_types_to_censor=list(),
                 entity_types_to_use=None,
                 tag_types_to_censor=list(),
                 tag_types_to_use=None,
                 strip_final_period=False):
        """Initialise object."""
        self._entity_types_to_use = entity_types_to_use
        self._tag_types_to_use = tag_types_to_use
        FeatsFromSpacyDoc.__init__(self, use_lemmas, set(entity_types_to_censor),
                                   set(tag_types_to_censor), strip_final_period)

    def get_feats(self, doc):
        tag_counts = [
            token.norm_
            for token
            in doc
            if ((self._tag_types_to_use is None
                 or token.tag_ in self._tag_types_to_use)
                and (token.tag_ not in self._tag_types_to_censor))
        ]
        ent_counts = [
            ' '.join(str(ent).split()).lower()
            for ent
            in doc.ents
            if ((self._entity_types_to_use is None
                 or ent.label_ in self._entity_types_to_use)
                and (ent.label_ not in self._entity_types_to_censor))
        ]
        return Counter(tag_counts + ent_counts)


def build_document_dataframe(json_dir, start, end, extra_fields, random_sampling):
    """Build the document dataframe."""
    # Build dataframe columns
    columns = ['name', 'text', 'date']
    for key, _ in extra_fields.items():
        if key not in columns and key != 'tags':
            columns.append(key)
    # Build file list
    file_list = [file for file in os.listdir(json_dir) if file.endswith('.json')]
    sampled_list = []
    if random_sampling is not None:
        sample_size = random_sampling / 100
        for x in range(int(len(file_list) * sample_size)):
            sampled_list.append(choice(file_list))
        file_list = sampled_list
    # Get the data
    data = []
    bad_json = 0
    for file in file_list[start:end]:
        try:
            with open(os.path.join(json_dir, file), 'r') as f:
                doc = json.loads(f.read())
        except ValueError:
            bad_json += 1
            pass
        fields = {'name': doc['name'], 'text': doc['content']}
        for key, field_name in extra_fields.items():
            if key != 'tags':
                fields[key] = doc[field_name]
                tags = {}
            else:
                tags = tags_to_dict(doc)
                for field_name in tags:
                    if field_name not in columns:
                        columns.append(field_name)
        data.append({**fields, **tags})
    if bad_json > 0:
        display(HTML('<p style="color:red;">Number of skipped files: ' + str(bad_json) + '</p>'))
    df = pd.DataFrame(data, columns=columns)
    df.to_parquet('data/documents_df.parquet')
    df.fillna('', inplace=True)
    qgrid_widget = qgrid.show_grid(df, grid_options=qgrid_options, show_toolbar=False)
#     qgrid.show_grid(df)
    return qgrid_widget

def display_link(filename, project_dir, WRITE_DIR, PORT):
    """Display a link to the visualisation."""
    filename = re.sub('\.html$', '', filename) + '.html'
    index_path = project_dir.replace(WRITE_DIR, '') + '/modules/metadata/' + filename
    if PORT != '' and PORT is not None:
        index_path = ':' + PORT + index_path
    javascript = 'event.srcElement.href = \'http://\' + window.location.hostname + \'' + index_path + '\';'
    link = '<a target="_blank" href="#" onfocus="' + javascript + '">View your visualization</a>'
    display(HTML('<p>' + link + '</p>'))
    display(HTML('<p>Note: This can be a large HTML file. With a 2000 document corpus it may take about fifteen minutes to load.</p>'))
    
def generate_corpus(module_data_dir, corpus_file, nlp, df, field, stoplist_path=None, use_lemmas=True, entity_types_to_use='all',
                    tag_types_to_use=None, entity_types_to_censor=set(), tag_types_to_censor=set(), strip_final_period=False):
    """Generate and save a corpus."""
    # Load stoplist
    if stoplist_path is not None:
        with open(stoplist_path, 'r') as f:
            stopwords = f.read()
        stoplist = stopwords.split('\n')
    else:
        stoplist = None
    uc_stoplist = [w.title() for w in stoplist]
    # Add custom lemmatisation to the spaCy pipeline
    lemmatization_cases = {
        "humanities": [{'ORTH': u'humanities', 'LEMMA': u'humanities', 'POS': u'NOUN', 'TAG': u'NNS'}]
    }
    for k, v in lemmatization_cases.items():
        nlp.tokenizer.add_special_case(k, v)
    # Handle entity and tag removal/customistion
    if isinstance(entity_types_to_use, str) and entity_types_to_use.lower() == 'all':
        entity_types_to_use = SPACY_ENTITY_TYPES
    elif isinstance(entity_types_to_use, str) and entity_types_to_use.lower() == 'none':
        entity_types_to_use = []
    elif  entity_types_to_use is None:
        entity_types_to_use = []
    if isinstance(tag_types_to_use, str) and tag_types_to_use.lower() == 'all':
        tag_types_to_use = SPACY_TAG_TYPES
    elif isinstance(tag_types_to_use, str) and tag_types_to_use.lower() == 'none':
        tag_types_to_use = []
    elif tag_types_to_use is None:
        tag_types_to_use = []
    # Get features from spaCy docs
    feats_from_spacy_doc = SpacyTagsEntities(use_lemmas=use_lemmas, entity_types_to_use=None, tag_types_to_use=None,
                                             entity_types_to_censor=entity_types_to_censor, tag_types_to_censor=tag_types_to_censor,
                                             strip_final_period=strip_final_period)
    # Build the corpus
    corpus = st.CorpusFromPandas(df, category_col=field, text_col='text', nlp=nlp,
                                 feats_from_spacy_doc=feats_from_spacy_doc).build().get_stoplisted_unigram_corpus(stoplist=stoplist)
    # Remove entities
    corpus = corpus.remove_terms(uc_stoplist, ignore_absences=True)
    # corpus = corpus.remove_entity_tags()
    # Save the corpus to disk
    with gzip.GzipFile(os.path.join(module_data_dir, corpus_file + '.gz'), 'wb', compresslevel=3) as f:  
        joblib.dump(corpus, f)
    display(HTML('<p style="color:green;">Corpus generated.</p>'))
    return corpus

def generate_counts_report(df, start_column, preview):
    """Generate and display the Column Counts report."""
    if isinstance(df, pd.DataFrame):
        display(HTML('<p">Number of Documents: ' + str(df.shape[0]) + '</p>'))
        warning = """Note: This number will be less than the total number of documents in the collection as a whole 
                     if you applied a document limit or random sampling in the cell above."""
        display(HTML('<p style="color:red;">' + warning + '</p>'))

        start_column = start_column - 1
        tag_cols = df.columns.values.tolist()[start_column:]
        all_tag_counts = {}
        for col in tag_cols:
            column_vals = df[col].values.tolist()
            counts = dict(Counter(column_vals))
            if '0' in counts:
                counts['No Subtags'] = counts.pop('0')
            if '1' in counts:
                counts['All Documents'] = counts.pop('1')
            all_tag_counts[col] = counts
        report = pd.DataFrame.from_dict(all_tag_counts)
        report = report.fillna(0)
        report = report.astype(int)
        display(report.head(preview))
    else:
        msg = 'Could not find a valid dataframe. You may be trying to pass a qgrid widget to the function. If the first argument is called <code>df</code> and the table produced in the <strong>Load Documents</strong> cell is called <code>table</code>, try changing <code>df</code> to <code>table.df</code>'
        display(HTML('<p style="color:red;">' + msg + '</p>'))
    
def load_corpus(module_data_dir, filename):
    """Load a corpus from disk."""
    try:
        with gzip.GzipFile(os.path.join(module_data_dir, filename + '.gz'), 'rb') as f:
            return joblib.load(f)
    except IOError:
        return None

def load_documents_df(module_data_dir, to_qgrid=False):
    """Check for the presence of a documents dataframe or load one from disk."""
#     try:
    df = pd.read_parquet(os.path.join(module_data_dir, 'documents_df.parquet'))
#     except IOError:
#         df = None
#         warning = 'You must first run the Load Documents cell to generate a Documents dataframe.'
#         display(HTML('<p style="color:red;">' + warning + '</p>'))
    if to_qgrid:
        qgrid_widget = qgrid.show_grid(df, grid_options=qgrid_options, show_toolbar=False)
        return qgrid_widget
    else:
        return df

def tags_to_dict(doc):
    """Process the tags from a single document and return a dict.

    Assumes a tag schema with the fields in `fields`. Boolean values are represented as '0' and '1'.
    Also retrieves the `country` and `language` fields as tags if they are present in the document.
    """
    # Initialise dict with all fields
    d = {'education': '0'}
    fields = ['affiliation', 'demographic', 'emphasis', 'funding', 'identity', 'institution', 'media', 'perspective', 'politics', 'reach', 'region', 'religion']
    for prop in fields:
        d[prop] = '0'
    # Add country and language if available
    if 'country' in doc:
        d['country'] = doc['country']
    if 'language' in doc:
        d['language'] = doc['language']
    # If the doc contains tags...
    if 'tags' in doc:
        # Iterate through the doc tags
        for tag in doc['tags']:
            # Set education to True if the education tag is detected
            if re.search('^education', tag):
                d['education'] = '1'
                tag = re.sub('^education/', '', tag)
            # Find all subtags and get the penult as the key
            subtag_properties = '^demographic|^emphasis|^funding|^identity|^institution|^media|^politics|^reach|^region|^religion'
            subtags = re.findall(subtag_properties, tag)
            if len(subtags) > 0:
                tail = tag.split('/')
                head = tail.pop(0)
                tail = '/'.join(tail)
                if tail.startswith('demographic/religion/'):
                    head = 'religion'
                    tail = tail.replace('demographic/religion/', '')
                if head.startswith('demographic'):
                    head = 'demographic'
                    tail = tail.replace('demographic/', '')
                if head.startswith('affiliation'):
                    head = 'affiliation'
                    tail = tail.replace('affiliation/', '')
                if head.startswith('institution'):
                    head = 'institution'
                    tail = tail.replace('institution/', '')
                if head.startswith('funding'):
                    head = 'funding'
                    tail = tail.replace('funding/', '')
                if head.startswith('emphasis'):
                    head = 'emphasis'
                    tail = tail.replace('emphasis/', '')
                if tail.startswith('religion'):
                    head = 'religion'
                    tail = tail.replace('religion/', '')
                # Combine UK and US with the rest of the tag
                tail = re.sub('^UK/', 'UK-', tail)
                tail = re.sub('^US/', 'US-', tail)
                # Set the new dict key and value
                d[head] = tail
    # Return the dict
    return d
