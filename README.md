MarkForMe 🚀

MarkForMe is a background, seamless Markdown renderer designed specifically for Microsoft OneNote.

By listening to global system keyboard events and taking over the clipboard, it enables instant, in-place conversion of plain text into beautifully formatted rich text in OneNote—an editor that lacks native Markdown support.

✨ Key Features

⚡️ Seamless Interception & Rendering: Input your text or select your code in OneNote, press Enter or Ctrl+Enter, and it will instantly be replaced in-place with rendered rich text.

📐 Native Math Formula Support: Supports inline $E=mc^2$ and block $$...$$ formulas, leveraging latex2mathml to convert them into native MathML recognizable by OneNote.

💻 IDE-Grade Code Block Highlighting: Powered by Pygments to render code blocks (wrapped in triple backticks), offering 3 built-in themes (PyCharm Dark (Dark+), Monokai, and Classic Light (VS Light)). It injects formatting at the <table> level to perfectly solve OneNote's annoying issue of stripping background colors.

🔧 Three Highly Flexible Interaction Modes:

Append Render: Reads the clipboard and writes the rendered output directly on the line below the current cursor.

Partial Overwrite: Reads the clipboard and directly overwrites the currently selected plain text.

Fully Automatic Replacement: Automatically simulates Ctrl+C to copy the selected area, renders it in the background, and overwrites it automatically—no manual copy-pasting required!

🎨 Modern Config UI: A beautiful dark, semi-transparent control panel designed with customtkinter, with support for persistent setting state storage.

Demo Interface

!(https://github.com/user-attachments/assets/aaf3ead2-2501-4a47-bcad-0490367960a7)
!(https://github.com/user-attachments/assets/ef21ce12-e6db-4237-9407-ee884b93564f)

System Requirements

Operating System: Windows 10 / Windows 11 (Relies on pywin32 to manipulate the native Windows HTML clipboard format)

Python Version: Python 3.10+

Dependencies

You can quickly install all dependencies via requirements.txt in the root directory:

pip install -r requirements.txt


(Main dependencies include: customtkinter, markdown-it-py, mdit-py-plugins, latex2mathml, pygments, keyboard, pywin32, pyperclip, psutil)

Instructions for Use

1. Running from Source Code

Activate your Python environment in your terminal, and run the following command in the project root:

python main.py


A control panel will pop up. Ensure that the "Background Listening" (后台运行监听) switch is turned on. Then, simply select the plain Markdown text in OneNote and press Enter to trigger the rendering!

2. Packaging into a Standalone .exe Executable

If you wish to run this on a computer without a Python environment, you can package it into a single-file executable using PyInstaller.

Note: Since latex2mathml relies on internal static data dictionaries, you need to explicitly use the --add-data flag to bundle the local environment files:

# Please replace "D:\Python\envs\MarkForMe" in the path below with your actual local Python virtual environment path
pyinstaller --clean -F -w --add-data "D:\Python\envs\MarkForMe\lib\site-packages\latex2mathml\unimathsymbols.txt;latex2mathml\" -y main.py


Once successfully packaged, you can find main.exe inside the dist/ directory.

Project Structure

MarkForMe/
├── main.py                # Main entry file
├── core/
│   ├── state.py           # Global state management & local configuration persistence (config.json)
│   ├── key_listener.py    # Global keyboard event hook & mode routing
│   ├── clipboard_mgr.py   # Deep wrapper for native Windows HTML clipboard format
│   └── window_utils.py    # Focus window tracking, locking OneNote process state
├── parser/
│   └── md_parser.py       # Core rendering engine coordinating Markdown, Pygments, and LaTeX -> MathML
├── ui/
│   └── main_window.py     # Modern console control panel UI built with CustomTkinter
└── requirements.txt       # Project third-party library dependencies manifest

🔔 Note on Language > The software's main user interface is in Chinese. If you wish to change the display language, please manually modify the language configurations or strings directly in the source code.

License

This project is licensed under the MIT License, allowing free modification and redistribution.
