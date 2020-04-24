from sortedcontainers import SortedSet
import math
EPSILON = 0.001

def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K:
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K

class Pair:
    __slots__ = "first", "second"
    
    def __repr__(self):
        return "(" + str(self.first) + ", " + str(self.second) + ")"

class ActuatorPoint(Pair):
    __slots__= "first", "second", "start", "durations", "timer_max_intensity"

    def __init__(self, x : float, y : float):
        self.first = x
        self.second = y
        self.timer_max_intensity = 0.0
        self.durations = Pair()
        self.start = 0.0

    def get_duration(self):
        return float(self.durations.first) + float(self.durations.second)

    def get_start(self):
        return self.start

    def __key(self):
        return (self.first, self.second)

    def __repr__(self):
        return "(" + str(self.first) + ", " + str(self.second) + ")"

    def __str__(self):
        return "Virtual actuator at position (" + str(self.first) + ", " + str(self.second) + ") cm" + \
               " triggered at " + str(self.start) + " ms for " + str(self.get_duration()) + " msec. " + \
               "Max intensity reached at " + str(self.timer_max_intensity) + " msec."

    def __eq__(self, value):
        if isinstance(value, ActuatorPoint):
            return self.__key() == value.__key()

        return NotImplemented

    def __hash__(self):
        return hash(self.__key())

    def __gt__(self, value):        
        if self.first == value.first:
            return self.second > value.second
        return self.first > value.first


class Stroke:
    __slots__ = "_startX", "_startY", "_endX", "_endY", "_duration", "_intensity", "_start", "_end", "_virtual_points"

    def __init__(self, startX : float, startY : float, endX : float, endY : float, duration : float, intensity : float):
        self._startX = startX
        self._startY = startY
        self._endX = endX
        self._endY = endY
        self._duration = duration
        self._intensity = intensity
        self._virtual_points = []
        self._start = ActuatorPoint(0,0)
        self._end = ActuatorPoint(0,0)

    def compute_parameters(self, lines : float, columns : float, inter_dist : float):
        self._compute_virtual_points(lines, columns, inter_dist)
        self._compute_max_intensity_timers()
        self._compute_durations_and_SOAs()
        return self._virtual_points

    def get_duration(self):
        return self._duration

    def get_intensity(self):
        return self._intensity

    def get_start(self):
        return self._start

    def get_end(self):
        return self._end

    def pretty_print(self):
        for p in self._virtual_points:
            print(str(p))

    def _cmp(self, a : ActuatorPoint, b : ActuatorPoint):
        diffX = b.first - a.first
        if diffX > EPSILON:
            return -1
        return (1, -1)[abs(diffX) < EPSILON and b.second - a.second > EPSILON]

    def _compute_virtual_points(self, lines : float, columns : float, inter_dist : float):
        self._start = ActuatorPoint(self._startX * inter_dist, self._startY * inter_dist)
        self._end = ActuatorPoint(self._endX * inter_dist, self._endY * inter_dist)

        v = SortedSet(key = cmp_to_key(self._cmp))

        v.add(self._start)

        if abs(self._end.first - self._start.first) < EPSILON:
            for l in range(0, lines):
                c = ActuatorPoint(self._start.first, l * inter_dist)
                if self._is_point_on_stroke(c):
                    v.add(c)

        else:
            coef = (self._end.second - self._start.second) / (self._end.first - self._start.first)
            orig = self._start.second - coef * self._start.first

            for l in range(0, lines):
                y = l * inter_dist

                ant = ActuatorPoint((y - orig)/coef, y)
                if self._is_point_on_stroke(ant):
                    v.add(ant)

                
            for c in range(0, columns):
                x = c * inter_dist
                res = ActuatorPoint(x, coef * x + orig)
                if self._is_point_on_stroke(res):
                    v.add(res)

        v.add(self._end)

        self._virtual_points = list(v.islice(0, len(v)))        

        if self._start > self._end:
            self._virtual_points = reversed(self._virtual_points)

    def _compute_max_intensity_timers(self):
        speed = math.hypot(self._start.first - self._end.first, self._start.second - self._end.second) / self._duration
        begin = self._virtual_points[0]

        for i in range(1, len(self._virtual_points)):
            e = self._virtual_points[i]
            e.timer_max_intensity = math.hypot(e.first - begin.first, e.second - begin.second) / speed

    def _compute_durations_and_SOAs(self):
        sumSOA = 0.0
        self._virtual_points[0].start = 0

        self._virtual_points[0].durations.first = 0

        for i in range(0, len(self._virtual_points) -1):
            current = self._virtual_points[i]
            next = self._virtual_points[i + 1]
            sumSOA += (0.32 * (current.durations.first - sumSOA + next.timer_max_intensity) + 47.3) / 1.32
            next.start = sumSOA
            next.durations.first = current.durations.second = next.timer_max_intensity - sumSOA
        
        last = len(self._virtual_points) - 1
        self._virtual_points[last].durations.first = self._duration - sumSOA
        self._virtual_points[last].durations.second = 0

    def _is_point_on_stroke(self, point : ActuatorPoint):
        seg_dist = math.hypot(self._start.first - self._end.first, self._start.second - self._end.second)
        start_to_point_dist = math.hypot(self._start.first - point.first, self._start.second - point.second)
        point_to_end_dist = math.hypot(self._end.first - point.first, self._end.second - point.second)

        return start_to_point_dist + point_to_end_dist - seg_dist < EPSILON 

if __name__ == "__main__":
    s = Stroke(0, 1, 3, 0, 1000, 1)
    s.compute_parameters(1,3,2.5)
    s.pretty_print()