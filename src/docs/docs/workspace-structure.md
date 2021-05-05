# Workspace Structure

The WE1S Workspace is a cloud of virtual computers with all the resources you will require to manage your workflow. Most of your work will be on the `write` volume, which we will generally refer to as the Workspace. Technically, however, the Workspace also includes other volumes, such as the MongoDB instance described below. Each volume has access to the same data files.

This section provides a brief overview of what you will see when you launch the Workspace. An outline of the over structure is displayed below, followed by explanations of each component.

:material-folder-outline: [`write`](#write)<br>
┣ :material-folder-outline: [`getting_started`](#getting-started)<br>
┣ :material-folder-outline: [`project_template`](#project-template)<br>
┣ :jupyter-jupyter-logo: [`create_template_archive.ipynb`](#create-template-archive)<br>
┣ :fontawesome-brands-html5: [`getting_started.html`](#getting-started-html)<br>
┣ :fontawesome-brands-html5: [`mongo_express.html`](#mongo-express)<br>
┣ :jupyter-jupyter-logo: [`new_project.ipynb`](#new-project)<br>
┣ :material-language-python: [`template_package.py`](#template-package)<br>
┗ :material-file-outline: [`README.md`](#readme)

## <a name="write"></a>:material-folder-outline: The `write` Folder

The `write` folder is the location where you will do most of your work. When you launch the Workspace, you will see five files and two folders located inside your `write` folder. The functions of each of these is described below.

### <a name="getting-started-html"></a>:fontawesome-brands-html5: `getting_started.html`

This is simply a convenient file that you can open to launch this Getting Started guide. It actually just redirects the browser to `getting_started/index.html`. It is a read-only file and cannot be modified.

### <a name="readme"></a>:material-file-outline: `README.md`

This is a <a href="https://www.markdownguide.org/" target="_blank">Markdown</a> file containing information about the version of the project template in your Workspace. If you download a later version, it may no longer be compatible, and you may have to install the most recent version of the Workspace. The information in this file can therefore be useful to check whether your project template and your Workspace container are compatible. The `README.md` file is a read-only file and cannot be edited.

### <a name="template-package"></a>:material-language-python: `template_package.py`

This is Python script that contains functions used by both the `create_template_archive` and `new_project` notebooks. It is a read-only file and cannot be edited.

### <a name="create-template-archive"></a> :jupyter-jupyter-logo: `create_template_archive.ipynb`

This notebook can be used to make a compressed `.tar.gz` file of your `project_template` folder. Generally, you will only want to do this if you have customized the template and wish to use your customizations in another project. Use this notebook to create an archive of your custom template, and you can point to it as your template source when creating projects with the `new_project` notebook.

### <a name="new-project"></a>:jupyter-jupyter-logo: `new_project.ipynb`

This notebook is the main starting point for you workflow. Use the `new_project` notebook to create a new copy of the `project_template` folder with metadata about your specific project. You can then enter the new project folder to import your data into the new project.

### <a name="getting-started"></a> :material-folder-outline: `getting_started`

This folder contains the Getting Started web site you are currently reading. The site can be launched by going to `getting_stared/index.html` or by launching `getting_started.html` from the Workspace `write` folder. You should not need to modify anything in this folder, unless you want to use the Getting Started site as a place to add notes to yourself in the site's individual web pages.

### <a name="project-template"></a>:material-folder-outline: `project_template`

This folder contains are the files and resources required for the individual modules in WE1S Workspace. When a new project is created, these resources are copied from the `project_template` folder into the new project folder and become available for use in the new project.

## <a name="mongo-express"></a>:material-database-outline: MongoDB

The Workspace comes packaged with an instance of the <a href="https://www.mongodb.com/try/download/community" target="_blank">MongoDB</a> database, running on `mongodb://mongo:27017`. You can use this the MongoDB instance to manage your data. MongoDB stores data in json-like records similar to the json files used in Workspace projects, making the interchange of data between the two relatively transparent. Modules access MongoDB databases through Python's <a href="https://pymongo.readthedocs.io/en/stable/" target="_blank">pymongo</a> wrapper. The use of MongoDB is optional. You can also choose to import your data from flat files.

If you wish to use MongoDB, the `mongo-express.html` file will launch <a href="https://github.com/mongo-express/mongo-express" target="_blank">MongoExpress</a>, a web-based admin interface for MongoDB, running on port 8081. This will allow you to perform some database administration tasks without running Python code.

!!! danger "To Do"
    What other information might be useful here?