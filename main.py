import json
import multiprocessing as mp
import os
import zipfile
from io import BytesIO

from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from starlette.responses import StreamingResponse

import champion
from ModelClass import InputModel
from champion_functions import MILLIS

test_json = {'blue': [{'name': 'pyke', 'stars': 1, 'items': [], 'y': 3, 'x': 2},
                      {'name': 'wukong', 'stars': 1, 'items': [], 'y': 3, 'x': 3},
                      {'name': 'lissandra', 'stars': 1, 'items': [], 'y': 1, 'x': 2},
                      {'name': 'warwick', 'stars': 1, 'items': [], 'y': 1, 'x': 3},
                      {'name': 'irelia', 'stars': 1, 'items': [], 'y': 1, 'x': 4}],
             'red': [{'name': 'tahmkench', 'stars': 1, 'items': [], 'y': 6, 'x': 2},
                     {'name': 'sylas', 'stars': 1, 'items': [], 'y': 6, 'x': 3},
                     {'name': 'cassiopeia', 'stars': 1, 'items': [], 'y': 6, 'x': 4},
                     {'name': 'construct', 'stars': 1, 'items': [], 'y': 4, 'x': 2},
                     {'name': 'jarvaniv', 'stars': 1, 'items': [], 'y': 4, 'x': 3}]}

app = FastAPI()

cwd = os.getcwd()
output = 'output'


def run_model(model: InputModel):
    result = {}
    data = []
    blue_teams = model.blue_teams
    count = len(blue_teams)
    tasks_count = min(count, 4)
    tasks = np.array_split(blue_teams, tasks_count)
    pool = mp.Pool(tasks_count)
    tasks_pool = [pool.apply_async(blue_fight, args=(teams, model)) for teams in tasks]
    for p in tasks_pool:
        data.append(p.get())

    result['data'] = data
    return result


def blue_fight(blue_teams: [], model: InputModel):
    data = []
    for b_team in blue_teams:
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
            try:
                champion.run(champion.champion, team_data, model, r_team.lineup_id, b_team.lineup_id)
                result = champion.get_result()
                data.append(result)
                save(str(champion.outputResult.batch_battle_id), champion.outputResult.match_id, result)
            except Exception as e:
                print(e)

    return data


def save(path, file_name, content):
    file_path = os.path.join(cwd, output, path)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    with open(os.path.join(file_path, file_name + '.json'), 'w') as out:
        print(file_path)
        out.write(content)
    out.close()


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

            # with open(filename + '.txt', 'a') as out:
            #     if MILLIS() < 75000:
            #         if champion.log[-1] == 'BLUE TEAM WON':
            #             champion.test_multiple['blue'] += 1
            #         if champion.log[-1] == 'RED TEAM WON':
            #             champion.test_multiple['red'] += 1
            #     elif MILLIS() < 200000:
            #         champion.test_multiple['draw'] += 1
            #     for line in champion.log:
            #         out.write(str(line))
            #         out.write('\n')
            # out.close()

    champion.test_multiple = {'blue': 0, 'red': 0, 'bugged out': 0, 'draw': 0}


if __name__ == '__main__':
    run()


@app.put("/run/{test_id}")
async def run_simulate(model: InputModel):
    result = run_model(model)
    return result


@app.get("/battle/log/{battle_id}")
async def get_battle(battle_id: str):

    file_path = os.path.join(cwd, output, battle_id)

    if os.path.exists(file_path):
        files = []
        for root, directories, filenames in os.walk(file_path):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        zip_io = BytesIO()
        with zipfile.ZipFile(zip_io, mode='w') as temp_zip:
            for file in files:
                # Add the file to the ZIP file
                temp_zip.write(file, os.path.relpath(file, file_path))
        return StreamingResponse(
            iter([zip_io.getvalue()]),
            media_type="application/x-zip-compressed",
            headers={f"Content-Disposition": f"attachment; filename={battle_id}.zip"}
        )
    else:
        return 'wrong battle id in: ' + f'{file_path}'
