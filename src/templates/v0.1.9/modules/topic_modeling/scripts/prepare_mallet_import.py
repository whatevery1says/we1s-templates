"""prepare_mallet_import.py.

Generates a PrepareMalletImport object, which is line-delimited string of rows,
one per document in the collection. Each row is a space-separated list
of terms with each term repeated once for the number of times it
occurs in the document. This format is suitable for import into MALLET.

Sample Usage:

prepare_import = PrepareMalletImport(language_model, stoplist_file, log_file)
prepare_import.prepare_data(json_dir)
prepare_import.preview(rows=5, clip=200)
prepare_import.display_log()

For use with model_topics.ipynb v 2.0.

Last update: 2020-08-12
"""

## PYTHON IMPORTS
import json
import os
import re
import sys
import spacy
from spacy.tokenizer import Tokenizer
from collections import Counter
from IPython.display import display, HTML
from itertools import islice

from timer import Timer

## CONSTANTS
LINEBREAK_REGEX = re.compile(r'((\r\n)|[\n\v])+')
NONBREAKING_SPACE_REGEX = re.compile(r'(?!\n)\s+')
PREFIX_RE = re.compile(r'''^[\[\]\("'\.,;:-]''')
SUFFIX_RE = re.compile(r'''[\[\]\)"'\.,;:-]$''')
INFIX_RE = re.compile(r'''[-~]''')
SIMPLE_URL_RE = re.compile(r'''^https?://''')

## MalletImport CLASS
class PrepareMalletImport:
    """Configure a MALLET import object."""

    def __init__(self, import_file_path, model_dir, language_model='en_core_web_sm', stoplist_file=None,
                 strip_digits=True, include_pos=None, include_tags=None, use_lemmas=False,
                 exclude_entity_types=None, use_existing_bow=True, log_file='mallet_import_log.txt'):
        """Initialize the class.

        Note: The default model should be changed to 'en_core_web_lg'
        in the production environment.
        """
        self.import_file_path = import_file_path
        self.model_dir = model_dir
        self.language_model = language_model
        self.stoplist = self.load_stoplist(stoplist_file)
        self.strip_digits = strip_digits
        self.include_pos = include_pos
        self.include_tags = include_tags
        self.use_lemmas = use_lemmas
        self.exclude_entity_types = exclude_entity_types
        self.use_existing_bow = use_existing_bow
        self.log_file = log_file
        self.log = ''
        if self.stoplist is not None:
            self.strip_stopwords = True
        self.use_filters = False
        filters = [self.include_pos, self.include_tags, self.exclude_entity_types]
        for filter in filters:
            if isinstance(filter, list):
                self.use_filters = True

    def bagify(self, tokens, trim_punct=True):
        """Convert a list of values to a dict of value frequencies.

        Parameters:
        - trim_punct (Bool): If True, strips attached punctuation that may have survived tokenisation.
        """
        # An attempt to strip predictably meaningless stray punctuation
        punct = re.compile(r'\.\W|\W\.|^[\!\?\(\),;:\[\]\{\}]|[\!\?\(\),;:\[\]\{\}]$')
        # Make sure we are working with a list of values
        if trim_punct == True:
            tokens = [re.sub(punct, '', token) for token in tokens]
        else:
            tokens = [token for token in tokens]
        return dict(Counter(tokens))

    def custom_tokenizer(self):
        """Add custom tokenizer settings."""
        return Tokenizer(self.nlp.vocab, prefix_search=PREFIX_RE.search,
                                    suffix_search=SUFFIX_RE.search,
                                    infix_finditer=INFIX_RE.finditer,
                                    token_match=SIMPLE_URL_RE.match)

    def display(self, rows=5, clip=200):
        """Display a preview of the import file.

        Parameters:
        - rows (int): The number of doc_terms rows to display.
        - clip (int): The number of characters after which the row will be clipped.
        """
        try:
            with open(self.import_file_path, 'r', encoding='utf-8') as f:
                if rows is not None:
                    result = list(islice(f, rows))
                    if clip is not None:
                        result = [x[0:clip] + '...' for x in result]
                    for row in result:
                        print(row)
                else:
                    result = f.read()
                    print(result)
        except IOError:
            display(HTML('<p style="color: red;">Error! Could not read import file.</p>'))

    def display_log(self, from_file=False):
        """Display the log or log file.

        Parameters:
        - from_file (Bool): Sets whether to read the log from the object's log attribute or from file.
        """
        if from_file == True:
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    log_list = f.read().split('\n')
            except IOError:
                display(HTML('<p style="color: red;">Error! Could not read log file.</p>'))
        else:
            log_list = self.log.split('\n')
        if log_list != ['']:
            for item in log_list:
                print(item)
        else:
            display(HTML('<p>No errors are listed in the log.</p>'))

    def filter_features(self, features):
        """Filter features by POS, tag, or entity types."""
        exclude_entity_types = self.exclude_entity_types
        if exclude_entity_types is None:
            exclude_entity_types = []
        if self.include_pos is not None and self.include_tags is not None:
            return [feature for feature in features
                        if feature[3] in self.include_pos
                        and feature[4] in self.include_tags
                        and feature[6][1] not in exclude_entity_types]
        elif self.include_pos is not None:
            return [feature for feature in features
                        if feature[3] in self.include_pos
                        and feature[6][1] not in exclude_entity_types]
        elif self.include_tags is not None:
            return [feature for feature in features
                        if feature[4] in self.include_tags
                        and feature[6][1] not in exclude_entity_types]
        else:
            return [feature for feature in features if feature[6][1] not in exclude_entity_types]

    def get_tokens(self, doc, form='text'):
        """Return a list of tokens. from a spaCy doc."""
        if self.use_lemmas:
            form = 'lemma_'
        if self.use_filters:
            exclude_entity_types = self.exclude_entity_types
            if exclude_entity_types is None:
                exclude_entity_types = []
            if self.include_pos is not None and self.include_tags is not None:
                return [getattr(token, form) for token in doc
                          if token.pos_ in self.include_pos
                          and token.tag_ in self.include_tags
                          and token.ent_type_ not in exclude_entity_types]
            elif self.include_pos is not None:
                return [getattr(token, form) for token in doc
                          if token.pos_ in self.include_pos
                          and token.ent_type_ not in exclude_entity_types]
            elif self.include_tags is not None:
                return [getattr(token, form) for token in doc
                          if token.pos_ in self.include_tags
                          and token.ent_type_ not in exclude_entity_types]
            else:
                return [getattr(token, form) for token in doc
                          if token.ent_type_ not in exclude_entity_types]
        else:
            return [getattr(token, form) for token in doc]

    def get_bow_row(self, filename, index, bag):
        """Convert a dictionary bag of words to a sequence of terms based on term counts.

        Parameters:
        - filename (str): The name of the file to head the row.
        - index (int): The index to be attached to the file row.
        - bag (dict): A bag of words dict of the format `{word: count}`.
        - self.strip_stopwords (Bool): Boolean to remove words from a custom list.
        - self.strip_digits (Bool): Boolean to remove digits from a custom list.
        """
        row = filename + ' ' + str(index) + ' '
        try:
            for k, v in bag.items():
                # Another check on stray punctuation
                if not k.isalnum():
                    pass
                # Do not include digits
                elif self.strip_digits and k.isdigit():
                    pass
                # Otherwise, handle stop words and add the row
                else:
                    if not self.strip_stopwords:
                        term = k.replace(' ', '_') + ' '
                        terms = (term * v)
                        row += terms
                    elif self.strip_stopwords and k.lower() not in self.stoplist:
                        term = k.replace(' ', '_') + ' '
                        term = re.sub('the_|a_|an_', '', term)
                        terms = (term * v)
                        row += terms
                    else:
                        pass
        except (RuntimeError, TypeError):
            self.log += filename + ',Could not generate row from bag of words.\n'
        return row.strip()

    def load_stoplist(self, stoplist_file):
        """Load the stoplist.

        Parameters:
        - stoplist_file (str): The path to the stoplist file.
        """
        if stoplist_file is not None:
            try:
                with open(stoplist_file, 'r', encoding='utf-8') as f:
                    stopwords = f.read().split('\n')
            except IOError:
                self.log += stoplist_file + ',Could not read stoplist file.\n'
                display(HTML('<p style="color: red;">Error! Could not read stoplist file.</p>'))
        else:
            stopwords = []
        return stopwords

    def read_manifest(self, filepath):
        """Read the manifest file."""
        try:
            with open(filepath, 'rb') as f:
                return json.loads(f.read())
        except (IOError, ValueError):
            self.log += filepath + ',Could not read file.\n'

    def save(self, bow_row):
        """Append the row to the import file."""
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
        try:
            with open(self.import_file_path, 'a', encoding='utf-8') as f:
                f.write(bow_row.strip() + '\n')
        except IOError:
            self.log += self.import_file_path + ',Could not append row to import file.\n'

    # Custom entity merging filter
    def skip_ents(self, doc, skip=['CARDINAL', 'DATE', 'QUANTITY', 'TIME']):
        """Duplicate spaCy's ner pipe, but with additional filters.

        Parameters:
        - doc (Doc): The Doc object.
        - ignore (list): A list of spaCy ner categories to ignore (e.g. DATE) when merging entities.

        # RETURNS (Doc): The Doc object with merged entities.
        """
        # Match months
        months = re.compile(r'(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sept(?:ember)?|oct(?:ober)?|nov(?:ember)?|Dec(?:ember)?)')
        with doc.retokenize() as retokenizer:
            for ent in doc.ents:
                merge = True
                if ent.label_ in skip:
                    merge = False
                if ent.label_ == 'DATE' and re.match(months, ent.text.lower()):
                    merge = True
                if merge == True:
                    attrs = {"tag": ent.root.tag, "dep": ent.root.dep, "ent_type": ent.label}
                    retokenizer.merge(ent, attrs=attrs)
        return doc

    def prepare_data(self, json_path):
        """Prepare a file or directory for import."""
        timer = Timer()
        if os.path.exists(self.import_file_path):
            os.remove(self.import_file_path)
        if os.path.isfile(json_path):
            doc = self.read_manifest(json_path)
            self.prepare_data_file(doc, json_path, 0)
        else:
            files = sorted(file for file in os.listdir(json_path) if file.endswith('.json'))
            for i, file in enumerate(files):
                file = json_path + '/' + file
                doc = self.read_manifest(file)
                self.prepare_data_file(doc, file, i)
        display(HTML('<h4>Done!</h4>'))
        print('Time elapsed: %s' % timer.get_time_elapsed())

    def prepare_data_file(self, doc, filepath, index):
        """Prepare a single file for import."""
        filename = os.path.basename(filepath)
        try:
            # Look for bag_of_words, then features; otherwise, tokenise with spaCy
            if self.use_existing_bow and 'bag_of_words' in doc and self.use_filters is None and self.use_lemmas is None:
                bag = doc['bag_of_words']
            elif 'features' in doc:
                if self.use_filters:
                    features = self.filter_features(doc['features'])
                else:
                    features = doc['features']
                if self.use_lemmas:
                    tokens = [feature[2] for feature in features[1:]]
                else:
                    tokens = [feature[0] for feature in features[1:]]
                bag = self.bagify(tokens)
            else:
                # Load the language model with custom tokenizer and entity merger
                self.nlp = spacy.load(self.language_model)
                self.nlp.tokenizer = self.custom_tokenizer()
                self.nlp.add_pipe(self.skip_ents, after='ner')
                # Create a spaCy document, extract tokens, then bagify
                self.spacy_doc = self.nlp(doc['content'])
                tokens = self.get_tokens(self.spacy_doc)
                bag = self.bagify(tokens)
            # Create a row and save it to the import file
            bow_row = self.get_bow_row(filename, index, bag)
            self.save(bow_row)
        except (RuntimeError, TypeError):
            pass
        if self.log is not '':
            with open(self.log_file, 'a') as f:
                f.write(self.log)
