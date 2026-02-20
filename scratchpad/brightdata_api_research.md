# BrightData API Research: Facebook & TikTok Data Collection

## Date: 2026-02-19

---

## 1. Do You Need a Dataset ID? (Yes)

**You cannot use just a page URL + API key.** You **must** provide a `dataset_id` in every trigger request. The `dataset_id` identifies which pre-built scraper to use. These IDs are fixed/pre-assigned by BrightData -- you do not create them yourself.

### Known Dataset IDs

**Facebook:**
| Scraper Type | Dataset ID |
|---|---|
| Facebook Posts (by page/profile URL) | `gd_lkaxegm826bjpoo9m5` |
| Facebook Reels | `gd_lyclm3ey2q6rww027t` |
| Facebook Comments | `gd_lkay758p1eanlolqw8` |

**TikTok:**
| Scraper Type | Dataset ID |
|---|---|
| TikTok Profiles | `gd_l1villgoiiidt09ci` |
| TikTok Posts (individual post URL) | `gd_lu702nij2f790tmv9h` |
| TikTok Comments | `gd_lkf2st302ap89utw5k` |

**Note:** The TikTok Posts dataset ID `gd_lu702nij2f790tmv9h` supports multiple input modes:
- By individual post URL
- By profile URL (get all posts from a user)
- By keyword search

---

## 2. How the Dataset API Works (End-to-End Workflow)

The BrightData Web Scraper API uses a 3-step asynchronous workflow:

### Step 1: Trigger Collection
```
POST https://api.brightdata.com/datasets/v3/trigger?dataset_id={DATASET_ID}&format=json
```

Headers:
```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

Body (JSON array of input objects):
```json
[{"url": "https://www.facebook.com/PageName/", "num_of_posts": 25}]
```

Response: Returns a `snapshot_id` immediately.
```json
{"snapshot_id": "s_abc123xyz"}
```

### Step 2: Monitor Progress (Polling)
```
GET https://api.brightdata.com/datasets/v3/progress/{snapshot_id}
Authorization: Bearer YOUR_API_KEY
```

Possible statuses: `starting` -> `running` -> `ready` (or `failed`)

Poll every ~10 seconds until status is `ready`.

### Step 3: Download Results
```
GET https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}
Authorization: Bearer YOUR_API_KEY
```

Returns the collected data in the format specified during trigger (JSON, CSV, etc.).

### Alternative: Webhook Delivery
Instead of polling, you can pass `&notification_url=YOUR_WEBHOOK` to the trigger URL and BrightData will POST the results to your webhook when ready.

---

## 3. Free Tier / Trial Access

- **Free trial available** -- "No credit card required" is advertised on their site.
- **Deposit matching**: BrightData matches your first deposit dollar-for-dollar up to $500.
- **Pay-as-you-go pricing**: $1.50 per 1,000 records (no commitment).
- **Sample datasets on GitHub**: BrightData publishes free sample data:
  - [Facebook dataset samples](https://github.com/luminati-io/Facebook-dataset-samples) (~1,000 posts)
  - [TikTok dataset samples](https://github.com/luminati-io/TikTok-dataset-samples) (~1,000 profiles)
- The exact number of free records in the trial is not publicly documented.

---

## 4. Minimum Steps to Collect Data

### Facebook Posts from a Public Page

```bash
# Step 1: Trigger collection
curl -X POST \
  "https://api.brightdata.com/datasets/v3/trigger?dataset_id=gd_lkaxegm826bjpoo9m5&format=json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '[{"url":"https://www.facebook.com/LeBron/","num_of_posts":25}]'

# Response: {"snapshot_id": "s_xxxxx"}

# Step 2: Poll for completion
curl -X GET \
  "https://api.brightdata.com/datasets/v3/progress/s_xxxxx" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Wait until status is "ready"

# Step 3: Download results
curl -X GET \
  "https://api.brightdata.com/datasets/v3/snapshot/s_xxxxx" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -o facebook_posts.json
```

### TikTok Posts from a Public Account

```bash
# Step 1: Trigger collection (using TikTok Posts dataset ID with profile URL)
curl -X POST \
  "https://api.brightdata.com/datasets/v3/trigger?dataset_id=gd_lu702nij2f790tmv9h&format=json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '[{"url":"https://www.tiktok.com/@username","num_of_posts":25}]'

# Response: {"snapshot_id": "s_yyyyy"}

# Step 2: Poll for completion
curl -X GET \
  "https://api.brightdata.com/datasets/v3/progress/s_yyyyy" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Step 3: Download results
curl -X GET \
  "https://api.brightdata.com/datasets/v3/snapshot/s_yyyyy" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -o tiktok_posts.json
```

### Input Parameters Summary

**Facebook Posts inputs:**
- `url` (required) -- Facebook page/profile/group URL
- `num_of_posts` (optional) -- number of posts to collect
- `start_date` (optional) -- format: MM-DD-YYYY
- `end_date` (optional) -- format: MM-DD-YYYY
- `posts_to_not_include` (optional) -- post IDs to exclude

**TikTok Posts inputs:**
- `url` (required) -- TikTok profile URL or post URL
- `num_of_posts` (optional) -- number of posts to collect
- `start_date` (optional) -- format: mm-dd-yyyy
- `end_date` (optional) -- format: mm-dd-yyyy
- `country` (optional) -- country code
- `posts_to_not_include` (optional) -- post IDs to exclude

---

## 5. Data Fields Returned

### Facebook Posts
- `url`, `post_id`, `user_url`, `user_name`, `content`, `post_date`
- `hashtags`, `num_comments`, `num_likes`, `num_shares`
- `attachments`, `page_name`, `page_followers`, `is_verified`

### TikTok Posts
- `url`, `post_id`, `description`, `create_time`
- `digg_count` (likes), `share_count`, `collect_count`, `comment_count`
- `play_count`, `video_duration`, `hashtags`, `original_sound`
- `profile_id`, `profile_username`, `profile_url`, `profile_followers`, `is_verified`

---

## 6. Key Takeaways for Implementation

1. **You MUST have a BrightData account and API key** -- get it from https://brightdata.com/cp/setting/users
2. **Dataset IDs are pre-assigned** -- no need to create or purchase datasets manually
3. **The API is asynchronous** -- trigger, poll, download (or use webhooks)
4. **Minimum cost**: $1.50 per 1,000 records on pay-as-you-go
5. **For 25 posts each** (Facebook + TikTok = 50 records total), cost would be ~$0.075
6. **Free trial exists** but exact free record count is unclear -- sign up to find out
