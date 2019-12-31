import logging.handlers 
import requests 
import uuid 
import random
 
from ask_sdk_core.skill_builder import SkillBuilder 
from ask_sdk_core.utils import is_request_type, is_intent_name 
from ask_sdk_core.handler_input import HandlerInput 
from ask_sdk_core.serialize import DefaultSerializer 
 
from ask_sdk_model import IntentRequest 
from ask_sdk_model.ui import PlayBehavior 
 
from ask_sdk_model.interfaces.custom_interface_controller import ( 
    StartEventHandlerDirective, EventFilter, 
    Expiration, FilterMatchAction, 
    StopEventHandlerDirective, SendDirectiveDirective, 
    Header, Endpoint, 
    EventsReceivedRequest, ExpiredRequest 
) 

import data

logger = logging.getLogger() 
logger.setLevel(logging.INFO) 
serializer = DefaultSerializer() 
skill_builder = SkillBuilder() 


############################################################################## 
############################################################################## 
## 
## CREATE TOKEN
##
##      Used to identify responses from EV3 brick
## 
############################################################################## 
############################################################################## 


def create_token():
    token = str(uuid.uuid4())
    logger.info("== creating session token %s ==", token)
    return token


############################################################################## 
############################################################################## 
## 
## CUSTOM EVENT HANDLER
##
##      handle custom event sent back from the EV3
## 
############################################################################## 
############################################################################## 


@skill_builder.request_handler(can_handle_func=is_request_type("CustomInterfaceController.EventsReceived"))
def custom_interface_event_handler(handler_input: HandlerInput):
    logger.info("== Received Custom Event ==")

    request = handler_input.request_envelope.request
    session_attr = handler_input.attributes_manager.session_attributes
    response_builder = handler_input.response_builder

    ##
    ## Validate event handler token
    ##
    logger.info("== reading session token %s ==", session_attr['token'])
    logger.info("== reading request token %s ==", request.token)

    if session_attr['token'] != request.token:
        logger.info("== EventHandler token doesn't match. Ignoring this event. ==")

        return response_builder.response

    custom_event = request.events[0]
    payload = custom_event.payload
    namespace = custom_event.header.namespace
    name = custom_event.header.name

    ## 
    ## this is probably the wrong place to start interacting with the
    ## user ... going to use this for cloud status updates only
    ##
    if namespace == 'Custom.EV3SearchGadget':

        if name == 'EV3ResponseAfterLaunch':
            ##
            ## On receipt of 'Custom.EV3SearchGadget.EV3Response' event, speak the report
            ##
            logger.info("== EV3 responded after launch: %s ==", payload['report'])

        elif name == 'EV3ResponseAfterMove':
            ##
            ## On receipt of 'Custom.EV3SearchGadget.EV3Response' event, speak the report
            ##
            logger.info("== EV3 responded after move: %s ==", payload['report'])


            confirmation = random.choice(data.CONFIRMATIONS)
            message = data.AFTER_MOVE_ROBOT_MESSAGE
            action_question = random.choice(data.ACTION_QUESTIONS)

            msg = ' '.join([confirmation, message, action_question])

            response_builder.speak(msg).set_should_end_session(False) 

 

        elif name == 'EV3ResponseAfterTurn':
            ##
            ## On receipt of 'Custom.EV3SearchGadget.EV3Response' event, speak the report
            ##
            logger.info("== EV3 responded after turn: %s ==", payload['report'])

            confirmation = random.choice(data.CONFIRMATIONS)
            message = data.AFTER_TURN_ROBOT_MESSAGE
            action_question = random.choice(data.ACTION_QUESTIONS)

            msg = ' '.join([confirmation, message, action_question])

            response_builder.speak(msg).set_should_end_session(False)

        elif name == 'EV3ResponseAfterStartSearch':
            ##
            ## On receipt of 'Custom.EV3SearchGadget.EV3Response' event, speak the report
            ##
            logger.info("== EV3 responded after start search: %s ==", payload['report'])

            confirmation = random.choice(data.CONFIRMATIONS)
            message = data.AFTER_START_SEARCH_MESSAGE
            action_question = random.choice(data.ACTION_QUESTIONS)

            msg = ' '.join([confirmation, message, action_question])

            response_builder.speak(msg).set_should_end_session(False)

        elif name == 'EV3ResponseAfterWalkPerimeter':
            ##
            ## On receipt of 'Custom.EV3SearchGadget.EV3Response' event, speak the report
            ##
            logger.info("== EV3 responded after walk perimeter: %s ==", payload['report'])

            confirmation = random.choice(data.CONFIRMATIONS)
            message = data.AFTER_WALK_PERIMETER_MESSAGE
            action_question = random.choice(data.ACTION_QUESTIONS)

            msg = ' '.join([confirmation, message, action_question])

            response_builder.speak(msg).set_should_end_session(False)
 
        elif name == 'EV3ResponseAfterPause':
            ##
            ## On receipt of 'Custom.EV3SearchGadget.EV3Response' event, speak the report
            ##
            logger.info("== EV3 responded after pause: %s ==", payload['report'])

            confirmation = random.choice(data.CONFIRMATIONS)
            message = data.AFTER_PAUSE_ROBOT_MESSAGE
            action_question = random.choice(data.ACTION_QUESTIONS)

            msg = ' '.join([confirmation, message, action_question])

            response_builder.speak(msg).set_should_end_session(False)

        elif name == 'EV3ResponseAfterKillSwitch':
            ##
            ## On receipt of 'Custom.EV3SearchGadget.EV3Response' event, speak the report
            ##
            logger.info("== EV3 responded after killswitch: %s ==", payload['report'])

            confirmation = random.choice(data.CONFIRMATIONS)
            message = data.AFTER_KILLSWITCH_MESSAGE
            action_question = random.choice(data.ACTION_QUESTIONS)

            msg = ' '.join([confirmation, message, action_question])

            response_builder.speak(msg).set_should_end_session(False)

        elif name == 'EV3ResponseAfterSetGrid':
            ##
            ## On receipt of 'Custom.EV3SearchGadget.EV3Response' event, speak the report
            ##
            logger.info("== EV3 responded after set grid: %s ==", payload['report'])

            confirmation = random.choice(data.CONFIRMATIONS)
            message = data.AFTER_SET_GRID_MESSAGE.format('')
            action_question = random.choice(data.ACTION_QUESTIONS)

            msg = ' '.join([confirmation, message, action_question])

            response_builder.speak(msg).set_should_end_session(False) 

    return response_builder.response


############################################################################## 
############################################################################## 
## 
## LAUNCH: starting point for all invocations
## 
############################################################################## 
############################################################################## 
 
 
@skill_builder.request_handler(can_handle_func=is_request_type("LaunchRequest")) 
def launch_request_handler(handler_input: HandlerInput): 
    logger.info("== Launch Intent ==") 
 
    response_builder = handler_input.response_builder 
 
    system = handler_input.request_envelope.context.system 
    api_access_token = system.api_access_token 
    api_endpoint = system.api_endpoint 
 
    ##
    ## Get connected gadget endpoint ID.
    ##
    alexa_message = 'No gadgets found. Please try again after connecting your gadget.'
    endpoints = get_connected_endpoints(api_endpoint, api_access_token) 
    logger.debug("== Checking endpoint.. ==") 
    if not endpoints: 
        logger.debug("== No connected gadget endpoints available. ==") 
        return (response_builder 
                .speak(alexa_message) 
                .set_should_end_session(True) 
                .response) 
 
    endpoint_id = endpoints[0]['endpointId'] 

    ## 
    ## Store endpoint ID for using it to send custom directives later. 
    ##
    logger.debug("== Received endpoints. Storing Endpoint Id: %s ==", endpoint_id) 
    session_attr = handler_input.attributes_manager.session_attributes 
    session_attr['endpointId'] = endpoint_id 
 
    ##
    ## invokation message = GREETINGS + WELCOME_MESSAGE
    ##
    greeting = random.choice(data.GREETINGS)
    welcome_msg = random.choice(data.WELCOME_MESSAGES)

    w_msg = ' '.join([greeting, welcome_msg])

    reprompt_msg = random.choice(data.REPROMPT_MESSAGES)

    session_attr['token'] = create_token()

    response_builder = handler_input.response_builder

    payload = {
        'intent' : 'launch',
    }
 
    ##
    ## Send the deirective 
    ##
    no_response_msg = random.choice(data.NO_RESPONSE_MESSAGES)

    return (response_builder 
            .speak(w_msg)
            .ask(reprompt_msg)
            .add_directive(build_ev3_directive(endpoint_id, payload))
            .add_directive(build_start_event_handler_directive(session_attr['token'], 90000,
                                                               'Custom.EV3SearchGadget', 'EV3ResponseAfterLaunch',
                                                               FilterMatchAction.SEND_AND_TERMINATE,
                                                               {'data': no_response_msg}))
            .response) 


############################################################################## 
############################################################################## 
## 
## MOVE robot
## 
############################################################################## 
############################################################################## 
 
 
@skill_builder.request_handler(can_handle_func=is_intent_name("MoveRobotIntent")) 
def move_robot_intent_handler(handler_input: HandlerInput): 
    logger.info("== MoveRobotIntent received ==") 
 
    ##
    ## Retrieve the stored gadget endpoint ID from the SessionAttributes. 
    ##
    session_attr = handler_input.attributes_manager.session_attributes 
    endpoint_id = session_attr['endpointId'] 

    session_attr['token'] = create_token()

    response_builder = handler_input.response_builder 
 
    ##
    ## get slots
    ##

    slots=handler_input.request_envelope.request.intent.slots
    
    ##
    ## list of list of comparators
    ##
    loloco = {
        'forward_slots' : data.FORWARD_SLOTS,
        'backward_slots' : data.BACKWARD_SLOTS
    }

    ##
    ## build the payload
    ##
    payload = {
        'intent' : 'move_robot',
        'slots' : slots,
        'loloco' : loloco
    }
 
    if 'BowStearnDirection' in slots:
        direction = None
        if slots['BowStearnDirection'].value in data.FORWARD_SLOTS:
            direction = 'forward'
        else:
            direction = 'backward'

    affirmation = random.choice(data.AFFIRMATIONS)
    message = data.MOVE_ROBOT_MESSAGE.format(direction)

    msg = ' '.join([affirmation, message])

    no_response_msg = random.choice(data.NO_RESPONSE_MESSAGES)

    return (response_builder 
            .speak(msg)
            .add_directive(build_ev3_directive(endpoint_id, payload))
            .add_directive(build_start_event_handler_directive(session_attr['token'], 90000,
                                                               'Custom.EV3SearchGadget', 'EV3ResponseAfterMove',
                                                               FilterMatchAction.SEND_AND_TERMINATE,
                                                               {'data': no_response_msg}))
            .response)

 
############################################################################## 
############################################################################## 
## 
## TURN robot
## 
############################################################################## 
############################################################################## 


@skill_builder.request_handler(can_handle_func=is_intent_name("TurnRobotIntent")) 
def turn_robot_intent_handler(handler_input: HandlerInput): 
    logger.info("== TurnRobotIntent received ==") 
 
    ##
    ## Retrieve the stored gadget endpoint ID from the SessionAttributes. 
    ##
    session_attr = handler_input.attributes_manager.session_attributes 
    endpoint_id = session_attr['endpointId'] 
 
    session_attr['token'] = create_token()

    response_builder = handler_input.response_builder 
 
    ##
    ## get slots
    ##
    slots=handler_input.request_envelope.request.intent.slots

    ##
    ## build payload
    ##
    payload = {
        'intent' : 'turn_robot',
        'slots' : slots
    }

    if 'PortStarboardDirection' in slots:
        direction = None
        if slots['PortStarboardDirection'].value == 'right':
            direction = 'right'
        else:
            direction = 'left'

    duration = ''
    if 'PortStarboardDuration' in slots:
        duration = slots['PortStarboardDuration'].value


    m = '{} {} degrees'.format(direction, duration) 
    affirmation = random.choice(data.AFFIRMATIONS)
    message = data.TURN_ROBOT_MESSAGE.format(m)

    msg = ' '.join([affirmation, message])

    no_response_msg = random.choice(data.NO_RESPONSE_MESSAGES)

    return (response_builder 
            .speak(msg)
            .add_directive(build_ev3_directive(endpoint_id, payload))
            .add_directive(build_start_event_handler_directive(session_attr['token'], 90000,
                                                               'Custom.EV3SearchGadget', 'EV3ResponseAfterTurn',
                                                               FilterMatchAction.SEND_AND_TERMINATE,
                                                               {'data': no_response_msg}))
            .response)


############################################################################## 
############################################################################## 
## 
## start search
## 
############################################################################## 
############################################################################## 
 
 
@skill_builder.request_handler(can_handle_func=is_intent_name("StartSearchIntent")) 
def start_search_intent_handler(handler_input: HandlerInput): 
    logger.info("== StartSearchIntent received ==") 
 
    ##
    ## Retrieve the stored gadget endpoint ID from the SessionAttributes. 
    ##
    session_attr = handler_input.attributes_manager.session_attributes 
    endpoint_id = session_attr['endpointId'] 
 
    session_attr['token'] = create_token()

    response_builder = handler_input.response_builder 
 
    ##
    ## build payload
    ##
    payload = {
        'intent' : 'start_search'
    }


    affirmation = random.choice(data.AFFIRMATIONS)
    message = data.START_SEARCH_MESSAGE

    msg = ' '.join([affirmation, message])

    no_response_msg = random.choice(data.NO_RESPONSE_MESSAGES)

    return (response_builder 
            .speak(msg)
            .add_directive(build_ev3_directive(endpoint_id, payload))
            .add_directive(build_start_event_handler_directive(session_attr['token'], 90000,
                                                               'Custom.EV3SearchGadget', 'EV3ResponseAfterStartSearch',
                                                               FilterMatchAction.SEND_AND_TERMINATE,
                                                               {'data': no_response_msg}))
            .response)

############################################################################## 
############################################################################## 
## 
## start search
## 
############################################################################## 
############################################################################## 
 
 
@skill_builder.request_handler(can_handle_func=is_intent_name("WalkPerimeterIntent")) 
def walk_perimeter_intent_handler(handler_input: HandlerInput): 
    logger.info("== WalkPerimeterIntent received ==") 
 
    ##
    ## Retrieve the stored gadget endpoint ID from the SessionAttributes. 
    ##
    session_attr = handler_input.attributes_manager.session_attributes 
    endpoint_id = session_attr['endpointId'] 
 
    session_attr['token'] = create_token()

    response_builder = handler_input.response_builder 
 
    ##
    ## build payload
    ##
    payload = {
        'intent' : 'walk_perimeter'
    }

    affirmation = random.choice(data.AFFIRMATIONS)
    message = data.WALK_PERIMETER_MESSAGE

    msg = ' '.join([affirmation, message])

    no_response_msg = random.choice(data.NO_RESPONSE_MESSAGES)

    return (response_builder 
            .speak(msg)
            .add_directive(build_ev3_directive(endpoint_id, payload))
            .add_directive(build_start_event_handler_directive(session_attr['token'], 90000,
                                                               'Custom.EV3SearchGadget', 'EV3ResponseAfterWalkPerimeter',
                                                               FilterMatchAction.SEND_AND_TERMINATE,
                                                               {'data': no_response_msg}))
            .response)


############################################################################## 
############################################################################## 
## 
## PAUSE robot
## 
############################################################################## 
############################################################################## 
 
 
@skill_builder.request_handler(can_handle_func=is_intent_name("PauseRobotIntent")) 
def pause_robot_intent_handler(handler_input: HandlerInput): 
    logger.info("== PauseRobotIntent received ==") 
 
    ##
    ## Retrieve the stored gadget endpoint ID from the SessionAttributes. 
    ##
    session_attr = handler_input.attributes_manager.session_attributes 
    endpoint_id = session_attr['endpointId'] 
 
    session_attr['token'] = create_token()

    response_builder = handler_input.response_builder 
 
    ##
    ## get slots
    ##
    slots=handler_input.request_envelope.request.intent.slots

    ##
    ## build payload
    ##
    payload = {
        'intent' : 'pause_robot',
        'slots' : slots
    }
 
    affirmation = random.choice(data.AFFIRMATIONS)
    message = data.PAUSE_ROBOT_MESSAGE

    msg = ' '.join([affirmation, message])

    no_response_msg = random.choice(data.NO_RESPONSE_MESSAGES)

    return (response_builder 
            .speak(msg)
            .add_directive(build_ev3_directive(endpoint_id, payload))
            .add_directive(build_start_event_handler_directive(session_attr['token'], 90000,
                                                               'Custom.EV3SearchGadget', 'EV3ResponseAfterPause',
                                                               FilterMatchAction.SEND_AND_TERMINATE,
                                                               {'data': no_response_msg}))
            .response)


############################################################################## 
############################################################################## 
## 
## KILLSWITCH
## 
############################################################################## 
############################################################################## 
 
 
@skill_builder.request_handler(can_handle_func=is_intent_name("KillSwitchIntent")) 
def killswitch_intent_handler(handler_input: HandlerInput): 
    logger.info("== KillSwitchIntent received ==") 
 
    ##
    ## Retrieve the stored gadget endpoint ID from the SessionAttributes. 
    ##
    session_attr = handler_input.attributes_manager.session_attributes 
    endpoint_id = session_attr['endpointId'] 
 
    session_attr['token'] = create_token()

    response_builder = handler_input.response_builder 
 
    ##
    ## get slots
    ##
    slots=handler_input.request_envelope.request.intent.slots

    ##
    ## build payload
    ##
    payload = {
        'intent' : 'killswitch',
        'slots' : slots
    }

    affirmation = random.choice(data.AFFIRMATIONS)
    message = data.KILLSWITCH_MESSAGE

    msg = ' '.join([affirmation, message])

    no_response_msg = random.choice(data.NO_RESPONSE_MESSAGES)

    return (response_builder 
            .speak(msg)
            .add_directive(build_ev3_directive(endpoint_id, payload))
            .add_directive(build_start_event_handler_directive(session_attr['token'], 90000,
                                                               'Custom.EV3SearchGadget', 'EV3ResponseAfterKillSwitch',
                                                               FilterMatchAction.SEND_AND_TERMINATE,
                                                               {'data': no_response_msg}))
            .response)


############################################################################## 
############################################################################## 
## 
## EXPIRED
## 
############################################################################## 
############################################################################## 
 
 
@skill_builder.request_handler(can_handle_func=is_request_type("CustomInterfaceController.Expired")) 
def custom_interface_expiration_handler(handler_input): 
    logger.info("== Custom Event Expiration Input ==") 
 
    request = handler_input.request_envelope.request 
    response_builder = handler_input.response_builder 
    session_attr = handler_input.attributes_manager.session_attributes 
    endpoint_id = session_attr['endpointId'] 

    payload = {
        'intent' : 'expired'
    }
 
    ##
    ## When the EventHandler expires end skill session.
    ##
    return (response_builder 
            .add_directive(build_ev3_directive(endpoint_id, payload)) 
            .speak(request.expiration_payload['data']) 
            .set_should_end_session(True) 
            .response)
 

############################################################################## 
############################################################################## 
## 
## STOP/CANCEL
## 
############################################################################## 
############################################################################## 
 
 
@skill_builder.request_handler(can_handle_func=lambda handler_input: 
                               is_intent_name("AMAZON.CancelIntent")(handler_input) or 
                               is_intent_name("AMAZON.StopIntent")(handler_input)) 
def stop_and_cancel_intent_handler(handler_input): 
    logger.info("== Received a Stop or a Cancel Intent.. ==") 
    session_attr = handler_input.attributes_manager.session_attributes 
    response_builder = handler_input.response_builder 
    endpoint_id = session_attr['endpointId'] 

    ## 
    ## When the user stops the skill, stop the EventHandler, 
    ##
    if 'token' in session_attr.keys():
        try:
            logger.debug("== Active session detected, sending stop EventHandlerDirective. ==") 
            response_builder.add_directive(StopEventHandlerDirective(session_attr['token'])) 
        except Exception as e:
            logger.error('== EXCEPTION: %s ==', e) 

    payload = {
        'intent' : 'stop_cancel'
    }

    affirmation = random.choice(data.AFFIRMATIONS)
    message = data.CANCEL_STOP_MESSAGE 

    msg = ' '.join([affirmation, message])

    return (response_builder 
            .speak(msg) 
            .add_directive(build_ev3_directive(endpoint_id, payload)) 
            .set_should_end_session(True)
            .response)

 
############################################################################## 
############################################################################## 
## 
## SESSION END
## 
############################################################################## 
############################################################################## 


@skill_builder.request_handler(can_handle_func=is_request_type("SessionEndedRequest")) 
def session_ended_request_handler(handler_input): 
    logger.info("== Session ended with reason: ==" + 
                handler_input.request_envelope.request.reason.to_str()) 
    return handler_input.response_builder.response 
 
 
############################################################################## 
############################################################################## 
## 
## ERROR HANDLER
## 
############################################################################## 
############################################################################## 
 
 
@skill_builder.exception_handler(can_handle_func=lambda i, e: True) 
def error_handler(handler_input, exception): 

    logger.info("==Error==") 
    logger.error(exception, exc_info=True) 
    msg = random.choice(data.ERROR_MESSAGES)

    return (handler_input.response_builder 
            .speak(msg).response) 
 
 
############################################################################## 
############################################################################## 
## 
## LOG REQUEST
## 
############################################################################## 
############################################################################## 
 
 
@skill_builder.global_request_interceptor() 
def log_request(handler_input): 
    ##
    ## fires before every request globally
    ## Log the request for debugging purposes. 
    ##
    logger.info("==Request==\r" + 
                str(serializer.serialize(handler_input.request_envelope))) 
 
 
############################################################################## 
############################################################################## 
## 
## LOG RESPONSE
## 
############################################################################## 
############################################################################## 
 
 
@skill_builder.global_response_interceptor() 
def log_response(handler_input, response): 
    ##
    ## fires after every request globally
    ## Log the response for debugging purposes. 
    ##
    logger.info("==Response==\r" + str(serializer.serialize(response))) 
    logger.info("==Session Attributes==\r" + 
                str(serializer.serialize(handler_input.attributes_manager.session_attributes))) 
 
 
############################################################################## 
############################################################################## 
## 
## GET ENDPOINT
## 
############################################################################## 
############################################################################## 
 
 
def get_connected_endpoints(api_endpoint, api_access_token): 

    logger.info("== get connected endpoints (inside function) ==")

    headers = { 
        'Content-Type': 'application/json', 
        'Authorization': 'Bearer {}'.format(api_access_token) 
    } 
 
    api_url = api_endpoint + "/v1/endpoints" 
    endpoints_response = requests.get(api_url, headers=headers) 
 
    if endpoints_response.status_code == requests.codes['ok']: 
        return endpoints_response.json()["endpoints"] 
 
 
############################################################################## 
############################################################################## 
## 
## EV3 DIRECTIVE
## 
############################################################################## 
############################################################################## 
 
 
def build_ev3_directive( endpoint_id, payload, 
                         namespace='Custom.EV3SearchGadget', 
                         name='Response'): 

    logger.info("== build_ev3_directive ==")

    return SendDirectiveDirective( 
        header=Header(namespace=namespace, name=name), 
        endpoint=Endpoint(endpoint_id=endpoint_id), 
        payload=payload
    )
 

############################################################################## 
############################################################################## 
## 
## START EVENT HANDLER
## 
############################################################################## 
############################################################################## 
 
 
def build_start_event_handler_directive( token, duration_ms, 
                                         namespace, name, 
                                         filter_match_action, 
                                         expiration_payload ): 

    logger.info("== build_start_event_handler_directive ==")


    return StartEventHandlerDirective( 
        token=token, 
        event_filter=EventFilter( 
            filter_expression={ 
                'and': [ 
                    {'==': [{'var': 'header.namespace'}, namespace]}, 
                    {'==': [{'var': 'header.name'}, name]} 
                ] 
            }, 
            filter_match_action=filter_match_action 
        ), 
        expiration=Expiration( 
            duration_in_milliseconds=duration_ms, 
            expiration_payload=expiration_payload)) 
 
 
############################################################################## 
############################################################################## 
## 
## STOP EVENT HANDLER
## 
############################################################################## 
############################################################################## 
 
 
def build_stop_event_handler_directive(token): 
    logger.info("== build_stop_event_handler_directive ==")
    return StopEventHandlerDirective(token=token) 
 
 
############################################################################## 
############################################################################## 
## 
## SET GRID HEIGHT/WIDTH
## 
############################################################################## 
############################################################################## 
 
 
@skill_builder.request_handler(can_handle_func=lambda handler_input: 
                               is_intent_name("SetGridHeightIntent")(handler_input) or 
                               is_intent_name("SetGridWidthIntent")(handler_input) or
                               is_intent_name("SetGridPositionIntent")(handler_input)) 
def set_grid_intent_handler(handler_input): 
    logger.info("== SetGrid[Height/Width/Position]Intent received ==") 
 
    ##
    ## Retrieve the stored gadget endpoint ID from the SessionAttributes. 
    ##
    session_attr = handler_input.attributes_manager.session_attributes 
    endpoint_id = session_attr['endpointId'] 

    session_attr['token'] = create_token()

    response_builder = handler_input.response_builder 
 
    ##
    ## get slots
    ##
    slots=handler_input.request_envelope.request.intent.slots

    ##
    ## build the payload
    ##
    payload = {
        'intent' : 'set_grid',
        'slots' : slots,
    }
 
    if 'GridWidth' in slots:
        m = 'width to {} feet'.format(slots['GridWidth'].value)

    if 'GridHeight' in slots:
        m = 'height to {} feet'.format(slots['GridHeight'].value)

    if 'GridPositionCardinal' in slots:

        position = None
        if slots['GridPositionCardinal'].value in data.NORTHWEST_CARDINAL_VALUES:
            position = 0
        elif slots['GridPositionCardinal'].value in data.NORTH_CARDINAL_VALUES:
            position = 1
        elif slots['GridPositionCardinal'].value in data.NORTHEAST_CARDINAL_VALUES:
            position = 2
        elif slots['GridPositionCardinal'].value in data.WEST_CARDINAL_VALUES:
            position = 3
        elif slots['GridPositionCardinal'].value in data.CENTER_CARDINAL_VALUES:
            position = 4
        elif slots['GridPositionCardinal'].value in data.EAST_CARDINAL_VALUES:
            position = 5
        elif slots['GridPositionCardinal'].value in data.SOUTHWEST_CARDINAL_VALUES:
            position = 6
        elif slots['GridPositionCardinal'].value in data.SOUTH_CARDINAL_VALUES:
            position = 7
        elif slots['GridPositionCardinal'].value in data.SOUTHEAST_CARDINAL_VALUES:
            position = 8

        if position is not None:
            payload['position'] = position

            m = 'cardinal position to {}'.format(data.CARDINAL_POSITIONS[position])

    affirmation = random.choice(data.AFFIRMATIONS)
    message = data.SET_GRID_MESSAGE.format(m) 

    msg = ' '.join([affirmation, message])

    no_response_msg = random.choice(data.NO_RESPONSE_MESSAGES)

    return (response_builder 
            .speak(msg)
            .add_directive(build_ev3_directive(endpoint_id, payload))
            .add_directive(build_start_event_handler_directive(session_attr['token'], 90000,
                                                               'Custom.EV3SearchGadget', 'EV3ResponseAfterSetGrid',
                                                               FilterMatchAction.SEND_AND_TERMINATE,
                                                               {'data': no_response_msg}))
            .response)


############################################################################## 
############################################################################## 
## 
## LAMBDA HANDLER
## 
############################################################################## 
############################################################################## 
 
lambda_handler = skill_builder.lambda_handler() 