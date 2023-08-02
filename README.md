# twdl-resilient

This Python script is designed to robustly download Twitch streams. It will download the HLS segments of a Twitch stream in real-time, with the ability to automatically start recordings as well as resume recording in the event of ffmpeg crashing or a loss of connection to the stream. This script was designed with long streams in mind (subathons, 24 hours streams, etc.) with the goal of capturing as much of a stream as possible even in bad network conditions. Does your favorite streamer's ISP suck and cause stream to go down often? This stream recording script will pick right back up once the stream resumes.

Intended to be used alongside the [mergets](https://github.com/vodboysunited/mergets) script for handling the resulting .ts files.

## Why capture segmented (.ts) video clips rather than one continuous video file?

- For stream archivists, this makes it easier to archive long streams where it would otherwise be difficult or impractical to manage massive video files of potentially multi-day streams. The [mergets](https://github.com/vodboysunited/mergets) script allows you to specify a range of .ts files to merge into one video file and export to a separate location, ready for uploading/archival. All of this can be done while continuing to record the ongoing live stream without interruptions. In fewer words, you can pluck segments of video of configurable length from an ongoing recording to merge into a single video file.
- This approach reduces the chance of a corrupted video file causing a complete loss of the entire recorded stream.

## Features

- **Robust Downloading:** The script automatically retries when the stream is not available, ensuring a continuous recording process.
- **Quality Selection:** The script allows the user to choose the quality of the stream that they want to download.
- **Detailed Logging:** The script logs every disconnect and provides detailed information about each session, including uptime, number of segments downloaded, and disconnect counts.

## How to Use

Before first run, edit the script and adjust the configurable constants to your preference.
- `HLS_SEGMENT_LENGTH`: How long should each segment of video (.ts) should be
- `REFRESH_INTERVAL`: How often the script should check for an available stream. This applies both to checking for a stream to start and checking for the stream to resume in the case of the stream going down/offline
- `OUTPUT_DIRECTORY`: Where the .ts video files and disconnect log should be saved.
- `OAUTH_TOKEN`: Your OAuth token (see: https://github.com/streamlink/streamlink/discussions/4400#discussioncomment-2377338)

To use the script, you need to pass the channel name as an argument and optionally specify the stream quality:

`
python twdl_resilient.py <channel_name> --quality <quality>
`

Available Arguments:

- `<channel_name>`: The name of the Twitch channel from which you want to download the stream.
- `<quality>`: The quality of the stream you want to download. Leaving out this arg will select "best" quality by default.

Example:

`
python twdl_resilient.py paymoneywubby
`
or
`
python twdl_resilient.py paymoneywubby --quality 480p
`

The first command will start downloading the stream from PaymoneyWubby at the best quality available. The second command will start downloading the stream from PaymoneyWubby at 480p resolution.

## Dependencies

This script relies on the following external tools and libraries:

- `streamlink`: This tool is used to fetch the actual URL of the stream. Please ensure that you have installed it and added it to your PATH.
- `ffmpeg`: This tool is used to download and convert the video files. Make sure to have it installed and added to your PATH.
