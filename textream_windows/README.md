# Textream for Windows

This is a Windows port of the popular [Textream](https://github.com/f/textream) macOS app.
It brings the "Dynamic Island" teleprompter experience to Windows using Python and PyQt6.

## Requirements

- Python 3.10+
- A microphone

## Installation

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Download Speech Model**:
    -   Go to [Vosk Models](https://alphacephei.com/vosk/models).
    -   Download a model (e.g., `vosk-model-small-en-us-0.15` for English or `vosk-model-small-tr-0.3` for Turkish).
    -   Extract the downloaded zip file.
    -   Rename the extracted folder to `model` and place it inside this `textream_windows` folder.
    
    Structure should look like:
    ```
    textream_windows/
    ├── main.py
    ├── model/              <-- Your extracted model here
    │   ├── am/
    │   ├── conf/
    │   └── ...
    ├── ui/
    └── ...
    ```

## Usage

Run the application:

```bash
python main.py
```

The app will launch as a floating "Notch" at the top of your screen. Speak into your microphone to see the text highlight in real-time.
