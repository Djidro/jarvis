# J.A.R.V.I.S. (flat version: all files in one folder)

## Install (Windows 10/11)
1. Install Python 3.11+ from python.org (tick "Add Python to PATH").
2. Put all these files in one folder, e.g. C:\JARVIS, then in Command Prompt:
   cd C:\JARVIS
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
3. (Optional AI brain) Install Ollama from ollama.com, then run: ollama pull qwen2.5:1.5b
4. Test: python tests_phase1.py
5. (Voice) Download "vosk-model-small-en-us-0.15" from alphacephei.com/vosk/models and unzip it
   INSIDE C:\JARVIS, so the folder is C:\JARVIS\vosk-model-small-en-us-0.15
6. Run: python main.py   (browser opens at http://127.0.0.1:5000)

## Use
Click "Mic: off" to turn listening on. Say "Jarvis, what time is it". Say "stop" to interrupt speech.
Examples: open youtube | open notepad | open downloads | find file invoice | note: buy milk |
task: call mom | show tasks | set a timer for 5 minutes | remind me in 10 minutes to stretch |
volume up | take a screenshot | look up Alan Turing | delete file C:\Users\You\x.txt | daily report

## Safety
Only whitelisted apps launch; deletes need "yes"; actions are logged in actions.log;
SAFE_MODE in config.py blocks app launching. The AI never runs commands.
Your data (jarvis.db, actions.log) stays local. Do not upload them to GitHub.
