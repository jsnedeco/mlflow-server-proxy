# Copyright 2020 American Express Travel Related Services Company, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and limitations under
# the License.

"""
Return config on servers to start for mlflow-server-proxy

"""
import os
import shutil
import logging
from pathlib import Path
import subprocess
import shlex

logger = logging.getLogger(__name__)
logger.setLevel('INFO')


def setup_mlflow():
    """
    # NOTE: Make sure mlflow is installed

    :return: config for starting mlflow server
    """

    def _mlflow_command(port):
        executable = shutil.which('mlflow')
        if not executable:
            raise FileNotFoundError('Can not find mlflow executable')
        mlflow_dir = os.environ.get('MLFLOW_STORE')

        bash_profile = Path(os.environ['HOME']) / Path(".bashrc")
        if bash_profile.is_file():
            logger.info("Loading bash environment variables")
            command = shlex.split("env -i bash -c 'source ~/.bashrc && env'")
            proc = subprocess.Popen(command, stdout=subprocess.PIPE)
            for line in proc.stdout:
                line = line.decode("utf-8")
                (key, value) = line.split("=")
                os.environ[key] = value
            proc.communicate()

        if mlflow_dir:
            mlflow_db_dir = '{0}/mlflow/db'.format(mlflow_dir)

            if not os.path.exists(mlflow_db_dir):
                try:
                    os.makedirs(mlflow_db_dir)
                    logger.info("Created mlflow db directory {0}".format(mlflow_db_dir))
                except Exception as e:
                    logger.error(e)
                    raise e
            else:
                logger.info("Directory {0} already exists".format(mlflow_db_dir))



            # mlflow config
            host = '127.0.0.1'
            backend_store_uri = mlflow_db_dir
            default_artifact_root = mlflow_db_dir
            workers = '1'
        else:
            host = '127.0.0.1'
            backend_store_uri = os.environ.get('MLFLOW_BACKEND_URI')
            default_artifact_root = os.environ.get("MLFLOW_ARTIFACT_ROOT")
            workers = '1'

        cmd = ['mlflow', 'server', '--host', host, '--port', str(port),
                '--backend-store-uri', backend_store_uri,
                '--default-artifact-root', default_artifact_root,
                '--workers', workers]

        logger.error(os.environ)
        logger.error(" ".join(cmd))

        return ['mlflow', 'server', '--host', host, '--port', str(port),
                '--backend-store-uri', backend_store_uri,
                '--default-artifact-root', default_artifact_root,
                '--workers', workers]

    title = "MLFlow"
    return {
        'command': _mlflow_command,
        'absolute_url': False,
        'timeout': 10,
        'launcher_entry': {
            'title': title.strip(),
            'icon_path': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons',
                                      'mlflow.svg')
        }
    }
