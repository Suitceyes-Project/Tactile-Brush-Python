# Tactile Brush 
This repository contains a python implementation of the original TactileBrush algorithm found [here](https://github.com/Chostakovitch/TactileBrush):

## Requirements
- sortedcontainers : install via `pip install sortedcontainers`

## Example
```python
# Grid with 2 lines and 4 columns with a spacing of 2.5 cm
t = TactileBrush(2, 4, 2.5) 

# Create a stroke that starts at the top left and ends at the bottom right
# Coordinates are given in units (not centimetres!)
s = Stroke(0, 1, 3, 0, 1000, 1) 

# Run algorithm
t.compute_stroke_steps(s)

t.pretty_print()
```

Output of `pretty_print()`:
```
Time 0 ms:
         Physical actuator at column 0 and line 1 triggered for 216.69191919191914 msec with intensity 1
Time 116.64141414141412 ms:
         Physical actuator at column 1 and line 0 triggered for 545.0130088766451 msec with intensity 0.5773502691896257
         Physical actuator at column 1 and line 1 triggered for 545.0130088766451 msec with intensity 0.816496580927726
Time 338.34557698194055 ms:
         Physical actuator at column 2 and line 0 triggered for 714.1481156839282 msec with intensity 0.816496580927726
         Physical actuator at column 2 and line 1 triggered for 714.1481156839282 msec with intensity 0.5773502691896258
Time 614.1729740007977 ms:
         Physical actuator at column 3 and line 0 triggered for 385.8270259992023 msec with intensity 1
```

## JSON Converter
The `PatternConverter.py` script allows you to create a vibration pattern from a stroke that can then be used with [Vibration Pattern Player](https://github.com/Suitceyes-Project-Code/Vibration-Pattern-Player).

### Setup
Setup the mapping of actuators and the grid size in the `config.json` file. 

```json
{
    "mapping": // Maps grid coordinates to a vibration pin
    {
        "0,0": 4,
        "1,0" : 5,
        "2,0" : 6,
        "3,0" : 7,
        "0,1" : 0,
        "1,1" : 1,
        "2,1" : 2,
        "3,1" : 3,
        "0,2" : 8,
        "1,2" : 9,
        "2,2" : 10,
        "3,2" : 11,
        "0,3" : 12,
        "1,3" : 13,
        "2,3" : 14,
        "3,3" : 15
    }, 
    "grid":
    {
        "columns" : 4, // the number of columns your grid has
        "lines" : 4, // the number of lines your grid has
        "spacing" : 2.5 // the spacing in centimetres between each vibration motor
    }
}
```

### Run application
Simply run the `PatternConverter.py` in a terminal of your choice and follow the instructions. The script prints a JSON string in the terminal after completion. 