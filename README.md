# **Pokeflix Downloader (pkfxdl)**

This project provides a Python script and browser extension to download Pokeflix videos with multiple audio tracks, using yt-dlp and ffmpeg to create a single MKV file.

## **Features**

* Downloads video with both the default English audio and additional languages of your choice.  
* Merges all streams into a single .mkv file.  
* Companion browser extension to easily copy video information.  
* Live progress updates in the terminal.

## **Prerequisites**

* **Python 3.x**  
* **yt-dlp**  
* **ffmpeg**  
* A **Chromium-based browser** (e.g., Google Chrome, Edge, Brave).

## **Installation & Setup**

### **1\. Get the Project Files**

Clone or download this repository.

### **2\. Set Up Dependencies (yt-dlp & ffmpeg)**

**For Windows:** The simplest method is to place the `yt-dlp.exe` and `ffmpeg.exe` executables in the same directory as the script.

**Alternative:** Install `yt-dlp` and `ffmpeg` and add them to your system's PATH.

### **3\. Install the Browser Extension**

1. In your browser, go to the extensions page (e.g., chrome://extensions).  
2. Enable **Developer mode**.  
3. Click **Load unpacked** and select the `pokeflixex` directory from this project.  
4. The "Pokeflix Copier" extension will now be available in your toolbar.

## **How to Use**

1. Go to a Pokeflix episode page.  
2. Click the extension icon, then **Copy Value** to copy the command arguments.  
3. Open a terminal in the script's directory.  
4. Type python script.py (or python3), followed by a space, and paste the content from your clipboard. It should look like this:  
   \# Example command  
   `python script.py "https://example.com/some/video.m3u8" "Series Name" "Episode Title"`

5. Press Enter to start the download. The final video will be saved in the Series Name directory.

## **Configuration**

### **Customizing Audio Languages**

1. Open download.py in a text editor.  
2. Find the `LANGS_TO_DOWNLOAD` list (on line 20).  
3. Modify this list with your desired language codes. See the `ALL_LANGS` dictionary for all available options.  
   \# Example: To download Polish and German audio  
   `LANGS_TO_DOWNLOAD = ["audio_pl", "audio_de"]`

4. Save the file. Your new language choices will be used on the next run.

The final .mkv file will contain all selected audio tracks. Use your media player's audio options to switch between them.
