"""
Video Processor - Simple Workflow
1. Upscale video 3x to 1080x1920
2. Remove watermark (bottom-right corner)
3. KEEP ORIGINAL AUDIO - NO CHANGES
"""
import os
import subprocess
import glob
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Paths
input_dir = "Videos"
output_dir = "Processed_Videos"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Get specific video path from command line if provided
specific_video = sys.argv[1] if len(sys.argv) > 1 else None

if specific_video:
    # Process specific video only
    if not os.path.exists(specific_video):
        print(f"Error: Video not found: {specific_video}")
        sys.exit(1)
    videos = [specific_video]
    print(f"Processing: {os.path.basename(specific_video)}")
else:
    # Process all videos in input directory
    videos = glob.glob(os.path.join(input_dir, "*.mp4"))
    print(f"Found {len(videos)} videos to process.")

for vid in videos:
    filename = os.path.basename(vid)
    out_path = os.path.join(output_dir, filename)

    # Skip if already processed
    if os.path.exists(out_path):
        print(f"Skipping {filename} - already processed")
        continue

    # Get original resolution
    cmd_probe = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", vid
    ]
    try:
        res = subprocess.check_output(cmd_probe).decode("utf-8").strip()
        width, height = map(int, res.split("x"))
    except Exception as e:
        print(f"Failed to get resolution for {vid}: {e}")
        continue

    print(f"Original size: {width}x{height}")

    # Calculate watermark position AFTER upscaling to 1080x1920
    # Watermark is at bottom-right corner
    # After upscale: 1080x1920
    # Watermark size: ~180x80 (proportional)
    w_delogo = 180  # watermark width after upscale
    h_delogo = 80   # watermark height after upscale
    
    x_delogo = 1080 - w_delogo - 5   # right side, 5px padding
    y_delogo = 1920 - h_delogo - 5   # bottom, 5px padding

    print(f"Processing {filename}...")
    print(f"  Upscaling to: 1080x1920")
    print(f"  Removing watermark at: x={x_delogo}, y={y_delogo}, w={w_delogo}, h={h_delogo}")
    print(f"  Audio: KEPT ORIGINAL (no changes)")

    # STEP 1: Upscale to 1080x1920
    # STEP 2: Remove watermark (delogo)
    # STEP 3: Keep original audio unchanged
    vf_filter = f"[0:v]scale=1080:1920:flags=spline,delogo=x={x_delogo}:y={y_delogo}:w={w_delogo}:h={h_delogo},cas=0.6[v]"

    cmd_ffmpeg = [
        "ffmpeg", "-y", "-i", vid,
        "-filter_complex", vf_filter,
        "-map", "[v]",
        "-map", "0:a?",  # Include audio if exists (keep original)
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-c:a", "copy",  # COPY ORIGINAL AUDIO - NO CHANGES
        out_path
    ]

    print("  Processing... (this may take a few minutes)")
    result = subprocess.run(cmd_ffmpeg, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ Saved: {out_path}")
    else:
        print(f"❌ Failed: {result.stderr[:200]}")
        continue

print("\n" + "=" * 60)
print("PROCESSING COMPLETE")
print("=" * 60)
