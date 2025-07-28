#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import glob
import re
import math
from datetime import datetime
from pathlib import Path

def find_ffmpeg():
    """Find ffmpeg executable and let user choose"""
    all_paths = []
    
    # Check PATH first
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        all_paths.append(("PATH", ffmpeg_path))
        print(f"Found ffmpeg in PATH: {ffmpeg_path}")
    else:
        print("ffmpeg not found in PATH")
    
    # Try to find it using where/which command
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(['where', 'ffmpeg'], capture_output=True, text=True)
        else:  # Unix-like systems
            result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            paths = result.stdout.strip().split('\n')
            for path in paths:
                path = path.strip()
                if path not in [p[1] for p in all_paths]:  # Avoid duplicates
                    all_paths.append(("System", path))
    except Exception:
        pass
    
    # Search common directories if no PATH version found
    if not any(source == "PATH" for source, _ in all_paths):
        print("Searching for ffmpeg in system directories...")
        search_dirs = []
        
        if os.name == 'nt':  # Windows
            # Search Program Files and common download locations
            for root_dir in [r"C:\Program Files", r"C:\Program Files (x86)", os.path.expanduser("~")]:
                if os.path.exists(root_dir):
                    for root, dirs, files in os.walk(root_dir):
                        if 'ffmpeg.exe' in files:
                            full_path = os.path.join(root, 'ffmpeg.exe')
                            if full_path not in [p[1] for p in all_paths]:  # Avoid duplicates
                                all_paths.append(("Found", full_path))
                        # Limit depth to avoid long searches
                        if root.count(os.sep) - root_dir.count(os.sep) > 3:
                            dirs.clear()
    
    if not all_paths:
        raise FileNotFoundError("ffmpeg not found. Please install ffmpeg or add it to PATH.")
    
    # If only one path found (and it's in PATH), use it automatically
    if len(all_paths) == 1 and all_paths[0][0] == "PATH":
        return all_paths[0][1]
    
    # Let user choose which ffmpeg to use
    print(f"\nFound {len(all_paths)} ffmpeg installation(s):")
    for i, (source, path) in enumerate(all_paths, 1):
        print(f"  [{i}] {source}: {path}")
    
    while True:
        try:
            choice = input(f"\nSelect ffmpeg to use (1-{len(all_paths)}, or Enter for default): ").strip()
            if not choice:
                selected_path = all_paths[0][1]
                print(f"Using default: {selected_path}")
                return selected_path
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(all_paths):
                selected_path = all_paths[choice_num - 1][1]
                print(f"Using: {selected_path}")
                return selected_path
            else:
                print(f"Please enter a number between 1 and {len(all_paths)}.")
        except ValueError:
            print("Please enter a valid number.")

def format_duration(seconds):
    """Format duration in seconds to hh:mm:ss"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def get_video_duration(ffmpeg_path, video_path):
    """Get video duration in seconds using ffmpeg"""
    try:
        result = subprocess.run([
            ffmpeg_path, '-i', video_path
        ], capture_output=True, text=True)
        
        # Parse duration from ffmpeg output (ffmpeg outputs to stderr)
        output = result.stderr if result.stderr else result.stdout
        duration_match = re.search(r'Duration: (\d+):(\d+):(\d+(?:\.\d+)?)', output)
        if duration_match:
            hours, minutes, seconds_str = duration_match.groups()
            hours, minutes = int(hours), int(minutes)
            seconds = float(seconds_str)
            return int(hours * 3600 + minutes * 60 + seconds)
        else:
            raise ValueError("Could not parse video duration")
    except subprocess.SubprocessError as e:
        raise RuntimeError(f"Failed to get video duration: {e}")

def select_video_file(ffmpeg_path):
    """Interactive video file selection with duration info"""
    video_files = glob.glob("*.mp4")
    
    if not video_files:
        print("No MP4 files found in current directory.")
        sys.exit(1)
    
    print("Please select the video file you want to process:")
    print("Getting video durations...")
    
    video_info = []
    for i, video_file in enumerate(video_files, 1):
        file_path = Path(video_file)
        size_mb = round(file_path.stat().st_size / (1024 * 1024), 2)
        modified_time = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        
        try:
            duration = get_video_duration(ffmpeg_path, video_file)
            duration_str = format_duration(duration)
            video_info.append((video_file, duration))
        except Exception:
            duration_str = "Unknown"
            video_info.append((video_file, 0))
        
        print(f"[{i}] {video_file} - {duration_str} - {modified_time} - {size_mb} MB")
    
    while True:
        try:
            choice = int(input("Enter the number: "))
            if 1 <= choice <= len(video_files):
                return video_info[choice - 1]
            else:
                print("Invalid selection. Please enter a valid number.")
        except ValueError:
            print("Invalid selection. Please enter a valid number.")

def handle_existing_file(output_path):
    """Handle existing output file with user choices"""
    if not os.path.exists(output_path):
        return output_path
    
    while True:
        choice = input(f"{output_path} already exists. Do you want to [O]verwrite, [S]kip, or [R]ename? (O/S/R): ").upper()
        
        if choice == 'O':
            print(f"Overwriting {output_path}")
            os.remove(output_path)
            return output_path
        elif choice == 'S':
            print("Skipping operation.")
            sys.exit(0)
        elif choice == 'R':
            new_name = input("Enter the new filename (without extension): ")
            return str(Path(output_path).parent / f"{new_name}.mp4")
        else:
            print("Invalid choice. Please enter O, S, or R.")

def get_clip_length():
    """Get clip length from user with 10 second default"""
    while True:
        try:
            clip_input = input("\nEnter clip length in seconds (default 10): ").strip()
            if not clip_input:
                return 10
            clip_length = int(clip_input)
            if 1 <= clip_length <= 60:
                return clip_length
            else:
                print("Please enter a clip length between 1 and 60 seconds.")
        except ValueError:
            print("Please enter a valid number.")

def get_preview_percentage(duration, clip_length):
    """Get preview percentage from user with examples"""
    print(f"\nOriginal video duration: {format_duration(duration)}")
    print(f"Clip length: {clip_length} seconds")
    print("Choose preview percentage:")
    
    percentages = [5, 10, 15, 20, 25]
    for pct in percentages:
        preview_time = duration * (pct / 100)
        num_clips = math.ceil(preview_time / clip_length)
        print(f"  {pct}% would be {format_duration(preview_time)} ({num_clips} clips)")
    
    while True:
        try:
            percentage = float(input("\nEnter percentage (1-50): "))
            if 1 <= percentage <= 50:
                preview_duration = round(duration * (percentage / 100))
                num_clips = math.ceil(preview_duration / clip_length)
                print(f"Preview will be {format_duration(preview_duration)} ({percentage}% of original, {num_clips} clips)")
                return percentage / 100
            else:
                print("Please enter a percentage between 1 and 50.")
        except ValueError:
            print("Please enter a valid number.")

def create_preview_clips(ffmpeg_path, input_video, clips_dir, duration, preview_duration, clip_length):
    """Extract preview clips from video"""
    number_of_clips = math.ceil(preview_duration / clip_length)
    clip_paths = []
    
    print(f"Extracting {number_of_clips} clips of {clip_length} seconds each...")
    
    for i in range(number_of_clips):
        start_time = (duration / number_of_clips) * i
        clip_path = clips_dir / f"clip{i}.mp4"
        
        cmd = [
            ffmpeg_path,
            '-ss', str(start_time),
            '-t', str(clip_length),
            '-i', input_video,
            '-c:v', 'libx264',
            '-crf', '10',
            '-c:a', 'aac',
            '-b:a', '320k',
            '-shortest',
            str(clip_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            clip_paths.append(clip_path)
            print(f"Extracted clip {i+1}/{number_of_clips}")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to extract clip {i}: {e}")
    
    return clip_paths

def create_concat_file(clip_paths, concat_file_path):
    """Create ffmpeg concat file"""
    with open(concat_file_path, 'w') as f:
        for clip_path in clip_paths:
            # Use forward slashes for ffmpeg compatibility
            abs_path = str(clip_path.resolve()).replace('\\', '/')
            f.write(f"file '{abs_path}'\n")

def combine_clips(ffmpeg_path, concat_file_path, output_preview):
    """Combine clips into final preview video"""
    cmd = [
        ffmpeg_path,
        '-f', 'concat',
        '-safe', '0',
        '-i', str(concat_file_path),
        '-c', 'copy',
        output_preview
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"Preview created: {output_preview}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to combine clips: {e}")

def cleanup_temp_files(clips_dir, concat_file_path):
    """Clean up temporary files and directories"""
    try:
        if clips_dir.exists():
            shutil.rmtree(clips_dir)
        if concat_file_path.exists():
            concat_file_path.unlink()
        print("Temporary files cleaned up.")
    except Exception as e:
        print(f"Warning: Could not clean up temporary files: {e}")

def main():
    try:
        # Find ffmpeg
        ffmpeg_path = find_ffmpeg()
        print(f"Using ffmpeg at: {ffmpeg_path}")
        
        # Get input video
        if len(sys.argv) > 1:
            input_video = sys.argv[1]
            if not os.path.exists(input_video):
                print(f"Error: Video file '{input_video}' not found.")
                sys.exit(1)
            duration = get_video_duration(ffmpeg_path, input_video)
        else:
            input_video, duration = select_video_file(ffmpeg_path)
        
        # Get clip length from user
        clip_length = get_clip_length()
        
        # Get preview percentage from user
        preview_percentage = get_preview_percentage(duration, clip_length)
        preview_duration = round(duration * preview_percentage)
        
        # Create output filename
        input_path = Path(input_video)
        output_preview = str(input_path.parent / f"{input_path.stem} sampler.mp4")
        output_preview = handle_existing_file(output_preview)
        
        # Create temporary directory
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S%f")[:-3]
        clips_dir = Path(f"clips_{timestamp}")
        clips_dir.mkdir(exist_ok=True)
        
        # Create preview clips
        clip_paths = create_preview_clips(
            ffmpeg_path, input_video, clips_dir, 
            duration, preview_duration, clip_length
        )
        
        # Create concat file and combine clips
        concat_file_path = Path("concat.txt")
        create_concat_file(clip_paths, concat_file_path)
        combine_clips(ffmpeg_path, concat_file_path, output_preview)
        
        # Clean up
        cleanup_temp_files(clips_dir, concat_file_path)
        
        print("Preview creation completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()