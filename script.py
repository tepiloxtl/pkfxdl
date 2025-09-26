import sys
import os
import subprocess
import shutil
from urllib.parse import urlparse, urlunparse

# Provided list of available languages and their identifiers
ALL_LANGS = {
    "audio_ar": "Arabic", "audio_cs": "Czech", "audio_da": "Danish",
    "audio_nl": "Dutch", "audio_en_descriptive": "English (Descriptive)",
    "audio_fi": "Finnish", "audio_fr": "French", "audio_de": "German",
    "audio_he": "Hebrew", "audio_it": "Italian", "audio_cmn-TW": "Mandarin Chinese (Taiwan)",
    "audio_nb": "Norwegian Bokmal", "audio_pl": "Polish", "audio_pt-BR": "Portuguese (Brazil)",
    "audio_pt-PT": "Portuguese (Portugal)", "audio_ro": "Romanian", "audio_ru": "Russian",
    "audio_es-419": "Spanish (Latin America)", "audio_es-ES": "Spanish (Spain)",
    "audio_sv": "Swedish", "audio_th": "Thai", "audio_tr": "Turkish", "audio_uk": "Ukrainian",
}

# Variable containing which languages to download (in addition to default English)
LANGS_TO_DOWNLOAD = ["audio_pl", "audio_de"]

# Mapping for ffmpeg's 3-letter language codes
LANG_CODE_MAP = {
    "audio_pl": "pol", "audio_de": "ger", "audio_fr": "fre", "audio_es-ES": "spa",
    "audio_ar": "ara", "audio_cs": "ces", "audio_da": "dan", "audio_nl": "nld",
    "audio_fi": "fin", "audio_he": "heb", "audio_it": "ita", "audio_cmn-TW": "chi",
    "audio_nb": "nor", "audio_pt-BR": "por", "audio_pt-PT": "por", "audio_ro": "ron",
    "audio_ru": "rus", "audio_es-419": "spa", "audio_sv": "swe", "audio_th": "tha",
    "audio_tr": "tur", "audio_uk": "ukr"
}

def run_command_live(command, command_title=""):
    """Executes a command and prints its output live."""
    print(f"\n----- Running: {command_title} -----")
    print(subprocess.list2cmdline(command))
    print("-" * 30)
    
    # On Windows, ffmpeg can hang if its stderr buffer fills up.
    # Redirecting stderr to stdout solves this by allowing us to read both streams together.
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding='utf-8', errors='replace', bufsize=1
    )

    was_last_line_progress = False
    if process.stdout:
        for line in iter(process.stdout.readline, ''):
            stripped_line = line.lstrip()
            # Check for yt-dlp or ffmpeg progress lines
            if stripped_line.startswith(('[download]', '[ffmpeg]', 'frame=', 'size=')):
                print(line.strip(), end='\r')
                was_last_line_progress = True
            else:
                if was_last_line_progress: print()
                print(line, end='')
                was_last_line_progress = False
    
    if was_last_line_progress: print()
    
    return_code = process.wait()
    print("----- End Live Output -----\n")

    if return_code != 0:
        # The error message from stderr was already printed live because we merged the streams.
        # We just need to raise an exception to halt the script's execution.
        raise subprocess.CalledProcessError(
            returncode=return_code, cmd=command, stderr="See console output above for details."
        )

def download_video(url, series, title, extra_langs):
    """
    Downloads a video and additional audio tracks, then muxes them together.
    """
    # Check for required command-line tools
    if not shutil.which('yt-dlp'):
        print("\nError: 'yt-dlp' command not found.")
        print("Please ensure yt-dlp is installed and in your system's PATH.")
        sys.exit(1)
    if not shutil.which('ffmpeg'):
        print("\nError: 'ffmpeg' command not found.")
        print("Please ensure ffmpeg is installed and in your system's PATH.")
        sys.exit(1)

    # Use a temporary directory for intermediate files
    temp_dir = os.path.join(series, f".{title}_temp")
    
    try:
        # Step 1: Create directories
        os.makedirs(series, exist_ok=True)
        os.makedirs(temp_dir, exist_ok=True)

        # Step 2: Download the main video with its default (English) audio
        print(f"Downloading main video for '{title}'...")
        main_video_path = os.path.join(temp_dir, 'video_en.mkv')
        yt_dlp_cmd_main = [
            'yt-dlp', url, '-f', 'bestvideo+bestaudio/best',
            '--merge-output-format', 'mkv', '--output', main_video_path
        ]
        run_command_live(yt_dlp_cmd_main, "Download Main Video + English Audio")

        # Step 3: Download additional audio tracks
        additional_audio_files = []
        parsed_url = urlparse(url)
        base_path = os.path.dirname(parsed_url.path)

        for lang_code in extra_langs:
            lang_name = ALL_LANGS.get(lang_code, lang_code)
            print(f"Downloading {lang_name} audio...")
            
            audio_url_path = f"{base_path}/{lang_code}.m3u8"
            audio_url = urlunparse(parsed_url._replace(path=audio_url_path))
            audio_output_path = os.path.join(temp_dir, f"{lang_code}.m4a")
            
            yt_dlp_cmd_audio = ['yt-dlp', audio_url, '-o', audio_output_path]
            run_command_live(yt_dlp_cmd_audio, f"Download {lang_name} Audio")
            additional_audio_files.append(audio_output_path)

        # Step 4: Mux video and all audio tracks using ffmpeg
        print("Muxing video and all audio tracks...")
        output_path = os.path.join(series, f"{title}.mkv")
        
        ffmpeg_cmd = ['ffmpeg', '-y', '-i', main_video_path]
        for audio_file in additional_audio_files:
            ffmpeg_cmd.extend(['-i', audio_file])
            
        # Map streams: 1 video, and N audio streams
        ffmpeg_cmd.extend(['-map', '0:v:0', '-map', '0:a:0'])
        for i in range(len(additional_audio_files)):
            ffmpeg_cmd.extend(['-map', f'{i+1}:a:0'])
            
        # Add metadata for each audio track
        ffmpeg_cmd.extend(['-metadata:s:a:0', 'language=eng', '-metadata:s:a:0', 'title=English'])
        for i, lang_code in enumerate(extra_langs):
            lang_name = ALL_LANGS.get(lang_code, lang_code)
            lang_3_letter = LANG_CODE_MAP.get(lang_code, lang_code[:3])
            ffmpeg_cmd.extend([f'-metadata:s:a:{i+1}', f'language={lang_3_letter}'])
            ffmpeg_cmd.extend([f'-metadata:s:a:{i+1}', f'title={lang_name}'])
            
        ffmpeg_cmd.extend(['-c', 'copy', output_path])
        
        run_command_live(ffmpeg_cmd, "Muxing final video file")
        
        print(f"\nSuccessfully created '{output_path}' with multiple audio tracks.")

    except subprocess.CalledProcessError as e:
        print("\nAn error occurred while running a command.")
        print(f"Return code: {e.returncode}")
        print("\n----- STDERR -----")
        print(e.stderr)
        print("----- END STDERR -----\n")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)
    finally:
        # Step 5: Clean up temporary files
        if os.path.isdir(temp_dir):
            print("Cleaning up temporary files...")
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python download.py \"<url>\" \"<series>\" \"<title>\"")
        print("Example: python download.py \"https://example.com/playlist.m3u8\" \"My Series\" \"Episode 1\"")
        sys.exit(1)

    video_url = sys.argv[1]
    series_name = sys.argv[2]
    video_title = sys.argv[3]

    download_video(video_url, series_name, video_title, LANGS_TO_DOWNLOAD)

