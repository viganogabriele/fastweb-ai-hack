# eval

The only code allowed to read `generated/ground_truth/` (RFC §7.1). It reads the frozen export of a
product run and the answer key, and writes metrics. Product code (`backend/`) never imports from
here, and nothing here is used to build prompts, fixtures or aliases. Package created by EVL-01.
