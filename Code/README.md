 Chess software

This folder contains the computer-vision and chess-game scripts for KnightShift.

## What the scripts do

- `wykrywaj_ruchy.py` reads a physical chessboard from a camera, tracks legal moves, and asks Stockfish to suggest Black's reply. The robotic arm is not controlled by this script yet.
- `# Rozpoznawanie figur szachowych ze zdjęcia.py` detects and labels chess pieces in a camera image or a saved photo.
- `oznacz_szachy.py` is a small tool for annotating chess-piece images for YOLO training.
- `Uruchom szachy.bat` starts the game-tracking script on Windows.

## Technologies used

- Python for the application code.
- OpenCV for camera input, image processing, and the on-screen board.
- Ultralytics YOLO for chess-piece detection.
- `python-chess` for legal moves, game state, and communication with a UCI chess engine.
- Stockfish for choosing the robot's chess moves.

## Setup

For step-by-step Windows instructions in Polish, see [INSTALACJA.md](./INSTALACJA.md).

Install the Python packages:

```powershell
python -m pip install -r requirements.txt
```

Install Stockfish separately. The game script searches the user's local
`AppData\Local\Programs\Stockfish` folder automatically. If Stockfish is in a
different location, pass its executable path with `--stockfish`.

The trained YOLO weights and the image dataset are not included in this
repository. Place the trained model at `models\best.pt`, or pass its location
with `--model`.

## Run on Windows

After placing the model at `models\best.pt`, double-click `Uruchom szachy.bat`,
or run:

```powershell
python .\wykrywaj_ruchy.py --orientation black --model .\models\best.pt --engine-time 1.0
```

The program detects the human's move and displays Stockfish's suggested reply.
Move the black piece by hand; the camera should detect the move. The software
does not send commands to the robotic arm yet.

To detect pieces in a photo or with the camera, run:

```powershell
python ".\# Rozpoznawanie figur szachowych ze zdję.py" --camera --model .\models\best.pt --orientation black
```
