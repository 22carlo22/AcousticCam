# Project Logs
This folder contains early prototypes, and test results that laid the foundation for the entire project.

## Early April, 2026
My first goal was simply to play around with the basic math equations and see if it was actually possible to pinpoint a sound using only 4 microphones. Spoiler alert: it is! For this test, I used a standard earbud to play a steady, single-frequency tone. I dumped the raw matrix data and used GNU Octave to run the calculations.

<img width="2298" height="3037" alt="574454858-636ea669-2af8-4f88-829e-7a58ab6031be" src="https://github.com/user-attachments/assets/c49da3e1-af8d-465c-857f-6a72a016984e" />

<img width="656" height="368" alt="574456689-2f5d6e8a-2f1b-4da5-b624-e3df61f7b9f6" src="https://github.com/user-attachments/assets/9e0efba2-9d2d-4522-955b-50b06bb6b868" />

## April 20, 2026
Once the basic math was proven, my next goal was to split the sound processing so the camera could calculate locations for individual frequencies. This upgrade allows the system to track multiple different kinds of real-world noises at the same time instead of just a single steady tone. I used GNU Octave to build and verify this.

<img width="492" height="277" alt="581115861-f1701a3e-be62-45ef-97c3-9c5914c32b69" src="https://github.com/user-attachments/assets/819d71fa-0784-4388-abc8-cb8feac08d7a" />

