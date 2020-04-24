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