# Purpose
The main purpose of this Python script is to take raw audio data from the microphone array, run all the heavy signal processing calculations in real time, and draw a visual sound heatmap over the camera feed.

# How does it work? 
## 1. Fourier Transform
First, we smooth the raw audio frames using a Hamming window so the edges don't cause spectral artifacts. Then, we convert the audio from the time domain into individual pitch frequencies (the frequency domain).

$$X(k) = \text{FFT}\Big(x[n] \times \text{HammingWindow}[n]\Big)$$

## 2. PHAT
With four microphones in a square, there are 6 unique pairs to cross-examine: (M1–M2), (M1–M3), (M3–M4), (M4–M2), (M2–M3), and (M4–M1). To prevent spatial aliasing (ghost sounds), we apply $\text{Bandpass}(k)$ based on the physical distance between the mics. We then test how well the measured phase aligns with the expected phase for every $(x, y)$ pixel coordinate using a Steering Vector. The result is a confidence score between $0$ and $1$ indicating whether frequency $k$ originates from $(x, y)$.

$$\text{PairBeamform}(x, y, k) = \text{RealPart}\left( X_{1,\text{phase}}(k) \times \overline{X_{2,\text{phase}}(k)} \times \text{Bandpass}(k) \times \text{SteeringVector}(x, y, k) \right)$$

Note: The SteeringVector is a formula that predicts the exact travel time delay for a sound wave hitting each microphone pair from any given horizontal $(x)$ and vertical $(y)$ angle.

## 3. Spatial Summation
We add the grid calculations from all 6 microphone pairs together and average them. Where a real sound source exists, the phase waves from all pairs line up perfectly and reinforce each other constructively, creating a strong energy  peak.

$$\text{SpatialSum}(x, y, k) = \frac{1}{6} \sum_{p=1}^{6} \text{PairBeamform}_p(x, y, k)$$

## 4. Spatial Blob Thresholding
Four microphones naturally produce broad, blurry sound clouds. To sharpen the heatmap, we apply a high-pass threshold ($T_{\text{blob}}$). Any energy below this threshold (ambient background noise and destructive interference) is zeroed out, and the remaining peaks are rescaled from $0$ to $1$.

$$\text{BlobFilter}(x, y, k) = \max\Big(\text{SpatialSum}(x, y, k) - T_{\text{blob}}, 0\Big)$$

$$\text{SharpenedGrid}(x, y, k) = \frac{\text{BlobFilter}(x, y, k)}{1.0 - T_{\text{blob}} + \epsilon}$$

## 5. Frequency Integration
We collapse our 3D grid into a flat 2D surface map by summing up all the frequency:

$$\text{IntensityMap}(x, y) = \sum_{k} \text{SharpenedGrid}(x, y, k)$$

## 6. Temporal Moving Average
To keep the visual overlay steady and prevent high-speed flickering between camera frames, we apply an Exponential Moving Average (EMA) smoothing filter using a smoothing factor $\alpha$:

$$\text{SmoothedMap}_t(x, y) = \alpha \times \text{IntensityMap}_t(x, y) + (1 - \alpha) \times \text{SmoothedMap}_{t-1}(x, y)$$

## 7. Logarithmic Contrast Scaling
We apply a logarithmic to compress loud energy spikes and boost quieter ones. In other words, this ensures that faint secondary sounds remain visible alongside loud primary sources.

$$\text{LogMap}(x, y) = \log_{10}\Big(\text{SmoothedMap}(x, y) + 1\Big)$$

## 8. Normalize
Finally, we scale it from $0.0$ to $1.0$, allowing us to easily map to color spectrum.

$$\text{NormalizedMap}(x, y) = \frac{\text{LogMap}(x, y)}{\max_{(x,y)}\Big(\text{LogMap}(x,y)\Big) + \epsilon}$$

# How to use? 

1. Install the dependencies if you don’t have them
- opencv-python 
- numpy 
- Pillow 
- RangeSlider
2. Power on your ESP32 and connect your computer to the "Esp32" Wi-Fi network.
3. Finally, run main.py. 

