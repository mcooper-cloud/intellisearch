#!/bin/bash

echo "Exit status $?"
echo "[+] $(date) - Entered STAGE 1 PREBUILD - phase 3 build"

ENV_SH_PATH=$CODEBUILD_SRC_DIR/$ENV_PATH/$ENV_SH
source $ENV_SH_PATH

validate_template(){
    echo "[+] $(date) - Validating CloudFormation template ... $STACK_NAME"
    aws cloudformation validate-template \
        --template-body 'file://'$CODEBUILD_SRC_DIR/$LAMBDA_TEMPLATE_PATH
}

deploy_stack(){
    echo "[+] $(date) - Deploying CloudFormation stack ... $STACK_NAME"
    aws cloudformation create-stack \
        --template-body 'file://'$CODEBUILD_SRC_DIR/$LAMBDA_TEMPLATE_PATH \
        --stack-name $STACK_NAME \
        --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND
}

wait_stack_create(){
    echo "[+] $(date) - Waiting for stack-create-complete ... $STACK_NAME"    
    aws cloudformation wait stack-create-complete \
        --stack-name $STACK_NAME
}


create_change_set(){
    CHANGE_SET_NAME=$(openssl rand -base64 32 | sed 's/[^a-zA-Z]//g')

    echo "[+] $(date) - Creating change set ... $STACK_NAME"

    aws cloudformation create-change-set \
        --stack-name $STACK_NAME \
        --template-body 'file://'$CODEBUILD_SRC_DIR/$LAMBDA_TEMPLATE_PATH \
        --change-set-name $CHANGE_SET_NAME \
        --capabilities CAPABILITY_NAMED_IAM

    echo "[+] $(date) - Waiting on change-set-create-complete ... $STACK_NAME"

    aws cloudformation wait change-set-create-complete \
        --stack-name $STACK_NAME \
        --change-set-name $CHANGE_SET_NAME

}

describe_change_set(){
    echo "[+] $(date) - Describing change set ... $STACK_NAME"

    aws cloudformation describe-change-set \
        --stack-name $STACK_NAME \
        --change-set-name $CHANGE_SET_NAME
}


update_stack(){
    echo "[+] $(date) - Executing CloudFormation change set $CHANGE_SET_NAME for stack $STACK_NAME"
    aws cloudformation execute-change-set \
        --change-set-name $CHANGE_SET_NAME \
        --stack-name $STACK_NAME

}

wait_stack_update(){
    echo "[+] $(date) - Waiting for stack-update-complete ..."    
    aws cloudformation wait stack-update-complete \
        --stack-name $STACK_NAME
}


describe_events(){
    echo "[+] $(date) - Describing stack events ... $STACK_NAME"    
    aws cloudformation describe-stack-events \
        --stack-name $STACK_NAME
}

validate_template

STATUS=$(aws cloudformation describe-stacks --stack-name $STACK_NAME)

if [ $? -eq 0 ]; then

    ##
    ## check to see if there's a change to the stack
    ##
    if ! create_change_set; then
        ##
        ## no change to stack ... just update the lambda code
        ##
        function_arn=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query "Stacks[0].Outputs[?OutputKey=='FunctionARN'].OutputValue" --output text)
        aws lambda update-function-code \
            --function-name $function_arn \
            --s3-bucket $STAGING_BUCKET_NAME \
            --s3-key $PACKAGE_KEY

    else

        describe_change_set
        update_stack
        if ! wait_stack_update; then
            echo "[-] $(date) - Stack update failed ... "
            describe_events
        else
            echo "[+] $(date) - Stack update complete ... "
            describe_events
            echo "[+] $(date) - SUCCESS! Stack update complete."
        fi
    fi
else

    deploy_stack
    wait_stack_create
    describe_events

fi
