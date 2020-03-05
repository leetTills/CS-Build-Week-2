import json
import requests
from urls import base, end, post, get
from utils import Queue, Stack, Graph, dirs_reversal
from random import choice
import os


# init endpoint - loads current room
data = get(end['init'])

gr = Graph()    
gr.add_vertex(data)
# print(gr.rooms)
# map_data = {}

# map_data[data['room_id']] = data

# print("map_data", map_data)


visited = set()
while len(visited) < 500:
    dfs = gr.dfs(data)

    curr_room = gr.rooms[dfs[-1]]
    for room_id in dfs:
        visited.add(room_id)
    print('visited rooms ---->', visited)
    unexplored_dirs = gr.get_unexplored_dir(curr_room)
    data = curr_room
    if not len(unexplored_dirs):
        data = gr.backtrack_to_unex(curr_room)
    print("current room ---->", data)




"""
After traversal
"""

with open('map.json', 'w') as outfile:
  json.dump(gr.rooms, outfile)