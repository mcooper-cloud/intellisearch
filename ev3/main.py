#!/usr/bin/env python3 
 
import json 
import logging 
import sys 
import os
import trace 
import datetime
import time 
import uuid
import multiprocessing
import math

from agt import AlexaGadget 

##
## port B = left large motor
## port C = right large motor
##
from ev3dev2.motor import (
    LargeMotor, MoveSteering, MoveTank,
    OUTPUT_B, OUTPUT_C
)


##
## port 4 = color sensor
## port 3 = IR sensor
## port 2 = touch sensor
## port 1 = gyro sensor
##
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from ev3dev2.sensor.lego import ColorSensor, TouchSensor, GyroSensor, InfraredSensor

from ev3dev2.sound import Sound


logging.basicConfig(stream=sys.stdout, level=logging.INFO) 
logger = logging.getLogger(__name__) 


############################################################################## 
############################################################################## 
## 
## 
## 
############################################################################## 
############################################################################## 

 
class EV3SearchGadget(AlexaGadget): 
    """ 
    An Alexa Gadget that communicates w/ Lego EV3
    """  
 
    def __init__(self): 
        super().__init__() 
 
        ##
        ## EV3 motors and sensors
        ##
        self.tank_pair = MoveTank(OUTPUT_B, OUTPUT_C)

        ##
        ## Setup a separate thread for server-like operations 
        ##

        self.proc_manager = multiprocessing.Manager().dict()
        self.proc_manager['search'] = False
        self.proc_manager['blocking'] = False
        self.proc_manager['subject_found'] = False
        self.proc_manager['motor_processes'] = []

        self.data = {}

        ##
        ## default color to search for == green
        ##
        self.data['default_color'] = 3

        self.data['inches_per_rotation'] = 3.75
        self.data['default_bowstearn_speed'] = 70
        self.data['default_portstarboard_speed'] = 50
        self.data['default_portstarboard_angle'] = 90
        self.data['default_portstarboard_direction'] = 'right'

        self.data['instruction_id_list'] = []
        self.data['instruction_data'] = {}

        self.data['coordinate_data'] = {}

        ##
        ## grid size to assist in intelligent search (in feet)
        ##
        ##      default: 10ft X 10ft
        ##
        self.data['coordinate_data']['grid_width'] = 10
        self.data['coordinate_data']['grid_height'] = 10

        '''
        starting cardinal position relative to the grid
        
            0 = center of the grid (default)
            1 = north west quadrant
            2 = north east quadrant
            3 = south east quadrant
            4 = south west quadrant
            5 = true north (half way between 0 and 2)
            6 = true east (half way between 2 and 8)
            7 = true south (half way between 6 and 8)
            8 = true west (half way between 0 and 6)
        
        '''
        self.data['coordinate_data']['starting_grid_position'] = 4
        self.data['coordinate_data']['current_grid_position'] = None

        '''
        headings

            0 = true north
            1 = true east
            2 = true south
            3 = true west
        '''

        self.data['coordinate_data']['heading_list'] = {
            0 : 'north',
            1 : 'east',
            2 : 'south',
            3 : 'west'
        }

        '''
        Assumptions about heading:

            - bot assumes that if starting position is
              true north/south/east/west quadrant, that the bot
              heading is facing directly toward the center
              of the search grid

            - bot asumes that if starting position is 
              one of the north east/west or south east/west quadrants,
              that the bot heading is the opposite of the major heading.
              For example if quadrant is set to north east, the bot 
              assumes a heading of true south, and if the quadrant is
              set to south east, the bot assumes a heading of true north

            - if the quadrant is set to 0 (center of the grid), the bot
              assumes a heading of true north

            - default: 0 (center of grid)

        '''

        self.data['coordinate_data']['heading_compliments'] = {}
        self.data['coordinate_data']['heading_compliments'][0] = 2
        self.data['coordinate_data']['heading_compliments'][1] = 3
        self.data['coordinate_data']['heading_compliments'][2] = 0
        self.data['coordinate_data']['heading_compliments'][3] = 1

        ##
        ## agnles to get from one heading to another
        ##   if my heading is n, then 
        ##      go heading_angles[n][x] to get to 
        ##      heading x
        ##
        self.data['coordinate_data']['heading_angles'] = {}

        ##
        ## pointing north
        ##
        self.data['coordinate_data']['heading_angles'][0] = {
            1 : 90, # east, right turn
            2 : 180, # south, behind me
            3 : -90 # west, left turn
        }

        ##
        ## pointing east
        ##
        self.data['coordinate_data']['heading_angles'][1] = {
            0 : -90, # north, left turn
            2 : 90, # south, right turn
            3 : 180 # west, behind me
        }

        ##
        ## pointing south
        ##
        self.data['coordinate_data']['heading_angles'][2] = {
            0 : 180, # north, behind me
            1 : -90, # east, left turn
            3 : 90 # west, right turn
        }

        ##
        ## pointing west
        ##
        self.data['coordinate_data']['heading_angles'][3] = {
            0 : 90, # north, right turn
            1 : 180, # east, behind me
            2 : -90 # south, left turn
        }

        ##
        ## default heading = North
        ##
        self.data['coordinate_data']['heading'] = 0

        '''
        edges (to assist in future graph theory)

        To aid in determining best possible search routes throughtout
        the defined grid, edges will be assigned letters and given a
        source and destination node number.  Source nodes will be the
        north or western most node in the pair, and destination nodes
        will be the south or eastern most node in the pair

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

            a = 0 to 1
            b = 1 to 2
            c = 0 to 3
            d = 1 to 4
            e = 2 to 5
            f = 3 to 4
            g = 4 to 5
            h = 3 to 6
            i = 4 to 7
            j = 5 to 8
            k = 6 to 7
            l = 7 to 8
        '''
    
        self.data['coordinate_data']['quadrant_list'] = {
            0 : 'northwest',
            1 : 'north',
            2 : 'northeast',
            3 : 'west',
            4 : 'center',
            5 : 'east',
            6 : 'southwest',
            7 : 'south',
            8 : 'southeast',
        }

        ##
        ## nodes
        ##
        self.data['coordinate_data']['nodes'] = {}

        self.data['coordinate_data']['nodes'][0] = {
            'edges' : ['a', 'c']
        }
        self.data['coordinate_data']['nodes'][1] = {
            'edges' : ['a', 'b', 'd']
        }
        self.data['coordinate_data']['nodes'][2] = {
            'edges' : ['b', 'e']
        }
        self.data['coordinate_data']['nodes'][3] = {
            'edges' : ['c', 'f', 'h']
        }
        self.data['coordinate_data']['nodes'][4] = {
            'edges' : ['d', 'g', 'i', 'f']
        }
        self.data['coordinate_data']['nodes'][5] = {
            'edges' : ['e', 'g', 'j']
        }
        self.data['coordinate_data']['nodes'][6] = {
            'edges' : ['h', 'k']
        }
        self.data['coordinate_data']['nodes'][7] = {
            'edges' : ['k', 'i', 'l']
        }
        self.data['coordinate_data']['nodes'][8] = {
            'edges' : ['j', 'l']
        }

        ##
        ## edges
        ##
        self.data['coordinate_data']['edges'] = {}

        self.data['coordinate_data']['edges']['a'] = {
            'source_node' : 0,
            'destination_node' : 1,
            'heading' : 1,
            'description' : 'northwest to true north'
        }

        self.data['coordinate_data']['edges']['b'] = {
            'source_node' : 1,
            'destination_node' : 2,
            'heading' : 1,
            'description' : 'true north to northeast'
        }

        self.data['coordinate_data']['edges']['c'] = {
            'source_node' : 0,
            'destination_node' : 3,
            'heading' : 2,
            'description' : 'northwest to true west'
        }

        self.data['coordinate_data']['edges']['d'] = {
            'source_node' : 1,
            'destination_node' : 4,
            'heading' : 2,
            'description' : 'true north to center'
        }

        self.data['coordinate_data']['edges']['e'] = {
            'source_node' : 2,
            'destination_node' : 5,
            'heading' : 2,
            'description' : 'northeast to true east'
        }

        self.data['coordinate_data']['edges']['f'] = {
            'source_node' : 3,
            'destination_node' : 4,
            'heading' : 1,
            'description' : 'true west to center'
        }

        self.data['coordinate_data']['edges']['g'] = {
            'source_node' : 4,
            'destination_node' : 5,
            'heading' : 1,
            'description' : 'center to true east'
        }

        self.data['coordinate_data']['edges']['h'] = {
            'source_node' : 3,
            'destination_node' : 6,
            'heading' : 2,
            'description' : 'true west to south west'
        }

        self.data['coordinate_data']['edges']['i'] = {
            'source_node' : 4,
            'destination_node' : 7,
            'heading' : 2,
            'description' : 'center to true south'
        }

        self.data['coordinate_data']['edges']['j'] = {
            'source_node' : 5,
            'destination_node' : 8,
            'heading' : 2,
            'description' : 'true east to south east'
        }

        self.data['coordinate_data']['edges']['k'] = {
            'source_node' : 6,
            'destination_node' : 7,
            'heading' : 1,
            'description' : 'south west to true south'
        }

        self.data['coordinate_data']['edges']['l'] = {
            'source_node' : 7,
            'destination_node' : 8,
            'heading' : 1,
            'description' : 'true south to south east'
        }


############################################################################## 
############################################################################## 
## 
## 
## 
############################################################################## 
############################################################################## 


    def artificial_block(self, rotations):
        ##
        ## seconds for motors to come up to speed
        ##        
        self.rampup_time = 0.05

        ##
        ## @ 70% power it takes roughly 0.5 seconds per rotation
        ##
        self.seconds_per_rotation = 0.5

        rampup_time = self.rampup_time
        running_time = self.seconds_per_rotation*rotations

        total_time = rampup_time+running_time

        floor = math.floor(total_time)
        ceiling = math.ceil(total_time)
        delta = float(total_time-floor)

        self.proc_manager['blocking'] = True

        for a in range(int(ceiling)):
            ##
            ## sleep for one second up to the ceiling iteration
            ## and then sleep for the delta between running_time
            ## and floor
            ##
            if self.proc_manager['blocking'] is True:

                if a == int(ceiling-1):
                    ##
                    ## sleep delta value
                    ##
                    sleep_time = delta

                else:
                    ##
                    ## sleep whole second
                    ##
                    sleep_time = 1

                time.sleep(sleep_time)

            else:
                print('[+] ({}) Artificial blocker interrupted at {}'.format(datetime.datetime.now(), a))
                break

        return


############################################################################## 
############################################################################## 
## 
## 
## 
############################################################################## 
############################################################################## 


    def respond_to_alexa( self, report=None, 
                          namespace='Custom.EV3SearchGadget', 
                          name='EV3Response'):
        """
        Callback to Alexa to report
        """
        try:
            logger.info('Responding to Alexa')

            ##
            ## Send custom event to skill
            ##
            payload = {
                'report' : report
            }

            print('[+] Responding to Alexa: {} : {}'.format(namespace, name))
            self.send_custom_event(namespace, name, payload)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print('[-] respond_to_alexa Error: {} on line {}'.format(e, exc_tb.tb_lineno))


############################################################################## 
############################################################################## 
## 
## 
## 
############################################################################## 
############################################################################## 
 
 
    def on_custom_ev3searchgadget_response(self, directive): 
        """ 
        Handles Custom.EV3SearchGadget.Response directive sent from skill 
        """ 

        payload = json.loads(directive.payload.decode("utf-8")) 
  
        self.data['instruction_id_list'].append(payload)

        ## 
        ## do thing here 
        ## 

        if 'slots' in payload:
            slots = payload['slots']
            print(slots)

        if 'intent' in payload:
            if payload['intent'] == 'launch':
                print('[+] {}'.format('Receieved Launch'))
                self.launch_robot()

            elif payload['intent'] == 'move_robot':
                print('[+] {}'.format('Receieved move robot'))


                kwargs = {
                    'payload' : payload,
                    'slots' : slots
                }

                mv = multiprocessing.Process(target=self.move_robot, kwargs=kwargs) 
                mv.start() 
                self.proc_manager['motor_processes'].append(mv)

                self.respond_to_alexa( report='move robot',
                                       name='EV3ResponseAfterMove')

            elif payload['intent'] == 'turn_robot':
                print('[+] {}'.format('Receieved turn robot'))
                self.turn_robot(payload=payload, slots=slots)

            elif payload['intent'] == 'start_search':
                print('[+] ({}) {}'.format(datetime.datetime.now(), 'Receieved start_search'))

                self.proc_manager['search'] = True

                kwargs = {
                    'payload' : payload
                }

                search = multiprocessing.Process(target=self.start_search, kwargs=kwargs) 
                search.start() 
                self.proc_manager['motor_processes'].append(search)

                self.respond_to_alexa( report='start search',
                                       name='EV3ResponseAfterStartSearch')


            elif payload['intent'] == 'walk_perimeter':
                print('[+] {}'.format('Receieved walk_perimeter'))
                self.walk_perimeter(payload=payload)

            elif payload['intent'] == 'pause_robot':
                print('[+] {}'.format('Receieved pause robot'))
                self.pause_robot()

            elif payload['intent'] == 'killswitch':
                print('[+] {}'.format('Receieved killswitch'))
                self.killswitch()

            elif payload['intent'] == 'stop_cancel':
                print('[+] {}'.format('Receieved stop/cancel'))
                self.stop_cancel_robot()

            elif payload['intent'] == 'expired':
                print('[+] {}'.format('Receieved expired'))
                self.stop_cancel_robot()

            elif payload['intent'] == 'set_grid':
                print('[+] {}'.format('Receieved set grid'))
                self.set_grid(payload=payload, slots=slots)


############################################################################## 
############################################################################## 
## 
## 
## 
############################################################################## 
############################################################################## 
 
 
    def walk_perimeter(self, payload=None): 

        print('[+] Executing walk_perimeter function')

        instruction_id = str(uuid.uuid4())
        s = time.time()
        self.data['instruction_id_list'].append(instruction_id)

        i = {
            'type' : 'start_walk_perimeter',
            'start_time' : s
        }

        self.data['instruction_data'][instruction_id] = i

        ##
        ## color search thread
        ##
        color_search = multiprocessing.Process(target=self.color_search_function) 
        color_search.start() 

        walker = multiprocessing.Process(target=self.walk_perimeter_function) 
        walker.start() 
        self.proc_manager['motor_processes'].append(walker)

        end = time.time()
        self.data['instruction_data'][instruction_id]['end_time'] = end


############################################################################## 
############################################################################## 
## 
## 
## 
############################################################################## 
############################################################################## 


    def walk_perimeter_function(self, payload=None): 
        print('[+] Executing walk_perimeter_function')

        instruction_id = str(uuid.uuid4())
        s = time.time()
        self.data['instruction_id_list'].append(instruction_id)

        try:

            self.proc_manager['search'] = True

            speed = self.data['default_bowstearn_speed']
            width = self.data['coordinate_data']['grid_width']
            height = self.data['coordinate_data']['grid_height']

            if self.data['coordinate_data']['current_grid_position'] is None:
                position = self.data['coordinate_data']['starting_grid_position']
            else:
                position = self.data['coordinate_data']['current_grid_position']

            heading = self.data['coordinate_data']['heading']

            i = {
                'type' : 'walk_perimeter_function',
                'start_time' : s,
                'grid_width' : width,
                'grid_height' : height,
                'position' : position,
                'heading' : heading
            }
            self.data['instruction_data'][instruction_id] = i

            nodes = self.data['coordinate_data']['nodes']
            edges = self.data['coordinate_data']['edges']

            total_nodes = len(nodes)
            total_edges = len(edges)

            nodes_traversed = []
            edges_traversed = []
            perimeter_edges_traversed = []

            nodes_repeated = []
            edges_repeated = []

            ##
            ## need to append starting node to list
            ## to prevent an immediate repeat visit
            ##
            nodes_traversed.append(position)

            p = self.data['coordinate_data']['quadrant_list'][position]

            print('[+] Starting position: {}'.format(p))
            print('[+] Starting heading: {}'.format(heading))
            print('[+] There are {} nodes to traverse'.format(total_nodes))
            print('[+] There are {} edges to traverse'.format(total_edges))

            while (len(nodes_traversed) < total_nodes) or (len(perimeter_edges_traversed) < 8):

                if self.proc_manager['search'] is True:

                    ##
                    ## get the current node
                    ##
                    current_node = nodes[position]

                    ##
                    ## walk through the current nodes and score them as
                    ## possible next-hop targets
                    ##
                    data = {}
                    for line in current_node['edges']:
                        node_score = 0
                        edge = edges[line]
                        edge_heading = edge['heading']
                        edge_destination = edge['destination_node']
                        edge_source = edge['source_node']

                        ##
                        ## if the edge destination node is less than the current node
                        ## then lookup the heading compliment to get the reverse heading 
                        ## from the heading data structure
                        ##
                        if edge_destination == position:
                            edge_destination = edge_source

                        if position > edge_destination:
                            edge_heading = self.data['coordinate_data']['heading_compliments'][edge_heading]

                        p = self.data['coordinate_data']['quadrant_list'][edge_destination]

                        if edge_heading == heading:
                            node_score += 1
                        else:
                            turn_angle = self.data['coordinate_data']['heading_angles'][heading][edge_heading]
                            if turn_angle > 0:
                                node_score -= (abs(turn_angle)/90)

                        if edge_destination not in nodes_traversed:
                            node_score += 1

                        if line not in edges_traversed:
                            node_score += 1

                            ##
                            ## check that destination node is not center
                            ##
                            dest_edges = self.data['coordinate_data']['nodes'][edge_destination]['edges']
                            if len(dest_edges) < 4:
                                ##
                                ## then the destination node for this edge is the center
                                ## node.  And since this algorithm should favor
                                ## untraversed perimeter nodes, then downgrade this
                                ## edge's node score
                                ##
                                node_score += 1

                        data[line] = node_score

                    ##
                    ## select the next node based on scoring
                    ##
                    top_score = None
                    for d in data:
                        if top_score is None:
                            top_score =  data[d]
                            selected_edge = d
                        elif data[d] >= top_score:
                            top_score = data[d]
                            selected_edge = d

                    ##
                    ## OK, travelling to next hop
                    ##
                    selected_edge_heading = edges[selected_edge]['heading']
                    selected_edge_destination = edges[selected_edge]['destination_node']
                    selected_edge_source = edges[selected_edge]['source_node']

                    if selected_edge_destination == position:
                        selected_edge_destination = selected_edge_source
                        selected_edge_heading = self.data['coordinate_data']['heading_compliments'][selected_edge_heading]


                    print('[+] ({}) Destination node: {} Destination Heading: {}'.format(datetime.datetime.now(), selected_edge_destination, selected_edge_heading))

                    if selected_edge_heading != heading:
                        print('[+] ({}) Calculating turn angle based on current heading {} and destination heading {}'.format(datetime.datetime.now(), heading, selected_edge_heading))
                        turn_angle = self.data['coordinate_data']['heading_angles'][heading][selected_edge_heading]
                        ##
                        ## now turn the bot
                        ##
                        print('[+] ({}) Turning the bot {} degrees'.format(datetime.datetime.now(), turn_angle))
                        self.move_port_starboard( degrees=turn_angle, block=False)

                    ##
                    ## now drive the bot to the new position
                    ##
                    position = selected_edge_destination
                    heading = selected_edge_heading

                    rot_inches = self.data['inches_per_rotation']

                    if heading%2 > 0:
                        ##
                        ## odd headings are east/west
                        ## so use grid width to calculate distance
                        ##
                        width = self.data['coordinate_data']['grid_width']
                        grid_inches = width*12
                        segment_inches = grid_inches/2
                        rotations = segment_inches/rot_inches

                    else:
                        ##
                        ## even headings are north/south
                        ## so use grid height to calculate distance
                        ##
                        height = self.data['coordinate_data']['grid_height']
                        grid_inches = height*12
                        segment_inches = grid_inches/2
                        rotations = segment_inches/rot_inches

                    print('[+] ({}) Driving {} inches using {} rotations'.format(datetime.datetime.now(), segment_inches, rotations))

                    self.move_bow_stearn( rotations=rotations, 
                                          speed=speed,
                                          brake=False,
                                          block=False )

                    self.artificial_block(rotations)

                    if selected_edge_destination not in nodes_traversed:
                        nodes_traversed.append(selected_edge_destination)
                    else:
                        nodes_repeated.append(selected_edge_destination)

                    if selected_edge not in edges_traversed:
                        edges_traversed.append(selected_edge)

                        edge = edges[selected_edge]
                        edge_heading = edge['heading']
                        edge_destination = edge['destination_node']
                        edge_source = edge['source_node']

                        dest_edges = self.data['coordinate_data']['nodes'][edge_destination]['edges']
                        src_edges = self.data['coordinate_data']['nodes'][edge_source]['edges']

                        if len(dest_edges) < 4 and len(src_edges) < 4:
                            perimeter_edges_traversed.append(selected_edge)

                    else:
                        edges_repeated.append(selected_edge)

            print('[+] Perimeter walk complete')

            ##
            ## got to the end and didn't find the subject ... subject not on perimeter
            ##
            self.proc_manager['search'] = False
            self.proc_manager['subject_found'] = True # stops the color search function

            print('[+] Traversed {} nodes of {}'.format(len(nodes_traversed), total_nodes))
            print('[+] Traversed {} edges of {}'.format(len(edges_traversed), total_edges))
            print('[+] Repeated {} nodes'.format(len(nodes_repeated)))
            print('[+] Repeated {} edges'.format(len(edges_repeated)))

            end = time.time()
            self.data['instruction_data'][instruction_id]['end_time'] = end

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print('[-] walk_perimeter_function Error: {} on line {}'.format(e, exc_tb.tb_lineno))


############################################################################## 
############################################################################## 
## 
## 
## 
############################################################################## 
############################################################################## 
 
 
    def start_search(self, payload=None): 
        print('[+] ({}) Executing start_search function'.format(datetime.datetime.now()))

        instruction_id = str(uuid.uuid4())
        s = time.time()
        self.data['instruction_id_list'].append(instruction_id)

        i = {
            'type' : 'start_search',
            'start_time' : s,
        }

        self.data['instruction_data'][instruction_id] = i

        ##
        ## color search thread
        ##
        color_search = multiprocessing.Process(target=self.color_search_function) 
        color_search.start() 

        intellisearch = multiprocessing.Process(target=self.intellisearch_function) 
        intellisearch.start() 
        self.proc_manager['motor_processes'].append(intellisearch)

        end = time.time()
        self.data['instruction_data'][instruction_id]['end_time'] = end


############################################################################## 
############################################################################## 
## 
## 
## 
############################################################################## 
############################################################################## 
 
 
    def launch_robot(self): 
        print('[+] Executing launch_robot function')

        instruction_id = str(uuid.uuid4())
        s = time.time()
        self.data['instruction_id_list'].append(instruction_id)

        self.respond_to_alexa( report='launch robot',
                               name='EV3ResponseAfterLaunch')

        end = time.time()

        i = {
            'type' : 'launch',
            'start_time' : s,
            'end_time' : end
        }

        self.data['instruction_data'][instruction_id] = i

 
############################################################################## 
############################################################################## 
## 
## 
## 
############################################################################## 
############################################################################## 
 
 
    def move_robot(self, payload=None, slots=None): 
        print('[+] Executing move_robot function')

        instruction_id = str(uuid.uuid4())
        s = time.time()
        self.data['instruction_id_list'].append(instruction_id)

        bow_stearn_value = None

        ##
        ## defaults
        ##
        speed = self.data['default_bowstearn_speed']
        rotations = 10

        try:
            if slots is not None:
                if 'BowStearnDirection' in slots:
                    bow_stearn_value = slots['BowStearnDirection']['value']
                    print('[+] moving {}'.format(bow_stearn_value))

                if 'BowStearnDuration' in slots:
                    rotations = int(slots['BowStearnDuration']['value'])


            print('[+] ({}) moving {} {} rotations'.format(datetime.datetime.now(), bow_stearn_value, rotations))

            if bow_stearn_value is not None:
                if payload is not None and 'loloco' in payload:

                    if 'backward_slots' in payload['loloco']:
                        if bow_stearn_value in payload['loloco']['backward_slots']:
                            ##
                            ## we're going backward ... negative speed
                            ##
                            speed = (0-self.data['default_bowstearn_speed'])

            d = {
                'type' : 'move',
                'start_time' : s,
                'speed' : speed,
                'rotations' : rotations
            }

            self.data['instruction_data'][instruction_id] = d

            ##
            ## when block = true, the kill switch
            ## doesn't function properly ... or at all; FYSA
            ##
            kwargs = {
                'rotations':rotations, 
                'speed':speed,
                'brake':False,
                'block':False
            }

            mv = multiprocessing.Process(target=self.move_bow_stearn, kwargs=kwargs) 
            mv.start() 
            self.proc_manager['motor_processes'].append(mv)


            ##
            ## use artificail block so we can still use killswitch
            ##
            self.artificial_block(rotations)

            end = time.time()
            self.data['instruction_data'][instruction_id]['end_time'] = end

            print('[+] ({}) The bot traveled {} rotations in {} seconds'.format(datetime.datetime.now(),rotations, end-s))

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print('[-] move_robot Error: {} on line {}'.format(e, exc_tb.tb_lineno))


############################################################################## 
############################################################################## 
## 
## 
## 
############################################################################## 
############################################################################## 
 
 
    def turn_robot(self, payload=None, slots=None): 
        print('[+] Executing turn_robot function')

        instruction_id = str(uuid.uuid4())
        s = time.time()
        self.data['instruction_id_list'].append(instruction_id)

        direction = self.data['default_portstarboard_direction']
        degrees = self.data['default_portstarboard_angle']

        try:

            if slots is not None:
                if 'PortStarboardDirection' in slots:
                    direction = slots['PortStarboardDirection']['value']

                if 'PortStarboardDuration' in slots:
                    degrees = int(slots['PortStarboardDuration']['value'])

            d = {
                'type' : 'turn',
                'start_time' : s,
                'direction' : direction,
                'degrees' : degrees
            }
            self.data['instruction_data'][instruction_id] = d

            if direction == self.data['default_portstarboard_direction']:
                ##
                ## turn right
                ##
                degrees=degrees

            else:
                ##
                ## turn left
                ##
                degrees=(0-degrees)

            self.move_port_starboard( degrees=degrees, block=False)

            end = time.time()
            self.data['instruction_data'][instruction_id]['end_time'] = end

            self.respond_to_alexa( report='turn robot',
                                   name='EV3ResponseAfterTurn')

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print('[-] turn_robot Error: {} on line {}'.format(e, exc_tb.tb_lineno))


############################################################################## 
############################################################################## 
## 
## 
## 
############################################################################## 
############################################################################## 
 
 
    def set_grid(self, payload=None, slots=None): 
        print('[+] Executing set_grid function')

        instruction_id = str(uuid.uuid4())
        s = time.time()
        self.data['instruction_id_list'].append(instruction_id)

        d = {}

        try:
            if slots is not None:
                if 'GridWidth' in slots:
                    width = int(slots['GridWidth']['value'])
                    self.data['coordinate_data']['grid_width'] = width
                    print('[+] Setting grid width to {}'.format(width))

                    d = {
                        'type' : 'set_grid',
                        'start_time' : s,
                        'width' : width
                    }

                elif 'GridHeight' in slots:
                    height = int(slots['GridHeight']['value'])
                    self.data['coordinate_data']['grid_height'] = height
                    print('[+] Setting grid height to {}'.format(height))

                    d = {
                        'type' : 'set_grid',
                        'start_time' : s,
                        'height' : height
                    }

                elif 'GridPositionCardinal' in slots or 'GridPosition' in slots:

                    ##
                    ## position should be in the payload
                    ##
                    if 'position' in payload:
                        position = payload['position']
                    else:
                        ##
                        ## cardinal wasn't given ... look for number
                        ##
                        if 'GridPosition' in slots:
                            position = int(slots['GridPosition']['value'])
                        else:
                            ##
                            ## for whatever reason, position wasn't sent
                            ##
                            position = self.data['coordinate_data']['starting_grid_position']

                    if position <= 9 and position >= 0:
                        self.data['coordinate_data']['starting_grid_position'] = position
                        self.data['coordinate_data']['current_grid_position'] = position
                        print('[+] Setting grid position to {}'.format(position))

                        d = {
                            'type' : 'set_grid',
                            'start_time' : s,
                            'position' : position
                        }

                        if position == 4:
                            ##
                            ## center of grid assume heading north
                            ##
                            heading = 0
                        elif position >= 0 and position <= 2:
                            ##
                            ## one of the north quadrants assume heading south
                            ##
                            heading = 2
                        elif position >= 6 and position <= 8:
                            ##
                            ## one of the south quadrants assume heading north
                            ##
                            heading = 0

                        elif position == 5:
                            ##
                            ## true east assume heading west
                            ##
                            heading = 3
                        elif position == 3:
                            ##
                            ## true west assume heading east
                            ##
                            heading = 1

                        self.data['coordinate_data']['heading'] = heading

                        print('[+] Setting grid position to {} and heading to {}'.format(position, heading))

                    else:
                        print('[-] Position out of range ... using default position and heading')

            self.data['instruction_data'][instruction_id] = d

            end = time.time()
            self.data['instruction_data'][instruction_id]['end_time'] = end

            self.respond_to_alexa( report='set grid',
                                   name='EV3ResponseAfterSetGrid')

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print('[-] set_grid Error: {} on line {}'.format(e, exc_tb.tb_lineno))


############################################################################## 
############################################################################## 
## 
## 
## 
############################################################################## 
############################################################################## 
 
 
    def color_search_function(self): 
        print('[+] Executing color_search_function')

        ##
        ## Color comparisons:
        ##      0: No color
        ##      1: Black
        ##      2: Blue
        ##      3: Green
        ##      4: Yellow
        ##      5: Red
        ##      6: White
        ##      7: Brown
        ##

        ##
        ## default color == green
        ##
        default_color = self.data['default_color']

        instruction_id = str(uuid.uuid4())
        s = time.time()
        self.data['instruction_id_list'].append(instruction_id)

        d = {
            'type' : 'color_search',
            'start_time' : s,
        }
        self.data['instruction_data'][instruction_id] = d
        self.proc_manager['subject_found'] = False

        cl = ColorSensor()

        while self.proc_manager['subject_found'] is not True:
            if cl.color == default_color:
                print('[+] Found subject')

                self.proc_manager['subject_found'] = True
                self.proc_manager['search'] = False
                self.killswitch()

                opts = '-a 200 -s 130 -v'
                msg = 'Sir, I have found the subject'
                sound = Sound()
                sound.speak(msg, espeak_opts=opts+'en-rp')


############################################################################## 
############################################################################## 
## 
## 
## 
############################################################################## 
############################################################################## 


    def intellisearch_function(self): 
        print('[+] Executing intellisearch_function')


        instruction_id = str(uuid.uuid4())
        s = time.time()
        self.data['instruction_id_list'].append(instruction_id)

        bow_stearn_value = None

        speed = self.data['default_bowstearn_speed']

        bow_stearn_rotations = 1
        port_starboard_rotations = 1.39

        try:
            ##
            ## only extend the rotations every other iteration
            ##
            iteration = 0

            while self.proc_manager['search'] is True:
                ##
                ## move forward
                ##
                instruction_id = str(uuid.uuid4())
                s = time.time()
                self.data['instruction_id_list'].append(instruction_id)

                d = {
                    'type' : 'move',
                    'start_time' : s,
                    'speed' : speed,
                    'rotations' : bow_stearn_rotations
                }

                self.data['instruction_data'][instruction_id] = d

                kwargs = {
                    'rotations':bow_stearn_rotations, 
                    'speed':speed,
                    'brake':False,
                    'block':False
                }

                mv = multiprocessing.Process(target=self.move_bow_stearn, kwargs=kwargs) 
                mv.start() 
                self.proc_manager['motor_processes'].append(mv)

                if bow_stearn_rotations == 1:
                    blocking_time = 2
                else:
                    blocking_time = bow_stearn_rotations

                print('[+] ({}) Intellisearch blocking for {} rotations'.format(datetime.datetime.now(), blocking_time))
                self.artificial_block(blocking_time)
                print('[+] ({}) Intellisearch finished blocking for {} rotations'.format(datetime.datetime.now(), blocking_time))

                end = time.time()
                self.data['instruction_data'][instruction_id]['end_time'] = end

                ##
                ## turn default direction
                ##
                instruction_id = str(uuid.uuid4())
                s = time.time()
                self.data['instruction_id_list'].append(instruction_id)

                ##
                ## have to test again here in case we've been stopped mid-move
                ##
                if self.proc_manager['search']:
                    direction = self.data['default_portstarboard_direction']
                    degrees = self.data['default_portstarboard_angle']

                    d = {
                        'type' : 'turn',
                        'start_time' : s,
                        'direction' : self.data['default_portstarboard_direction'],
                        'degrees' : self.data['default_portstarboard_angle']
                    }

                    self.data['instruction_data'][instruction_id] = d


                    self.move_port_starboard( degrees=degrees, 
                                              direction=direction, 
                                              block=False)

                    ##
                    ## non-blocking call doesn't have enough time to complete
                    ##
                    time.sleep(1)

                    end = time.time()
                    self.data['instruction_data'][instruction_id]['end_time'] = end

                if iteration > 0 and iteration%2 < 1:
                    bow_stearn_rotations += 2

                iteration += 1

            return

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()            
            print('[-] intellisearch_function Error: {} on line {}'.format(e, exc_tb.tb_lineno))

 
############################################################################## 
############################################################################## 
## 
## 
## 
############################################################################## 
############################################################################## 


    def pause_robot(self): 
        print('[+] Executing pause_robot function')

        instruction_id = str(uuid.uuid4())
        s = time.time()
        self.data['instruction_id_list'].append(instruction_id)

        d = {
            'type' : 'pause',
            'start_time' : s,
        }

        self.data['instruction_data'][instruction_id] = d

        self.respond_to_alexa( report='pause robot',
                               name='EV3ResponseAfterPause')


############################################################################## 
############################################################################## 
## 
## 
## 
############################################################################## 
############################################################################## 


    def killswitch(self): 
        print('[+] Executing killswitch function')

        try:

            ##
            ## turn off any true/false flags that are controlling any
            ## movement loops throughout
            ##
            self.proc_manager['search'] = False
            self.proc_manager['blocking'] = False


            instruction_id = str(uuid.uuid4())
            s = time.time()
            self.data['instruction_id_list'].append(instruction_id)

            d = {
                'type' : 'killswitch',
                'start_time' : s,
            }

            self.data['instruction_data'][instruction_id] = d

            ##
            ## next, kill the motors
            ##

            print('[+] Stopping running motor processes now')
            for t in self.proc_manager['motor_processes']:
                t.join()
                t.terminate()
                self.proc_manager['motor_processes'].remove(t)


            print('[+] Stopping tank now')
            self.tank_pair.off()

            end = time.time()
            self.data['instruction_data'][instruction_id]['end_time'] = end

            self.respond_to_alexa( report='killswitch',
                                   name='EV3ResponseAfterKillSwitch')

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print('[-] killswitch Error: {} on line {}'.format(e, exc_tb.tb_lineno))


############################################################################## 
############################################################################## 
## 
## 
## 
############################################################################## 
############################################################################## 
 
 
    def stop_cancel_robot(self): 
        print('[+] Executing stop_cancel_robot function')

        instruction_id = str(uuid.uuid4())
        s = time.time()
        self.data['instruction_id_list'].append(instruction_id)

        d = {
            'type' : 'close_skill',
            'start_time' : s,
        }


############################################################################## 
############################################################################## 
## 
## 
## 
############################################################################## 
############################################################################## 
 
 
    def expire_robot(self): 
        print('[+] Executing expire_robot function')

        instruction_id = str(uuid.uuid4())
        s = time.time()
        self.data['instruction_id_list'].append(instruction_id)

        d = {
            'type' : 'expire',
            'start_time' : s,
        }

        return


############################################################################## 
############################################################################## 
## 
## 
## 
############################################################################## 
############################################################################## 
 
 
    def move_bow_stearn( self, 
                         speed=None, 
                         rotations=10, 
                         brake=True, 
                         block=False ):

        '''
        NOTE: if block is set to True, then the killswitch won't work
              which means that long distance forward movements can't
              be interrupted, and long distance search legs will
              overshoot the search subject
        '''

        if speed is None:
            speed=self.data['default_bowstearn_speed']


        ##
        ## 1 rotation == 3.75 inches
        ##
        print('[+] ({}) Moving robot bow/stearn {} rotations'.format(datetime.datetime.now(),rotations))

        try:

            kwargs = {
                'rotations':rotations, 
                'left_speed':speed,
                'right_speed':speed,
                'brake':brake,
                'block':block
            }


            mv = multiprocessing.Process(target=self.tank_pair.on_for_rotations, kwargs=kwargs) 
            mv.start() 
            self.proc_manager['motor_processes'].append(mv)

            print('[+] ({}) Finished moving robot bow/stearn {} rotations'.format(datetime.datetime.now(),rotations))

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print('[-] move_bow_stearn Error: {} on line {}'.format(e, exc_tb.tb_lineno))

        return

 
############################################################################## 
############################################################################## 
## 
## 
## 
############################################################################## 
############################################################################## 
 
 
    def move_port_starboard( self, 
                             degrees=None,
                             direction=None, 
                             brake=True, 
                             block=False ):

        if degrees is None:
            degrees=self.data['default_portstarboard_angle']

        if direction is None:
            direction=self.data['default_portstarboard_direction']

        speed = self.data['default_portstarboard_speed']

        wiggle_room = 4

        ##
        ## as angles become larger, the gyro seems to fall off by about 5 degrees
        ##
        correction_factor = 5

        print('[+] ({}) Moving robot port/starboard {} degrees'.format(datetime.datetime.now(), degrees))

        try:

            gyro = GyroSensor()
            gyro.reset()

            start_angle = gyro.angle

            if degrees > 0:
                ##
                ## turn right
                ##
                left_speed=speed 
                right_speed=(0-speed)

            else:
                ##
                ## turn left
                ##
                left_speed=(0-speed)
                right_speed=speed

            self.tank_pair.on( left_speed=left_speed, 
                               right_speed=right_speed )

            if abs(degrees) > correction_factor*2:
                gyro.wait_until_angle_changed_by((abs(degrees)-correction_factor), direction_sensitive=False)

            else:
                gyro.wait_until_angle_changed_by((abs(degrees)), direction_sensitive=False)

            self.tank_pair.off()

            end_angle = gyro.angle
            delta_angle = abs((end_angle-start_angle))

            if (delta_angle-abs(degrees)) >= wiggle_room:
                ##
                ## correct turn in opposite direction
                ##
                c_left_speed = (0-left_speed)
                c_right_speed = (0-right_speed)

                print('[+] ({}) Correcting turn by {} degrees'.format(datetime.datetime.now(), abs(delta_angle-degrees)))

                self.tank_pair.on( left_speed=c_left_speed, 
                                   right_speed=c_right_speed )

                if abs(delta_angle-degrees) > correction_factor*2:
                    gyro.wait_until_angle_changed_by((abs(delta_angle-degrees)-correction_factor), direction_sensitive=False)

                else:
                    gyro.wait_until_angle_changed_by((abs(delta_angle-degrees)), direction_sensitive=False)


                self.tank_pair.off()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print('[-] move_port_starboard Error: {} on line {}'.format(e, exc_tb.tb_lineno))

        return


############################################################################## 
############################################################################## 
## 
## 
## 
############################################################################## 
############################################################################## 
 
 
    def _ev3_waiter(self):
        """ 
        continious cycle function 
        """ 
        while True:

            time.sleep(0) 
 

############################################################################## 
############################################################################## 
## 
## 
## 
############################################################################## 
############################################################################## 
 
 
if __name__ == '__main__': 
    try: 
        EV3SearchGadget().main() 
    except Exception as e: 
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print('[-] Error: {} on line {}'.format(e, exc_tb.tb_lineno))
