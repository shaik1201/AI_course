import copy
import json
import random
import math
import utils
from itertools import product
import itertools

ids = ["111111111", "222222222"]

class OptimalTaxiAgent:
    def __init__(self, initial):
        our_state = self.build_our_state(initial)
        self.initial = our_state
        self.all_possible_states = self.generate_all_possible_states()
        self.initial_value_vector = self.get_initial_values_vector()
        self.policy_vactor=dict()
        self.value_iteration()

    ## states creation methods :


    def build_our_state(self,state):
        new_state=dict()

        new_state.update({'optimal' : state['optimal']})
        new_state.update({'map' : state['map']})
        new_state.update({'taxis' : state['taxis']})
        new_state.update({'passengers' : state['passengers']})
        new_state.update({'turns to go' : state['turns to go']})

        return new_state

    def find_all_possible_taxis_location(self):
        state = self.initial
        map = state['map']
        taxis_location=[]

        for i in range(len(map)):
            for j in range(len(map[0])):
                if map[i][j] != 'I':
                    taxis_location.append((i,j))

        if len(state['taxis'])==1:
            return taxis_location
        else:
            duplicate_loc = []
            for taxi in state['taxis']:
                duplicate_loc.append(taxis_location)
            result = list(itertools.product(*duplicate_loc))
            return result

    def find_all_possible_fuel(self):
        state = self.initial
        if (len(state['taxis'])==1):
            all_possible_fuel=[]
            for taxi in state['taxis']:
                for i in range(state['taxis'][taxi]['fuel']+1):
                    all_possible_fuel.append(i)

            return all_possible_fuel

        else:

            fuels_range = []
            for taxi in state['taxis']:
                temp_arr = []
                max_fuel = state['taxis'][taxi]['fuel']
                for i in range(max_fuel+1):
                    temp_arr.append(i)
                fuels_range.append(temp_arr)
            result = list(itertools.product(*fuels_range))
            return result

    def find_all_possible_capacity(self):
        state = self.initial
        if len(state['taxis'])==1:
            for taxi in state['taxis']:
                max_capacity = state['taxis'][taxi]['capacity']
            all_possible_capacity = []
            for i in range(max_capacity+1):
                all_possible_capacity.append(i)

            return all_possible_capacity
        else:
            all_possible_capacity=[]
            for taxi in state['taxis']:
                temp_arr = []
                temp_val = state['taxis'][taxi]['capacity']
                for i in range(temp_val+1):
                    temp_arr.append(i)
                all_possible_capacity.append(temp_arr)

            result = list(itertools.product(*all_possible_capacity))
            return result

    def find_all_possible_passengers_location(self):
        state = self.initial
        all_possible_passenger_loc = []
        for taxi in state['taxis']:
            all_possible_passenger_loc.append(taxi)

        flag = True
        if len(state["passengers"]) == 1:

            for passenger in state['passengers']:
                if state['passengers'][passenger]['destination'] not in state['passengers'][passenger]['possible_goals']:
                    all_possible_passenger_loc.append(state['passengers'][passenger]['destination'])
                for item in state['passengers'][passenger]['possible_goals']:
                    if state['passengers'][passenger]['location'] == item:
                        flag = False
                    all_possible_passenger_loc.append(item)
                if flag == True:
                    all_possible_passenger_loc.append(state['passengers'][passenger]['location'])
            return all_possible_passenger_loc

        else:
            range_loc = []
            for passenger in state['passengers']:
                flag = True
                temp_arr = []
                if state['passengers'][passenger]['destination'] not in state['passengers'][passenger][
                    'possible_goals']:
                    temp_arr.append(state['passengers'][passenger]['destination'])

                for item in all_possible_passenger_loc:
                    temp_arr.append(item)
                for item in state['passengers'][passenger]['possible_goals']:
                    if item == state['passengers'][passenger]['location']:
                        flag = False
                    temp_arr.append(item)
                if flag == True:
                    temp_arr.append(state['passengers'][passenger]['location'])
                range_loc.append(temp_arr)
            result = list(itertools.product(*range_loc))
            return result

    def find_all_passengers_destination(self):
        state = self.initial
        all_possible_passenger_dest = []

        if len(state["passengers"]) == 1:

            for passenger in state['passengers']:
                if state['passengers'][passenger]['destination'] not in state['passengers'][passenger]['possible_goals']:
                    all_possible_passenger_dest.append(state['passengers'][passenger]['destination'])

                for item in state['passengers'][passenger]['possible_goals']:
                    all_possible_passenger_dest.append(item)
            return all_possible_passenger_dest
        else:
            range2_loc = []
            for passenger in state['passengers']:
                temp2_arr = []
                for item in state['passengers'][passenger]['possible_goals']:
                    temp2_arr.append(item)
                range2_loc.append(temp2_arr)
            result2 = list(itertools.product(*range2_loc))
            return result2

    def find_all_turns_to_go(self):
        state = self.initial
        all_possible_turns_to_go = []
        turns = state['turns to go']
        for i in range(turns+1) : all_possible_turns_to_go.append(i)
        return all_possible_turns_to_go

    def state_is_possible(self,state):
        taxis = state['taxis']
        passengers = state['passengers']
        taxis_names=[]
        taxis_init_capacity=[]
        for taxi in taxis:
            taxis_names.append(taxi)
            taxis_init_capacity.append(self.initial['taxis'][taxi]['capacity'])


        loc_set = set()
        for taxi in taxis:
            loc_set.add(taxis[taxi]['location'])
        if len(loc_set) < len(taxis):
            return False
        passengers_in_taxis = []
        for i in range(len(state['taxis'])):
            passengers_in_taxis.append(0)
        for passenger in passengers:
            for i in range(len(taxis_names)):
                if passengers[passenger]['location'] == taxis_names[i] :
                    passengers_in_taxis[i]+=1

        for i in range(len(taxis_names)):
            if taxis_init_capacity[i]-taxis[taxis_names[i]]['capacity'] != passengers_in_taxis[i]:
                return False

        return True

    def generate_all_possible_states(self):

        all_possible_states={}
        all_possible_states_per_turn=[]
        state = self.initial
        optimal = state['optimal']
        map = state['map']
        taxis_names = []
        for taxi in state['taxis']:
            taxis_names.append(taxi)

        passengers_names = []
        for passenger in state['passengers']: passengers_names.append(passenger)

        all_possible_taxis_loc = self.find_all_possible_taxis_location()
        all_possible_fuels = self.find_all_possible_fuel()
        all_possible_capacity = self.find_all_possible_capacity()
        all_possible_passengers_loc = self.find_all_possible_passengers_location()
        all_passengers_destination = self.find_all_passengers_destination()
        all_turns_to_go = self.find_all_turns_to_go()

        for turns in all_turns_to_go:
            for taxi_loc in all_possible_taxis_loc:
                for fuel in all_possible_fuels:
                    for capacity in all_possible_capacity:
                        for passenger_loc in all_possible_passengers_loc:
                            for passenger_dest in all_passengers_destination:


                                if len(state['taxis'])==1:
                                    all_taxis_dict = {
                                        taxis_names[0]: {"location": taxi_loc,
                                                         "fuel": fuel,
                                                         "capacity": capacity
                                                         }
                                    }
                                else:
                                    all_taxis_dict=dict()
                                    for i in range(len(state['taxis'])):
                                        taxi_dict = {
                                            taxis_names[i] : {"location":taxi_loc[i] ,
                                                              "fuel": fuel[i],
                                                              "capacity": capacity[i]
                                                    }
                                        }
                                        all_taxis_dict.update(taxi_dict)

                                if len(state["passengers"])==1:
                                    all_passengers_dict = {
                                        passengers_names[0]: {"location": passenger_loc,
                                                              "destination": passenger_dest,
                                                              "possible_goals":
                                                                  state['passengers'][passengers_names[0]][
                                                                      'possible_goals'],
                                                              "prob_change_goal":
                                                                  state['passengers'][passengers_names[0]][
                                                                      'prob_change_goal']

                                                              }
                                    }

                                else:
                                    all_passengers_dict=dict()
                                    for i in range(len(state['passengers'])):
                                        passenger_dict={
                                            passengers_names[i]:{"location":passenger_loc[i],
                                                                 "destination":passenger_dest[i],
                                                                 "possible_goals":state['passengers'][passengers_names[i]]['possible_goals'],
                                                                 "prob_change_goal":state['passengers'][passengers_names[i]]['prob_change_goal']

                                            }
                                        }
                                        all_passengers_dict.update(passenger_dict)

                                state_dict = {
                                    "optimal":optimal,
                                    "map":map,
                                    "taxis":all_taxis_dict,
                                    "passengers":all_passengers_dict,
                                    "turns to go":turns
                                }
                                if self.state_is_possible(state_dict) == True:
                                    all_possible_states_per_turn.append(state_dict)

            all_possible_states.update({turns : all_possible_states_per_turn})
            all_possible_states_per_turn=[]
        return copy.deepcopy(all_possible_states)

    ## value iteration methods :

    def actions(self, state):
        """Returns all the actions that can be executed in the given
        state. The -result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""

        key_state = self.get_key_of_state(state)

        init_key = self.get_key_of_state(self.initial)
        if init_key == key_state:
            print("")



        if state['turns to go']==0:
            return [("Terminate",)]

        map = self.initial['map']
        rows, cols = len(map) - 1, len(map[0]) - 1
        taxis = state['taxis']
        passengers = state['passengers']
        taxis_action = []
        for taxi in taxis:
            taxi_action = []

            #waiting

            x, y = state['taxis'][taxi]['location'][0], state['taxis'][taxi]['location'][1]
            taxi_action.append(('wait', taxi))

            # movement:

            if state['taxis'][taxi]['fuel'] > 0:

                if x < rows and map[x + 1][y] != 'I':
                    taxi_action.append(("move", taxi, (x + 1, y)))
                if x >= 1 and map[x - 1][y] != 'I':
                    taxi_action.append(("move", taxi, (x - 1, y)))
                if y < cols and map[x][y + 1] != 'I':
                    taxi_action.append(("move", taxi, (x, y + 1)))
                if y >= 1 and map[x][y - 1] != 'I':
                    taxi_action.append(("move", taxi, (x, y - 1)))

            # picking:

            if state['taxis'][taxi]['capacity'] > 0 :
                for passenger in passengers:
                    if ((x != passengers[passenger]['destination'][0]) or (y != passengers[passenger]['destination'][1])) \
                             \
                            and (x == passengers[passenger]['location'][0]) \
                            and (y == passengers[passenger]['location'][1]):
                        taxi_action.append(("pick up", taxi, passenger))

            # dropping:

#maybe we can drop passenger not in their destination...

            for passenger in passengers:
                if passengers[passenger]['location'] == taxi and\
                        x == state['passengers'][passenger]['destination'][0] and\
                        y == state['passengers'][passenger]['destination'][1]:

                    taxi_action.append(("drop off", taxi, passenger))

            # refuel:

            if map[x][y] == 'G':
                taxi_action.append(("refuel", taxi))

            taxis_action.append(taxi_action)

        if len(taxis_action) == 1:
            result = tuple(tuple(sub) for sub in taxi_action)
            result += ("reset",)
            result += ("terminate",)
            return result

        action_result = list(product(*taxis_action))
        count=0
        r_action_result = copy.deepcopy(action_result)
        for action in action_result:
            locations_count = 0
            location_set = set()

            for tax_act in action:
                if (tax_act[0] != "move"):
                    location = ' '.join([str(elem) for elem in state['taxis'][tax_act[1]]['location']])

                else:
                    location = ' '.join([str(elem) for elem in tax_act[2]])
                location_set.add(location)
                locations_count += 1

            if (locations_count != len(location_set)):
                r_action_result.remove(action)
        returned_action_result = tuple(tuple(sub) for sub in r_action_result)
        returned_action_result += ("reset",)
        returned_action_result += ("terminate",)

        return returned_action_result

    def get_initial_values_vector(self):
        values_vec = {}
        for state in self.all_possible_states[0]:
            key = json.dumps(state)
            values_vec[key] = 0
        return values_vec

    def get_key_of_state(self,state):
        return json.dumps(state)

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        if (action == "reset"):
            turns_to_go = state["turns to go"]
            state1 = copy.deepcopy(self.initial)
            state1.pop("turns to go")
            state1["turns to go"] = turns_to_go-1
            return copy.deepcopy(state1)


        if isinstance(action[0], str):
            self.apply_taxi_action(state, action)
        else:
            for taxi_action in action:
                self.apply_taxi_action(state, taxi_action)

        state["turns to go"] -= 1
        return copy.deepcopy(state)

    def apply_taxi_action(self, state, taxi_action):

        if (taxi_action[0] == "move"):
            state["taxis"][taxi_action[1]]["location"] = taxi_action[2]
            state["taxis"][taxi_action[1]]["fuel"] -= 1

        if (taxi_action[0] == "pick up"):
            state["taxis"][taxi_action[1]]["capacity"] -= 1
            state["passengers"][taxi_action[2]]["location"] = taxi_action[1]

        if (taxi_action[0] == "drop off"):
            state["taxis"][taxi_action[1]]["capacity"] += 1
            state["passengers"][taxi_action[2]]["location"] = state["taxis"][taxi_action[1]]["location"]

        if (taxi_action[0] == "refuel"):
            state["taxis"][taxi_action[1]]["fuel"] = self.initial['taxis'][taxi_action[1]]["fuel"]

        return

    def reward_function(self,state,action):

        total_reward = 0
        if len(state['taxis'])==1:
            if action[0] == "drop off":
                return 100
            if action[0] == "refuel":
                return -10
            if action == "reset":
                return -50

            return 0

        else:
            if isinstance(action,tuple):
                for i in range(len(state['taxis'])):
                    if action[i][0] == "drop off":
                        total_reward += 100
                    if action[i][0] == "refuel":
                        total_reward -= 10
            else:
                if action == "reset":
                    return -50

        return total_reward

    def prob_function(self,old_state,act,next_state):
        prob=1
        if act=='reset':
            return 1
        old_passengers = old_state['passengers']
        passengers = next_state['passengers']
        for passenger in passengers :
            if old_state['passengers'][passenger]['destination'] in old_passengers[passenger]['possible_goals']:

                prob_change_goal = passengers[passenger]['prob_change_goal']
                num_of_possible_change = len(passengers[passenger]['possible_goals'])
                prob_for_each_change = prob_change_goal / num_of_possible_change
                if passengers[passenger]['destination'] == old_passengers[passenger]['destination']:
                    temp_prob = (1-prob_change_goal) + prob_for_each_change
                    prob = prob * temp_prob
                else:
                    prob = prob * prob_for_each_change
            else:

                prob_change_goal = passengers[passenger]['prob_change_goal']
                num_of_possible_change = len(passengers[passenger]['possible_goals'])
                prob_for_each_change = prob_change_goal/num_of_possible_change
                if passengers[passenger]['destination'] == old_passengers[passenger]['destination']:
                    prob = prob * (1-prob_change_goal)
                else:
                    prob = prob * prob_for_each_change

        return prob

    def find_value_expectation_of_state(self,state,action,value_vec):

        key_state = self.get_key_of_state(state)
        init_key = self.get_key_of_state(self.initial)



        if(action=='terminate'):
            return 0
        e_val = 0
        next_possible_states = (self.find_next_states(state,action))
        for next_state in next_possible_states:
            next_state_key = self.get_key_of_state(next_state)
            e_val += self.prob_function(state,action,next_state)* value_vec[next_state_key]
        return e_val

    def find_next_states(self,state,action):
        state1 = copy.deepcopy(state)
        if state1['turns to go']==0:
            return []
        result_state = copy.deepcopy(self.result(state1, action))

        if action == 'reset':
            arr=[]
            arr.append(result_state)
            return arr

        optimal = result_state['optimal']
        map = result_state['map']
        taxis = result_state['taxis']
        turn_to_go = result_state['turns to go']

        next_states=[]
        passengers_names=[]
        for passenger in state1['passengers']: passengers_names.append(passenger)

        if len(state['passengers'])==1:
            all_possible_goals = state1['passengers'][passengers_names[0]]['possible_goals']

            for possible_goal in all_possible_goals:
                passengers={}
                passenger={}
                passenger.update({'location':result_state['passengers'][passengers_names[0]]['location']})
                passenger.update({'destination':possible_goal})
                passenger.update({'possible_goals':result_state['passengers'][passengers_names[0]]['possible_goals']})
                passenger.update({'prob_change_goal':result_state['passengers'][passengers_names[0]]['prob_change_goal']})


                passengers.update({passengers_names[0] : passenger})
                curr_state={}
                curr_state.update({'optimal':optimal})
                curr_state.update({'map': map})
                curr_state.update({'taxis': taxis})
                curr_state.update({'passengers': passengers})
                curr_state.update({'turns to go' : turn_to_go})
                next_states.append(curr_state)
            return next_states
        else:
            all_possible_dest=[]
            pass_possible_dest=[]
            for passenger in passengers_names:
                possible_goals = state1['passengers'][passenger]['possible_goals']
                if state1['passengers'][passenger]['destination'] not in state1['passengers'][passenger]['possible_goals']:
                    possible_goals.append(state1['passengers'][passenger]['destination'])

                all_possible_dest.append(possible_goals)

            temp = list(itertools.product(*all_possible_dest))



            for possible_goals in temp:
                passengers = {}
                for i in range(len(passengers_names)):

                    passenger = {}
                    passenger.update({'location': result_state['passengers'][passengers_names[i]]['location']})
                    passenger.update({'destination': possible_goals[i]})
                    passenger.update({'possible_goals': result_state['passengers'][passengers_names[i]]['possible_goals']})
                    passenger.update({'prob_change_goal': result_state['passengers'][passengers_names[i]]['prob_change_goal']})
                    passengers.update({passengers_names[i]: passenger})
                curr_state = {}
                curr_state.update({'optimal': optimal})
                curr_state.update({'map': map})
                curr_state.update({'taxis': taxis})
                curr_state.update({'passengers': passengers})
                curr_state.update({'turns to go': turn_to_go})
                next_states.append(curr_state)

            return next_states


    def value_iteration(self):
        stop=self.initial['turns to go']
        value_vector = copy.deepcopy(self.initial_value_vector)
        for i in range(1,stop+1):
            print(i)
            old_value_vec = copy.deepcopy(value_vector)
            value_vector={}
            for state in self.all_possible_states[i]:

                state1 = copy.deepcopy(state)
                key_state = self.get_key_of_state(state1)
                all_possible_action = self.actions(state1)

                # init_key = self.get_key_of_state(self.initial)
                # if init_key == key_state:
                #     print(all_possible_action)

                max_val = -1000000
                best_action = None
                for action in all_possible_action:
                    reward = self.reward_function(state1,action)
                    exp_val = self.find_value_expectation_of_state(state1,action,old_value_vec)

                    current_val = reward + exp_val
                    if current_val > max_val:
                        max_val = current_val
                        best_action = action
                        temp = {key_state: max_val}
                        opt_pol ={key_state: best_action}

                value_vector.update(temp)
                self.policy_vactor.update(opt_pol)

                init_key = self.get_key_of_state(self.initial)
                if init_key == key_state:
                    print("init value = ",max_val)

        #
        # policy_vector={}
        # num_of_turns = self.initial['turns to go']
        # for state in self.all_possible_states[num_of_turns]:
        #     key_state = self.get_key_of_state(state)
        #     all_possible_action = self.actions(state)
        #     max_val = -1000000
        #     best_act = None
        #     for action in all_possible_action:
        #         reward = self.reward_function(state, action)
        #         exp_val = self.find_value_expectation_of_state(state,action,value_vector)
        #         current_val = reward + exp_val
        #
        #         if current_val > max_val:
        #             best_act = action
        #             max_val = current_val
        #
        #     temp = {key_state : best_act}
        #     policy_vector.update(temp)
        #
        # return policy_vector

    def act(self, state):
        our_state = self.build_our_state(state)
        key = self.get_key_of_state(our_state)
        act = self.policy_vactor[key]
        if act=="reset" or act == "terminate":
            return act
        if len(state['taxis'])==1:
            return ((act,))
        return self.policy_vactor[key]



class TaxiAgent:
    def __init__(self, initial):
        self.initial = initial

    def act(self, state):
        raise NotImplemented


