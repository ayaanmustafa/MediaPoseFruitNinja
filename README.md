# Fruit Ninja Hand Tracker 🍎

Hey there! Welcome to **Fruit Ninja Hand Tracker**, a super fun Python-based game that brings the classic Fruit Ninja experience to life using your webcam and hand gestures. Instead of a touchscreen, you'll slice fruits with your finger movements tracked in real-time.

This project uses MediaPipe for hand landmark detection, OpenCV for video processing, and some physics to make the fruits bounce around realistically. Perfect for a quick gaming session or as a cool demo of computer vision.

## 🎮 Salient Features

- **Real-time Hand Tracking**: Uses MediaPipe's HandLandmarker to detect your hand and track your fingertip movements. No controllers needed – just wave your hand around!
- **Physics-Based Fruit Movement**: Fruits spawn with gravity, velocity, and rotation, making them feel alive and bouncy.
- **Dynamic Difficulty**: As your score increases, more fruits appear, and the respawn rate speeds up for extra challenge.
- **Smooth Trail Effects**: Your finger leaves a colorful trail as you "slice" through the fruits.
- **Sound Effects**: Satisfying swish sounds when you hit a fruit, and a game-over tune when you miss.
- **Score Tracking**: Keep track of your slicing skills with a live score counter.
- **Restart Functionality**: Game over? Just press 'R' to restart and try again!

## 🕹️ How to Play

1. **Setup Your Space**: Make sure your webcam is on and you're in a well-lit area. Hold up your hand so the camera can see it clearly.
2. **Start the Game**: Run the script, and a window will pop up showing your webcam feed.
3. **Slice the Fruits**: Move your index finger (or any tracked point) to "draw" lines across the screen. When your trail touches a fruit, it gets sliced!
4. **Avoid Missing**: If a fruit falls to the bottom without being hit, it's game over. Quick reflexes required!
5. **Score Points**: Each fruit you hit adds to your score. Reach milestones (10, 25, 40 points) to spawn extra fruits and ramp up the fun.
6. **Restart**: When the game ends, press 'R' to reset and play again. Press 'ESC' to quit anytime.

Pro Tip: Keep your hand steady for smoother slicing, and experiment with different gestures for the best experience!

## 🛠️ Project Explanation

Here's a quick breakdown of how the magic happens under the hood:

1. **Hand Detection**: The script uses MediaPipe's HandLandmarker model to process each video frame from your webcam. It detects hand landmarks and focuses on the fingertip (landmark 8) for tracking.
2. **Smoothing**: Raw hand positions are smoothed using exponential smoothing to reduce jitter and make movements feel natural.
3. **Trail Creation**: Recent fingertip positions are stored in a deque (a queue) to draw a fading trail behind your finger.
4. **Fruit Physics**: Each fruit has properties like position, velocity, gravity, rotation, and spin. They update each frame with physics calculations.
5. **Collision Detection**: The game checks if any point in your trail is within a hit radius of a fruit's center. If so, boom – fruit sliced!
6. **Respawn Logic**: Sliced fruits have a short delay before respawning with new random properties to avoid feeling teleported.
7. **Game Loop**: Everything runs in a loop: capture frame → detect hand → update physics → check collisions → draw everything → repeat.
8. **Audio Feedback**: Uses Windows' winsound for simple sound effects (sorry, Linux/Mac folks – might need tweaks for cross-platform audio).

The code is modular, with functions for drawing PNGs with alpha blending, rotating images, and spawning fruits. It's a great example of combining computer vision with game mechanics!

## 🚀 Setup Instructions

Ready to slice some virtual fruit? Follow these steps to get the project running on your machine. (Note: This is designed for Windows, but should work on other OSes with minor tweaks.)

### Prerequisites
- **Python 3.8+**: Make sure you have Python installed. Download from [python.org](https://www.python.org/).
- **Webcam**: A built-in or external camera for hand tracking.
- **Windows**: For the sound effects (winsound module). If you're on another OS, you might need to replace the audio parts.

### Step-by-Step Setup

1. **Clone or Download the Project**:
   - Download the zip from wherever you got this, or clone it if it's a repo. Extract to a folder, say `fruitNinja`.

2. **Set Up a Virtual Environment** (Recommended):
   - Open a terminal (Command Prompt or PowerShell) in the project folder.
   - Create a virtual env: `python -m venv env`
   - Activate it: `env\Scripts\activate` (on Windows)

3. **Install Dependencies**:
   - The project uses a `requirements.txt` file. Install everything with:
     ```
     pip install -r requirements.txt
     ```
     This will grab OpenCV, MediaPipe, NumPy, and more.

4. **Download the MediaPipe Model**:
   - The `hand_landmarker.task` file should already be in your project folder. If not, you can download it from MediaPipe's resources (search for "MediaPipe Hand Landmarker model").

5. **Prepare Assets**:
   - Make sure the `asset/` folder has the fruit images (apple1.png, pineapple.png, etc.) and sound files (airswish.wav, gameover.wav). If missing, you'll need to source or create them.

6. **Run the Game**:
   - In your activated virtual environment, run:
     ```
     python main.py
     ```
   - A window should open with your webcam feed. Start slicing!

### Troubleshooting
- **Camera Issues**: If the webcam doesn't work, check permissions or try a different camera index in `cv2.VideoCapture(0)`.
- **Hand Not Detected**: Ensure good lighting and hold your hand clearly in view. Adjust confidence thresholds in the code if needed.
- **Import Errors**: Double-check your virtual env is activated and all packages are installed.
- **Sound Not Playing**: On non-Windows systems, replace `winsound` with something like `playsound` library.
- **Performance**: If it's laggy, lower the frame rate or reduce smoothing.

## 📁 Project Structure

- `main.py`: The heart of the game – all the logic here.
- `mediapipeTest.py`: A simple test script for MediaPipe (optional).
- `requirements.txt`: List of Python packages needed.
- `hand_landmarker.task`: MediaPipe's hand detection model.
- `asset/`: Images (fruits) and sounds.
- `env/`: Virtual environment (created during setup).
