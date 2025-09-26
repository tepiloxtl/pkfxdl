# pkfxdl
Pokeflix downloader. I'm not going to hide it, it was made using Gemini. Deal with it  

Requires:  
* Python 3.x
* yt-dlp
* ffmpeg
* Chrome or other Chromium-related browser

This should work on Windows, assuming yt-dlp and ffmpeg executables are in the same directory as script

To use the script, go to your browsers extension page, check the "Developer mode" box and click newly shown "Load sparse" or "Load unpacked extension" button, and load the pokeflixex directory from this repo. This will show new button in your extension toolbar. Using this button on Pokeflix website and clicking "Copy value" will put link to video and series/episode title into your clipboard. Open command prompt in the directory containing script.py, type in `python3` for linux or `python` for windows, followed by space and paste contents of clipboard. Run this and it will download chosen episode.  

To download different language versions of episodes, open script.py and change LANGS_TO_DOWNLOAD variable on line 20. English version will always be downloaded and muxed alongside your chosen languages into a single file. To change langauge you will need to find audio track options in your player of choice.
