from collections import defaultdict
import json
from typing import NamedTuple, List, Mapping
from utils import *
from pathlib import Path
import pickle


class Hall(NamedTuple):
    id: str
    name: str

    def dict(self):
        return self._asdict()

class Floor(NamedTuple):
    id: int
    number: str
    name: str
    svg: str
    halls: Mapping[int, Hall]

    def dict(self):
        d = self._asdict().copy()
        del d['halls']
        return d


class Building(NamedTuple):
    id: int
    name: str
    address: str
    img: str
    coords: str
    path: str
    brief: str
    tel: str
    floors: Mapping[int, Floor]

    def dict(self):
        d = self._asdict().copy()
        del d['floors']
        return d



src_json = '/home/roman/Downloads/MuseumData/buildings.json'
backup_path = Path(__file__).parent / 'buildings.pkl'


def building_from_json():
    with open(src_json, 'r', encoding='utf-8') as f:
        data = json.load(f)

    buildings = {}

    for i, content in data.items():
        floors = content.get('floors')
        floors_mapping: Mapping[int, Floor] = {}
        if floors:
            for fid, floor in floors.items():
                hall_mapping: Mapping[int, Hall] = {}
                halls = floor.get('halls')

                if halls is not None:
                    for hid, hall in halls.items():
                        hall_mapping[int(hid)] = Hall(int(hid), hall['name']['ru'])

                floors_mapping[int(fid)] = Floor(
                    int(fid),
                    maybe_get(floor, 'number'),
                    maybe_get(floor, 'name'),
                    maybe_get(floor, 'plan'),
                    hall_mapping
                )

        buildings[int(i)] = Building(
            int(i),
            maybe_get(content, 'name'),
            maybe_get(content, 'adress'),
            maybe_get(content, 'img'),
            maybe_get(content, 'yamapcoords'),
            maybe_get(content, 'path'),
            maybe_get(content, 'brief'),
            maybe_get(content, 'tel'),
            floors_mapping
        )

    print(buildings)
    return buildings


def create_serialized():
    buildings = building_from_json()

    with backup_path.open('wb') as f:
        pickle.dump(buildings, f)


def load_serialized():
    try:
        with backup_path.open('rb') as f:
            return pickle.load(f)
    except:
        create_serialized()
        with backup_path.open('rb') as f:
            return pickle.load(f)


def find_building(id):
    if isinstance(id, str):
        id = int(id)

    return load_serialized().get(id)

def find_location(id):
    if isinstance(id, str):
        id = int(id)

    buildings = load_serialized()
    if id in buildings:
        return (buildings[id],)

    for b_id, b in buildings.items():
        if id in b.floors:
            return b.floors[id], b

        for f_id, f in b.floors.items():
            if id in f.halls:
                return f.halls[id], f, b

    return None


def find_human_readable(id):
    out = find_location(id)
    if out is None:
        return None

    if len(out) == 1:
        return {'text': f'{out[0].name}, адрес: {out[0].brief}', 'ref': out[0].dict()}

    if len(out) == 2:
        return {'text': f'{out[0].number} этаж, {out[1].name}', 'ref': out[0].dict()}

    if len(out) == 3:
        return {'text': f'Зал {id} ({out[0].name}), на {out[1].number} этаже, {out[2].name}',
                'ref': out[0]._asdict()}


if __name__ == '__main__':
    print(find_human_readable(126))
    # Building.__dict__
