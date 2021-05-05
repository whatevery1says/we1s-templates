# How Jupyter Notebooks Work

In the WE1S Workspace, users interact with their data using a <a href="https://jupyter.org/" target="_blank">Jupyter notebooks-based</a> environment. Jupyter notebooks are a web-based interface for running code inside your web browser. There are two varieties of Jupyter notebooks: the classic Jupyter notebooks interface and the newer Jupyter Lab interface. The WE1S Workspace works with both, but the Jupyter Lab interface is opened by default.

A "notebook" is like a web page with form fields (called "cells") into which you type your Python code. You can then run the code and get feedback. There are a number different notebook implementations, but Jupyter notebooks (formerly called iPython notebooks) are by far the most popular.

When you open a specific notebook, you enter (or paste) your code in the cells and then click the `Run` button or type ++shift+enter++ to run your code. The WE1S Workspace provides notebooks in which the cells are pre-populated with the code necessary to perform specific tasks. Jupyter notebooks also contain documentation cells (written in a combination of Markdown and HTML) that describe the purpose of the cell's code. In some cases, you will be asked to enter configuration information, and this will require you to write some _very_ basic Python code. If you are new to Python, this section provides instructions that will help you configure your cells. If you are more experienced with Python, you can modify the code in the WE1S Workspace to suit your needs. This provides a very flexible research environment suitable for beginners and more advanced users.

Here is a small sample. The cell below contains some code that displays a message, waits 10 seconds, and then displays another message.

<figure>
  <img src="../img/sample-jupyter-notebook-cell.png" />
  <figcaption>Sample Jupyter notebook cell.</figcaption>
</figure>

Notice the small `#!python In []:` to the left of the cell. This tells you that the cell contains some input code. When you run the cell, it will display `#!python In [*]:`. When the code has finished running, it will display `#!python In [1]:` The next cell will display `#!python In [2]:`, and so on. When the code finishes, the output of whatever the code is doing will display right below the cell.  Also notice that there is a small white circle next to the words "Python 3" at the top right of the screen. When you are running a cell, the circle will turn grey. It will turn white again when the circle is finished.

If you make a mistake when running a cell &mdash; or if there is a bug in the code we haven't caught or an issue we haven't anticipated &mdash; an error message will be displayed in the output section. Note that for longer code blocks, you may have to scroll to see the error, so, if something doesn't seem to be working, look for an error. The meaning of Python error messages can be somewhat opaque until you get used to them, so we recommend copying the error you get, pasting it into a Google search bar, and starting there.

You can clear the output by selecting **Cell > Current Outputs > Clear** or **`Cell > All Output > Clear** in the menu at the top of the notebook. There are lots of other menu items which allow you to add and delete cells, as well as to run cells.

For a full tutorial on Jupyter notebooks, see Quinn Dombrowski, Tassie Gniady, and David Kloster's <a href="https://programminghistorian.org/en/lessons/jupyter-notebooks" _target="_blank">Introduction to Jupyter Notebooks</a>.

### Using Jupyter Lab

In the Classic notebook environment, you typically start in a browser tab showing your file and folder hierarchy. By clicking the `New` button at the top right corner, you can open new tabs containing notebooks, text files, or terminals for running processes from the command line. By contrast, Jupyter Lab operates in a single browser tab with the file/folder hierarchy in a sidebar and subtabs containing notebooks, files, and terminals. To open a new subtab, you click the appropriate icon for a notebook, text file, or terminal. One of the other main differences is that many functions are now located in the contextual menu opened by right-clicking on the screen. A screenshot of Jupyter Lab illustrates the appearance of the interface.

<figure>
  <img src="../img/jupyter_lab.png" />
  <figcaption>Screenshot of Jupyter Lab.</figcaption>
</figure>

It is always possible to switch the Classic interface from within Jupyter Lab by selecting "Launch Classic Notebook" from the `Help` menu. For more information, see <a href="https://jupyterlab.readthedocs.io/en/latest/user/interface.html" target="_blank">the Jupyter Lab interface</a>.

!!! Hint
    Classic notebooks will always have the path `tree` in the url in the browser's address bar. By changing `tree` to `lab`, and vice versa, you can switch between the two interfaces.
