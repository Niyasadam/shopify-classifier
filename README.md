# Shopify Product Taxonomy Classifier

A Python web application that automatically detects Shopify Product Taxonomy categories, category attributes, and attribute values for product catalogues of 10,000+ products.

---

## Features

- **Import CSV/XLSX** — Upload product files via web UI or API
- **Auto-classification** — Matches products to 69 Shopify taxonomy nodes across 15 categories
- **Attribute detection** — Extracts Color, Material, Shape, Style, and more
- **Confidence scoring** — 0.0–1.0 score with automatic flagging for review
- **Alternative suggestions** — Top 3 runner-up categories when confidence is low
- **Manual review** — Flagged products with approve/reject/reclassify actions
- **Batch operations** — Bulk approve, reject, or reclassify multiple products
- **Error handling** — Missing images, incomplete data, classification errors don't stop processing
- **Resume capability** — Import checkpoint file enables resuming interrupted imports

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.11+ / Flask 3.1.3 |
| WSGI Server | Gunicorn 23.0.0 |
| Database | SQLite 3 |
| Excel Parsing | openpyxl |
| Hosting | Render / any WSGI host |

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

# Open http://localhost:8080
# Go to /import and upload a CSV or XLSX file
```

---

## Project Structure

```
shopify-classifier/
├── app.py              # Flask app (routes, classifier, API, UI)
├── import_xlsx.py      # Standalone import/classify script
├── requirements.txt    # flask, gunicorn
├── Procfile            # Render deployment config
├── db.sqlite3          # SQLite database (auto-created)
└── README.md
```

---

## Data Model

### Product

| Field | Type | Description |
|-------|------|-------------|
| `product_number` | VARCHAR(100) | SKU (e.g. `EEI-1010-WHI`) |
| `product_name` | TEXT | Full product name |
| `product_description` | TEXT | Product description |
| `brand` | VARCHAR(255) | Brand name (extracted from "by Brand" pattern) |
| `product_type` | VARCHAR(255) | Product type hint |
| `image_url` | VARCHAR(500) | Primary image URL |
| `materials` | TEXT | Material description |
| `source_category` | VARCHAR(255) | Original category |
| `source_subcategory` | VARCHAR(255) | Original subcategory |

### TaxonomyNode (69 nodes)

| Field | Type | Description |
|-------|------|-------------|
| `shopify_id` | VARCHAR(64) | e.g. `tax_0001` |
| `name` | VARCHAR(255) | Node name (e.g. "Sofas") |
| `parent_id` | BIGINT | Parent node (null for root) |
| `level` | SMALLINT | 0=top, 1=sub-category |
| `keywords` | TEXT | Matching keywords |
| `attributes` | TEXT | Expected category attributes (JSON) |

### Classification

| Field | Type | Description |
|-------|------|-------------|
| `product_id` | BIGINT | Linked product |
| `taxonomy_node_id` | BIGINT | Assigned category |
| `confidence` | REAL | Score 0.0–1.0 |
| `status` | VARCHAR(20) | auto_classified / needs_review / approved / rejected |
| `alternatives` | TEXT | Top 3 alternative categories (JSON) |
| `detected_attributes` | TEXT | Detected attributes (JSON) |
| `needs_review` | BOOL | Flagged for human review |
| `review_reason` | VARCHAR(255) | Why flagged |

---

## Classification Algorithm

### Scoring

1. **Category map** — Direct match from source_category + source_subcategory (confidence: 0.95)
2. **Keyword scoring** — Match product text against each node's keywords (0.6–0.94)
3. **Parent boost** — +0.05 if parent keywords also match

### Attribute Detection

| Attribute | Method |
|-----------|--------|
| Color | Match against 26 color words |
| Material | Match against 30+ material types |
| Shape | Match against 6 shape keywords |
| Style | Match against 25+ style keywords |

### Decision Rules

- **Confidence ≥ 0.4** → Auto-classified
- **Confidence < 0.4** → Needs review
- **Missing description + no image** → Needs review
- **Missing description only** → Needs review

---

## Web Interface

### Dashboard (`/`)
- Stats cards: Total Products, Classified, Needs Review, Avg Confidence
- Status breakdown chart
- Top categories chart

### Products (`/products`)
- Search by name, SKU, brand
- Filter by status
- Paginated (50 per page)
- Thumbnail images, color-coded confidence

### Product Detail (`/products/<id>`)
- Full product info with image gallery
- Classification with confidence bar
- Detected attributes + expected category attributes
- Alternative categories
- Approve / Reject / Reclassify actions

### Import (`/import`)
- Upload CSV or XLSX files
- Auto-classifies all products on import
- Clears previous data on new import

### Batches (`/batches`)
- View import history

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stats` | GET | Product counts, status breakdown, avg confidence |
| `/api/products` | GET | List products (paginated) |
| `/api/products/<id>` | GET | Product detail with classification |
| `/api/classifications` | GET | List classifications (filterable) |
| `/api/classifications/<id>` | PUT | Update a classification |
| `/api/classifications/batch` | POST | Batch approve/reject/reclassify |
| `/api/taxonomy` | GET | List all taxonomy nodes |
| `/api/taxonomy/<id>` | GET | Taxonomy node detail |
| `/api/import` | POST | Import CSV file via API |

### Batch API Example

```json
POST /api/classifications/batch
{
  "ids": [1, 2, 3, 4, 5],
  "action": "approve"
}
```

---

## Supported File Formats

### CSV Columns

```
product_number, product_name, product_description, source_category,
source_subcategory, materials, brand, product_type, image_url,
product_weight, country_of_origin, collection_name, model_number,
bullets, product_dimensions, product_url
```

### XLSX Support

- Reads headers from first row
- Auto-maps common column names
- Extracts brand from "Product Name by Brand" pattern
- Supports `.xlsx` and `.xls` formats

---

## Deployment

1. Push to GitHub
2. Deploy to any Python WSGI host (Render, Heroku, Railway, etc.)
3. Build: `pip install -r requirements.txt`
4. Start: `gunicorn app:app --bind 0.0.0.0:$PORT`
5. Upload your product file via `/import`

---

## Key Design Decisions

1. **Single Flask app** — No framework overhead, self-contained
2. **SQLite** — Zero-config, sufficient for 10K+ products
3. **Keyword-based scoring** — Deterministic, explainable, no ML dependency
4. **Confidence thresholds** — Automatic flagging for human review
5. **Import resets DB** — Clean slate on each upload, easy to identify products
6. **Web UI + REST API** — Both interface and programmatic access
