from urls import post, get, end
from utils import Queue, Stack, Graph, dirs_reversal
from miner import proof_of_work
import json
"""
1. pick up treasure
2. sell treasure (up to 1000 gc)
3. change name
4. get location from well
5. go to location from well, start mining
"""


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

# for room in gr:
#   print(room['items'])

data = get(end['init'])
# print(data)
gr = Graph()
# gr.add_vertex(data)

with open('map.json') as map:
  completed_map = json.load(map)
  for room in completed_map:
    if completed_map[room] == data['room_id']:
      data = completed_map[room]
    gr.add_vertex(completed_map[room])
# print(gr.rooms)

status = post(end['status'], {})
inventory = status['inventory']
gold = int(status['gold'])
name = status['name']
encumbrance = int(status['encumbrance'])
strength = int(status['strength'])

# print(gold)
if status['name'][:4] == 'User':
    rooms_with_items = []
    for room_id, room in gr.rooms.items():
        if len(room['items']):
            rooms_with_items.append(room_id)
    while gold < 1000:
        while encumbrance < strength:
            item_room = rooms_with_items.pop()
            room_with_item = gr.get_path_to_room(data, item_room)
            if len(room_with_item['items']):
                take_item = post(
                    end['take'], {'name': room_with_item['items'][0]})
                gr.rooms[item_room]['items'] = []
                status = post(end['status'], {})
                gold = int(status['gold'])
                encumbrance = int(status['encumbrance'])
                strength = int(status['strength'])
            print("current room ---->", data)
        print(data)
        # 1 is the shop
    #     path = gr.get_path_to_room(data, 1)
    #     print("path -------------->", path)
    #     while len(inventory) > 0:
    #         post(end['sell'], {"name": "treasure"})
    #         post(end['sell'], {"name": "treasure", "confirm": "yes"})
    #         status = post(end['status'], {})
    #         inventory = status['inventory']
    #         gold = int(status['gold'])
    #         encumbrance = int(status['encumbrance'])
    #         print("Status", status)
    # print("was this reached")
    # 467
    print("before")
    path = gr.get_path_to_room(data, 467)
    print("hello")
    print("path to namechanger --------->", path)
    name = input("What is your name? ")
    res = post(end['name'], {"name": f"{name}"})
    confirm = post(end['name'], {"name": f"{name}", "confirm": "aye"})
    print(confirm)
    status = post(end['status'], {})
    print(status)
if status['name'][:4] != 'User':
    # print('status ---->', status)
    # # 55 is wishing well
    # well = gr.get_path_to_room(data, 55)
    # print("wishing well ---->", well)
    # mine_room = gr.get_path_to_room(data, int(
    #     input('Which room is your mining room? ')))
    balance = get(end['bal'])
    print('balance ---->', balance)
    while True:
        last_proof = get(end['lp'])
        next_proof = proof_of_work(last_proof)
        check_proof = post(end['mine'], {'proof': next_proof})
        mine_status = post(end['status'], {})
        print('mine_status ---->', mine_status)
        balance = get(end['bal'])
        print('balance ---->', balance)