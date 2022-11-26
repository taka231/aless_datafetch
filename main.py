import requests
import os
import datetime
import math
import pickle
import json
from pathlib import Path

API = "https://5-data.amae-koromo.com/api/v2/pl4"

def now_timestamp():
    return math.floor(datetime.datetime.now().timestamp()) * 1000

def timestamp_by_date(year, month, day):
    day_0h_0s = datetime.datetime(year, month, day)
    return math.floor(day_0h_0s.timestamp()) * 1000

def get_fetchplayer_url():
    now = now_timestamp()
    today = datetime.datetime.today()
    today_timestamp = timestamp_by_date(today.year, today.month, today.day)
    return f'{API}/games/{now}/{today_timestamp}?limit=500&descending=true&mode=12'

def fetch_game_stats_by_startTime(data, player):
    startTime = data['startTime']
    endTime = data['endTime']
    url = f'{API}/player_extended_stats/{player["id"]}/{startTime}/{endTime}?mode=12'
    data = requests.get(url)
    return data.json()

def player_order(data, player):
    players = data["players"]
    players.sort(key=lambda x: x["score"])
    result = 4
    for player_ in players:
        if player_["accountId"] == player["id"]:
            return result
        else:
            result -= 1
def player_level(data, player):
    level = [i["level"] for i in data["players"] if i["accountId"] == player["id"]][0]
    if level == 10401:
        return "gou1"
    elif level == 10402:
        return "gou2"
    elif level == 10403:
        return "gou3"
    elif level == 10501:
        return "sei1"
    elif level == 10502:
        return "sei2"
    else:
        return "sei3"

def generate_filename(date):
    return f'{date.year}-{date.month}-{date.day}.json'

def get_player_stats(player):
    now = now_timestamp()
    timestamp_2022_1_1 = timestamp_by_date(2018, 1, 1)
    player_records_url = f'{API}/player_records/{player["id"]}/{now}/{timestamp_2022_1_1}?limit=500&mode=12&descending=false'
    data = requests.get(player_records_url)
    if data.status_code != 200: return data.status_code
    data = data.json()[::-1]
    date = datetime.datetime.fromtimestamp(data[0]['startTime'])
    result = []
    for item in data:
        date2 = datetime.datetime.fromtimestamp(item['startTime'])
        stats = fetch_game_stats_by_startTime(item, player)
        stats["order"] = player_order(item, player)
        if (date.year, date.month, date.day) == (date2.year, date2.month, date2.day):
            result.append(stats)
        else:
            if len(result) >= 4:
                level = player_level(item, player)
                filename = generate_filename(date)
                dir_path = f'{level}/{player["id"]}'
                os.makedirs(dir_path, exist_ok=True)
                with open(f'{dir_path}/{filename}', 'w') as f:
                    json.dump(result, f, ensure_ascii=False)
                print(result)
            result = [stats]
            date = date2
    return 200
def main():
    os.makedirs("gou1", exist_ok=True)
    os.makedirs("gou2", exist_ok=True)
    os.makedirs("gou3", exist_ok=True)
    os.makedirs("sei1", exist_ok=True)
    os.makedirs("sei2", exist_ok=True)
    os.makedirs("sei3", exist_ok=True)
    player_set = set()
    if os.path.isfile("players"):
        f = open("players", "rb")
        player_set = pickle.load(f)
        print(player_set)
        f.close
    else:
        Path("players").touch(exist_ok=True)
    url = get_fetchplayer_url()
    data = requests.get(url)
    print(data.status_code)
    data = data.json()
    players = [{'id': i['accountId'], 'rank': i['level']} for item in data for i in item['players']]
    for player in players:
        if player["id"] in player_set: continue
        status = get_player_stats(player)
        if status != 200: continue
        player_set.add(player["id"])
        with open("players", "wb") as f:
            pickle.dump(player_set, f)

if __name__ == "__main__":
    main()
