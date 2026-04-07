classdef Ears
  properties(Constant = true)
    Fsample = 44100;
    Vsound = 343;
    N = 1024;
  endproperties

  properties
    bandpass_filter;
    phase_const;
  endproperties

  methods
    function obj = Ears(Mref, Moth, u)
      # Get the expected delay for each direction of sound
      n0 = round(((Mref-Moth)' * u) * obj.Fsample / obj.Vsound);

      # Find the "best" frequencies suitable to be detected between the given 2 mics
      max_n0 = max(abs(n0));
      Nlow = obj.N / (6.5*max_n0);
      Nhigh = obj.N / (4*max_n0);

      printf("Fmin: %d Hz    Fmax: %d Hz\n", Nlow*Ears.Fsample/obj.N, Nhigh*Ears.Fsample/obj.N);

      # the expected delay in the freqeuncy domain
      k = 0:(obj.N-1);
      obj.phase_const = exp(-i*2*pi * k .* (n0') / obj.N);


      # band pass filter to allow the 2 mics to only listen for the "best" frequencies
      n = 0:(obj.N-1);
      obj.bandpass_filter = ((n >= Nlow & n <= Nhigh) | (n>= (obj.N - Nhigh) & n <= (obj.N - Nlow)));
    endfunction

    # Perform Delay-and-Sum Beamformer
    function Q = getQuantity(obj, Xref, Xoth)
      R = Xref .* conj(Xoth);
      P = R .* obj.phase_const;
      filtered = P .*  obj.bandpass_filter;
      Q = sum(real(filtered), 2)';
    endfunction

  endmethods
endclassdef
