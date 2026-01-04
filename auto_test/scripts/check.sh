#!/bin/bash

function grn_msg () {
    echo -e "\033[32m$*\033[0m"
}

function red_msg () {
    echo -e "\033[31m$*\033[0m"
}

function check_ret () {
    local ret=${1}
    local msg=${2}

    if [ "${ret}" -eq 0 ]; then
        [ "${msg}" == "" ] || grn_msg "Passed: ${msg}"
    else
        [ "${msg}" == "" ] || red_msg "Failed: ${prefix}${msg}"
        exit ${ret}
    fi
}

function code_style_check() {
    PYTHONPATH=. python3 -m pylint .
}

code_style_check
check_ret $? "Code style check"
