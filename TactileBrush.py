from Stroke import ActuatorPoint, Stroke, EPSILON
import math

class ActuatorStep:
    __slots__ = "line", "column", "intensity", "duration", "max_intensity"

    def __init__(self, column : int, line : int, intensity : float, duration : float, max_intensity : float):
        self.column = column
        self.line = line
        self.intensity = intensity
        self.duration = duration
        self.max_intensity = max_intensity
    
    def __str__(self):
        return "Physical actuator at column " + str(self.column) + " and line " + str(self.line) + \
               " triggered for " + str(self.duration) + " msec with intensity " + str(self.intensity)

class TactileBrush:
    __slots__ = "_lines", "_columns", "_inter_dist", "_min_coord", "_max_coord", "_actuator_triggers"

    def __init__(self, lines : int, columns : int, distance : float):
        self._lines = lines - 1
        self._columns = columns - 1
        self._inter_dist = distance
        self._min_coord = ActuatorPoint(0, 0)
        self._max_coord = ActuatorPoint(columns * self._inter_dist, lines * self._inter_dist)
        self._actuator_triggers = { }
    
    def compute_stroke_steps(self, s : Stroke):
        if (self._is_point_within_grid(s.get_start()) and self._is_point_within_grid(s.get_end())) == False:
            raise Exception("Stroke start or end point are out of the grid range.")
        
        virtual_points = s.compute_parameters(self._lines, self._columns, self._inter_dist)
        self._actuator_triggers.clear()
        self._compute_physical_mapping(virtual_points, s.get_intensity())
        return self._actuator_triggers

    def pretty_print(self):
        for p in self._actuator_triggers:
            print("Time " + str(p) + " ms:")
            for s in self._actuator_triggers[p]:
                print("\t " + str(s))

    def _insert_actuator_step(self, time : float, step : ActuatorStep):
        if time in self._actuator_triggers:
            self._actuator_triggers[time].append(step)
            return
        
        self._actuator_triggers[time] = list()
        self._actuator_triggers[time].append(step)

    def _compute_physical_mapping(self, virtual_points : list, global_intensity : float):
        for e in virtual_points:

            if math.fmod(e.first, self._inter_dist) < EPSILON and math.fmod(e.second, self._inter_dist) < EPSILON:
                step = ActuatorStep(round(e.first / self._inter_dist), round(e.second / self._inter_dist), global_intensity, e.get_duration(), e.timer_max_intensity)
                self._insert_actuator_step(e.get_start(), step)
            else:
                l1 = 0
                c1 = 0
                l2 = 0
                c2 = 0

                if math.fmod(e.first, self._inter_dist) < EPSILON:
                    c1 = c2 = round(e.first / self._inter_dist)
                    l1 = math.floor(e.second / self._inter_dist)
                    l2 = math.ceil(e.second / self._inter_dist)

                elif math.fmod(e.second, self._inter_dist) < EPSILON:
                    l1 = l2 = round(e.second / self._inter_dist)
                    c1 = math.floor(e.first / self._inter_dist)
                    c2 = math.ceil(e.first / self._inter_dist)

                else:
                    raise Exception("Virtual actuator at position (" + str(e.first) + ", " + str(e.second) + " is not on the physical actuators grid")

                ratio = math.hypot(c1 - e.first / self._inter_dist, l1 - e.second / self._inter_dist) / math.hypot(c1 - c2, l1 - l2)

                phy1 = ActuatorStep(c1, l1, math.sqrt(1 - ratio) * global_intensity, e.get_duration(), e.timer_max_intensity)
                phy2 = ActuatorStep(c2, l2, math.sqrt(ratio) * global_intensity, e.get_duration(), e.timer_max_intensity)

                self._insert_actuator_step(e.get_start(), phy1)
                self._insert_actuator_step(e.get_start(), phy2)

    def _is_point_within_grid(self, point : ActuatorPoint):
        if point.first < self._min_coord.first or point.first > self._max_coord.first:
            return False
        
        if point.second < self._min_coord.second or point.second > self._max_coord.second:
            return False
        
        return True 


if __name__ == "__main__":
    #t = TactileBrush(2, 4, 2.5)
    #s = Stroke(0, 1, 3, 0, 1000, 1)
    t = TactileBrush(3, 4, 1.5)
    s = Stroke(0.6666, 2, 3, 0.6666, 1000.0, 1.0)
    t.compute_stroke_steps(s)
    t.pretty_print()