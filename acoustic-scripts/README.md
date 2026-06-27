# Description
The main purpose of this Python script is to take the raw sound data from the ESP32, handle all the heavy mathematical calculations, and draw the visual sound heatmap. When using only four microphones, the system is highly prone to catching "ghost sounds" or false mathematical reflections (artifacts). Because of this, the calculation became more complex than I expected.

# How does it work? 

## Fourier Transform & Noise Removal
First, we convert the raw audio into the frequency domain. At the same time, we completely mute any frequencies that match steady background environmental noise, like a room fan or computer hum.

$$\text{FrequencyWaves}(f) = \text{FFT}\Big(\text{RawAudio}(t) \times \text{HammingWindow}(t)\Big)$$

$$\text{If } \big|\text{FrequencyWaves}(f)\big| < \text{NoiseBaseline}(f) \implies \text{FrequencyWaves}(f) = 0$$

## Pairwise GCC-PHAT & Bandpass Filtering
Next, we calculate the exact timing alignments between different microphone pairs. Since our four microphones are arranged in a physical square, we have a total of 6 unique pairs to cross-examine: (M1-M2), (M1-M3), (M4-M2), (M4-M3), (M1-M4), and (M3-M2).

For every single pair, we apply a bandpass filter based on the physical distance between the two mic to prevent spatial aliasing or ghost frequencies. Then, we calculate how well the actual phase aligns with the theoretical phase for a paticular (x, y) coordinate.

$$\text{PairGrid}(x, y, f) = \text{RealPart} \left( \text{Phase}_1(f) \times \overline{\text{Phase}_2(f)} \times \text{BandpassFilter}(f) \times \text{SteeringVector}(x, y, f) \right)$$

Note: The SteeringVector is a mathematical formula that predicts exactly how long a sound wave should take to travel to each microphone pair from any given horizontal angle (x) and vertical angle (y).

## Spatial Focused Summation
We overlay and add the grid calculations from all six microphone pairs together. Where a real sound source actually exists in the room, the mathematical math waves from all pairs line up perfectly and reinforce each other constructively, generating a massive energy spike at that coordinate.

$$\text{AggregateGrid}(x, y, f) = \sum_{p=1}^{6} \text{PairGrid}_p(x, y, f)$$

## Destructive Filter & Per-Frequency Normalization
Next we extract the constructive interference. This is done by removing the negative values (destructive interference) and normalizing each frequency component independently.

$$\text{CleanGrid}(x, y, f) = \max\big(\text{AggregateGrid}(x, y, f), 0\big)$$

$$\text{NormalizedGrid}(x, y, f) = \frac{\text{CleanGrid}(x, y, f)}{\max_{(x,y)} \big(\text{CleanGrid}(x, y, f)\big) + \epsilon}$$

## Spatial Blob Thresholding
Because four microphones naturally generate wide, blurry sound clouds rather than sharp points, we apply a strict threshold filter to sharpen our tracking resolution. We zero out any pixels that fall below the top 5% of energy, turning a blurry cloud into a tight pinpoint dot.

$$\text{BlobFilter}(x, y, f) = \max\big(\text{NormalizedGrid}(x, y, f) - 0.95, 0\big)$$

$$\text{SharpenedGrid}(x, y, f) = \frac{\text{BlobFilter}(x, y, f)}{1.0 - 0.95}$$

## FOV Gating (Field-of-View Filtering)
The microphones can hear in all directions ($360^\circ$), but our camera lens can only see what is directly in front of it. This step looks for the loudest peak of a frequency. If that peak sits on the absolute border frame edge of our scanning grid, it means the sound is coming from behind or to the side of the device. If it is out of sight, the system dynamically mutes it.

$$\text{PeakCoordinates}(f) = \arg\max_{(x,y)} \big(\text{SharpenedGrid}(x, y, f)\big)$$

$$\text{GatedGrid}(x, y, f) = 
\begin{cases} 
0, & \text{if } \text{PeakCoordinates}(f) \text{ lands on the grid borders} \\ 
\text{SharpenedGrid}(x, y, f), & \text{otherwise} 
\end{cases}$$

## Loudness Power Scaling
We then scale the grid by the power of the audio. This ensures a loud noise generates a deep, bright hotspot while a quiet whisper stays faint.

$$\text{AvgPower}(f) = \frac{\big|X_1(f)\big|^2 + \big|X_2(f)\big|^2 + \big|X_3(f)\big|^2 + \big|X_4(f)\big|^2}{4}$$

$$\text{ScaledGrid}(x, y, f) = \text{GatedGrid}(x, y, f) \times \text{AvgPower}(f)$$

## Frequency Integration
In this final step, we collapse our 3D frequency matrix into a flat 2D surface map by summing up the calculated energy from all valid frequency channels at each specific (x,y) coordinate.

$$\text{IntensityMap}(x, y) = \sum_{\text{all } f} \text{ScaledGrid}(x, y, f)$$

$$\text{IntensityMapNormal}(x, y) = \frac{\text{IntensityMap}(x, y)}{\max \big(\text{IntensityMap}\big + \epsilon)}$$
