#!/bin/bash

WORKDIR="/projects/lakala/lkl"
PYTHON="/opt/workon_home/lakala/bin/python"
MANAGE="manage_pro.py"

function safe_run()
{
    file="/tmp/$1.lock"

    (
        flock -xn -w 10 200 || exit 1
        cd ${WORKDIR};${PYTHON} $MANAGE  $*
    ) 200>${file}

}

source /root/.bash_profile
echo `date`
time safe_run $*
