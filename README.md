# Create Video Preview

A Python script that creates video previews by extracting and combining short clips from throughout a video file, perfect for creating quick "sampler" videos to preview content.

## Features

- **Automatic FFmpeg Detection**: Finds and lets you select from available FFmpeg installations
- **Interactive Video Selection**: Browse MP4 files with duration, size, and modification date information
- **Customizable Preview Length**: Choose clip duration (1-60 seconds) and total preview percentage (1-50%)
- **Smart File Handling**: Options to overwrite, skip, or rename existing output files
- **High Quality Output**: Uses optimized encoding settings (CRF 10, 320k audio bitrate)
- **Automatic Cleanup**: Removes temporary files after processing

## Requirements

- Python 3.6+
- FFmpeg (automatically detected or manually specified)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/dataforge/create-video-preview.git
cd create-video-preview
```

2. Ensure FFmpeg is installed and accessible:
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) or install via package manager
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg` (Ubuntu/Debian) or equivalent for your distribution

## Usage

### Interactive Mode (Recommended)
```bash
python create_preview.py
```

This will:
1. Detect available FFmpeg installations
2. Show all MP4 files in the current directory with metadata
3. Let you select a video file
4. Configure clip length and preview percentage

### Command Line Mode
```bash
python create_preview.py path/to/video.mp4
```

### Example Workflow

1. **Select Video**: Choose from available MP4 files with duration info
2. **Set Clip Length**: Default 10 seconds (1-60 seconds allowed)
3. **Choose Preview Percentage**: Select what portion of the video to sample
   - 5% of a 60-minute video = 3 minutes of preview (18 clips at 10 seconds each)
   - 10% of a 30-minute video = 3 minutes of preview (18 clips at 10 seconds each)
4. **Output**: Creates `[original_name] sampler.mp4`

## How It Works

The script extracts clips evenly distributed throughout the video:

1. **Analysis**: Gets video duration and calculates clip positions
2. **Extraction**: Creates temporary clips at calculated intervals
3. **Concatenation**: Combines clips into a single preview video
4. **Cleanup**: Removes temporary files

For example, with a 60-minute video and 10% preview:
- Total preview time: 6 minutes
- With 10-second clips: 36 clips extracted
- Clips taken every ~100 seconds throughout the video

## Output Format

- **Video Codec**: H.264 (libx264) with CRF 10 (high quality)
- **Audio Codec**: AAC at 320k bitrate
- **Naming**: `[original_filename] sampler.mp4`

## Error Handling

- Validates FFmpeg installation and accessibility
- Checks video file existence and readability
- Handles file conflicts with user choices (overwrite/skip/rename)
- Provides clear error messages for common issues

## Technical Details

- Uses FFmpeg's `-ss` (seek) and `-t` (duration) parameters for precise clip extraction
- Creates a concat file for efficient clip combination
- Temporary files use timestamps to avoid conflicts
- Cross-platform compatibility (Windows, macOS, Linux)

## Troubleshooting

**FFmpeg not found:**
- Ensure FFmpeg is installed and in your system PATH
- The script will search common installation directories
- You can select from multiple detected installations

**Video not processing:**
- Check that the video file is a valid MP4
- Ensure sufficient disk space for temporary files
- Verify the video isn't corrupted or encrypted

**Output quality issues:**
- The script uses high-quality settings (CRF 10)
- For smaller files, increase CRF value in the code (line 230)

## License

This project is open source. Feel free to modify and distribute as needed.