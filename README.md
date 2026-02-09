<p align="center">
  <img src="Textream/Textream/Assets.xcassets/AppIcon.appiconset/icon_256x256.png" width="128" height="128" alt="Textream icon">
</p>

<h1 align="center">Textream</h1>

<p align="center">
  <strong>A free teleprompter that highlights your script in real-time as you speak.</strong>
</p>

<p align="center">
  Built for streamers, presenters, and creators. Now supporting <b>macOS</b> and <b>Windows</b>.
</p>

<p align="center">
  <a href="#windows-setup">Windows Setup</a> · <a href="#mac-download">macOS Download</a> · <a href="#features">Features</a> · <a href="#how-it-works">How It Works</a>
</p>

<p align="center">
  <img src="docs/video.gif" width="600" alt="Textream demo">
</p>

---

## 🪟 Windows Setup

Textream for Windows is built with Python, PyQt6, and Vosk for high-performance offline speech recognition.

### Quick Start
Run these commands in your terminal:

```powershell
# 1. Clone the project
git clone https://github.com/f/textream.git
cd textream

# 2. Install dependencies
pip install -r textream_windows/requirements.txt

# 3. Launch Textream
python textream_windows/main.py
```

> **Note:** On first launch, the app will automatically download the necessary language models for offline recognition.

### 🎮 Windows Controls & Shortcuts
Once the overlay is active, you can use the floating controls or **Right-Click** for settings:
- 🎤/🔇 **Microphone Toggle:** Quickly enable or disable voice recognition.
- ⏪/⏩ **Word Jump:** Skip forward or go back by one word.
- ⏸/▶️ **Play/Pause:** Pause the tracker and resume when ready.
- 🏎️ **Auto-Advance:** Set a speed (1x to 5x) to move text automatically if you prefer a steady pace.
- 🖱️ **Drag & Move:** Click and drag anywhere on the overlay to reposition it.

---

## 🍎 macOS Download

**[Download the latest .dmg from Releases](https://github.com/f/textream/releases/latest)**

Or install with Homebrew:

```bash
brew install f/textream/textream
```

### First launch (macOS)
Since Textream is distributed outside the App Store, run this once in Terminal:
```bash
xattr -cr /Applications/Textream.app
```
Then **Right-Click → Open**.

---

## ✨ Features

- **Real-time voice tracking** — High-performance offline speech recognition highlights words as you say them. No cloud, works everywhere.
- **Dynamic Overlay** — A sleek, floating overlay that sits above all apps. Visible only to you, invisible to your audience (perfect for OBS/Zoom).
- **Live Waveform** — Visual voice activity indicator with multiple styles (**Bars, Dots, Wave, Solid, Mirror, Outline**).
- **Control Center** — Built-in buttons for Mic toggle, Rewind/Forward, and variable Auto-Advance speeds.
- **Rich Customization** — Change themes (Dark/Light), fonts, colors, and line counts (1 to 5) instantly via the **Right-Click** menu.
- **Multi-language Support** — Recognition support for Turkish, English, Spanish, French, German, and Chinese.
- **Privacy First** — All processing happens locally using Vosk. Your voice never leaves your machine.

## 🚀 How It Works

1. **Paste your script** — Drop your text into the editor. Use the 📋 **Paste** shortcut for speed.
2. **Hit Start** — The teleprompter overlay appears at the top of your screen.
3. **Start speaking** — Words highlight in real-time. When you finish, the overlay stays until you close it, or you can jump around the text manually.
4. **Tune on the fly** — Right-click the overlay anytime to switch languages, themes, or font sizes without stopping.

---

## 🛠️ Developer Information

### Windows (Python)
- **UI:** PyQt6 (Hardware accelerated)
- **Engine:** Vosk API (Offline Kaldi-based recognition)
- **Matcher:** Fuzzy String Matching with anchor-based tracking.

### macOS (Swift)
- **UI:** SwiftUI
- **Engine:** Apple Speech Framework

---

## 📄 License
MIT

<p align="center">
  Original idea by <a href="https://x.com/semihdev">Semih Kışlar</a><br>
  Made with ❤️ by <a href="https://fka.dev">Fatih Kadir Akin</a> & Contributors
</p>
