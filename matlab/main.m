clc;
clear;
clear classes;
pkg load instrument-control;
pkg load statistics;

# Serial
expected_bytes = Ears.N*4*4;     # (# of samples)(sizeof(int32))(# of mics)
s1 = serial("COM7", 921600, 10);

# Direction of the sound to be detected. For spatial scanning.
grid_size = 0.1;
grid_res = 10;
grid_height = 0.1;
grid_units = -grid_size/2 : grid_size/grid_res : grid_size/2;
num_pts = length(grid_units);
[X_grid, Y_grid] = meshgrid(grid_units, grid_units);

u = [];
for y = grid_units
  for x = grid_units
    dist = sqrt(x^2 + y^2 + grid_height^2);
    u = [u, [x/dist; y/dist; grid_height/dist]];  # get vector of the sound direction
  endfor
endfor

# Arrangement of the mics in meters
M1 = [0; 0; 0];
M2 = [0; 0.08; 0];
M3 = [0.09; 0.08; 0];
M4 = [0.09; 0; 0];
e1 = Ears(M1, M2, u);
e2 = Ears(M1, M4, u);
e3 = Ears(M1, M3, u);
e4 = Ears(M4, M2, u);

hamming_window = hamming(Ears.N)';

# For smooth visual
Q_alpha = 0.25;
current_Q =  zeros(1, columns(u));

# 3d graph
Z_initial = reshape(current_Q, num_pts, num_pts);
h_bar = bar3(Z_initial);

for i = 1:numel(h_bar)
  set(h_bar(i), 'CData', get(h_bar(i), 'ZData'));
  set(h_bar(i), 'FaceColor', 'interp');
end
view(3);

# run the program. Exit when the user enters "q".
while(!strcmp(kbhit(1), 'q'))

   # Get data from the esp32
   raw = [];
   while(length(raw) != expected_bytes)
     srl_write(s1, uint8(0));
     raw = srl_read(s1, expected_bytes);
   end
   data = typecast(uint8(raw), 'int32');

   # Calculations
   if(length(data) == Ears.N*4)
     # Smooth out the edges first to reduce discontinuities.
     x4 = data(1:4:end) .* hamming_window;
     x3 = data(2:4:end) .* hamming_window;
     x1 = data(3:4:end) .* hamming_window;
     x2 = data(4:4:end) .* hamming_window;

     # Convert it to frequency domain
     X1 = fft(x1);
     X2 = fft(x2);
     X3 = fft(x3);
     X4 = fft(x4);

     prev_Q = current_Q;

     # Add all of the energy (or the sound intensity) detected from the mics
     current_Q = e1.getQuantity(X1, X2)+e2.getQuantity(X1, X4)+e3.getQuantity(X1, X3)+e4.getQuantity(X4, X2);
     current_Q(current_Q < 1000) = 0;
     current_Q = current_Q .^ 2;                                  # make the peak more visible
     current_Q = (1-Q_alpha) * current_Q + Q_alpha * prev_Q;      # make less "jumpy"


    # Update the 3d graph
     Z_data = reshape(current_Q, num_pts, num_pts);
     delete(h_bar);
     h_bar = bar3(Z_data);
     for i = 1:numel(h_bar)
       set(h_bar(i), 'CData', get(h_bar(i), 'ZData'), 'FaceColor', 'interp');
     end
     drawnow;
   endif

end

fclose(s1);
close all;

