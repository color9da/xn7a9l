"""
Video Processor - Quality Enhancement + Upscale
1. Upscale to 1080x1920 with high-quality algorithm
2. ENHANCE quality (sharpen + improve clarity)
3. Remove watermark (bottom-right corner)
4. KEEP ORIGINAL AUDIO - NO CHANGES
"""
import os
import subprocess
import sys
from pathlib import Path

# Set UTF-8 encoding for console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Paths
input_dir = "Videos"
output_dir = "Processed_Videos"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)


def process_single_video(video_path):
    """
    Process a single video: upscale + enhance quality + remove watermark
    
    Args:
        video_path: Path to input video (e.g., "Videos/video.mp4")
    
    Returns:
        Path to processed video, or None if failed
    """
    if not os.path.exists(video_path):
        print(f"Error: Video not found: {video_path}")
        return None

    filename = os.path.basename(video_path)
    out_path = os.path.join(output_dir, filename)

    # Skip if already processed
    if os.path.exists(out_path):
        print(f"Skipping {filename} - already processed")
        return out_path

    # Get original resolution
    cmd_probe = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", video_path
    ]
    try:
        res = subprocess.check_output(cmd_probe).decode("utf-8").strip()
        width, height = map(int, res.split("x"))
    except Exception as e:
        print(f"Failed to get resolution for {video_path}: {e}")
        return None

    print(f"Original size: {width}x{height}")

    # Calculate watermark position AFTER upscaling to 1080x1920
    w_delogo = 180  # watermark width after upscale
    h_delogo = 80   # watermark height after upscale
    
    x_delogo = 1080 - w_delogo - 5
    y_delogo = 1920 - h_delogo - 5

    print(f"Processing {filename}...")
    print(f"  Upscaling to: 1080x1920")
    print(f"  Removing watermark at: x={x_delogo}, y={y_delogo}, w={w_delogo}, h={h_delogo}")
    print(f"  Audio: KEPT ORIGINAL (no changes)")
    print(f"  Quality: ENHANCED (sharpen + clarity boost)")

    # QUALITY ENHANCEMENT CHAIN:
    # 1. scale=1080:1920:flags=lanczos - Highest quality upscaling (better than spline)
    # 2. unsharp=5:5:1.0:5:5:0.0 - Sharpening (makes edges clearer)
    # 3. cas=0.7 - Contrast Adaptive Sharpening (enhances details)
    # 4. delogo - Remove watermark
    
    vf_filter = f"[0:v]scale=1080:1920:flags=lanczos,unsharp=5:5:1.0:5:5:0.0,cas=0.7,delogo=x={x_delogo}:y={y_delogo}:w={w_delogo}:h={h_delogo}[v]"

    cmd_ffmpeg = [
        "ffmpeg", "-y", "-i", video_path,
        "-filter_complex", vf_filter,
        "-map", "[v]",
        "-map", "0:a?",
        "-c:v", "libx264", "-preset", "slow", "-crf", "16",  # CRF 16 = Very High Quality
        "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        out_path
    ]

    print("  Processing... (quality enhancement in progress)")
    result = subprocess.run(cmd_ffmpeg, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ Saved: {out_path} (ENHANCED QUALITY)")
        return out_path
    else:
        print(f"❌ Failed: {result.stderr[:200]}")
        return None


def main():
    """Process all videos in input directory or a specific video."""
    specific_video = sys.argv[1] if len(sys.argv) > 1 else None

    if specific_video:
        result = process_single_video(specific_video)
        if result:
            print("\n" + "=" * 60)
            print("PROCESSING COMPLETE - QUALITY ENHANCED")
            print("=" * 60)
        else:
            sys.exit(1)
    else:
        videos = [f for f in os.listdir(input_dir) if f.endswith('.mp4')]
        print(f"Found {len(videos)} videos to process.")

        for filename in videos:
            vid_path = os.path.join(input_dir, filename)
            process_single_video(vid_path)

        print("\n" + "=" * 60)
        print("PROCESSING COMPLETE")
        print("=" * 60)


if __name__ == "__main__":
    main()
