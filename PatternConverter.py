from Stroke import Stroke
from TactileBrush import TactileBrush
import json
from sortedcontainers import SortedList

EPSILON = 0.001

class Point:
    def __init__(self, x : int, y : int):
        self.x = int(x)
        self.y = int(y)
    
    def __repr__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def __key(self):
        return (self.x, self.y)

    def __eq__(self, value):
        if isinstance(value, Point):
            return self.__key() == value.__key()

        return NotImplemented

    def __hash__(self):
        h = hash(self.__key())
        return h

class ActuatorValue:
    __slots__ = ("pin", "value")

    def __init__(self, pin : int, value : float):
        self.pin = pin
        self.value = value

class Frame:
    __slots__ = ("time", "actuators")

    def __init__(self, time : float):
        self.time = time
        self.actuators = set()

class VibrationPattern:
    __slots__ = ("isLooped", "duration", "interpolation", "frames")
    
    def __init__(self, duration : float, is_looped : bool, interpolation : int):
        self.duration = duration
        self.isLooped = is_looped
        self.interpolation = interpolation
        self.frames = SortedList(key = lambda frame: frame.time) # sort frames by time

    def add_frame(self, frame : Frame):
        for f in self.frames:
            time = abs(f.time - frame.time)
            if time < EPSILON:
                f.actuators |= frame.actuators
                return
        
        self.frames.add(frame)
    
    def to_json(self):
        d = dict()
        d["isLooped"] = self.isLooped
        d["duration"] = self.duration / 1000.0
        d["interpolation"] = self.interpolation
        d["frames"] = list()
        for f in self.frames:
            fr = dict()
            fr["time"] = f.time / 1000.0
            fr["actuators"] = list()
            for actuator in f.actuators:
                a = dict()
                a["pin"] = actuator.pin
                a["value"] = actuator.value 
                fr["actuators"].append(a)
            d["frames"].append(fr)

        return json.dumps(d, indent=4, sort_keys=True)

class Config:
    with open('config.json') as json_file:
        config = json.load(json_file)
        lines = config["grid"]["lines"]
        columns = config["grid"]["columns"]
        spacing = config["grid"]["spacing"]
        mapping = dict()
        for coord in config["mapping"]:
            coords_list = coord.split(",")
            mapping[Point(coords_list[0], coords_list[1])] = int(config["mapping"][coord])

def create_pattern(motion : dict):
    pattern = VibrationPattern(duration, False, 0)

    for activation_time, steps in motion.items():    
        # Create starting frame
        start_frame = Frame(activation_time)    
        for step in steps:
            # Calculate end time
            end_time = max(0, min(activation_time + step.duration, pattern.duration))
            point = Point(step.column, step.line)
            # Get pin from config
            pin = Config.mapping[point]
            value = step.intensity
            # Add to starting frame
            start_frame.actuators.add(ActuatorValue(pin, value))
            # Create end frame
            end_frame = Frame(end_time)
            end_frame.actuators.add(ActuatorValue(pin, 0.0))
            # Add frames
            pattern.add_frame(start_frame)
            pattern.add_frame(end_frame)

    return pattern


def get_position_from_string(s : str):
    s = s.strip() # remove whitespace
    pos_x = 0
    pos_y = 0
    try:
        split = s.split(',')
        pos_x = float(split[0])
        pos_y = float(split[1])
    except Exception as e:
        raise Exception("Invalid position was passed. Format must be 'x,y.")

    return pos_x, pos_y

def get_duration_from_string(s : str):
    s = s.strip()
    duration = 0
    try:
        duration = float(s)
    except Exception as e:
        raise Exception("Invalid duration was passed. A decimal value must be passed.")

    return duration
        

if __name__ == "__main__":
    print("Enter stroke start position (x,y):")
    start_str = input()
    start_x, start_y = get_position_from_string(start_str)

    print("Enter stroke start position (x,y):")
    end_str = input()
    end_x, end_y = get_position_from_string(end_str)

    print("Enter duration of stroke in msec:")
    duration_str = input()  
    duration = get_duration_from_string(duration_str)

    t = TactileBrush(Config.lines, Config.columns, Config.spacing)
    s = Stroke(start_x, start_y, end_x, end_y, duration, 1)

    motion = t.compute_stroke_steps(s)
    pattern = create_pattern(motion)
    print("Json Pattern:\n")
    print(pattern.to_json())