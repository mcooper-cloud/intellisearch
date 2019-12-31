#!/bin/bash

export_env(){
    echo "[+] $(date) - Exporting 1 stage skeleton Global ENV"
    DATE_STRING=$(date | sed -e 's/ /_/g' | sed -e 's/:/_/g')
    export PHASE_START=$DATE_STRING
    echo "[+] $(date) PHASE_START: $PHASE_START"

    export STAGING_BUCKET_NAME="[YOUR BUCKET NAME HERE]"
    export PACKAGE_KEY="skill/function.zip"

    export LAMBDA_TEMPLATE_PATH="lambda/intellisearch_cf.json"
    export STACK_NAME="AlexaSkillStack"

}

export_env
