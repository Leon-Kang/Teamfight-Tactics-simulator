import json
from datetime import datetime
from typing import List
from pydantic import BaseModel


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# input
class Champion(BaseModel):
    champion: str
    position: str
    star: int
    items: List[str]


class Lineup(BaseModel):
    lineup_id: int
    champions: List[Champion]


class Team(BaseModel):
    team_id: int
    lineups: List[Lineup]


class InputModel(BaseModel):
    test_id: int
    batch_battle_id: int
    blue_lineups_num: int
    red_lineups_num: int
    blue_teams: List[Team]
    red_teams: List[Team]


# output
class OutputTeam:
    def __init__(self, lineup_id, champions):
        self.lineup_id = lineup_id
        self.champions = [OutputChampion(**c) for c in champions]


class OutputChampion:
    def __init__(self, champion, position, star, items):
        self.champion = champion
        self.position = position
        self.star = star
        self.items = items


class BattleResult:
    def __init__(self, test_id, batch_battle_id, blue_lineups_num, red_lineups_num, blue_teams, red_teams):
        self.test_id = test_id
        self.batch_battle_id = batch_battle_id
        self.blue_lineups_num = blue_lineups_num
        self.red_lineups_num = red_lineups_num
        self.blue_teams = [OutputTeam(**t) for t in blue_teams]
        self.red_teams = [OutputTeam(**t) for t in red_teams]


# Parse the JSON data


json_data = '''
{
  "test_id": 111233, 
  "batch_battle_id": 11111111, 
  "blue_lineups_num": 1000,
  "red_lineups_num": 500,
  "blue_teams": [
    {
      "lineup_id": 123,
      "champions": [
        {
          "champion": "A",
          "position": "(4,2)",
          "star": 1,
          "items": [
            "item1",
            "item2",
            "item3"
          ]
        },
        {
          "champion": "B",
          "position": "(2,3)",
          "star": 1,
          "items": [
            "item1"
          ]
        }
      ]
    },
    {
      "lineup_id": 124,
      "champions": [
        {
          "champion": "A",
          "position": "(4,2)",
          "star": 1,
          "items": [
            "item1",
            "item2",
            "item3"
          ]
        },
        {
          "champion": "B",
          "position": "(2,3)",
          "star": 1,
          "items": [
            "item1"
          ]
        }
      ]
    }
  ],
  "red_teams": [
    {
      "lineup_id": 222,
      "champions": [
        {
          "champion": "A",
          "position": "(4,2)",
          "star": 1,
          "items": [
            "item1",
            "item2",
            "item3"
          ]
        },
        {
          "champion": "B",
          "position": "(2,3)",
          "star": 1,
          "items": [
            "item1"
          ]
        }
      ]
    },
    {
      "lineup_id": 333,
      "champions": [
        {
          "champion": "A",
          "position": "(4,2)",
          "star": 1,
          "items": [
            "item1",
            "item2",
            "item3"
          ]
        },
        {
          "champion": "B",
          "position": "(2,3)",
          "star": 1,
          "items": [
            "item1"
          ]
        }
      ]
    }
  ]
}
'''

battle = BattleResult(**json.loads(json_data))


class ChampionStatus:
    def __init__(self, name, star, position, damage, hp, max_hp, team, c_shield, c_AD, c_items):
        self.stars = star
        self.name = name
        self.position = position
        self.position_move = {'x': 0, 'y': 0}
        self.damage = damage
        self.hp = hp
        self.max_hp = max_hp
        self.team = team
        self.shield = c_shield
        self.AD = c_AD
        self.items = c_items


class ChampionActive:
    def __init__(self, active_type, status, target_stat=None, alive=None, action_id=0, round_team=0):
        if alive is None:
            alive = {'red': 0, 'blue': 0}
        self.round = 0
        # move, attack, dies, mana
        self.type = active_type
        # red, blue
        self.round_team = round_team
        self.champion: ChampionStatus = status
        self.target: ChampionStatus = target_stat
        self.alive = alive
        self.timestamp = datetime.now().__str__()
        self.id = action_id
