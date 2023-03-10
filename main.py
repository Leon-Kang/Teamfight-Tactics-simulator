import datetime
import json
import multiprocessing as mp
import os
import zipfile
from io import BytesIO
import uvicorn
from fastapi import FastAPI, BackgroundTasks, Depends
import numpy as np
from starlette.responses import StreamingResponse

import champion
from ModelClass import InputModel

try:
    mp.set_start_method('spawn')
except RuntimeError:
    pass

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
    works = model.num_workers
    tasks_count = min(count, works)
    tasks = np.array_split(blue_teams, tasks_count)
    print(tasks)
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
                log = champion.get_log()
                data.append(result)
                save(str(champion.outputResult.batch_battle_id), champion.outputResult.match_id, log)
            except Exception as e:
                print(e)
                save('error' + str(champion.outputResult.batch_battle_id), champion.outputResult.match_id, e.__str__())

    return data


def save(path, file_name, content):
    file_path = os.path.join(cwd, output, path)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    log_path = os.path.join(file_path, file_name + '.json')
    with open(log_path, 'w') as out:
        print(log_path)
        out.write(content)


def run():
    team_data = test_json

    if team_data:
        champion.run(champion.champion, team_data)


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
        os.rename(file_path, file_path + '-' + datetime.datetime.now().timestamp().__str__())
        return StreamingResponse(
            iter([zip_io.getvalue()]),
            media_type="application/x-zip-compressed",
            headers={f"Content-Disposition": f"attachment; filename={battle_id}.zip"}
        )
    else:
        return 'wrong battle id in: ' + f'{file_path}'


@app.get("/all/battles")
async def get_all_battle():
    file_path = os.path.join(cwd, output)

    if os.path.exists(file_path):
        for root, directories, filenames in os.walk(file_path):
            return directories


# @app.put("/start/task")
# async def run_task(model: InputModel):
#     result = run_model(model)
#     file = model.batch_battle_id
#     data = json.dumps(result)
#     save('response', file, data)
#     return f'FINISHED - Battle id: {file}'

def background_run_model(model):
    result = run_model(model)
    file = model.batch_battle_id
    data = json.dumps(result)
    save('response', file, data)


@app.put("/start/task")
async def run_task(model: InputModel,
                   background_tasks: BackgroundTasks):
    batch_battle_id = model.batch_battle_id
    background_tasks.add_task(background_run_model, model)
    return {"message": f'RECEIVED - Battle id: {batch_battle_id}'}


@app.get("/get/response/{battle_id}")
async def get_battle(battle_id: str):
    file_path = os.path.join(cwd, output, 'response', battle_id + '.json')
    result = None
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            result = json.load(file)
            file.close()
        return result
    return 'No Data'
