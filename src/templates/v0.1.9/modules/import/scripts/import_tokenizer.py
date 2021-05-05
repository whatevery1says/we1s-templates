"""import_tokenizer.py.

Tokenizes imported json file content and saves it in a `bag_of_words`
field in the original json doc file.

Call with

```python
tokenizer = ImportTokenizer(json_dir, language_model='en_core_web_sm',
                            log_file='tokenizer_log.txt')
tokenizer.start(bagify_features=False, mode=None)
```

The tokenizer class follows the algorithm below:

1. Skip tokenization if a `bag_of_words` field exists.
2. Create a `bag_of_words` from a `features` table if the user
   requests it with `start(bagify_features=True)`.
3. Use the WE1S tokenizer to create a `features` table or `bag_of_words`
   if the user requests it with `start(mode='we1s')`.
   Other tokenizers such as NLTK could be added easily in the future.
4. Create a `bag_of_words` by stripping non-word characters and
   splitting on white space. This the default.

Last update: 2021-02-15
"""

# Python imports
import json
import os
import re
import sys
import ipywidgets
import spacy
from spacy.tokenizer import Tokenizer
from collections import Counter
from IPython.display import clear_output, display, HTML
from itertools import islice
from natsort import natsorted
from ipywidgets import HBox, IntProgress, Label

from timer import Timer

IntProgress(
    description='Tokenizing...'
)

## CONSTANTS
LINEBREAK_REGEX = re.compile(r'((\r\n)|[\n\v])+')
NONBREAKING_SPACE_REGEX = re.compile(r'(?!\n)\s+')
PREFIX_RE = re.compile(r'''^[\[\]\("'\.,;:-]''')
SUFFIX_RE = re.compile(r'''[\[\]\)"'\.,;:-]$''')
INFIX_RE = re.compile(r'''[-~]''')
SIMPLE_URL_RE = re.compile(r'''^https?://''')

## ImportTokenizer Class
class ImportTokenizer:
    """Configure an ImportTokenizer object."""

    def __init__(self, json_dir, language_model='en_core_web_sm',
                log_file='tokenizer_log.txt'):
        """Initialize the class."""
        self.json_dir = json_dir
        self.language_model = language_model
        self.log_file = log_file
        self.tokenizer_errors = 0
        self.read_errors = 0

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
        bag = dict(Counter(tokens))
        return dict(natsorted(bag.items()))

    def custom_tokenizer(self):
        """Add custom tokenizer settings."""
        return Tokenizer(self.nlp.vocab, prefix_search=PREFIX_RE.search,
                                    suffix_search=SUFFIX_RE.search,
                                    infix_finditer=INFIX_RE.finditer,
                                    token_match=SIMPLE_URL_RE.match)

    def get_tokens(self, spacy_doc):
        """Return a list of tokens. from a spaCy doc."""
        return [token.text for token in spacy_doc]

    def read_manifest(self, filepath):
        """Read the manifest file."""
        try:
            with open(filepath, 'rb') as f:
                return json.loads(f.read())
        except (IOError, ValueError):
            self.read_errors += 1
            with open(self.log_file, 'a') as f:
                f.write('Read error: ' + os.path.basename(filepath) + '\n')

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

    def start(self, bagify_features=False, save_features_table=False, method=None):
        """Tokenize the files in the json directory."""
        clear_output()
        timer = Timer()
        num_iters = 0
        pbar = IntProgress(min=0, max=100) # instantiate the progress bar
        percent = ipywidgets.HTML(value='0%')
        display(HBox([Label('Tokenizing...'), pbar, percent]))
        if not os.path.exists(self.json_dir):
            raise ('Error: A json folder does not exist.')
        else:
            if save_features_table and method != 'we1s':
                msg = 'Warning! Features tables can only be saved using the "we1s" method.'
                display(HTML('<p style="color: red;">' + msg + '</p>'))
            files = sorted(file for file in os.listdir(self.json_dir) if file.endswith('.json'))
            for i, file in enumerate(files):
                filepath = self.json_dir + '/' + file
                doc = self.read_manifest(filepath)
                doc = self.tokenize_doc(doc, file, i, bagify_features=bagify_features,
                                        save_features_table=save_features_table,
                                        method=method)
                with open(filepath, 'w') as f:
                    f.write(json.dumps(doc))
                this_iter = i + 1
                progress = int(100. * this_iter/len(files))
                pbar.value = progress
                percent.value = '{0}%'.format(progress)
        display(HTML('<h4>Done!</h4>'))
        if self.read_errors > 0 or self.tokenizer_errors > 0:
            msg = ''
            if self.read_errors > 0:
                msg += '<p style="color: red;">' + str(self.read_errors) + ' document(s) could not be read.</p>'
            if self.tokenizer_errors > 0:
                msg += '<p style="color: red;">' + str(self.tokenizer_errors) + ' document(s) could not be tokenized.</p>'
            msg + '<p style="color: red;">Consult the log file for a list of filenames.</p>'
            display(HTML(msg))
        print('Time elapsed: %s' % timer.get_time_elapsed())

    def get_features_table(self):
        """Return a feature table as a list of lists."""
        feature_list = [['TOKEN', 'NORM', 'LEMMA', 'POS', 'TAG', 'STOPWORD', 'ENTITIES']]
        for token in self.spacy_doc:
            # Get named entity info (I=Inside, O=Outside, B=Begin)
            ner = (token.ent_iob_, token.ent_type_)
            token_features = [token.text, token.norm_, token.lemma_, token.pos_, token.tag_, str(token.is_stop), ner]
            feature_list.append(token_features)
        return feature_list
        
    def tokenize_doc(self, doc, filename, index, bagify_features=False, save_features_table=False, method=None):
        """Tokenize a single file."""
        try:
            # Look for bag_of_words, then features; otherwise, tokenise with spaCy
            if 'bag_of_words' in doc:
                return doc
            elif 'features' in doc and bagify_features == False:
                pass
            elif 'features' in doc and bagify_features == True:
                tokens = [feature[0] for feature in doc['features'][1:]]
                doc['bag_of_words'] = self.bagify(tokens)
            elif method == 'we1s':
                # Load the language model with custom tokenizer and entity merger
                self.nlp = spacy.load(self.language_model)
                self.nlp.tokenizer = self.custom_tokenizer()
                self.nlp.add_pipe(self.skip_ents, after='ner')
                # Create a spaCy document, extract tokens, then bagify
                self.spacy_doc = self.nlp(doc['content'])
                if save_features_table:
                    doc['features'] = self.get_features_table()
                if bagify_features:
                    tokens = self.get_tokens(self.spacy_doc)
                    doc['bag_of_words'] = self.bagify(tokens)
            elif 'content' in doc:
                tokens = [re.sub(r'\W+', '', token) for token in doc['content'].split()]
                if bagify_features:
                    doc['bag_of_words'] = self.bagify(tokens)
            else:
                self.tokenizer_errors += 1
                with open(self.log_file, 'a') as f:
                    f.write('Tokenizer error: ' + filename)
            return doc
        except (RuntimeError, TypeError):
            self.tokenizer_errors += 1
            with open(self.log_file, 'a') as f:
                f.write('Tokenizer error: ' + filename)
