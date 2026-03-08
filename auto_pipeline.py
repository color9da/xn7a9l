"""
Main Automation Pipeline for GitHub Actions
1. Fetch ONE video from Dropbox
2. Process (upscale + remove watermark)
3. Upload to social media platforms
"""
import os
import sys
import subprocess
from dotenv import load_dotenv

load_dotenv()


def run_pipeline():
    """
    Complete automation pipeline:
    Dropbox → Process → Upload to Social Media
    
    Only processes ONE new video per run.
    If no new videos, exits gracefully.
    """
    print("\n" + "=" * 60)
    print("🚀 STARTING AUTOMATION PIPELINE")
    print("=" * 60 + "\n")
    
    # Step 1: Fetch ONE video from Dropbox
    print("📥 STEP 1: Fetching video from Dropbox...")
    from dropbox_fetch import fetch_one_video_from_dropbox
    
    downloaded = fetch_one_video_from_dropbox()
    
    if not downloaded:
        print("\n✅ No new videos to process. Pipeline complete.")
        print("   (This is normal if all videos have been processed)")
        return
    
    print(f"\n✅ Step 1 complete: Video downloaded\n")
    
    # Step 2: Process video (upscale + watermark removal)
    print("🎬 STEP 2: Processing video (upscaling + watermark removal)...")
    result = subprocess.run([sys.executable, "process_videos.py", downloaded], capture_output=False)
    
    if result.returncode != 0:
        print("\n❌ Video processing failed!")
        sys.exit(1)
    
    print("\n✅ Step 2 complete: Video processed\n")
    
    # Step 3: Upload to social media
    print("📤 STEP 3: Uploading to social media platforms...")
    print("   Platforms: Instagram, Facebook, Threads, YouTube")
    print("\n" + "=" * 60 + "\n")
    
    # Get the processed video path
    processed_video = downloaded.replace("Videos/", "Processed_Videos/")
    
    # Run the daily publisher with the processed video
    from daily_publisher import main as publish_video
    sys.argv = ["daily_publisher.py", processed_video]
    publish_video()
    
    print("\n" + "=" * 60)
    print("🎉 AUTOMATION PIPELINE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
