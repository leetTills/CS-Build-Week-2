import json
import requests
import hashlib
import os
import time
# Globals

url = 'https://lambda-treasure-hunt.herokuapp.com/api/bc/'
headers = {'Authorization': f'Token ', 'Content-Type': 'application/json'}
hr = "---------------------------------"
while True:
    proof_response = requests.get(f"{url}last_proof/", headers=headers )
    repsonse = ""
    last_proof = ""
    try:
        repsonse = json.loads(proof_response.content)
    except:
        print(f"Waiting")
        break
    repsonse = json.loads(proof_response.content)
    try:
        last_proof = repsonse['proof']
    except:
        print(f"Missing last proof")
        break
    diff = repsonse['difficulty']
    proof = 101010101
    print(f"{hr} \n{proof_response}")
    print(f" proof: {repsonse['proof']}")
    print(f" difficulty: {repsonse['difficulty']}")
    print(f" cooldown: {repsonse['cooldown']}")
    print(f" messages: {repsonse['messages']}")
    print(f" errors: {repsonse['errors']}")
    while True:
        hash = hashlib.sha256((f'{last_proof}'+f'{proof}').encode()).hexdigest()
        if hash[:diff] == "0" * diff:
            print(f'proof found {proof}')
            break
        else:
            proof += 333
    data = {'proof': proof}
    print(f"This is being sent to mine {data}")
    response = requests.post(f"{url}mine/", headers=headers, data = json.dumps(data) )
    json_response = json.loads(response.content)
    print(f"all response: {json_response} \n", json_response["cooldown"])
    time.sleep(int(json_response["cooldown"] + 1))
    if len(json_response["messages"]) > 0:
        break