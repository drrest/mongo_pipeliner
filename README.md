MongoDB utility to make migrations and data processing.
Allow to create flexible configurable files to processing mongo databases on everal environments.

The main conception of MongoDB migrator is creating sets of instructions with special MGR files.
Examples of MGR files located in folder /examples

parameters:

    --list ( -l )   -  will show all applied migrations with separated steps and descriptions

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
  
MongoPipeLiner remember all completed steps of each configurable file (*.mgr) in special collection of mongo 'migrations' and skip completed steps to avoid repeat executing of them.

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
| depend_on        |     *    | Migrator will check that the file you specify here has already been successfully applied.                                 
|


AGGREGATION EXAMPLE (1 steps)
```json
[{
   "step_id": "1",
   "step_description": "Save list of comments with two additiona fields first_name and last_name to collection tmp_comments", // Next time migrator runned will check for this ID in migrations collection.
   "action": "aggregation",    // Action is aggregate
   "collection": "car",        // Name of collection to aggregate 
   "pipeline": [               // Pipeline can be mastered in MongoDB compass and exported to Python3 format
    {
        "$unwind": {
            "path": "$comments", 
            "preserveNullAndEmptyArrays": True
        }
    }, {
        "$lookup": {
            "from": "users", 
            "localField": "comments.created_by_user_name", 
            "foreignField": "username", 
            "as": "tmp_user"
        }
    }, {
        "$addFields": {
            "comments.created_by_first_name": "$tmp_user.first_name"
        }
    }, {
        "$addFields": {
            "comments.created_by_last_name": "$tmp_user.last_name"
        }
    }
]
}, {
  "$out": "tmp_comments"
}]
```

UPDATE EXAMPLE (2 steps)
```json
[{
   "step_id":"1",
   "step_description": "Set status 10 for car with id 6bf11c75-2c2e-41d4-8cc7-33e29d1e6cb7",
   "action": "update",      // Action is update
   "collection": "car",     // Name of collection to update
   "filter": {"id": "6bf11c75-2c2e-41d4-8cc7-33e29d1e6cb7"},  // Set of filters for update
   "update": {"$set": {"status_id": "10"}},    // Update with this data
   "args": {                                   // args will be {} is you have no additional arguments
       "upsert": False,
       "array_filters": None,
       "bypass_document_validation": False,
       "collation": None,
       "hint": None,
       "session": None}
},
{
   "step_id":"2",
   "step_description": "Set status 7 for car with id 6bf11c75-2c2e-41d4-8cc7-33e29d1e6cb7",
   "action": "update",
   "collection": "car",
   "filter": {"id": "6bf11c75-2c2e-41d4-8cc7-33e29d1e6cb7"},
   "update": {"$set": {"status_id": "7"}},
   "args": {
       "upsert": False,
       "array_filters": None,
       "bypass_document_validation": False,
       "collation": None,
       "hint": None,
       "session": None}
}]
```

COMMAND EXAMPLE (1 step)
```json
[{
 "step_id": "1",
 "step_description":"Apply new validator => car_tmp",
 "action": "command",         // Action is command
 "command": "collMod",        // MongoDB Command to modify collection
 "command_body": "car_tmp",   // Collection name (in the case of command collMod, otherwise will contain value of command you provided)
 "args":{                     // refer to MongoDB manual and pymongo manual
    "validator": {'$jsonSchema': ................. }},
    "validationLevel":"strict"
 }
}]
```

RENAME COLLECTION
```json
[{
   "step_id": "1",
   "step_description":"Rename collection car => car_old",
   "action": "rename_collection",      // Action is rename collection
   "from_name": "car",                 // from collection car
   "to_name": "car_old"                // to collection car_old
}]
```

DROP COLLECTION example
```json
[{
   "step_id": "1",
   "step_description":"Drop collection car_old",
   "action": "drop_collection",      // Action is drop collection
   "name": "car_old"                 // collection car_old
}]
```

PYTHON CODE example
```json
[{
   "step_id": "1",
   "step_description":"Copy indexes from collection car to collection car_new",
   "action": "py_code",    // Action yo run short code
   "code": "for name, index_info in mongo_client.car.index_information().items():\n    mongo_client.car_new.create_index(keys=index_info['key'], name=name)",   // Short Python script
}]
```

PYTHON FILE example
Next STEP with execute of python file you provided in field file
```json
[{
   "step_id": "1",
   "step_description": "Running of file mig1.py #1",
   "action": "py_file",     // Action to execute python file
   "file": "mig1.py"        // Will looking for file mig1.py in folder migrations/mongo_versions
}]
```

Example of file mig1.py
```python
tmp_case = mongo_client.car.find_one({"num": 2650})
global_variables['car_id'] = tmp_case['id']
global_variables['result'] = {"result": "ok", 
                              "step_description": f"Processed car #{global_variables['car_id']}"}
result = global_variables['result']
```

as you see python file not contains any imports
It will be executed inside migrator interpreter instance and will have access to all variables inside.
global_variables is only needed to manage results or other temporary variables

Also all variables will be accessed to all scripts runned in next steps of pipeline

for example:
```json
[{
   "step_id": "1",
   "step_description": "run of file mig1.py #1",
   "action": "py_file",     // Action os execute python file
   "file": "mig1.py"        // Will looking for file mig1.py in folder /migrations/mongo_versions
},
{
   "step_id": "2",
   "step_description": "run of file mig2.py #2",
   "action": "py_file",     // Action os execute python file
   "file": "mig2.py"        // Will looking for file mig2.py in folder /migrations/mongo_versions
}]
```
There is only example to understand, when you run the step “1” all variables you defined will be accessed from step “2”

RUN BASH example
```json
[{
   "step_id": "1",
   "step_description":"Run bash command to list files in directory and store into file",
   "run_bash": "run_bash",      // Run Bash command
   "cmd": "ls -l > list_dir.txt"         // the body of command
}]
```

In this way we can create a very flexible scripts for processing hard changes for MongoDB

BE CAREFUL. the changes applied to database with this migrator will have no any ways to backward, so you need to create backups of DB as a DUMP to consist all DATA, VALIDATORS, INDEXES ….


Example of full PipeLine for 8 steps:

```json
[
 {
   "step_id": "1",
   "step_description":"Creating temporary collection car_tmp_lookup",
   "action": "aggregation",
   "collection": "car",
   "pipeline": [
    {
        '$unwind': {
            'path': '$owner',
            'preserveNullAndEmptyArrays': True
        }
    }, {
        '$addFields': {
            'owner.metadata.master_username': {
                '$arrayElemAt': [
                    '$owner.metadata.master_user_id', 0
                ]
            }
        }
    }, {
        '$project': {
            'owner.metadata.master_user_id': False
        }
    }, {
        '$group': {
            '_id': '$id',
            'id': {
                '$first': '$id'
            },
            'owner': {
                '$push': '$owner'
            }
        }
    }, {
        '$out': 'car_tmp_lookup'
    }
 ]}
,
 {
   "step_id": "2",
   "step_description":"Creating temporary collection car_tmp_done",
   "action": "aggregation",
   "collection": "car",
   "pipeline": [
    {
        '$lookup': {
            'from': 'car_tmp_lookup',
            'localField': 'id',
            'foreignField': 'id',
            'as': 'linked_car'
        }
    }, {
        '$addFields': {
            'owner': {
                '$arrayElemAt': [
                    '$linked_car.owner', 0
                ]
            }
        }
    },{
       '$project' :{
          'linked_car':False
       }
    }, {
        '$out': 'car_tmp_done'
    }
 ]},
  {
   "step_id": "3",
   "step_description":"Apply new validator => car_tmp_done",
   "action": "command",
   "command": "collMod",
   "command_body": "car_tmp_done",
   "args":{
      "validator": {'$jsonSchema': {'bsonType': .....}},
      "validationLevel":"strict"
   }
  },
  {
   "step_id": "4",
   "step_description":"Copy indexes from old collection",
   "action": "py_code",
   "code": "for name, index_info in mongo_client.car.index_information().items():\n    mongo_client.car_tmp_done.create_index(keys=index_info['key'], name=name)",
  },
  {
   "step_id": "5",
   "step_description":"Rename collection car => car_old",
   "action": "rename_collection",
   "from_name": "car",
   "to_name": "car_old"
  },
  {
   "step_id": "6",
   "step_description":"Rename collection car_tmp_done => car",
   "action": "rename_collection",
   "from_name": "car_tmp_done",
   "to_name": "car"
  },
  {
   "step_id": "7",
   "step_description":"Drop collection car_tmp_lookup",
   "action": "drop_collection",
   "name": "car_tmp_lookup"
  },
  {
   "step_id": "8",
   "step_description":"Drop collection car_old",
   "action": "drop_collection",
   "name": "car_old"
  }
]
```

------------------------
INSTALLING AND RUNNING

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

