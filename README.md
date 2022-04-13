MongoDB utility to make migrations and data processing.
Allow to create flexible configurable files to processing mongo databases on everal environments.

The main conception of MongoDB migrator is creating sets of instructions with special MGR files.
Examples of MGR files located in folder /examples

Each MGR file will be located in folder /migrations/mongo_versions and will have next format:

[{
   "step_id": "<step ID1>",
   "step_description": "<step description1>",
   "action": "<some action name1>" 
   additional fields depends on action type..........
  },{
   "step_id": "<step ID2>",
   "step_description": "<step description2>",
   "action": "<some action name2>" 
   additional fields depends on action type..........
  }]
  
MongoPipeLiner remember all completed steps of each configurable file (*.mrg) in special collection of mongo 'migrations' and skip completed steps to avoid repeat executing of them.

So .mgr files can be used as a migration pipeline and will stay on folder migrations/mongo_versions for apply it on next enviromnent.

ACTIONS available to use in MGR files:
------------------------------------------------------------------------------------------------------------------------------
| ACTION            | DESCRIPTION                                                                                            |
|-------------------|--------------------------------------------------------------------------------------------------------|
| aggregation       | Traditional MongoDB Pipeline procedure (export format of MongoDB Compass)                              |
| update            | Traditional MongoDB procedure to update some data (using update_many)                                  |
| command           | Traditional MongoDB command (refer to this list) https://www.mongodb.com/docs/manual/reference/command |
| rename_collection | Rename collection                                                                                      |
| drop_collection   | Drop collection and all indexes                                                                        |
| py_code           | Custom short Python code to run in some step                                                           |
| py_file           | Custom Python file code to run a couple of lines                                                       |
| run_bash          | Run bash command                                                                                       |
------------------------------------------------------------------------------------------------------------------------------

All steps in MGR file can be fully customized and mixed with all of actions.

**Writing of MGR scripts:**

Common fields of each STEPS
| Field name       | Required | Description                                                                                                                       |
|------------------|----------|-----------------------------------------------------------------------------------------------------------------------------------|
| step_id          |     *    | Required STRING Identifier for exact step of MGR file. Will be unique for each MGR file                                           |
| step_description |          | Short information about STEP result processing. Autogenerate description if not set.<br> _Extremaly recommend to fill this field_ |
| action           |     *    | Action will explain to migrator STEP appointment                                                                                  |
| depend_on        |     *    | Migrator will check that the file you specify here has already been successfully applied.                                         |





All actions are eligible for MacOS

1) Install Homebrew

Open Terminal or your favorite OS X terminal emulator and run

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
```
The script will explain what changes it will make and prompt you before the installation begins. 
Once you’ve installed Homebrew, insert the Homebrew directory at the top of your PATH environment 
variable. You can do this by adding the following line at the bottom of your ~/.profile file

```
export PATH="/usr/local/opt/python/libexec/bin:$PATH"
```
if MacOS 10.12 or older:
```
export PATH=/usr/local/bin:/usr/local/sbin:$PATH
```

2) Install Python3 (on MACOS)
```
brew install python
```

3) Install VirtualEnv
```
pip3 install virtualenv
```

4) Create VirtualEnv
```
virtualenv venv
```

5) Switch to newly created VirtualEnv

```
source venv/bin/active
```

6) Install requirements
```
pip3 install -r requirements.txt
```

7) Setup environment variables
```
set -a
. ./prepare_environment/work.env
set +a
```

8) RUN
```
python3 main.py
```

