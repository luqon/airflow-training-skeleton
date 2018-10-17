#!/bin/bash

# ./pybuilder-init.sh
# This will build the environment if necessary and keep it active.
# installs all the dependencies

# Parameters
BASEDIR=$(cd $(dirname "$0"); pwd)
VENV_ROOT="$BASEDIR/venv"
VENV_ACTIVATE="$BASEDIR/venv/bin/activate"
DEPENDENCIES="$BASEDIR/requirements.txt"
#DEV_DEPENDENCIES="$BASEDIR/requirements-dev.txt"
PIP_CONF="[global]\nindex-url=https://artifactory.tools.bol.com/artifactory/api/pypi/pip-bol/simple\nextra-index-url=https://pypi.python.org/simple/\ntrusted-host=artifactory.tools.bol.com"
PIP_CONF_LOCATION="$BASEDIR/venv/pip.conf"

# Make virtualenv
if [ ! -d "$VENV_ROOT" ]; then
    echo "------------------------------------------------------------------"
    echo "Setting up Virtualenv for this project"
    echo "------------------------------------------------------------------"
    virtualenv ${VENV_ROOT}
    echo ">> Setting pip configuration"
    printf ${PIP_CONF} > ${PIP_CONF_LOCATION}
    echo ">> Done setting pip configuration"

    echo ">> Activating Virtualenv"
    source ${VENV_ACTIVATE}

    echo ">> Installing dependencies and dev dependencies"
    pip install -r ${DEPENDENCIES}
    #pip install -r ${DEV_DEPENDENCIES}
    echo ">> Done installing dependencies and dev dependencies"
    echo "------------------------------------------------------------------"
    echo "Virtualenv is ready to be used for this project"
    echo "------------------------------------------------------------------"
else
    # Only activate virtualenv
    source ${VENV_ACTIVATE}
    echo "------------------------------------------------------------------"
    echo "Virtualenv is ready to be used for this project"
    echo "------------------------------------------------------------------"
fi
