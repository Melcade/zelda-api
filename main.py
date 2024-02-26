import sqlite3

import requests

database = "zelda.sqlite"


def get_data(endpoint):
    data = []
    page = 0

    response = requests.get(url="https://zelda.fanapis.com/api/" + endpoint + "?page=" + str(page)).json()
    while response["count"] > 0:
        data += response["data"]
        page += 1
        response = requests.get(url=f"https://zelda.fanapis.com/api/" + endpoint + "?page=" + str(page)).json()
    return data


def create_schema():
    con = sqlite3.connect(database)
    cursor = con.cursor()

    with open("create-tables.sql") as f:
        schema = f.read()

    cursor.executescript(schema)
    con.commit()
    con.close()


def insert_games(games):
    con = sqlite3.connect(database)
    cursor = con.cursor()
    data = [(g["id"], g["name"], g["description"], g["developer"], g["publisher"], g["released_date"]) for g in games]
    cursor.executemany("REPLACE INTO game VALUES (?, ?, ?, ?, ?, ?)", data)   # SQL template, data
    con.commit()
    con.close()


def insert_staff(staff):
    con = sqlite3.connect(database)
    cursor = con.cursor()
    data = [(s["id"], s["name"]) for s in staff]
    cursor.executemany("REPLACE INTO staff VALUES (?, ?)", data)  # SQL template, data

    for employee in staff:
        for game in employee["worked_on"]:
            game_id = game.split("/")[-1]  # Get only the game ID out of the string
            cursor.execute("REPLACE INTO game_staff VALUES (?, ?)", (game_id, employee["id"]))
    con.commit()
    con.close()


def insert_monsters(monsters):
    con = sqlite3.connect(database)
    cursor = con.cursor()
    data = [(m["id"], m["name"], m["description"]) for m in monsters]
    cursor.executemany("REPLACE INTO monster VALUES (?, ?, ?)", data)  # SQL template, data

    for m in monsters:
        for game in m["appearances"]:
            game_id = game.split("/")[-1]
            cursor.execute("REPLACE INTO game_monster VALUES (?, ?)", (game_id, m["id"]))
    con.commit()
    con.close()


def insert_items(items):
    con = sqlite3.connect(database)
    cursor = con.cursor()
    data = [(i["id"], i["name"], i["description"]) for i in items]
    cursor.executemany("REPLACE INTO item VALUES (?, ?, ?)", data)  # SQL template, data

    for i in items:
        for game in i["games"]:
            game_id = game.split("/")[-1]
            cursor.execute("REPLACE INTO game_item VALUES (?, ?)", (game_id, i["id"]))

    con.commit()
    con.close()


if __name__ == '__main__':
    create_schema()

    games = get_data("games")
    insert_games(games)

    staff = get_data("staff")
    insert_staff(staff)

    monsters = get_data("monsters")
    insert_monsters(monsters)

    items = get_data("items")
    insert_items(items)
