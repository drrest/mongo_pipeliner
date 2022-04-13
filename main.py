"""

MongoDB One-side Migrator

  @Author: Igor Mykhailovskyi
  @Date: 10.04.2022

This program allow to manage pipelines used to migrate data of MongoDB

Example:
    You need to setup environment settings::
        MONGO_HOST = 0.0.0.0
        MONGO_PORT = 27017
        MONGO_USERNAME = admin
        MONGO_PASSWORD = password
        MONGO_DB = db1
        MONGO_AUTH = 1

        $ python3 main.py

Attributes:

    Running parameters:
        --list ( -l )  -   Show list of applied migrations

"""
import datetime
import sys
import subprocess

from os import listdir
from os.path import isfile, join


from logzero import logger as LOG
from prettytable import PrettyTable

from services.mongodb import mongo_client, uri
from settings.args import arguments
from settings.globals import mongo_migrations_folder

LOG.info(f"USE MONGO-URI: {uri}")

global_variables = {}

migrations_files = [f for f in listdir(mongo_migrations_folder)
                    if isfile(join(mongo_migrations_folder, f)) and f.endswith(".mgr")]

applied_migrations = {}

for each_file in migrations_files:
    get_applied_step_ids = mongo_client.migrations.find({"file": each_file})
    applied_migrations[each_file] = [_['step_id'] for _ in get_applied_step_ids]

if arguments.show_migrations:
    migration_table = PrettyTable(max_table_width=165, align="l")
    migration_table.field_names = ["Applied at",
                                   "Step description",
                                   "File",
                                   "Step ID",
                                   "Result"]
    migration_table.min_width = 16
    migration_table.align = "l"

    for each_migration_file in applied_migrations:
        applied_steps = list(mongo_client.migrations.find({"file": each_migration_file}))
        for applied_step in applied_steps:
            migration_table.add_row(
                [
                    applied_step['timestamp'].strftime('%d %b %y [%H:%M:%S]'),
                    applied_step['step_description'],
                    applied_step['file'],
                    applied_step['step_id'],
                    applied_step['result']
                ]
            )
    print(migration_table)
    sys.exit(0)

for migration_file in migrations_files:
    LOG.info(f"=========[ processing file: {migration_file} ]===========")

    script_entity = eval("".join(open(f"{mongo_migrations_folder}/{migration_file}", "r").readlines()))
    scenario = [script_entity] if not isinstance(script_entity, list) else script_entity

    for idx, scenario_step in enumerate(scenario, start=1):
        step_id = idx if 'step_id' not in scenario_step else scenario_step['step_id']
        LOG.info(f"-+-- ==> step {step_id}")

        if step_id not in applied_migrations[migration_file]:
            collection = scenario_step['collection'] if 'collection' in scenario_step else None
            mig_action = scenario_step['action']

            step_description = scenario_step['step_description'] if 'step_description' in scenario_step else ""
            depend_on = scenario_step['depend_on'] if 'depend_on' in scenario_step else None

            if depend_on and depend_on not in applied_migrations:
                LOG.error(f">>> file '{depend_on}' needs to be applied before migrate with '{migration_file}'")
                sys.exit(0)

            prepare_query = mongo_client[collection] if collection else None

            LOG.info(f"--+- action: '{mig_action}'")
            if mig_action == "aggregation":
                if 'pipeline' not in scenario_step:
                    LOG.error("Field 'pipeline' required in 'aggregation' step")
                    sys.exit(3)
                pipeline = scenario_step['pipeline']
                answer = list(prepare_query.aggregate(pipeline, allowDiskUse=True))
                result = {"result": "ok"}
                if step_description == "":
                    step_description = f"{mig_action.capitalize()} collection '{collection}'"

            elif mig_action == "update":
                if 'filter' not in scenario_step or 'update' not in scenario_step or 'args' not in scenario_step:
                    LOG.error("Fields 'filter', 'update', 'args' required in 'update' step")
                    sys.exit(3)
                filter_q = scenario_step['filter']
                update_q = scenario_step['update']
                args = scenario_step['args'] if 'args' in scenario_step else {}
                if step_description == "":
                    step_description = f"{mig_action.capitalize()} collection '{collection}' " \
                                       f"{({_: filter_q[_] for _ in filter_q})}"

                answer = prepare_query.update_many(filter_q, update_q, **args).raw_result
                result = {"result": "ok" if answer else "error"}

            elif mig_action == "command":
                if 'command' not in scenario_step or 'command_body' not in scenario_step:
                    LOG.error("Fields 'command', 'command_body' required in 'command' step")
                    sys.exit(3)
                command = scenario_step['command']
                command_body = scenario_step['command_body']
                kwargs = scenario_step['args'] if 'args' in scenario_step else {}

                answer = mongo_client.command(command, command_body, **kwargs)
                result = {"result": "ok" if answer else "error"}

            elif mig_action == "rename_collection":
                if 'from_name' not in scenario_step or 'to_name' not in scenario_step:
                    LOG.error("Fields 'from_name', 'to_name' required in 'rename_collection' step")
                    sys.exit(3)
                from_name = scenario_step['from_name']
                to_name = scenario_step['to_name']

                answer = mongo_client.get_collection(from_name).rename(to_name)
                result = {"result": "ok" if answer else "error"}

            elif mig_action == "drop_collection":
                if 'name' not in scenario_step:
                    LOG.error("Fields 'name' required in 'drop_collection' step")
                    sys.exit(3)
                collection_name = scenario_step['name']

                answer = mongo_client.drop_collection(collection_name)
                result = {"result": "ok" if answer else "error"}

            elif mig_action == "py_file":
                if 'file' not in scenario_step:
                    LOG.error("Fields 'file' required in 'py_file' step")
                    sys.exit(3)
                py_file = scenario_step['file']

                try:
                    with open(f"{mongo_migrations_folder}/{py_file}", "r") as py_code_file:
                        file_content = "".join(py_code_file.readlines())
                        exec(f"""{file_content}""")
                        answer = True
                        result = {"result": "ok" if answer else "error"}
                except Exception as e:
                    LOG.error(e)
                    sys.exit(1)

            elif mig_action == "py_code":
                if 'code' not in scenario_step:
                    LOG.error("Field 'code' required in 'py_code' step")
                    sys.exit(4)
                py_code = scenario_step['code']

                try:
                    exec(f"""{py_code}""")
                    answer = True
                    result = {"result": "ok" if answer else "error"}
                except Exception as e:
                    LOG.error(e)
                    sys.exit(1)

            elif mig_action == "run_bash":
                if 'cmd' not in scenario_step:
                    LOG.error("Field 'cmd' required in 'run' step")
                    sys.exit(4)

                cmd = scenario_step['cmd']

                process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
                answer, error = process.communicate()
                result = {"result": "ok" if not error else "error"}
                if error:
                    result['error'] = error
                else:
                    result['answer'] = answer

            else:
                text_error = f"---+ type '{mig_action}' is not available. " \
                             f"Please check step_id '{step_id}' of '{migration_file}' ..."
                LOG.error(text_error)
                sys.exit(2)

            if result['result'] == "ok":
                LOG.info(f"---! step {step_id} complete")

                mongo_client.migrations.insert_one({"file": migration_file,
                                                    "timestamp": datetime.datetime.now(),
                                                    "result": result,
                                                    "answer": answer,
                                                    "step_id": step_id,
                                                    "step_description": step_description})
        else:
            LOG.warning(f"x--- STEP '{step_id}' has been processed early ")

LOG.info("Migration complete")
