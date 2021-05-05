"""json_to_txt_csv.py

Exports a collection of plain text files plus metadata.csv to a project directory.

Last update: 2021-01-29
"""

import csv
import json
import os
from IPython.display import display, HTML
from pathlib import Path
from zipfile import ZipFile
import pandas as pd

def clear_txt(txt_dir, ext='txt', metafile=None, zipfile=None):
    """Remove txt files from dir (and optionally, metafile and zipfile)
    Metafile and zipfile are deleted if path is given, ignored in bad path or None.
    
    Parameters:
        txt_dir (str): Path string to create txt and csv output.
        ext (str): file extension to filter contents of txt_dir.
        metafile (str): csv file path/name for output.
        zipfile (str): zip file path/name for output.
    """
    if not txt_dir or not ext:
        return
    elif os.path.isdir(txt_dir) == False:
        return
    txtfiles = list(Path(txt_dir).glob('*.'+ext))
    for f in txtfiles:
        f.unlink()
    if metafile:
        mf = Path(txt_dir) / metafile
        if mf.exists():
            mf.unlink()
    if zipfile:
        zf = Path(txt_dir) / zipfile
        if zf.exists():
            zf.unlink()
    if len(os.listdir(txt_dir)) > 0:
        listing = ', '.join(os.listdir(txt_dir))
        display(HTML('<p>Directory after clear: ' + listing + '</p>'))
            
def debag(bag_of_words, join_token=' '):
    """
    Parameters:
        bag_of_words(dict): {word:count, word:count}
        join_token(str): token for joining words

    Returns:
        str: a sorted, joined list of tokens, repeated by key counts
        
    Example:
        {'the':3, 'quick':1, 'brown':2}
        'brown brown the the the quick'
    """
    words = []
    for key, val in bag_of_words.items():
        for i in range(val):
            words.append(key)
    words.sort()
    result = join_token.join(words)
    return result

def export_features_tables(save_path, json_dir):
    """Export features tables to a CSV file.
    
    Parameters:
        features (list): A list of lists.
        filepath (str): A path where the CSV file will be saved.
    """
    errors = []
    if os.path.isdir(save_path) == False:
        os.mkdir(save_path)
    if os.path.isdir(json_dir):
        files = [entry.path for entry in os.scandir(json_dir) if entry.path.endswith('.json')]
        for file in files:
            filename = os.path.basename(file)
            filename = filename.replace('.json', '.csv')
#             savepath = os.path.join(save_path, file.replace('.json', '.csv'))
            savepath = save_path + '/' + filename
            try:
                with open(os.path.join(json_dir, file), 'r') as f:
                    doc = json.loads(f.read())
                df = pd.DataFrame.from_records(doc['features'][1:], columns=doc['features'][0])
                df.to_csv(savepath, index=False)
            except IOError:
                errors.append(file)
    if len(errors) > 0:
        with open('error_log.txt', 'a') as f:
            for error in errors:
                f.write(error)
        msg = '<p style="color: red;">' + str(len(errors)) + ' file(s) could not be saved. '
        msg += 'Your features table(s) may be in the wrong format, which should be a list of lists. '
        msg += 'Please consule the <code>error_log.txt</code> file for names of files that could not be saved.</p>'
        display(HTML(msg))

def json_to_txt_csv(json_dir, txt_dir, txt_content_fields, csv_export_fields, metafile, limit=0):
    """Assumes that you have run the import notebook with Tokenize
    and generated a bag_of_words field in each json.
    Will create a parallel txt directory with txt files and a csv.

    Parameters:
        json_dir (str): Path string of source JSON files.
        txt_dir (str): Path string to create txt and csv output.
        txt_content_fields (str list): field names to check for contents, first found is used.
        csv_export_fields (str list): field names to find and copy into csv output columns, in order.
            The filename field is prepended to this list.
        metafile (str): csv file path/name for output.
        limit (int): maximum json files to process. 0=unlimited.
    """
    if os.path.isdir(json_dir):
        files = [entry.path for entry in os.scandir(json_dir) if entry.path.endswith('.json')]
        Path(txt_dir).mkdir(parents=True, exist_ok=True)
        # create csv for metadata
        with open(metafile, 'w+') as c:
            cw = csv.writer(c)
            headers = ['filename']
            headers.extend(csv_export_fields)
            cw.writerow(headers)
            # loop through json files
            for idx, f in enumerate(files):
                if limit>0 and idx==limit:
                    break
                # read json file
                with open(f, 'r') as jfile:
                    jdata = json.load(jfile)
                    cdata = None
                    # check for content sources, use first one
                    for field in txt_content_fields:
                        if not cdata and field in jdata and jdata[field]:
                            cdata = jdata.get(field)
                    # skip writing txt and csv row if no content
                    if not cdata: # no content, skip to next file
                        continue
                    # continue to try to write metadata
                    fname = str(Path(f).stem + '.txt')
                    row = [fname]
                    # add fields entries in order, or empty string if missing
                    for field in csv_export_fields:
                        if field in jdata and jdata[field]:
                            row.append(jdata.get(field))
                        else:
                            row.append('')
                    try:
                        cw.writerow(row)
                    except Exception as e:
                        print(e, fname)
                        continue
                    # save txt file after metadata row is written
                    fout = Path(txt_dir) / fname
                    with open(fout, 'w') as tfile:
                        if isinstance(cdata, str):
                            tfile.write(cdata)
                        else:
                            tfile.write(debag(cdata))

def report_results(txt_dir, metafile):
    """Display the tails of the text directory and metadata file.
    
    Parameters:
        txt_dir (str): input Path string to txt and csv files
    """
    display(HTML('<p>Text directory (tail sample):</p>'))
    # !ls -la $txt_dir | tail -n3
    ul = '<ul>'
    for file in os.listdir(txt_dir)[-2:]:
        ul += '<li>' + file + '</li>'
    ul += '</ul>'
    display(HTML(ul))
    display(HTML('<p>Metadata (tail sample):</p>'))
    df = pd.read_csv(metafile)
    df = df.tail(3)
    display(HTML(df.to_html()))
    # !tail -n3 $metafile

def zip_txt(txt_dir, zipfile, ext='.txt'):
    """Zip all txt files.

    Parameters:
        txt_dir (str): input Path string to txt and csv files
        zipfile (str): output zip file path/name
        ext (str): file extension to filter contents of txt_dir    
    """
    display(HTML('<p>Creating zip file...</p>'))
    with ZipFile(zipfile, "w") as newzip:
        if os.path.isdir(txt_dir):
            files = [entry for entry in os.scandir(txt_dir) if entry.path.endswith(ext)]
            for entry in files:
                newzip.write(entry.path, arcname=entry.name)
    # Remove zipped txts, but not metafile
    clear_txt(txt_dir, metafile=None)
    # Inspect the results
    display(HTML('<p>Zip archive (tail sample):</p>'))
    ul = '<ul>'
    for file in newzip.namelist()[-4:]:
        ul += '<li>' + file + '</li>'
    ul += '</ul>'
    display(HTML(ul))


# An alternative to a Python zip method is Jupyter shell magic:
#
#   pname = Path(project_dir).stem
#   %cd $txt_dir
#   !zip txt.zip *.txt
#   !ls *.zip
#   %cd -

# test unpack zip
#
# %pwd
# %cd $txt_dir
# !unzip $zipfile
# %cd -