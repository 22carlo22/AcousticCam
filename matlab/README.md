This simulates the acoustic camera's logic. As the esp32 supplies data through the serial,  the script performs a Delay-and-Sum Beamformer  to determine the sound location and displays it in a 3d graph.

The code has now been updated to include frequency spectrum heat map, allowing to locate more than one sound source at once. 
