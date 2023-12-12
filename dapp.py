from os import environ
import logging
import requests
import json

from eth_abi_ext import decode_packed

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

rollup_server = "http://localhost:8080/host-runner"
logger.info(f"HTTP rollup_server url is {rollup_server}")

# Setup contracts addresses
ETHERPortalFile = open(f'./EtherPortal.json')
etherPortal = json.load(ETHERPortalFile)

BALANCES = {}
BETS = {}


# Utils _________________________________________________________________
def hex2str(hex):
    """
    Decodes a hex string into a regular string
    """
    return bytes.fromhex(hex[2:]).decode("utf-8")


def str2hex(str):
    """
    Encodes a string as a hex string
    """
    return "0x" + str.encode("utf-8").hex()


# Getters _______________________________________________________________
# Retorna o saldo do usuário
def getBalance(payload):
        user_id = payload["user_id"]
        if user_id not in BALANCES:
            BALANCES[user_id] = 0
        balance = BALANCES[user_id]
        return [{"balance": balance}]

def getAllBets():
    bets_with_owner_address = []
    for betOwnerAddress, bets in BETS.items():
        for bet in bets:
            bet_copy = bet.copy()
            bet_copy['betOwnerAddress'] = betOwnerAddress
            bets_with_owner_address.append(bet_copy)
    return bets_with_owner_address


# Setters _______________________________________________________________

# Adiciona na carteira do usuário
def add_balance(data):
    binary = bytes.fromhex(data)
    try:
        decoded = decode_packed(['address', 'uint256'], binary)
        user_id = decoded[0]
        amount = decoded[1]
        if user_id not in BALANCES:
            BALANCES[user_id] = 0
        BALANCES[user_id] += amount
        return 'accept'
    except Exception as e:
        msg = "Payload does not conform to ETHER deposit ABI"
        logger.error(f"{msg}\n{traceback.format_exc()}")
        return reject_input(msg, data["payload"])
    

def reject_input(msg, payload):
    logger.error(msg)
    response = requests.post(rollup_server + "/report",
                             json={"payload": payload})
    logger.info(
        f"Received report status {response.status_code} body {response.content}")
    return "reject"


def create_bet(payload):
    betValue = payload["betValue"];
    betOwnerAddress = payload["betOwnerAddress"];
    matchId = payload["matchId"];
    betOwnerType = payload["betOwnerType"];

    if betOwnerAddress not in BALANCES or BALANCES[betOwnerAddress] < betValue:
        return "reject"
  
    if betOwnerAddress not in BETS:
        BETS[betOwnerAddress] = []
    BETS[betOwnerAddress].append({
        "matchId": matchId,
        "betValue": betValue,
        "betOwnerType": betOwnerType,
    })

    BALANCES[betOwnerAddress] -= betValue

    logger.info(f"Creating bet with payload {payload}")
    return "accept"



# Selectors _____________________________________________________________

def select_function_advance(payload):
    function_id = int(payload["function_id"])
    function_map = {
        1: lambda: create_bet(payload),
    }

    function = function_map.get(function_id)
    if function:
        return function()
    else:
        print("Function not found")



def select_function_inspect(payload):
    function_id = int(payload["function_id"])
    function_map = {
        0 : lambda: getBalance(payload),
        2 : lambda: getAllBets(), 
    }

    function = function_map.get(function_id)
    if function:
        result = function()
        return result
    else:
        return "Function not found"



def handle_advance(data):
    logger.info(f"Received advance request data {data}")
    try:
        if data["metadata"]["msg_sender"].lower() == etherPortal['address'].lower():
            return add_balance(data["payload"][2:])
        decode = hex2str(data["payload"])
        payload = json.loads(decode)
        payload["seed"] = data["payload"]
        response = select_function_advance(payload)
        return response
    except Exception as e:
        print("Error: ", e)
        return "reject"


def handle_inspect(data):
    decode = hex2str(data["payload"])
    payload = json.loads(decode)
    response = select_function_inspect(payload)
    responseToString = '\n'.join([str(offer) for offer in response])
    encoded = str2hex(responseToString)
    report = {"payload": encoded}
    response = requests.post(rollup_server + "/report", json=report)
    logger.info(f"Received report status {response.status_code}")
    return "accept"


handlers = {
    "advance_state": handle_advance,
    "inspect_state": handle_inspect,
}

finish = {"status": "accept"}

while True:
    logger.info("Sending finish")
    response = requests.post(rollup_server + "/finish", json=finish)
    logger.info(f"Received finish status {response.status_code}")
    if response.status_code == 202:
        logger.info("No pending rollup request, trying again")
    else:
        rollup_request = response.json()
        handler = handlers[rollup_request["request_type"]]
        finish["status"] = handler(rollup_request["data"])
