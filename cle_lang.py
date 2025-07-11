from typing import Dict, Tuple
import time

class SceneObject:
    def __init__(self, name: str, obj_type: str, position: Tuple[float, float, float], scale: Tuple[float, float, float]):
        self.name = name
        self.type = obj_type
        self.position = position
        self.scale = scale

    def move_to(self, new_pos: Tuple[float, float, float]):
        self.position = new_pos

    def __repr__(self):
        return f"<{self.type} '{self.name}': Pos={self.position}, Scale={self.scale}>"

class CleParser:
    def __init__(self):
        self.objects: Dict[str, SceneObject] = {}

    def parse_line(self, line: str):
        line = line.split('#')[0].strip()
        if not line:
            return

        parts = line.split()
        cmd = parts[0].upper()

        if cmd == "CREATE":
            # CREATE <name> TYPE <type / default: Cube> POSITION <x> <y> <z> SCALE <sx> <sy> <sz>
            if len(parts) < 12:
                print(f"Ошибка: слишком короткая команда CREATE: {line}")
                return
            try:
                name = parts[1]
                assert parts[2].upper() == "TYPE"
                obj_type = parts[3]
                assert parts[4].upper() == "POSITION"
                pos = tuple(map(float, parts[5:8]))
                assert parts[8].upper() == "SCALE"
                scale = tuple(map(float, parts[9:12]))
            except (AssertionError, ValueError):
                print(f"Ошибка синтаксиса или парсинга CREATE: {line}")
                return

            obj = SceneObject(name, obj_type, pos, scale)
            self.objects[name] = obj
            print(f"Создан объект: {obj}")

        elif cmd == "MOVE":
            # MOVE <name> TO <x> <y> <z>
            if len(parts) != 6:
                print(f"Ошибка: команде MOVE нужно 5 аргументов: {line}")
                return
            name = parts[1]
            if name not in self.objects:
                print(f"Ошибка: объект {name} не найден для MOVE")
                return
            if parts[2].upper() != "TO":
                print(f"Ошибка синтаксиса MOVE: ожидалось TO: {line}")
                return
            try:
                target_pos = tuple(float(x) for x in parts[3:6])
            except ValueError:
                print(f"Ошибка парсинга координат MOVE: {line}")
                return

            obj = self.objects[name]
            obj.move_to(target_pos)
            print(f"Объект {name} перемещён к {target_pos}")

    def parse_file(self, filepath: str):
        with open(filepath, 'r') as f:
            for line in f:
                self.parse_line(line)

    def get_objects(self):
        return self.objects

def main():
    parser = CleParser()
    while True:
        for obj in parser.get_objects().values():
            print(f"Текущий объект: {obj}")
        time.sleep(1)

if __name__ == "__main__":
    main()
