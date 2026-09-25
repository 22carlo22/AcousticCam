# Purpose
The main purpose of this Python script is to take raw audio data from the microphone array, run all the heavy signal processing calculations in real time, and draw a visual sound heatmap over the camera feed.

# How to use? 

1. Install the dependencies if you don’t have them
- opencv-python 
- numpy 
- Pillow 
- RangeSlider
2. Power on your ESP32 and connect your computer to the "Esp32" Wi-Fi network.
3. Finally, run main.py.

# About config.py
Everything you need to tweak is in config.py. While there are plenty of settings, these are the two main ones you’ll want to mess with:

1. SCANNER_QUALITY
This adjusts the heatmap resolution. Turn it up, and you get a sharper, more detailed image.

<img width="614" height="234" alt="Screenshot 2026-09-25 192812" src="https://github.com/user-attachments/assets/6d9a7088-e16a-4796-80bf-3241b4a392a4" />

3. AUDIO_SIZE
This changes how much audio data gets fed into the beamformer. Increasing this gives the algorithm more frequencies to analyze, making it much better at pinpointing specific sound sources (especially when CLEAN is turned on).

<img width="618" height="232" alt="Screenshot 2026-09-25 192848" src="https://github.com/user-attachments/assets/ed033f1d-4161-4815-9be2-08d64beaa317" />


# How does it work? 
## 1. Fourier Transform
First, we smooth the raw audio frames using a Hamming window so the edges don't cause spectral artifacts. Then, we convert the audio from the time domain into individual pitch frequencies (the frequency domain).

$$X(f) = \text{FFT}\Big(x(t) \times \text{HammingWindow}(t)\Big)$$

## 2. PHAT
With four microphones in a square, there are 6 unique pairs to cross-examine: (M1–M2), (M1–M3), (M3–M4), (M4–M2), (M2–M3), and (M4–M1). To prevent spatial aliasing (ghost sounds), we apply $\text{Bandpass}(f)$ based on the physical distance between the mics. We then test how well the measured phase aligns with the expected phase for every $(x, y)$ pixel coordinate using a Steering Vector. The result is a confidence score between $0$ and $1$ indicating whether frequency $k$ originates from $(x, y)$.

$$\text{PairBeamform}(x, y, f) = \frac{\text{Re}\left( X_{1,\text{phase}}(f) \times \overline{X_{2,\text{phase}}(f)} \times \text{Bandpass}(f) \times \text{SteeringVector}(x, y, f) \right) + 1}{2}$$

Note: The SteeringVector is a formula that predicts the exact travel time delay for a sound wave hitting each microphone pair from any given horizontal $(x)$ and vertical $(y)$ angle.

## 3. Spatial Summation
We add the grid calculations from all 6 microphone pairs together and average them. Where a real sound source exists, the phase waves from all pairs line up perfectly and reinforce each other constructively, creating a strong energy  peak.

$$\text{SpatialSum}(x, y, f) = \frac{1}{6} \sum_{p=1}^{6} \text{PairBeamform}_p(x, y, f)$$

## 4. Spatial Blob Thresholding
Four microphones naturally produce broad, blurry sound clouds. To sharpen the heatmap, we apply a high-pass threshold ($T_{\text{blob}}$). Any energy below this threshold (ambient background noise and destructive interference) is zeroed out, and the remaining peaks are rescaled from $0$ to $1$.

$$\text{BlobFilter}(x, y, f) = \max\Big(\text{SpatialSum}(x, y, f) - T_{\text{blob}}, 0\Big)$$

$$\text{SharpenedGrid}(x, y, f) = \frac{\text{BlobFilter}(x, y, f)}{1.0 - T_{\text{blob}} + \epsilon}$$

## 5. Temporal Moving Average
To keep the visual overlay steady and prevent high-speed flickering between camera frames, we apply an Exponential Moving Average (EMA) smoothing filter using a smoothing factor $\alpha$:

$$\text{SmoothedMap}_n(x, y, f) = \alpha \times \text{SharpenedGrid}(x, y, f) + (1 - \alpha) \times \text{SmoothedMap}_{n-1}(x, y, f)$$

## 6. Simplified CLEAN
In real-world settings, loud sounds can drown out quieter ones, hiding them on a heatmap. The simplified CLEAN method fixes this by finding the loudest sound, subtracting most of its volume, and repeating the process over multiple steps (where $n$ represents the current iteration step) so quieter sounds can show up.

First, we set the starting map $\text{Residual}_0$ ($n = 0$) to the initial smoothed data. Then, we combine all sound frequencies into one main map to find where the loudest sound is located for step $n$.

$$\text{Residual}_0(x, y, f) = \text{SmoothedMap}(x, y, f)$$

$$\text{Intensity}_n(x, y) = \sum_{f} \text{Residual}_n(x, y, f)$$

$$(\text{peakx}_n, \text{peaky}_n) = \arg\max_{(x, y)} \text{Intensity}_n(x, y)$$

Next, we take the sound frequencies at that exact spot, shrink them slightly using a `decay` factor, and subtract them to create the updated map for the next iteration ($n + 1$).

$$\text{Residual}_{n+1}(x, y, f) = \text{Residual}_n(x, y, f) - \text{decay} \cdot \text{Residual}_n(\text{peakx}_n, \text{peaky}_n, f)$$

Repeating this process for higher values of $n$ peels away the strongest sounds to uncover progressively quieter ones.

## 7.  Logarithmic Scaling
We apply a logarithmic to compress loud energy spikes and boost quieter ones. In other words, this ensures that faint secondary sounds remain visible alongside loud primary sources. 

$$\text{LogMap}(x, y) = \log_{10}\Big(\text{Intensity}(x, y) + 1\Big)$$

## 8. Normalize
Finally, we scale the values from 0.0 to 1.0 for easy color mapping. We also cap the highest peak in the heatmap as a fallback to prevent the visualization from being ruined by a  massive blob. 

$$\text{NormalizedMap}(x, y) = \frac{\text{LogMap}(x, y)}{\max_{(x,y)}\Big(\text{LogMap}(x,y)\Big) + \epsilon}$$
$$\text{PeakMap}(x, y) = \frac{\max(\text{NormalizedMap}(x, y) - \text{peak}, 0)}{1 - \text{peak} + \epsilon}$$

