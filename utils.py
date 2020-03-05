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

    def add_vertex(self, room):
        """
        Add a vertex to the graph.
        """
        if room['room_id'] not in self.rooms:
            self.rooms[room['room_id']] = room
            self.rooms[room['room_id']]['exits'] = {d: '?' for d in room['exits']}

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
    
        print('exits in dir ---->',
              self.rooms[room['room_id']]['exits'], end=', ')
        print('current room id ---->', room['room_id'])
        return self.rooms[room['room_id']]['exits'][direction]

    def explore(self, direction, room, next_room=None):
        prev_room = room['room_id']
        if len(room['items']):
            # pick up treasure
            for item in room['items']:
                take = post(end['take'], {'name': item})
                self.rooms[prev_room]['items'] = take['items']
                print(
                    f'response from taking {item} from room {prev_room} ---->', take)

        # if (shrine) then pray
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
        for d in all_dirs:
            next_room = self.get_room_in_dir(room, d)
            # enqueue inital directions in self.explore_path format
            q.enqueue([{'d': d, 'next_room': next_room}])
        current_room = room
        while q.size:
            back_path = q.dequeue()
            room_in_dir = back_path[-1]['next_room']
            current_room = self.rooms[room_in_dir]
            unex = self.get_unexplored_dir(self.rooms[room_in_dir])
            print('bfs path ---->', back_path)
            if len(unex):
                return self.explore_path(room, back_path)
            else:
                next_dirs = self.get_all_directions(self.rooms[room_in_dir])
                for d in next_dirs:
                    room_in_next_dir = self.get_room_in_dir(current_room, d)
                    # enqueue next room's directions in self.explore_path format
                    q.enqueue(list(back_path) +
                              [{'d': d, 'next_room': room_in_next_dir}])