import sqlite3
import pendulum
import requests
from airflow.decorators import task, task_group

from airflow.models.dag import dag


database = "zelda.sqlite"


@dag(start_date=pendulum.now(), catchup=False, schedule="@daily")
def zelda_dag():

    def get_data(endpoint):
        data = []
        page = 0

        response = requests.get(url=f"https://zelda.fanapis.com/api/" + endpoint + "?page=" + str(page)).json()
        # big complex object
        while response["count"] > 0:
            data += response["data"]
            page += 1
            response = requests.get(url=f"https://zelda.fanapis.com/api/" + endpoint + "?page=" + str(page)).json()
        return data

    @task # task for creating the sql schema of the database
    def create_schema():
        con = sqlite3.connect(database)
        cursor = con.cursor()

        with open("create-tables.sql") as f:
            schema = f.read()
        cursor.executescript(schema)
        con.commit()
        con.close()

    @task
    def get_games():
        return get_data("games")

    @task
    def get_staff():
        return get_data("staff")

    @task
    def get_monsters():
        return get_data("monsters")

    @task
    def get_items():
        return get_data("items")

    @task
    def insert_games(games):
        con = sqlite3.connect(database)
        cursor = con.cursor()
        # only extract the required data, dict, keys
        data = [(g["id"], g["name"], g["description"], g["developer"], g["publisher"], g["released_date"]) for g in
                games]
        cursor.executemany("REPLACE INTO game VALUES (?, ?, ?, ?, ?, ?)", data) # SQL template, data
        con.commit()
        con.close()

    @task
    def insert_staff(staff):
        con = sqlite3.connect(database)
        cursor = con.cursor()
        data = [(s["id"], s["name"]) for s in staff]
        cursor.executemany("REPLACE INTO staff VALUES (?, ?)", data) # SQL template, data

        for employee in staff:
            for game in employee["worked_on"]:
                game_id = game.split("/")[-1]
                cursor.execute("REPLACE INTO game_staff VALUES (?, ?)", (game_id, employee["id"]))
        con.commit()
        con.close()

    @task
    def insert_monsters(monsters):
        con = sqlite3.connect(database)
        cursor = con.cursor()
        data = [(m["id"], m["name"], m["description"]) for m in monsters]
        cursor.executemany("REPLACE INTO monster VALUES (?, ?, ?)", data) # SQL template, data

        for m in monsters:
            for game in m["appearances"]:
                game_id = game.split("/")[-1]
                cursor.execute("REPLACE INTO game_monster VALUES (?, ?)", (game_id, m["id"]))

        con.commit()
        con.close()

    @task
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

    @task_group # task group for the first tasks of the workflow
    def get_and_insert_games():
        games = get_games()
        insert_games(games)

    @task_group # task group for the following tasks
    def get_and_insert_staff_monsters_items():
        staff = get_staff()
        insert_staff(staff)
        monsters = get_monsters()
        insert_monsters(monsters)
        items = get_items()
        insert_items(items)
# execution of the tasks
    create_schema() >> get_and_insert_games() >> get_and_insert_staff_monsters_items()


zelda_dag()
