import json
from datetime import datetime
from typing import List
from pydantic import BaseModel


class Position(BaseModel):
    x: int
    y: int


# input
class Champion(BaseModel):
    champion: str
    position: Position
    star: int
    items: List[str]


class Lineup(BaseModel):
    lineup_id: int
    champions: List[Champion]


class InputModel(BaseModel):
    test_id: int
    batch_battle_id: int
    blue_lineups_num: int
    red_lineups_num: int
    blue_teams: List[Lineup]
    red_teams: List[Lineup]


# output
class OutputTeam:
    def __init__(self, lineup_id, champions):
        self.lineup_id = lineup_id
        self.champions = [OutputChampion(**c) for c in champions]


class PositionClass:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class OutputChampion:
    def __init__(self, champion, position, star, items):
        self.champion = champion
        self.position: PositionClass = position
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


class ChampionStatus:
    def __init__(self, name, star, position, hp, max_hp, team, c_shield, c_items):
        self.stars = star
        self.name = name
        self.position = position
        # self.position_move = {'x': 0, 'y': 0}
        self.hp = hp
        self.max_hp = max_hp
        self.team = team
        self.shield = c_shield
        self.items = c_items


class ChampionActive:
    def __init__(self, active_type, status, target_stat=None, alive=None):
        if alive is None:
            alive = {'red': 0, 'blue': 0}
        # move, attack, dies, mana
        self.type = active_type
        # red, blue
        self.agent: ChampionStatus = status
        self.recipient: ChampionStatus = target_stat
        self.survive = alive
        self.timestamp = datetime.now().timestamp().__str__()


class AttacksActive(ChampionActive):
    def __init__(self, status, target_stat, crit, damage):
        super().__init__('attacks', status, target_stat)
        self.crit = crit
        self.damage = damage
        self.trait_attack = 0
        self.trait_string = ''
        self.millis = 0
        self.ability = False


class HealActive(ChampionActive):
    def __init__(self, status, heal):
        super().__init__('heal', status, heal)
        self.heal = heal
        self.millis = 0


class Output:
    def __init__(self, won='', test_id='', batch_battle_id=0,
                 origin_red=None, origin_blue=None, final_lineup=None):
        if origin_red is None:
            origin_red = []
        if origin_blue is None:
            origin_blue = []
        if final_lineup is None:
            final_lineup = []

        self.test_id = test_id
        self.batch_battle_id = batch_battle_id
        self.won_team = won
        self.origin_red = [OutputTeam(**t) for t in origin_red]
        self.origin_blue = [OutputTeam(**t) for t in origin_blue]
        self.final_lineup = [OutputTeam(**t) for t in final_lineup]
        self.millis = 0
        self.startTime = datetime.now().timestamp().__str__()
        self.endTime = datetime.now().timestamp().__str__()
        self.match_id = ''
        self.blue_damages_total = 0
        self.red_damages_total = 0

    def get_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class StoryLog(Output):
    def __init__(self, actions=None):
        super().__init__()
        if actions is None:
            actions = []
        self.actions: [ChampionActive] = actions
        self.blue_damages = []
        self.red_damages = []

    def get_values(self, parent: Output):
        self.millis = parent.millis
        self.test_id = parent.test_id
        self.batch_battle_id = parent.batch_battle_id
        self.won_team = parent.won_team
        self.origin_red = parent.origin_red
        self.origin_blue = parent.origin_blue
        self.final_lineup = parent.final_lineup
        self.startTime = parent.startTime
        self.endTime = parent.endTime
        self.match_id = parent.match_id
