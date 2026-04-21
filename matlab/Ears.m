classdef Ears < handle
  properties(Constant = true)
    Fsample = 44100;
    Vsound = 343;
    N = 1024;
  endproperties

  properties
    bandpass_filter;
    phase_const;
    Nlow_Nhigh;
    freq_range;
  endproperties

  methods
    function obj = Ears(Mref, Moth, u)
      # Get the expected delay for each direction of sound
      n0 = round(((Mref-Moth)' * u) * obj.Fsample / obj.Vsound);

      # Find the "best" frequencies suitable to be detected between the given 2 mics
      max_n0 = max(abs(n0));
      Nlow = round(obj.N / (6*max_n0));
      Nhigh = round(obj.N / (4*max_n0));
      obj.Nlow_Nhigh = [Nlow, Nhigh];

      printf("Fmin: %d Hz    Fmax: %d Hz\n", Nlow*Ears.Fsample/obj.N, Nhigh*Ears.Fsample/obj.N);

      # the expected delay in the freqeuncy domain
      k = 0:(obj.N/2-1);
      obj.phase_const = exp(-i*2*pi * k .* (n0') / obj.N);


      # band pass filter to allow the 2 mics to only listen for the "best" frequencies
      n = 0:(obj.N/2-1);
      obj.bandpass_filter = (n >= Nlow & n <= Nhigh);

    endfunction

    # Perform Delay-and-Sum Beamformer
    function Q = getQuantity(obj, Xref, Xoth)
      R = Xref .* conj(Xoth);
      P = R .* obj.phase_const;
      filtered = P .*  obj.bandpass_filter;

      Q = zeros(size(obj.freq_range, 1), size(obj.phase_const, 1));

      for i = 1:size(obj.freq_range, 1)
        freq_target = filtered(:, obj.freq_range(i, 1):obj.freq_range(i, 2));
        Q_target = sum(real(freq_target), 2)';
        Q(i, :) = Q_target;
      endfor
    endfunction

    function out = getFrequencyRange(obj)
      out = obj.Nlow_Nhigh;
    endfunction

    function setupFrequencyRanges(obj, my_range)
      obj.freq_range = my_range;
    endfunction

  endmethods
endclassdef
