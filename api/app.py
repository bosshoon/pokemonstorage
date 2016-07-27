# -*- coding: utf-8 -*-

from datetime import datetime

import flask
from flask import Flask, request
import ipaddress
from api import protoparser, inventory_pb2
app = Flask(__name__)

pokemon_list = []
candies = []
last_updated = None

@app.route("/api/pokemon")
def status():

    global pokemon_list, candies, last_updated

    # Uncomment to load saved flow
#    raw_inventory = open("sampleinventory.bin", "rb").read()
#    (pokemon_list, candies) = split_inventory(raw_inventory)

    json_pokemon = [ {"number" : p.PokemonId,
                      "name" : name_dict[p.PokemonId],
                      "cp" : p.Cp,
                      "height" : p.HeightM,
                      "weight" : p.WeightKg,
                      "familyId" : family_mapping[p.PokemonId],
                      "individualAttack" : p.IndividualAttack,
                      "individualDefense" : p.IndividualDefense,
                      "individualSpeed" : p.IndividualStamina,
                      "ivPercentPerfect" : (p.IndividualAttack + p.IndividualDefense + p.IndividualStamina)/45.0,
                      "creationTimeMs" : p.CreationTimeMs } for p in pokemon_list]

    json_candies = { c.FamilyId : c.Candy for c in candies }

    json = { "pokemon" : json_pokemon, "candyInfo" : json_candies, "lastUpdatedDate" : last_updated }

    return flask.jsonify(meta = {"isSuccess": True}, body = json)

@app.route('/api/update', methods=["POST"])
def update_pokemon():
    global pokemon_list, candies, last_updated

    if last_updated and ((datetime.now() - last_updated).seconds < 10):
        print "ignoring, too soon"
        return ''

    if not ipaddress.ip_address(unicode(request.remote_addr)).is_private:
        print "Invalid ip ({}) trying to POST to update".format(request.remote_addr)
        return ''

    raw_data = request.get_data(cache=False)
    (tmp_pokemon_list, tmp_candies) = split_inventory(raw_data)
    if len(tmp_pokemon_list) > 0:
        print "Updating pokemon inventory, found {} pokemon".format(len(tmp_pokemon_list))

        pokemon_list = tmp_pokemon_list
        candies = tmp_candies
        last_updated = datetime.now()

        # write a sample inventory file
#        f = open("sampleinventory.bin", "wb")
#        f.write(raw_data)
#        f.close()

    return ''

def split_inventory(raw_data):

    message = protoparser.from_raw_data(raw_data)
    if not message or not message[100]: # inventory lives under tag 100
        return ([], [])

    pokemon = []
    candies = []
    for possible_inventory in message[100]:
        try:
            inv = inventory_pb2.GetInventoryOutProto()
            inv.ParseFromString(str(possible_inventory.unwrap()))
            if inv.InventoryDelta:
                for inv_item in inv.InventoryDelta.InventoryItem:
                    if inv_item.Item:
                        if inv_item.Item.Pokemon:
                            pokemon.append(inv_item.Item.Pokemon)
                        if inv_item.Item.PokemonFamily and inv_item.Item.PokemonFamily.FamilyId:
                            candies.append(inv_item.Item.PokemonFamily)
        except Exception as e:
            print "decode error:", e

    pokemon = [p for p in pokemon if p.CapturedS2CellId and not p.IsEgg]

    # sometimes only a partial list is sent during battles and things, wait for
    # a full list
    # TODO: should be using better logic here
    if len(pokemon) > 10:
        return (pokemon, candies)
    else:
        return ([], [])

name_dict = {
    1: "Bulbasaur",
    2: "Ivysaur",
    3: "Venusaur",
    4: "Charmander",
    5: "Charmeleon",
    6: "Charizard",
    7: "Squirtle",
    8: "Wartortle",
    9: "Blastoise",
    10: "Caterpie",
    11: "Metapod",
    12: "Butterfree",
    13: "Weedle",
    14: "Kakuna",
    15: "Beedrill",
    16: "Pidgey",
    17: "Pidgeotto",
    18: "Pidgeot",
    19: "Rattata",
    20: "Raticate",
    21: "Spearow",
    22: "Fearow",
    23: "Ekans",
    24: "Arbok",
    25: "Pikachu",
    26: "Raichu",
    27: "Sandshrew",
    28: "Sandslash",
    29: "Nidoran♀",
    30: "Nidorina",
    31: "Nidoqueen",
    32: "Nidoran♂",
    33: "Nidorino",
    34: "Nidoking",
    35: "Clefairy",
    36: "Clefable",
    37: "Vulpix",
    38: "Ninetales",
    39: "Jigglypuff",
    40: "Wigglytuff",
    41: "Zubat",
    42: "Golbat",
    43: "Oddish",
    44: "Gloom",
    45: "Vileplume",
    46: "Paras",
    47: "Parasect",
    48: "Venonat",
    49: "Venomoth",
    50: "Diglett",
    51: "Dugtrio",
    52: "Meowth",
    53: "Persian",
    54: "Psyduck",
    55: "Golduck",
    56: "Mankey",
    57: "Primeape",
    58: "Growlithe",
    59: "Arcanine",
    60: "Poliwag",
    61: "Poliwhirl",
    62: "Poliwrath",
    63: "Abra",
    64: "Kadabra",
    65: "Alakazam",
    66: "Machop",
    67: "Machoke",
    68: "Machamp",
    69: "Bellsprout",
    70: "Weepinbell",
    71: "Victreebel",
    72: "Tentacool",
    73: "Tentacruel",
    74: "Geodude",
    75: "Graveler",
    76: "Golem",
    77: "Ponyta",
    78: "Rapidash",
    79: "Slowpoke",
    80: "Slowbro",
    81: "Magnemite",
    82: "Magneton",
    83: "Farfetch'd",
    84: "Doduo",
    85: "Dodrio",
    86: "Seel",
    87: "Dewgong",
    88: "Grimer",
    89: "Muk",
    90: "Shellder",
    91: "Cloyster",
    92: "Gastly",
    93: "Haunter",
    94: "Gengar",
    95: "Onix",
    96: "Drowzee",
    97: "Hypno",
    98: "Krabby",
    99: "Kingler",
    100: "Voltorb",
    101: "Electrode",
    102: "Exeggcute",
    103: "Exeggutor",
    104: "Cubone",
    105: "Marowak",
    106: "Hitmonlee",
    107: "Hitmonchan",
    108: "Lickitung",
    109: "Koffing",
    110: "Weezing",
    111: "Rhyhorn",
    112: "Rhydon",
    113: "Chansey",
    114: "Tangela",
    115: "Kangaskhan",
    116: "Horsea",
    117: "Seadra",
    118: "Goldeen",
    119: "Seaking",
    120: "Staryu",
    121: "Starmie",
    122: "Mr.",
    123: "Scyther",
    124: "Jynx",
    125: "Electabuzz",
    126: "Magmar",
    127: "Pinsir",
    128: "Tauros",
    129: "Magikarp",
    130: "Gyarados",
    131: "Lapras",
    132: "Ditto",
    133: "Eevee",
    134: "Vaporeon",
    135: "Jolteon",
    136: "Flareon",
    137: "Porygon",
    138: "Omanyte",
    139: "Omastar",
    140: "Kabuto",
    141: "Kabutops",
    142: "Aerodactyl",
    143: "Snorlax",
    144: "Articuno",
    145: "Zapdos",
    146: "Moltres",
    147: "Dratini",
    148: "Dragonair",
    149: "Dragonite",
    150: "Mewtwo",
    151: "Mew"
}

family_mapping = {
    1: 1,
    2: 1,
    3: 1,
    4: 4,
    5: 4,
    6: 4,
    7: 7,
    8: 7,
    9: 7,
    10: 10,
    11: 10,
    12: 10,
    13: 13,
    14: 13,
    15: 13,
    16: 16,
    17: 16,
    18: 16,
    19: 19,
    20: 19,
    21: 21,
    22: 21,
    23: 23,
    24: 23,
    25: 25,
    26: 25,
    27: 27,
    28: 27,
    29: 29,
    30: 29,
    31: 29,
    32: 32,
    33: 32,
    34: 32,
    35: 35,
    36: 35,
    37: 37,
    38: 37,
    39: 39,
    40: 39,
    41: 41,
    42: 41,
    43: 43,
    44: 43,
    45: 43,
    46: 46,
    47: 46,
    48: 48,
    49: 48,
    50: 50,
    51: 50,
    52: 52,
    53: 52,
    54: 54,
    55: 54,
    56: 56,
    57: 56,
    58: 58,
    59: 58,
    60: 60,
    61: 60,
    62: 60,
    63: 63,
    64: 63,
    65: 63,
    66: 66,
    67: 66,
    68: 66,
    69: 69,
    70: 69,
    71: 69,
    72: 72,
    73: 72,
    74: 74,
    75: 74,
    76: 74,
    77: 77,
    78: 77,
    79: 79,
    80: 79,
    81: 81,
    82: 81,
    83: 83,
    84: 84,
    85: 84,
    86: 86,
    87: 86,
    88: 88,
    89: 88,
    90: 90,
    91: 90,
    92: 92,
    93: 92,
    94: 92,
    95: 95,
    96: 96,
    97: 96,
    98: 98,
    99: 98,
    100: 100,
    101: 100,
    102: 102,
    103: 102,
    104: 104,
    105: 104,
    106: 106,
    107: 106,
    108: 108,
    109: 109,
    110: 109,
    111: 111,
    112: 111,
    113: 113,
    114: 114,
    115: 115,
    116: 116,
    117: 116,
    118: 118,
    119: 118,
    120: 120,
    121: 120,
    122: 122,
    123: 123,
    124: 124,
    125: 125,
    126: 126,
    127: 127,
    128: 128,
    129: 129,
    130: 129,
    131: 131,
    132: 132,
    133: 133,
    134: 133,
    135: 133,
    136: 133,
    137: 137,
    138: 138,
    139: 138,
    140: 140,
    141: 140,
    142: 142,
    143: 143,
    144: 144,
    145: 145,
    146: 146,
    147: 147,
    148: 147,
    149: 147,
    150: 150,
    151: 151
}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

