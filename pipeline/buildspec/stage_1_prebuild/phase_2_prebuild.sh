#!/bin/bash

echo "Exit status $?"
echo "[+] $(date) - Entered STAGE 1 PREBUILD - phase 2 prebuild"

ENV_SH_PATH=$CODEBUILD_SRC_DIR/$ENV_PATH/$ENV_SH
source $ENV_SH_PATH

SKILL_PATH="skill_env"

PACKAGE="function.zip"

REQUIREMENTS_PATH="lambda/requirements.txt"
FUNCTION_PATH="lambda"
FUNCTION_EXE="function.py"
FUNCTION_DATA_CONF="data.py"
SKILL_ZIP_PATH="../../skill-code.zip"

mkdir $CODEBUILD_SRC_DIR/$SKILL_PATH
pip install -r $CODEBUILD_SRC_DIR/$REQUIREMENTS_PATH -t $CODEBUILD_SRC_DIR/$SKILL_PATH

echo '[+] Copying Lambda function into skill path'
cp $CODEBUILD_SRC_DIR/$FUNCTION_PATH/$FUNCTION_EXE $CODEBUILD_SRC_DIR/$SKILL_PATH

echo '[+] Copying data config into skill path'
cp $CODEBUILD_SRC_DIR/$FUNCTION_PATH/$FUNCTION_DATA_CONF $CODEBUILD_SRC_DIR/$SKILL_PATH

echo '[+] Running zip -r'

cd $CODEBUILD_SRC_DIR/$SKILL_PATH

zip -r $CODEBUILD_SRC_DIR/$FUNCTION_PATH/$PACKAGE ./
aws s3 cp $CODEBUILD_SRC_DIR/$FUNCTION_PATH/$PACKAGE s3://$STAGING_BUCKET_NAME/$PACKAGE_KEY