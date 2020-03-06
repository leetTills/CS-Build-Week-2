from random import choice
import json
from urls import post, get, end

class Queue:
    def __init__(self):
        self.storage = []
        self.size = 0

    def enqueue(self, val):
        self.size += 1
        self.storage.append(val)

    def dequeue(self):
        if self.size:
            self.size -= 1
            return self.storage.pop(0)
        else:
            return None


class Stack:
    def __init__(self):
        self.storage = []
        self.size = 0

    def push(self, val):
        self.size += 1
        self.storage.append(val)

    def pop(self):
        if self.size:
            self.size -= 1
            return self.storage.pop()
        else:
            return None


dirs_reversal = {
    'n': 's',
    's': 'n',
    'e': 'w',
    'w': 'e'
}


class Graph:

    """Represent the world as a dictionary of rooms mapping (room, dir) as edge."""

    def __init__(self):
        self.rooms = {}
        self.grid = {}

    def add_vertex(self, room):
        """
        Add a vertex to the graph.
        """
        if room['room_id'] not in self.rooms:
            self.rooms[room['room_id']] = room
            # self.rooms[room['room_id']]['exits'] = {d: '?' for d in room['exits']}

    def dfs(self, room, path=None):
        if not path:
            path = []
        next_dirs = self.get_unexplored_dir(room)
        path.append(room['room_id'])
        print('dfs path ---->', path)
        if len(next_dirs):
            direction = choice(next_dirs)
            explored = self.explore(direction, room)
            return self.dfs(explored, path)
        else:
            return path

    def get_unexplored_dir(self, room):
        return [direction for direction, value in self.rooms[room['room_id']]['exits'].items() if value == '?']

    def get_all_directions(self, room):
        return [d for d in self.rooms[room['room_id']]['exits']]

    def get_room_in_dir(self, room, direction):
        return self.rooms[room['room_id']]['exits'][direction]

    def explore(self, direction, room, next_room=None):
        prev_room = room['room_id']
        # if len(room['items']):
        #     status = post(end['status'], {})
        #     if int(status['encumbrance']) <= int(status['strength']):
        #         # pick up treasure
        #         for item in room['items']:
        #             take = post(end['take'], {'name': item})
        #             self.rooms[prev_room]['items'] = take['items']
        #             print(
        #                 f'response from taking {item} from room {prev_room} ---->', take)

        # if (shrine) pray
        # if (elevation) fly
        # if (know straight line) dash
        status = post(end['status'], {})
        print(status)
        if next_room:
            res = post(end['move'], {
                       'direction': direction, 'next_room_id': str(next_room)})
        else:
            res = post(end['move'], {'direction': direction})
            self.rooms[prev_room]['exits'][direction] = res['room_id']
            self.add_vertex(res)
            self.rooms[res['room_id']
                       ]['exits'][dirs_reversal[direction]] = prev_room

        # print(self.rooms[prev_room])
        # print(res)
        return res

    def explore_path(self, room, path):
        '''
        Accepts a path that has a direction and the room id
        for the next room in that direction and returns an 
        object of the room at the end of the path
        path = [
            {
                d: "n",
                next_room: 5
            }
        ]
        '''
        curr_room = room
        for obj in path:
            explored = self.explore(obj['d'], room, obj['next_room'])
            curr_room = explored
        return curr_room

    def btrack_to_unex(self, room):
        '''
        Accepts a full room object and finds a path to a 
        room with an unexplored direction and returns the 
        object of the room with an unexplored direction
        '''
        q = Queue()
        all_dirs = self.get_all_directions(room)
        visited = set()
        for d in all_dirs:
            next_room = self.get_room_in_dir(room, d)
            # enqueue inital directions in self.explore_path format
            q.enqueue([{'d': d, 'next_room': next_room}])
        current_room = room
        while q.size:
            back_path = q.dequeue()
            room_in_dir = back_path[-1]['next_room']
            visited.add(room_in_dir)
            current_room = self.rooms[room_in_dir]
            unex = self.get_unexplored_dir(self.rooms[room_in_dir])

            if len(unex):
                return self.explore_path(room, back_path)
            else:
                next_dirs = self.get_all_directions(self.rooms[room_in_dir])
                for d in next_dirs:
                    room_in_next_dir = self.get_room_in_dir(current_room, d)
                    if room_in_next_dir not in visited:
                        # enqueue next room's directions in self.explore_path format
                        q.enqueue(list(back_path) +
                                  [{'d': d, 'next_room': room_in_next_dir}])

    def get_path_to_room(self, curr, room_id):
        '''
        Accepts (current room, target room id)
        returns shortest path to target room from current room
        '''
        if curr['room_id'] == room_id:
            return curr
        curr_room = curr
        q = Queue()
        all_dirs = self.get_all_directions(curr)
        print('all dirs ---->', all_dirs)
        visited = set()
        for d in all_dirs:
            next_room = self.get_room_in_dir(curr, d)
            print('next_room ---->', next_room)
            q.enqueue([{'d': d, 'next_room': next_room}])
        while q.size:
            path_to_room = q.dequeue()
            room_in_dir = path_to_room[-1]['next_room']
            d_in_dir = path_to_room[-1]['d']
            curr_room = self.rooms[room_in_dir]
            visited.add(f'{room_in_dir}{d_in_dir}')
            if room_in_dir == room_id:
                return self.explore_path(curr, path_to_room)
            else:
                next_dirs = self.get_all_directions(self.rooms[room_in_dir])
                print('next_dirs ---->', f'{room_in_dir}: {next_dirs}')
                for d in next_dirs:
                    room_in_next_dir = self.get_room_in_dir(curr_room, d)
                    if f'{room_in_next_dir}{d}' not in visited:
                        q.enqueue(list(path_to_room) +
                                  [{'d': d, 'next_room': room_in_next_dir}])

    # def get_path_to_room(self, curr, room_id):
    #     '''
    #     Accepts (current room, target room id)
    #     returns shortest path to target room from current room
    #     '''
    #     curr_room = curr
    #     q = Queue()
    #     all_dirs = self.get_all_directions(curr)
    #     visited = set()
    #     for d in all_dirs:
    #         next_room = self.get_room_in_dir(curr, d)
    #         q.enqueue([{'d': d, 'next_room': next_room}])
    #     while q.size:
    #         path_to_room = q.dequeue()
    #         room_in_dir = path_to_room[-1]['next_room']
    #         curr_room = self.rooms[room_in_dir]
    #         if room_in_dir == room_id:
    #             return self.explore_path(curr, path_to_room)
    #         else:
    #             next_dirs = self.get_all_directions(self.rooms[room_in_dir])
    #             for d in next_dirs:
    #                 room_in_next_dir = self.get_room_in_dir(curr_room, d)
    #                 if room_in_next_dir not in visited:
    #                     print(room_in_next_dir)
    #                     if self.rooms[room_in_next_dir]['terrain'] != 'TRAP':
    #                         q.enqueue(list(path_to_room) +
    #                                   [{'d': d, 'next_room': room_in_next_dir}])
    #                     elif len(next_dirs) < 2:
    #                         q.enqueue(list(path_to_room) +
    #                                   [{'d': d, 'next_room': room_in_next_dir}])


"""
gold, encumbrance, strength = post(get gold, encumbrance, strength)
while gold < 1000:
  while encumbrance < strength:
    traverse and pick up treasure
    gold, encumbrance, strength = post(get gold, encumbrance, strength)
  go to shop, sell treasure
  gold, encumbrance, strength = post(get gold, encumbrance, strength)
go to namechanger, change name
"""