import multiprocessing

from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

import champion
from champion_functions import MILLIS


class InputModel(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


test_json = {"blue": [{"name": "nami", "stars": "1", "items": [], "y": "3", "x": "4"},
                      {"name": "ashe", "stars": "1", "items": [], "y": "2", "x": "1"},
                      {"name": "kayn", "stars": "1", "items": [], "y": "2", "x": "2"},
                      {"name": "kindred", "stars": "1", "items": [], "y": "2", "x": "4"},
                      {"name": "aphelios", "stars": "1", "items": [], "y": "1", "x": "3"}],
             "red": [{"name": "azir", "stars": "1", "items": [], "y": "7", "x": "2"},
                     {"name": "ashe", "stars": "1", "items": [], "y": "6", "x": "2"},
                     {"name": "kindred", "stars": "1", "items": [], "y": "6", "x": "3"},
                     {"name": "aphelios", "stars": "1", "items": [], "y": "5", "x": "4"},
                     {"name": "ezreal", "stars": "1", "items": [], "y": "5", "x": "5"}]}


app = FastAPI()


def run():
    team_data = test_json
    iterations_data = 1

    # filename = datetime.datetime.now().strftime("%H:%M:%S")
    filename = 'file1'
    jobs = []

    if team_data:
        for i in range(1, iterations_data + 2):
            # if status.get() == 'idle':
            #     break

            try:
                champion.run(champion.champion, team_data)
            except Exception as e:
                print(e)
                champion.test_multiple['bugged out'] += 1

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


@app.put("/run/{json}")
async def run_simulate(model: InputModel):
    print(model)
    return model
