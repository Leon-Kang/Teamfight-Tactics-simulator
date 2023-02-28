import json
import multiprocessing

from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

import champion
from ModelClass import InputModel
from champion_functions import MILLIS

test_json = {"blue": [{"name": "aatrox", "stars": "1", "items": [], "y": "3", "x": "4"},
                      {"name": "fiora", "stars": "1", "items": [], "y": "2", "x": "1"},
                      {"name": "veigar", "stars": "1", "items": [], "y": "2", "x": "2"},
                      {"name": "zed", "stars": "1", "items": [], "y": "2", "x": "4"},
                      {"name": "akali", "stars": "1", "items": [], "y": "1", "x": "3"}],
             "red": [{"name": "sylas", "stars": "1", "items": [], "y": "7", "x": "2"},
                     {"name": "vayne", "stars": "1", "items": [], "y": "6", "x": "2"},
                     {"name": "garen", "stars": "1", "items": [], "y": "6", "x": "3"},
                     {"name": "vi", "stars": "1", "items": [], "y": "5", "x": "4"},
                     {"name": "warwick", "stars": "1", "items": [], "y": "5", "x": "5"}]}

app = FastAPI()


def run_model(model: InputModel):
    result = {}
    data = []
    for b_team in model.blue_teams:
        blue_teams = []
        for t in b_team.champions:
            team = {'name': t.champion, 'stars': int(t.star), 'items': t.items, 'y': t.position.y, 'x': t.position.x}
            blue_teams.append(team)
        for r_team in model.red_teams:
            red_teams = []
            for r in r_team.champions:
                r_champion = {'name': r.champion, 'stars': int(r.star), 'items': r.items, 'y': r.position.y,
                              'x': r.position.x}
                red_teams.append(r_champion)
            team_data = {'blue': blue_teams, 'red': red_teams}
            print(team_data)
            champion.run(champion.champion, team_data, model)
            data.append(champion.get_result())
    result['data'] = data
    return result


def run():
    team_data = test_json
    iterations_data = 1

    # filename = datetime.datetime.now().strftime("%H:%M:%S")
    # 文件夹按照：batch_battle_id -> battle_id -> xxxx.log
    filename = 'file1'
    jobs = []

    if team_data:
        for i in range(1, iterations_data + 2):
            # if status.get() == 'idle':
            #     break
            champion.run(champion.champion, team_data)
            # try:
            #     champion.run(champion.champion, team_data)
            # except Exception as e:
            #     print(e)
            #     champion.test_multiple['bugged out'] += 1

            with open(filename + '.txt', 'a') as out:
                if MILLIS() < 75000:
                    if champion.log[-1] == 'BLUE TEAM WON':
                        champion.test_multiple['blue'] += 1
                    if champion.log[-1] == 'RED TEAM WON':
                        champion.test_multiple['red'] += 1
                elif MILLIS() < 200000:
                    champion.test_multiple['draw'] += 1
                for line in champion.log:
                    out.write(str(line))
                    out.write('\n')
            out.close()

    champion.test_multiple = {'blue': 0, 'red': 0, 'bugged out': 0, 'draw': 0}


if __name__ == '__main__':
    run()


@app.put("/run/{test_id}")
async def run_simulate(model: InputModel):
    result = run_model(model)
    return result
