import search
import random
import math
import utils
import itertools

ids = ["931188304", "345233563"]


class DroneProblem(search.Problem):
    """This class implements a medical problem according to problem description file"""

    def __init__(self, initial):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""

        # print("IN INIT")
        time = 0
        self.map = initial["map"]
        self.n = len(self.map)
        self.m = len(self.map[0])

        our_package = utils.hashabledict(initial["packages"])
        pack_available = []

        for pack in our_package:
            pack_available.append(pack)


        clients = initial["clients"]
        # Initial location for each client
        client_loc = {}
        pack_to_client = {}
        for key, val in initial["clients"].items():
            client_loc.update({key: val["path"]})
            pack_to_client.update({key: val["packages"]})
        self.client_loc = utils.hashabledict(client_loc)

        self.pack_to_client = utils.hashabledict(pack_to_client)

        # print(self.pack_to_client)
        drones = initial["drones"]
        drone_1 = '0'
        drone_2 = '0'
        drones_dict = {}
        for drone in drones:
            drone_loc = drones[drone]
            drones_dict[drone] = (drone, drone_loc, drone_1, drone_2)

        drones_dict = utils.hashabledict(drones_dict)


        package_loc = initial["packages"]

        package_client_dict = {}
        for client in clients:
            for package in clients[client]["packages"]:
                package_client_dict[package] = (package, client, clients[client]["path"][0], package_loc[package])

        drones_tuple = tuple(drones_dict.values())
        package_client_tuple = tuple(package_client_dict.values())
        pack_available = tuple(pack_available)

        initial = (drones_tuple, package_client_tuple, pack_available)
        # print("INITIAL :",initial)

        search.Problem.__init__(self, initial)

    def check_move_position(self, nx, ny):
        if nx < 0 or nx > self.n - 1 or ny < 0 or ny > self.m - 1:
            return False
        if self.map[nx][ny] == "I":
            return False
        return True

    def check_actions(self, package_client, drone, pack_available):

        move_legal = []
        actions_move = []
        pick_up_move = []
        deliver_move = []
        px = drone[1][0]
        py = drone[1][1]

        if self.check_move_position(px - 1, py):
            move_legal.append((px - 1, py))
        if self.check_move_position(px + 1, py):
            move_legal.append((px + 1, py))
        if self.check_move_position(px, py - 1):
            move_legal.append((px, py - 1))
        if self.check_move_position(px, py + 1):
            move_legal.append((px, py + 1))
        for i in move_legal:
            if ('move', drone[0], i) not in actions_move:
                actions_move.append(('move', drone[0], i))
        #print("actions_move", actions_move)

        for pack in package_client:
            package_name = pack[0]
            package_loc = pack[3]
            if package_loc == drone[1]:  # loc drone
                if ('pick up', drone[0], package_name) not in pick_up_move:
                    if package_name in pack_available:
                        if drone[2] == '0' or drone[3] == '0':
                            pick_up_move.append(('pick up', drone[0], package_name))

        #print(pick_up_move)

        pack_in_drone = [drone[2], drone[3]]
        drone_loc = drone[1]

        for pack in pack_in_drone:
            for p in package_client:
                if pack == p[0] and drone_loc == p[2]:
                    if ('deliver', drone[0],p[1] ,p[0]) not in deliver_move:
                        deliver_move.append(('deliver', drone[0],p[1], p[0]))



        actions_move.extend(pick_up_move)
        actions_move.extend(deliver_move)

        actions_move.append(('wait', drone[0]))
        act = tuple(actions_move)
        #print("ACTIONS-MOVE", act)
        return act

    def actions(self, state):
        # print(state)
        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        #print("ACTION")
        #print("state", state)

        drones = state[0]
        package_client = state[1]
        pack_available = state[2]
        actions = []
        actions_list = []

        for drone in drones:
            actions.append(self.check_actions(package_client, drone, pack_available))
            # print("ACTIONS IN FOR DRONE",actions)
        for element in itertools.product(*actions):
            actions_list.append(element)
            # print("ACTIONS_LIST IN FOR ELEMENT",actions_list)

        actions = tuple(actions_list)

        # print("Action:\n","\n",actions,"\n")
        return actions

    def result(self, state, action):
        #print("DEBUT RESULT",state)

        drone = [list(x) for x in state[0]]
        package_client = [list(x) for x in state[1]]
        package_available = list(state[2])
        #time = state[3]
        # print(drone)
        # print(package_client)
        # print(package_available)

        lst_pick_pack = []
        # print(" self.package_client_dict[pack][1]",current_pack_available)
        for act in action:
            i_d = 0
            for d in drone:
                if d[0] == act[1]:
                    if act[0] == 'move':
                        drone[i_d][1] = act[2]
                        #print(drone[i_d][1])
                    if act[0] == 'pick up':
                        #print("PICK UPPP",act)
                        #print(state)
                        #print(act)
                        if drone[i_d][2] == '0':
                            drone[i_d][2] = act[2]
                        elif drone[i_d][3] == '0':
                            drone[i_d][3] = act[2]
                        if act[2] in package_available:
                            package_available.remove(act[2])
                    if act[0] == 'deliver':
                        #print("DELIVERRR",act)
                        #print(state)
                        #print(act)
                        #print(drone[i_d])

                        if drone[i_d][2] == act[3]:
                            drone[i_d][2] = '0'
                        elif drone[i_d][3] == act[3]:
                            drone[i_d][3] = '0'
                        for pac in package_client:
                            if pac[0] == act[3]:
                                package_client.remove(pac)
                i_d += 1

        for client in self.client_loc.keys():
            count = len(self.client_loc[client])
            #i = self.client_loc[client].index()
            #index = (i + 1) % (count)
            i_pc=0
            for pack in package_client:
                if package_client[i_pc][1] == client:
                    i = self.client_loc[client].index(package_client[i_pc][2])
                    index = (i + 1) % (count)
                    # print ("dict pack 1",self.package_client_dict[pack][2])
                    package_client[i_pc][2] = self.client_loc[client][index]
                    package_client[i_pc][2] = self.client_loc[client][index]
                i_pc+=1

        #time += 1
        drone = [tuple(x) for x in drone]
        drone=tuple(drone)
        package_client = [tuple(x) for x in package_client]
        package_client=tuple(package_client)
        package_available = tuple(package_available)

        state = (drone, package_client, package_available)

        #print("FIN RESULT",state)

        return state

        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""

    def goal_test(self, state):

        package_client = [list(x) for x in state[1]]
        #print("package_client :", package_client)


        if not package_client:
            return True
        return False

        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""


    def distance2(self,p0, p1):
        return math.sqrt((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2)

    def distance(self, p0, p1):
        return abs(p0[0] - p1[0]) + abs(p0[1] - p1[1])

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""

        
        for drone in drones:
            drone_loc = drones[drone]
            drones_dict[drone] = (drone, drone_loc, drone_1, drone_2)

        drones = node.state[0]
        packages_client = node.state[1]
        package_available = node.state[2]
        h = len(package_available)
        h += len(packages_client)
        for pc in packages_client:
            for d in drones:
                if pc[0] not in package_available:
                    if pc[0]==d[2] or pc[0]==d[3]:
                        h += self.distance(pc[2] , d[1])
                        #h+=self.check_impassable(d[1],pc[2])
                        #h += random.randint(0, self.distance(pc[2] , d[1]))
                else:
                    h += self.distance(pc[3],pc[2])
                    h += self.distance(d[1],pc[3])


        #print(package_available)
        #h+= random.randint(0,2)
        print(h)
        return h

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""


def create_drone_problem(game):
    return DroneProblem(game)
