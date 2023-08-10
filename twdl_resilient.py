import os
import time
import argparse
import subprocess
import signal
import datetime
import logging

# Configurable constants
HLS_SEGMENT_LENGTH = '5'
REFRESH_INTERVAL = 5  # seconds
OUTPUT_DIRECTORY = r'/path/to/your/output/directory'
OAUTH_TOKEN = 'your-oauth-token-here'

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("channel_name", help="Twitch channel name")
parser.add_argument("--quality", default="best", help="Stream quality")
args = parser.parse_args()

def get_stream_url(channel_name, quality):
    try:
        stream_url = subprocess.check_output(['streamlink', '--http-header', f'Authorization=OAuth {OAUTH_TOKEN}', '--stream-url', f'https://www.twitch.tv/{channel_name}', quality])
        return stream_url.decode().strip()
    except subprocess.CalledProcessError:
        return None

def capture_stream(stream_url, directory):
    try:
        with open(os.devnull, 'w') as devnull:
            process = subprocess.Popen(['ffmpeg', '-i', stream_url, '-c:v', 'copy', '-c:a', 'copy', '-f', 'hls', '-hls_time', HLS_SEGMENT_LENGTH, '-hls_list_size', '0', '-hls_flags', 'append_list+omit_endlist', f'{directory}/stream.m3u8'], stdout=devnull, stderr=devnull)
        return process
    except subprocess.CalledProcessError as e:
        print(f"Error in capturing the stream: {str(e)}")

def create_directory(channel_name):
    directory = f'{OUTPUT_DIRECTORY}/{channel_name}_{len([name for name in os.listdir(OUTPUT_DIRECTORY) if name.startswith(channel_name)])+1}'
    os.makedirs(directory, exist_ok=True)
    return directory

def log_disconnect(disconnects_log, disconnects, uptime, segments):
    disconnects_log.write(f"Disconnect {disconnects + 1}: Uptime: {uptime} | Segments: {segments}\n")
    disconnects_log.flush()

def trunc_to_fit(output):
    terminal_width = os.get_terminal_size().columns
    return output[:terminal_width]

def main():
    loading_symbols = ['|', '/', '-', '\\']
    loading_index = 0
    if os.name == 'posix':
        os.system('clear')
    elif os.name in ('nt', 'dos', 'ce'):
        os.system('cls')

    try:
        start_time = None
        ffmpeg_process = None
        directory = None
        disconnects_log = None
        disconnects = 0
        while True:
            stream_url = get_stream_url(args.channel_name, args.quality)
            if stream_url is None:
                if ffmpeg_process is not None and ffmpeg_process.poll() is None:
                    log_disconnect(disconnects_log, disconnects, uptime, segments)
                    disconnects += 1
                    ffmpeg_process.terminate()
                    ffmpeg_process = None
                loading_symbol = loading_symbols[loading_index % len(loading_symbols)]
                message = f"\033[93mStream not available yet. Retrying in {REFRESH_INTERVAL} seconds... {loading_symbol}\033[0m"
                print(trunc_to_fit(message), end='\r')
                time.sleep(REFRESH_INTERVAL)
                loading_index += 1
            else:
                if start_time is None:
                    start_time = datetime.datetime.now()
                    print("\033[95mStream is live! Starting to create HLS segments...\033[0m")
                    directory = create_directory(args.channel_name)
                    print(f"Output Directory: \033[93m{directory}\033[0m")
                    disconnects_log = open(os.path.join(directory, 'disconnects.log'), 'w')
                    ffmpeg_process = capture_stream(stream_url, directory)
                elif ffmpeg_process is not None and ffmpeg_process.poll() is not None:
                    log_disconnect(disconnects_log, disconnects, uptime, segments)
                    disconnects += 1
                    ffmpeg_process = None
                if ffmpeg_process is None:
                    ffmpeg_process = capture_stream(stream_url, directory)
                if ffmpeg_process is not None and ffmpeg_process.poll() is None:
                    uptime = str(datetime.datetime.now() - start_time)[:-7]
                    segments = len([name for name in os.listdir(directory) if name.endswith('.ts')])
                    status_output = f"\033[91mRECORDING\033[0m: \033[92m{args.channel_name}\033[0m ({args.quality}) | Uptime: \033[92m{uptime}\033[0m | Segments: \033[92m{segments}\033[0m | Disconnects: \033[91m{disconnects}\033[0m"
                    print(trunc_to_fit(status_output), end='\r', flush=True)
                    time.sleep(1)
    except KeyboardInterrupt:
        print(f"\nScript terminated by user. Total uptime: {uptime} | Total segments created: {segments} | Total disconnects: {disconnects}")
        if ffmpeg_process is not None:
            ffmpeg_process.terminate()
        if disconnects_log is not None:
            disconnects_log.write(f"Total Uptime: {uptime} | Total Segments: {segments} | Total Disconnects: {disconnects}")
            disconnects_log.close()


if __name__ == "__main__":
    main()
