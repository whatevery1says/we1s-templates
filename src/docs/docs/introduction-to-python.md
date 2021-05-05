# Introduction to Python

Python is an easy-to-learn programming language that is very popular in the digital humanities, in part because it has a large user community that has developed tools for such tasks as natural language processing and machine learning. You should be aware that there are two common versions of the language: Python 2 and Python 3. Although tools developed in Python 2 are still common, it is no longer supported as of January 2020. All of the code in the WE1S is written in Python 3.7. The differences are fairly minor, but, if you need to Google how do something in Python, be sure that you are getting an answer that is compatible with version 3.7.

### Basic Python Concepts

#### File Paths

A file path specifies the unique location of a file on a file system. File paths are important to understand when navigating through your file system using your computer's command line and when using a programming language (for more on Mac command lines, we recommend Miriam Posner's <a href="http://miriamposner.com/classes/dh101f16/tutorials-guides/programming/get-to-know-your-terminal/" target="_blank">Get to know your terminal</a>); for more on Windows command lines, we recommend <a href="https://www.computerhope.com/issues/chusedos.htm" target="_blank">How to use the Windows command line</a>). There are 2 common kinds of file paths: absolute and relative. An **absolute file path** points to the location of a file by displaying the full directory tree hierarchy in which path components, separated by a delimiting character (usually a slash, `#!python /` or `#!python \`, depending on your operating system), represent each directory under which the file is stored.

For example, on a Mac or Linux machine, the absolute file path of a text file stored in a folder on a user's Desktop looks something like this:

```python
/Users/user_name/Desktop/folder_name/file_name.txt
```

On a Windows machine, the absolute file path of a text file stored on a user's Desktop looks like this:

```python
C:\Users\user_name\Desktop\folder_name\file_name.txt
```

A **relative file path**, in comparison, points to the location of a file relative to "where" the user is in the file system. So, if you used your command line to navigate to the folder on your Desktop described above and then looked at the text file, the relative file path would simply be:

```python
file_name.txt
```

If you then used your command line to move back up to your Desktop and looked for the text file, the relative file path would be: `#!python folder_name/file_name.txt` (Mac or Linux) or  `#!python folder_name\file_name.txt` (Windows).

!!! note "Note"
    The WE1S Workspace runs on a Linux machine, so any file path you see or need to enter will be of the Mac/Linux variety using a forward `#!python /`.

Many file paths will be automatically configured for you in the WE1S Workspace, but you will need to enter file paths from time to time. The instructions in each notebook will tell you whether to enter an absolute or relative file path. If you're not used to working with them, file paths can be vexing because entering in the wrong file path will cause errors in otherwise "working" code. In general, if you see a `#!python FileNotFoundError` output to a cell in your notebook, your issue could be related to file path(s) you have configured.

#### Python Packages

In Python, you use "functions" to perform operations. For example, the `#!python print()` function prints whatever message inside the parentheses to the screen. Python has a set, or "library", of functions (known as "the standard library") like `#!python print()`, which can be "called" out of the box. It is also possible to import libraries of functions, which are called either "packages" or "modules", into your code. Some Python packages like `time` have to be imported; they are not available by default in order to save memory. Other Python packages are designed by third-party contributors. These generally have to be installed on the machine running the code and then imported into the notebook. The WE1S Workspace comes with all required packages pre-installed. In the notebooks, a cell (generally at the beginning of the notebook) is pre-configured to import them into the notebook. You will see this where the cell contains lines like `#!python import PACKAGE_NAME` (where `#!python PACKAGE_NAME` represents the name of the package) or `#!python from PACKAGE_NAME import FUNCTION_NAME`. You will not need to modify this setup, but it is useful to be familiar with the terminology and aware of the purpose of this code.

#### Data Types

In most programming languages, content is categorised into types of data, each of which has its own set of behaviours. In particular, some functions can only operate with certain data types. In Python, some of the most common types of content are *integers*, *floats*, *strings*, *lists*, *dictionaries* (also known as "dicts"), and Booleans (True or False). The data type of any piece of data is defined using delimiter symbols:

- *strings*: enclosed in apostrophes or quotation marks (e.g. `#!python 'John'` or `#!python "John"`).
- *integers* and *floats*: no delimiters (e.g. `#!python 100`, `#!python 3.14`)
- *lists*: enclosed in square brackets (e.g. `#!python [1, 2]` or `#!python ['Jack', 'Jill']`).
- *dicts*: enclosed in curly brackets (e.g. `#!python {'Jack': 1}`).
- *Booleans*: `#!python True` or `#!python False` (capitalised with no delimiters)

We'll look at each of these datatypes more closely below.

**Strings** contain alphanumeric data — that is, either numbers or letters, as well as punctuation marks. Strings are delimited either by single or double quotation marks. So `#!python 'hello'` and `#!python "hello"` are exactly the same. In the WE1S Workspace, single quotation marks are used wherever possible (and also because that is a recommendation of a prominent Python code style guide). Quotation marks inside of apostrophe delimiters will be interpreted as part of the string, as will apostrophes inside quotation mark delimiters. For example, you could encode the sentence He said, "We are ready." as `#!python 'He said, "We are ready."'`

There are a number of gotchas when dealing with strings. First, curly quotes or smart quotes are not interpreted as quotation marks by Python; they will be treated as characters in the string. So be warned. If you try to copy code from a document with curly quotes, you are likely to get an error.

Some strings may contain apostrophes or quotation marks that are part of the string, not delimiter symbols. Take, for example, the sentence `#!python We're ready.`. Coding this as `#!python 'We're ready.'` will generate an error because Python will interpret the second apostrophe as a delimiter, ending the string. An obvious way around this problem is to use double quotation marks as the delimiters: `#!python "We're ready."`. That works. But what if you wanted to use the sentence `#!python He said, "We're ready."`? For this sentence you will probably want to use a method called "escaping" the ambiguous punctuation mark. In Python, characters like this are normally escaped with a preceding backslash. Here is any easy way to fix the problem: `#!python 'He said, "We\'re ready."'`. The backslash before the apostrophe tells Python not to interpret it as a string delimiter.

!!! note "Note"
    In the WE1S Workspace we try to use single quotation marks as consistently as possible, switching to double quotation marks only if there is a reason to switch. This conforms with Python's <a href="https://www.python.org/dev/peps/pep-0008/#string-quotes" target="_blank">PEP 8 recommendations</a> for code style.

Various types of **numbers** are recognised by Python. The most important types are floats, which can have decimal points, and integers, which cannot. The standard library contains functions to convert one to the other. Their different behaviours mostly become important when you are performing mathematical operations.

Mathematical operators are symbols like `#!python +` and `#!python -` that tell Python what operations to perform. As you can imagine, they indicate "add" and "subtract" respectively. Other mathematical operators are `#!python *` (multiply) and `#!python /` (divide). It is not necessary to put spaces around the operators, but it is generally good coding style.

For a fuller (but still digestible) description of mathematical operators, see <a href="https://codingexplained.com/coding/python/basic-math-operators-in-python" target="_blank">Basic Math Operators in Python</a>.

**Lists** are comma-separated items belonging to other data types such as numbers or strings, as in the examples above. You can also have lists of dictionaries, or even lists of lists. Items in lists are stored in a strict order, and each item has an index number. Like most programming languages, Python uses zero-indexing, so the first item in the list will have the index number 0. You can reference items in a list by giving its number in square brackets. For instance, if you had a list called `#!python my_list`, you could get the first item in the list with `#!python my_list[0]`.

**Dictionaries** (also called **dicts**) are like lists, except that each item is a key-value pair (separated by a colon). A common use of dictionaries is to contain word counts. Consider this dictionary: `#!python {'Jack': 1, 'Jill': 2}`. This might be used to indicate that the word "Jack" occurs once and the word "Jill" occurs twice.

Items in dictionaries are not stored in order, so they must be referenced by their keys. In order to illustrate this, we need to save our dict to a _variable_ a concept that will be explained in full below. We'll call our variable `#!python word_counts`. We can then find the number of times "Jill" occurs by calling `#!python word_counts['Jill']`. Try running the cell below to demonstrate this. Then experiment with creating your own dicts and re-run the cell.

**Booleans** are binary values, either `#!python True` or `#!python False`.

!!! important "Important"
    The Boolean values `#!python True` and `#!python False` must be capitalized, and they must not be contained in quotation marks (i.e. not `#!python 'True'` or `#!python 'False'`).

#### Variables

A variable is a container for some data of any type. This container is referenced by a label or variable name. The content, or _value_, of a variable is assigned to the variable name using the `#!python =` sign. For instance, `#!python firstname = 'John'` would assign the string `#!python 'John'` to the variable `#!python firstname`. If you also assigned `#!python lastname = 'Smith'`, then `#!python firstname + ' ' + lastname` would produce the string `#!python 'John Smith'`. In some cases, you have to create the variable before you assign a value to it. For instance, you might create an empty list like `#!python my_list = []`.

Once you have assigned a value to a variable name, you can reference it by the variable name in your subsequent code. This is what we did with the `#!python word_counts` variable in the discussion of dictionaries above.

You can name variables whatever you want, although they cannot have spaces or punctuation marks. It is good coding style to make variable names short and descriptive of the values they are storing. As in the case of `#!python word_counts`, it is conventional to use the underscore `_` where you might use a space in ordinary English. We have tried to follow these guidelines as much as possible in the development of configuration variables for the WE1S Workspace.

#### Functions

A function is a command to do something with one of the data types and send back (or "return") a result. When functions form part of larger libraries, they are often called "methods". Since `#!python print()` and `#!python str()` are part of the standard library, they are often referred to as the `#!python print()` and `#!python str()` methods.

Functions are called by using the name of the function (e.g. `#!python print`) followed by parentheses containing the data to be passed to the function. So `#!python print('Hello world.')` passes "Hello world." to the `#!python print()` function.  The value in parentheses is called the _argument_ or _parameter_. You can use a variable as the argument of a function. For instance, if you defined `#!python my_var = 1`, you could then use `#!python str(my_var)` to convert `#!python 1` to a `#!python '1'`. Another example is the `#!python append()` function, which adds an item to the end of a list. For instance, you could add the number 1 to the `#!python my_list` created above: `#!python my_list.append(1)`.

Code that is part of a function is indented by four spaces (a tab also works within the notebook environment). This also applies to certain function-like operations such as `#!python for` loops or `#!python if...then` clauses. If you get an error around a function or either of these key words in the code, you may have accidentally changed the indentation.

In the WE1S Workspace, many functions are pre-written and called from a single line of code that passes your configuration variables to the function. Complex functions are generally stored in separate files (typically in a `#!python scripts` folder) and imported into the notebook in order to reduce clutter. Experienced Python users can open and modify the functions files.

#### Comments

Comments are blocks of text in the code that do not get executed _as_ code. They exist to provide explanations for human readers to understand what the code is doing. In Python, comments are indicated by a preceding `#!python #`. Anything with this preceding hash will be ignored. In the WE1S Workspace, code is heavily commented to help you see what its purpose is.

A common trick is to **"comment out"** blocks of code so that they will not function by placing `#!python #` at the beginning of the line. The code can then be **"uncommented"** by removing the `#!python #`. A shortcut for commenting out and uncommenting code in the Jupyter notebooks environment is the key combination ++ctrl++ + `/`. Use this for toggling commented code on and off.

#### JSON

In the WE1S Workspace, data is typically accessed in a format called JSON. JSON is an acronym for Javascript Object Notation, and, as the name suggests, it derives originally from the Javascript programming language. JSON looks and behaves pretty much like a Python dict with one major gotcha: keys and values have to be in double quotation marks. (There are a few other differences as well, but this is the most obvious). So, if we want to work with JSON data in Python, we need to parse it into a Python dict. Likewise, if we want to, for instance, send the material in a Python dict to a web brower or save it to a file, we first convert it to JSON format, the data type of which is a string. Python has a `json` library that performs this task, and the WE1S Workspace uses it internally when it accesses project data stored as JSON files.