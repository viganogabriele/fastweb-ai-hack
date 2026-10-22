eventhub_global_feed.json: global ticketing/listings aggregator. start_local/end_local are local wall-clock time of the venue
unless the value ends with 'Z' (UTC; partner-synced records). expected_attendance is free-form (int, '12,000', '~120k', '1.5M').
Multi-day attendance is cumulative over the whole event.
asia_ticketing_feed_export.csv: crawl of an Asian ticketing/listing portal; dates in the format used by each country site
(KR yyyy.mm.dd, JP yyyy/m/d, CN/HK/TW yyyy-mm-dd, SG dd/mm/yyyy); visitor counts in local notation (만 = 10,000, 万/萬 = 10,000).
