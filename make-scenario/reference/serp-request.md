# SERP image search (step 5)

Goal: turn `image_search_query` (from OpenAI) into a real product image URL that
Shopify can ingest. Two good providers — pick one.

## Option A — SerpApi (most common in Make)

- **URL:** `https://serpapi.com/search.json`
- **Method:** GET
- **Query string:**
  - `engine = google_images`
  - `q = {{4.image_search_query}}`
  - `api_key = YOUR_SERPAPI_KEY`
  - `num = 5`
- **Parse response:** Yes
- **Image URL to use:** `{{5.images_results[1].original}}`
  (Make arrays are 1-indexed, so `[1]` = the first result.)

## Option B — Serper.dev (cheaper)

- **URL:** `https://google.serper.dev/images`
- **Method:** POST
- **Headers:** `X-API-KEY: YOUR_SERPER_KEY`, `Content-Type: application/json`
- **Body (raw JSON):** `{ "q": "{{4.image_search_query}}", "num": 5 }`
- **Parse response:** Yes
- **Image URL to use:** `{{5.images[1].imageUrl}}`

## Reliability tips

- **Error handler on this module = Resume**, output `{ "image_url": "" }`. A SERP
  miss should never block product creation — the product is just created without
  an image (you can add one later in Shopify).
- Map a single field named `image_url` out of whichever provider you use, so the
  rest of the flow (and `shopify-body.example.json`) stays provider-agnostic.
- **Optional validation:** add an HTTP GET on the chosen URL and only pass it to
  Shopify if the response status is `200` and `Content-Type` starts with
  `image/`. If not, fall back to result `[2]`, `[3]`, … This filters out
  hotlink-protected / dead images before Shopify ever sees them.
- ⚠️ Web images may be copyrighted. Use for **draft** products you review, or
  swap to your own/licensed images for anything you publish.
