clc;
clear;
clear classes;
pkg load instrument-control;
pkg load statistics;
pkg load communications;

# Linear interpolation. Used for visualizing how "loud" the frequency is.
function mapped = map(x, in_min, in_max, out_min, out_max)
  mapped = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
end

half_sample = Ears.N/2;

# Used for noise detection
power_baseline = zeros(1, half_sample);
power_baseline_alpha = 0.1;
power_noise = zeros(1, half_sample);
power_noise_const = 10;

# Variables for determining the number of bars (in the 3d bar) to be displayed for a particular frequency
cells_population_rate = 0.15;
cells_max = 15;
cells_baseline_to_exist = 10^9;

# Direction of the sound to be detected. For spatial scanning.
grid_size = 1;
grid_res = 10;
grid_height = 1;
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


# Divide the frequencies into groups
freq_seperator = 3;                   # Lower number means the 3d graph will show more frequency variety
freq_edges = [e1.getFrequencyRange(), e2.getFrequencyRange(), e3.getFrequencyRange(), e4.getFrequencyRange()];
freq_min = min(freq_edges);
freq_max = max(freq_edges);
freq_window = [freq_min:freq_seperator:freq_max];
if(freq_window(end) != freq_max)
  freq_window = [freq_window, freq_max];
endif

freq_ranges= zeros(length(freq_window)-1, 2);
freq_ranges(1, :) = [freq_window(1), freq_window(2)];
printf("Freq. capture %d: %d to %d\n", 1, freq_ranges(1, 1)*Ears.Fsample/Ears.N, freq_ranges(1, 2)*Ears.Fsample/Ears.N);
for i = 2:size(freq_ranges, 1)
  freq_ranges(i, :) = [freq_window(i)+1, freq_window(i+1)];
  printf("Freq. capture %d: %d to %d\n", i, freq_ranges(i, 1)*Ears.Fsample/Ears.N, freq_ranges(i, 2)*Ears.Fsample/Ears.N);
endfor

e1.setupFrequencyRanges(freq_ranges);
e2.setupFrequencyRanges(freq_ranges);
e3.setupFrequencyRanges(freq_ranges);
e4.setupFrequencyRanges(freq_ranges);

hamming_window = hamming(Ears.N)';

# Serial
expected_bytes = Ears.N*4*4;     # (# of samples)(sizeof(int32))(# of mics)
s1 = serial("COM7", 921600, 10);

# run the program. Exit when the user enters "q".
while(!strcmp(kbhit(1), 'q'))

  # Get data from the esp32
  raw = [];
  while(length(raw) != expected_bytes)
    srl_write(s1, uint8(0));
    raw = srl_read(s1, expected_bytes);
  end
  data = typecast(uint8(raw), 'int32');

  x4 = data(1:4:end) .* hamming_window;
  x3 = data(2:4:end) .* hamming_window;
  x1 = data(3:4:end) .* hamming_window;
  x2 = data(4:4:end) .* hamming_window;

  # Convert it to frequency domain
  X1 = fft(x1);
  X2 = fft(x2);
  X3 = fft(x3);
  X4 = fft(x4);

  # Only take the unique frequencies
  X1 = X1(1:half_sample);
  X2 = X2(1:half_sample);
  X3 = X3(1:half_sample);
  X4 = X4(1:half_sample);

  X1_abs = abs(X1);
  X2_abs = abs(X2);
  X3_abs = abs(X3);
  X4_abs = abs(X4);

  # Unify all of the mics. Very important if we want to always have a nice hill (instead of a random valley) appearing in our 3d graph.
  avg_abs =  (X1_abs + X2_abs + X3_abs + X4_abs)/4;
  X1 = avg_abs .* (X1 ./ (X1_abs+10^-10));
  X2 = avg_abs .* (X2 ./ (X2_abs+10^-10));
  X3 = avg_abs .* (X3 ./ (X3_abs+10^-10));
  X4 = avg_abs .* (X4 ./ (X4_abs+10^-10));

  # Get rid off the noise floor when the user enters "c".
  power = avg_abs .^2;
  power_baseline =  (1-power_baseline_alpha)*power_baseline + power_baseline_alpha*power;
  if(strcmp(kbhit(1), 'c'))
    disp("Calibrated");
    power_noise = power_noise_const*power_baseline;
  endif
  noise = (power - power_noise) < 0;
  X1(noise) = 0;
  X2(noise) = 0;
  X3(noise) = 0;
  X4(noise) = 0;

##   freq = (0:(half_sample-1)) .* (Ears.Fsample/Ears.N);
##   subplot(2, 1, 1);
##   plot(freq, abs(X1), freq, abs(X2), freq, abs(X3), freq, abs(X4));
##
##   subplot(2, 1, 2);
##   plot(freq, power_baseline);4


  # Calculate the location of the sound source
  Q = e1.getQuantity(X1, X2)+e2.getQuantity(X1, X4)+e3.getQuantity(X1, X3)+e4.getQuantity(X4, X2);
  for i = 1:size(Q, 1)
    Q_specific = Q(i, :);

    # Determine the number of bars to be displayed for that frequency. The louder it is, the more bars it will appear.
    num_cells = round(map(max(Q_specific), cells_baseline_to_exist, cells_baseline_to_exist*10, 0, cells_population_rate));
    if(num_cells > cells_max)
      num_cells = cells_max;
    endif

    # Only display them at the peak (where the sound is located)
    if(num_cells > 0)
      Q_sorted = sort(Q_specific, 'descend');
      threshold = Q_sorted(num_cells);
      Q_specific(Q_specific < threshold) = 0;
    else
      Q_specific = zeros(1, length(Q_specific));
    endif

    Q(i, :) = Q_specific;
  endfor

  # Data and color for the 3d graph. Prioritize frequencies that are loud.
  Q_toDisplay = zeros(1, size(Q, 2));
  color_toDisplay = zeros(1, size(Q, 2));
  for i = 1:size(Q, 2)
    [val, color] = max(Q(:, i));
    Q_toDisplay(i) = val;
    color_toDisplay(i) = color;
  endfor

  Z_data = reshape(Q_toDisplay, num_pts, num_pts);
  C_indices = reshape(color_toDisplay, num_pts, num_pts);

  N = max(color_toDisplay);
  cmap = jet(N);                                      # Blue = lower frequency. Red = higher frequency.

  # No color when the sound is silent.
  rgb_colors = cmap(C_indices(:), :);
  is_zero_height = (Q_toDisplay(:) == 0);
  num_zeros = sum(is_zero_height);
  if num_zeros > 0
    rgb_colors(is_zero_height, :) = repmat([1 1 1], num_zeros, 1);
  endif

  # Display the 3d bar.
  if(exist("h_bar", "var") && ishandle(h_bar))
    delete(h_bar);
  endif
  h_bar = bar3(Z_data, rgb_colors);
  zlim([0, inf]);
  view(2);

  drawnow;

end

fclose(s1);
close all;
