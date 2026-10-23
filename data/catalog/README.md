# Valentino product data

Data package for a future product view. It contains no UI or API implementation.

- `products.sqlite`: ready-to-query SQLite database.
- `products.json`: 46 synthetic styles, their 114 colour SKUs, and visual references.
- `sku_references.csv`: one row per synthetic SKU, with its local image and official source URL.
- `images/`: 46 downloaded reference photographs; displaying them needs no external network.
- `demo_signals.json`: four existing dev-fixture cases, seven source documents, eight observations,
  and explicit case-to-product links. Unknown product scope stays unlinked.
- `../../generated/sources/external/catalog/valentino.json`: public snapshot of 332 official
  Valentino product records, including official IDs, names, image URLs, prices and currency.

The commercial catalog and the simulation describe different things. Official Valentino products
are **visual references matched by category**; they are not the items in the synthetic ERP. A
reference photograph can differ in colour, material, fit or product type from a simulated item.
Model names such as `AUREA`, `NOVA` and `VEL` are synthetic labels. Original style codes,
SKUs, sizes, launch dates, prices and numerical series remain the simulation's identifiers and
values. `price_eur` in `products.json` and `synthetic_price_eur` in SQLite are synthetic prices;
the official reference price has its own currency and record. Photographs remain attributable
to Valentino, linked by `source_url`; this import does not grant image rights.

Cases, complaints, stock problems and demand signals in this package are **synthetic fixtures**,
not reports about Valentino products or customers. Every demo case has `mode = 'fixture'`.
The commercial snapshot is display metadata retrieved at its recorded `retrieved_at`, not a
historical demand signal. Do not feed it into extraction, linking, forecasts or historical
evaluation. Case attachments, source hashes, quotes and offsets come from the rebuilt fixtures.

## Use

Open `products.sqlite` in SQLite or any library that reads SQLite. The `product_cards` view is a
convenient starting point:

```sql
SELECT style_code, name, category, reference_name, local_image,
       color_count, demo_case_count
FROM product_cards
ORDER BY demo_case_count DESC, name;
```

The `local_image` path is relative to this directory. There are no bundled web routes. For the
detail of a demo product, join by the stable style code:

```sql
SELECT c.case_id, c.store_id, c.priority, c.status, c.priority_reason
FROM demo_case_products p JOIN demo_cases c USING (case_id)
WHERE p.style_code = 'I10919B00011';
```

`demo_cases.payload_json`, `demo_documents.payload_json` and `demo_observations.payload_json`
retain the existing contract records, including provenance and evidence. Preserve Unicode code
point offsets when highlighting quotes. Opaque artifact IDs are unchanged; model words inside
those identifiers are not display labels.

For future published runs, link `scope_level = style` by exact `style_code`, `sku` by exact `sku`,
and `sku_size` by the exact SKU followed by `-<size>`. Deduplicate case versions first. Category,
store and unknown scopes must remain separate; never assign them to every product or guess a
link. Read only one published run at a time and obey its `as_of` and store selection.

## Rebuild

From the repository root:

```bash
python scripts/import_valentino_catalog.py
python scripts/build_product_database.py
```

These commands rebuild the derived exports offline. To refresh the official public snapshot and
download missing images, use `python scripts/import_valentino_catalog.py --fetch`. Existing
SKU-to-reference associations stay fixed; a removed reference causes an explicit error rather
than a silent reassignment. `--download-images` uses the committed snapshot without refreshing
the listing. The importer stops on missing images or malformed source data.

The rebrand was an explicit dataset-maintenance request. Source email encodings, MIME structure,
Office containers and PDFs were processed without regenerating the synthetic world. Fixture
builders were rerun to update hashes, document segments and evidence offsets. Documentation
uses Valentino as a demo alias; altered track/transcript labels are not historical attribution
to Valentino. Runtime product code still reads only `generated/sources/`.
