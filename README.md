
# Project Name: 

EV3 IntelliSearch

# Project Objective: 

Alexa assisted search and rescue with Lego EV3

## Features:

### Invokation

Say "Alexa, open lego bot"

### Move robot

Say "Move forward 10 rotations" or "Move backward 20 rotations"

This will cause the robot to move forward or backward the specified number of motor rotations

### Turn robot

Say "Turn left 70 degrees" or "Turn right 90 degrees"

This will cause the robot to turn the specified direction for the specified number of degrees.  This function uses the Gyro Sensor to determine how far the bot has traveled in degrees.  This function can be sensitive to bumpy surfaces, as the gyro readings become less accurate as the plane of travel changes.


### Intellisearch

Say "Start search"

This will cause the robot to begin moving in a spiral pattern, while opening the Color Sensor for reading.  Once the color sensor reads the color green (default) the robot will stop and announce that the subject has been found.


### Walk perimiter

Say "Set grid width 5"

This will set the width of the grid to 10 feet

Say "Set grid height 12"

This will set the height of the grid to 12 feet

Say "Set grid position center"

This will set the robot's position in the grid to the center position.

Say "Walk perimeter"

This will cause the robot to traverse all of the nodes in the grid, while ensuring that all perimeter grid edges have been traversed.

#### About the grid

    To aid in determining best possible search routes throughtout
    the defined grid, edges are assigned letters and given a
    source and destination node number.  Source nodes will be the
    north or western most node in the pair, and destination nodes
    will be the south or eastern most node in the pair.  Additionally,
    each edge will be assigned a heading value that corolates to the
    direction from the highest number node (the most north westerly)
    to the lowest number node (the most south easterly) in the pair.

        0                   1                   2       North
        -------- a ------------------ b --------
        | | ->              | | ->            | |       ^
        | V                 | V               V |       |
        |                   |                   |

        c                   d                   e

        |                   |                   |
        |                   |                   |
        |                   |4                  |
       3 ------- f --------- -------- g --------- 5
        | | ->              | | ->            | |
        | V                 | V               V |
        |                   |                   |

        h                   i                   j

        |                   |                   |
        |                   |                   |       |
        | ->                | ->                |       V
        -------- k ------------------ l --------
        6                   7                   8       South


    In this way, based upon the node that the bot is positioned at,
    along with the bot's current heading, the bot can then dynamically
    calculate both path and heading to all other nodes in the graph.

Next, some assumptions about heading:

    - bot assumes that if starting position is
      true north/south/east/west quadrant, that the bot
      heading is facing directly toward the center
      of the search grid.  That is, if the bot is positoined at
      true west, it assumes a heading of east, and if the bot is
      positioned at true east, it assumes a heading of west

    - bot asumes that if starting position is 
      one of the north east/west or south east/west quadrants,
      that the bot heading is the opposite of the major heading.
      For example if quadrant is set to north east, the bot 
      assumes a heading of true south, and if the quadrant is
      set to south east, the bot assumes a heading of true north

    - if the quadrant is set to 0 (center of the grid), the bot
      assumes a heading of true north

    - default position and heading assumptions are: 0,0 (center of grid, heading north)


Cardinal positions relative to the grid, are assigned a number
        
    0 = center of the grid (default)
    1 = north west quadrant
    2 = north east quadrant
    3 = south east quadrant
    4 = south west quadrant
    5 = true north (half way between 0 and 2)
    6 = true east (half way between 2 and 8)
    7 = true south (half way between 6 and 8)
    8 = true west (half way between 0 and 6)


Cardinal headings are also assigned a number

    0 = true north
    1 = true east
    2 = true south
    3 = true west

### Killswitch

Say "Abort"

This will cause the robot to stop all motors

## Kaveats and error conditions

    - when the batteries get low, the gyro sensor will begin to fail.  This will cause a turn robot operation to continue for some time ... sometimes indefinitely. ([Errno 6] No such device or address)
    - Alexa does not seem to handle stuttering well


# Setup

## How to Setup EV3:

- download ev3dev operating system and flash to micro SD card
- boot EV3 w/ SD card
- on the EV3 enable wifi and attach to wifi network
- on EV3 enable bluetooth
- Initianlize blue tooth connection by running mission-01.py on the EV3 device

## How to Setup bluetooth connection w/ Alexa

- from the Alexa app on your phone 
    --> left dropdown 'Settings' 
    --> Device Settings 
    --> select the target echo device 
    --> Blootooth Devices 
    --> Pair a new device 
    --> Select the gadget ID (output by mission-01.py)

## Create your Alexa skill

Follow this tutorial for base instructions: https://www.hackster.io/alexagadgets/lego-mindstorms-voice-challenge-mission-1-f31925

## Then what?

After you've created your Alexa skill, and configured your LEGO EV3 brick:

- Push ev3/main.py and ev3/main.ini (and run main.py).  The easist way to do this is to configure wifi on your EV3 brick (see: https://www.ev3dev.org/docs/networking/).  However, you can also setup SSH connections via USB or Bluetooth tethering.

- Push the lambda/function.py and lambda/data.py to S3 where Lambda can pick up the fuction code.
    - There is a cloudformation template (lambda/intellisearch_cf.json) that can be used to deploy a full working lambda stack.
    - Additionally, have a look at pipeline/stage_1_prebuild.yml for an example of how to deploy this dynamically via AWS CodeBuild

Once you have main.py running on the EV3 brick, and the lambda function code hosted in AWS, return to your Alexa skill and configure the endpoint to trigger the AWS Lambda function by providing the Lambda ARN to the Alexa skill.

