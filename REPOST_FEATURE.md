# ♻️ Smart Reposting Feature

## Overview

The pipeline now **runs forever** by automatically reposting already processed videos when no new videos are available in Dropbox.

---

## How It Works

### Normal Flow (New Videos Available)
```
Dropbox has new video
    ↓
Download → Process (upscale + watermark removal)
    ↓
Upload to all platforms
    ↓
Move to Published_Videos/
```

### Fallback Flow (No New Videos)
```
Dropbox empty
    ↓
Select random video from Processed_Videos/
    ↓
Generate NEW AI caption (unique each time)
    ↓
Upload to all platforms
    ↓
Keep in Processed_Videos/ (for future reposts)
```

---

## Smart Selection Algorithm

Videos are selected using **weighted randomness**:

| Times Posted | Selection Weight | Probability |
|--------------|------------------|-------------|
| 0 times      | 1000             | ~90%        |
| 1 time       | 100              | ~9%         |
| 2 times      | 10               | ~0.9%       |
| 3+ times     | 1-3              | ~0.1%       |

**Formula:** `weight = max(1, 1000 // (3 ** post_count))`

This ensures:
- ✅ Less-posted videos get priority
- ✅ Randomness prevents predictable patterns
- ✅ Heavy repetition is extremely unlikely

---

## Example Scenario

You have 5 processed videos:
- `video_a.mp4` - never posted (weight: 1000)
- `video_b.mp4` - posted 1 time (weight: 100)
- `video_c.mp4` - posted 2 times (weight: 10)
- `video_d.mp4` - posted 1 time (weight: 100)
- `video_e.mp4` - never posted (weight: 1000)

**Next post selection:**
- `video_a` or `video_e` are **10x more likely** than `video_b` or `video_d`
- `video_c` is **100x less likely** than the never-posted ones

---

## Caption Generation

Each repost gets a **completely unique caption**:

- **Title**: AI-generated (different every time)
- **Description**: AI-generated (different every time)
- **Hashtags**: AI-generated (varied selection)

**Example:**
- **First post**: "I Walked Away and Made the Sunset Jealous"
- **Repost #1**: "Catch Me If You Can, But Make It Fashion"
- **Repost #2**: "I Turn Back Time (and Heads)"

Same video, fresh engagement!

---

## File Tracking

### `published_videos.json`

Tracks every post with:
```json
{
  "video_name": "my-video.mp4",
  "metadata": {
    "title": "Unique title for this post",
    "description": "Unique description for this post",
    "success_flags": {
      "instagram_reel": true,
      "facebook_reel": true,
      ...
    }
  }
}
```

**Multiple entries = multiple posts** (this is how repost count is calculated)

---

## Folder Structure

```
Processed_Videos/
├── video1_processed.mp4    ← Available for reposts
├── video2_processed.mp4    ← Available for reposts
└── video3_processed.mp4    ← Available for reposts

Published_Videos/
├── video1_processed.mp4    ← Original new video (moved after first post)
└── video4_from_dropbox.mp4 ← Original new video (moved after first post)
```

**Key difference:**
- **New videos** → Moved to `Published_Videos/` after posting
- **Reposted videos** → Stay in `Processed_Videos/` forever

---

## Benefits

1. **Never runs out of content** - Always has something to post
2. **Fresh engagement** - New captions = new interactions
3. **Smart variety** - Avoids over-posting the same videos
4. **Fully automated** - No manual intervention needed
5. **Efficient** - No re-processing (already upscaled)

---

## Configuration

### Adjust Selection Weights

Edit `auto_pipeline.py`:

```python
# Current: Exponential decay (aggressive variety)
weight = max(1, 1000 // (3 ** count))

# More balanced: Linear decay
weight = max(1, 1000 - (count * 200))

# Less strict: Slower decay
weight = max(1, 1000 // (2 ** count))
```

### Set Maximum Reposts

Add a limit to prevent over-posting:

```python
MAX_REPOSTS = 5  # Never post more than 5 times

# In select_random_processed_video():
if count >= MAX_REPOSTS:
    weights.append(0)  # Exclude from selection
else:
    weights.append(max(1, 1000 // (3 ** count)))
```

---

## Testing

Run the pipeline manually to test:

```bash
python auto_pipeline.py
```

**Expected output when Dropbox is empty:**
```
⚠️  No new videos in Dropbox
🔄 FALLBACK MODE: Looking for processed videos to repost...

🎲 Selected (posted 1 time(s) before): video1_processed.mp4

✅ Fallback: Using processed video for repost
```

---

## Monitoring

Check posting frequency:

```bash
python -c "
import json
with open('published_videos.json') as f:
    data = json.load(f)
    
counts = {}
for entry in data:
    name = entry['video_name']
    counts[name] = counts.get(name, 0) + 1

for name, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
    print(f'{count}x: {name}')
"
```

---

## Summary

| Feature | Before | After |
|---------|--------|-------|
| No new videos | Pipeline stops | Reposts old videos |
| Selection | First available | Weighted random |
| Captions | Same | New AI generation |
| File handling | Always moves | Keeps reposts in place |
| Runs forever | ❌ No | ✅ Yes |

**The pipeline is now truly autonomous!** 🚀
