# -*- coding: utf-8 -*-

import datetime
currentTime = datetime.datetime.now()


if currentTime.hour < 12:
    time_greeting = 'Good morning,'
elif 12 <= currentTime.hour < 18:
    time_greeting = 'Good afternoon,'
else:
    time_greeting = 'Good evening,'

SKILL_TITLE = "e v three Lego Bot"
BOT_NAME = "e v three"

##
## global settings
##
DEFAULT_FORWARD_SPEED=70
DEFAULT_BACKWARD_SPEED=-70

'''
message structures

invokation = GREETINGS + WELCOME_MESSAGE

stop/cancel = AFFIRMATIONS + CANCEL_STOP_MESSAGE + SALUTATIONS

commands = AFFIRMATIONS + [specific message]

command response (Alexa listener) = AFFIRMATIONS + ACTION_QUESTIONS

command no response (Alexa listener) = NO_RESPONSE_MESSAGES

'''

##
## generic conversation modifiers
##
GREETINGS = [
    "Hello,",
    "Hi,",
    time_greeting,
    "Howdy,",
    "What's up?",
    "Hey!",
    "Cool breeze,",
    "Giddyup,"
]

SALUTATIONS = [
    "Goodbye",
    "See you later",
    "Take it easy",
    "Stay classy"
]

AFFIRMATIONS = [
    "OK,",
    "Sure,",
    "Gotcha,",
    "Got it,",
    "All right,",
    "Allrighty then,",
    "easy breezy, lemon squeezy,"
]

CONFIRMATIONS = [
    "OK,",
    "Done,",
    "All done,",
    "All set,",
    "Finished,",
    "All finished,",
    "Complete,"
]

ACTION_QUESTIONS = [
    "What would you like to do?",
    "What would you like to do next?",
    "What would you like to do now?",
    "What's next?",
    "Anything else you'd like to do?",
    "Can I do anything else for you?",
    "Will that be all?"
]

NO_RESPONSE_MESSAGES = [
    "I haven't received a response in a while.  I'm going to take a break.",
    "It's been quiet for a while.  I'm going to take a rest",
    "The bot's been quiet.  That's probably not good.",
    "It's been quiet for a while.  That's a typical symptom of technical difficulties"
]

ERROR_MESSAGES = [
    "I'm sorry, something went wrong!",
    "Oops, something went wrong",
    "Hmmm, something seems to be wrong",
    "Well, that didn't work",
    "I don't get it.  That should have worked",
    "Nope",
    "Nope.  Not today.",
    "Nope, that didn't work"
    "Wait.  Something's up.",
    "The bot might be on fire.  You should check",
    "Hmm, I think I just stepped in it.",
    "Nah, I'm good.",
    "I might be broken.",
    "It's hard to look away from a train wreck.",
    "That was a train wreck",
    "I'm pretending to be a tomato",
    "Well, if it were easy, then every one would do it.",
    "I am being attacked by a giant screaming rainbow! Oh, sorry, it was just technical difficulties",
]

RANDOM_MESSAGES = [
    "I'm really proud of you.",
    "Come to the dark side. We have cookies.",
    "I’m not weird, I’m gifted.",
    "I’m not random! I just have lots of thoughts.",
    "You sound like yourself today",
    "You sound extra clever today",
]

##
## SKILL LEVEL MESSAGES
##
WELCOME_MESSAGES = [
    "Connecting to {}.  What would you like to do?".format(BOT_NAME),
    "I'm looking for {}.  What would you like to do?".format(BOT_NAME),
    "Bingo bango wango tango.  What's the angle of your dangle'?",
    "{} is waiting for your command".format(BOT_NAME),
    "Connecting to {}. Go ahead and aske me something".format(BOT_NAME),
]

EXIT_SKILL_MESSAGE = "Closing e v three Intellisearch."
REPROMPT_MESSAGES = [
    "What would you like to do?",
    "What can I help you with?",
]
HELP_MESSAGE = "I can interact with {}.  You can ask me to move or turn the robot.  What would you like to do?".format(BOT_NAME)
FALLBACK_ANSWER = "Sorry. I can't help you with that. {}".format(HELP_MESSAGE)
CANCEL_STOP_MESSAGE = "I'll ask {} to stop".format(BOT_NAME)

#ERROR_MESSAGE = "I'm sorry, something went wrong!"
#NO_RESPONSE_MESSAGE = "I haven't received a response in a while.  I'm going to take a break."

##
## MOVE MESSAGES
##
MOVE_ROBOT_MESSAGE = "moving {} now."
AFTER_MOVE_ROBOT_MESSAGE = "I have moved the robot."

##
## MOVE CONSTANTS
##
FORWARD_SLOTS = [
    "forwards",
    "front",
    "forward",
    "ahead"
]

BACKWARD_SLOTS = [
    "backwards",
    "backward",
    "reverse",
    "back",
    "back up",
    "behind"
]

##
## grid position cardinal values
##

CARDINAL_POSITIONS = {}
CARDINAL_POSITIONS[0] = 'northwest'
CARDINAL_POSITIONS[1] = 'north'
CARDINAL_POSITIONS[2] = 'northeast'
CARDINAL_POSITIONS[3] = 'west'
CARDINAL_POSITIONS[4] = 'center'
CARDINAL_POSITIONS[5] = 'east'
CARDINAL_POSITIONS[6] = 'southwest'
CARDINAL_POSITIONS[7] = 'south'
CARDINAL_POSITIONS[8] = 'southeast'

NORTH_CARDINAL_VALUES = [
    "north",
    "true north",
    "top"
]

SOUTH_CARDINAL_VALUES = [
    "south",
    "true south",
    "bottom"
]

EAST_CARDINAL_VALUES = [
    "east",
    "true east",
    "right"
]

WEST_CARDINAL_VALUES = [
    "west",
    "true west",
    "left"
]

NORTHEAST_CARDINAL_VALUES = [
    "northeast",
    "top right",
    "upper right"
]

NORTHWEST_CARDINAL_VALUES = [
    "northwest",
    "top left",
    "upper left"
]

SOUTHEAST_CARDINAL_VALUES = [
    "southeast",
    "bottom right",
    "lower right"
]

SOUTHWEST_CARDINAL_VALUES = [
    "southwest",
    "bottom left",
    "lower left"
]

CENTER_CARDINAL_VALUES = [
    "center",
    "middle"
]

##
## TURN MESSAGES
##
TURN_ROBOT_MESSAGE = "Turning {} now."
AFTER_TURN_ROBOT_MESSAGE = "I have turned the robot."

##
## START SEARCH MESSAGES
##
START_SEARCH_MESSAGE = "I am starting a search."
AFTER_START_SEARCH_MESSAGE = "I have started a search."

##
## WALK PERIMETER MESSAGES
##
WALK_PERIMETER_MESSAGE = "I am starting perimeter walk."
AFTER_WALK_PERIMETER_MESSAGE = "I have started a perimeter walk."

##
## PAUSE MESSAGES
##
PAUSE_ROBOT_MESSAGE = "pausing now."
AFTER_PAUSE_ROBOT_MESSAGE = "I have paused the robot."

##
## KILLSWITCH MESSAGES
##
KILLSWITCH_MESSAGE = "I will engage the kill switch."
AFTER_KILLSWITCH_MESSAGE = "I have stopped the robot."

##
## SET GRID MESSAGES
##
SET_GRID_MESSAGE = "Setting grid {}."
AFTER_SET_GRID_MESSAGE = "I have set the grid."

