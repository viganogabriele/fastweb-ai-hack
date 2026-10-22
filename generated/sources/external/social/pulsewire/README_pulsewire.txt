PULSEWIRE Social Listening - Data Export
Project: MCL-GLOBAL-SOCIAL      Delivery: monthly JSONL (one document per line, UTF-8)
Doc version 1.3 (2026-06-02)

Coverage: Instagram (posts + comments), TikTok, Twitter, Threads, Reddit.
Query: brand + product keywords, brand hashtags, logo detection on images,
       geofences around monitored retail addresses.
Timestamps are UTC (ISO 8601, "Z").

FIELDS
  doc_id            Pulsewire unique document id
  doc_type          post | comment
  source            instagram | tiktok | twitter | threads | reddit
  post_id, url      native id / permalink
  published_at      publication time, UTC
  collected_at      crawl time, UTC
  author.handle     "@handle" (reddit: "u/name")
  author.name       display name
  author.followers  follower count at crawl time (null for comments / reddit)
  author.verified   bool
  lang              ISO 639-1 detected language (auto)
  title             reddit only
  text              full text
  hashtags          list, without '#'
  media_type        image | carousel | video | reel | text | link
  metrics.likes / metrics.comments / metrics.shares / metrics.views
                    snapshot at collected_at; null = not exposed by platform
  geo               place tag if present, else null
                    {name, city, country, coordinates:[lat, lon]}
  sentiment         positive | negative | neutral (Pulsewire NLP v4)
  sentiment_score   0-1 confidence
  keywords_matched  list of query terms found
  match_type        keyword | hashtag | logo_detection | geofence
  subreddit         reddit only
  parent_url        comments only

NOTES
  - Monthly files may contain documents re-collected in the following export; use doc_id + latest collected_at.
  - Metrics are snapshots and keep growing after publication.
  - Sentiment is automatic and not validated for sarcasm or slang.
  - Contact: support@pulsewire.example
