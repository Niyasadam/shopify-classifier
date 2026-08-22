# Shopify Product Taxonomy Classifier

A full-stack web application that automatically classifies **4,999 Modway furniture products** into **69 Shopify Product Taxonomy nodes** across **15 top-level categories** using keyword-based NLP scoring.

**Live App:** https://shopify-taxonomy-classifier.onrender.com

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    DATA PIPELINE                         │
│                                                         │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────┐  │
│  │  Excel   │───>│  Django  │───>│    SQLite DB      │  │
│  │ .xlsx    │    │  Import  │    │ (products + nodes │  │
│  │ (source) │    │  + Class │    │  + classifications│  │
│  └──────────┘    └──────────┘    └──────────────────┘  │
│                       │                    │             │
│                       v                    v             │
│              ┌──────────────┐     ┌──────────────────┐  │
│              │  Classifier  │     │  Seed Export      │  │
│              │  (NLP score) │     │  (20 JSON chunks) │  │
│              └──────────────┘     └──────────────────┘  │
│                                            │             │
│                                            v             │
│                                 ┌──────────────────┐    │
│                                 │   Flask App       │    │
│                                 │ (production UI)   │    │
│                                 └──────────────────┘    │
│                                            │             │
│                                            v             │
│                                    ┌──────────────┐     │
│                                    │   Render      │     │
│                                    │   (hosting)   │     │
│                                    └──────────────┘     │
└─────────────────────────────────────────────────────────┘
```

### Two Deployment Modes

| Mode | Stack | Use Case |
|------|-------|----------|
| **Development** | Django 6.1 + DRF + SQLite | Import data, run classifier, admin interface, full REST API |
| **Production** | Flask 3.1.3 + Gunicorn + SQLite | Lightweight read-only web UI, auto-seeds from JSON chunks |

Both modes share the same SQLite database schema. The Django mode is used for data ingestion and classification; the Flask mode is deployed to Render for public viewing.

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Backend (Dev)** | Django | 6.1 |
| **API Framework** | Django REST Framework | 3.15+ |
| **Backend (Prod)** | Flask | 3.1.3 |
| **WSGI Server** | Gunicorn | 23.0.0 |
| **Database** | SQLite | 3 |
| **Excel Parsing** | openpyxl | latest |
| **Hosting** | Render | Free tier |
| **Version Control** | GitHub | - |

---

## Data Model

### TaxonomyNode (69 nodes)
Shopify's product taxonomy hierarchy with self-referential parent relationships.

```
Home & Garden (level 0)
├── Furniture (level 1)
│   ├── Living Room (level 2)
│   │   ├── Sofas ────────────── keywords: "sofa, couch, settee..."
│   │   ├── Coffee Tables ───── keywords: "coffee table, cocktail..."
│   │   └── ...
│   ├── Bedroom (level 2)
│   └── ...
├── Decor (level 1)
└── ... (15 top-level categories total)
```

| Field | Type | Description |
|-------|------|-------------|
| `shopify_id` | CharField(64) | Synthetic ID (e.g. `tax_0001`) |
| `name` | CharField(255) | Node name |
| `parent` | FK(self) | Parent node (null for root) |
| `level` | SmallIntegerField | Depth (0=top, 1=sub, 2=leaf) |
| `keywords` | TextField | Comma-separated matching keywords |
| `product_type_hint` | CharField(255) | Shopify product type hint |

### Product (4,999 items)
Imported Modway furniture catalog with full metadata.

| Field | Type | Description |
|-------|------|-------------|
| `product_number` | CharField(64) | SKU (e.g. `EEI-1010-WHI`) |
| `product_name` | CharField(512) | Full product name |
| `product_description` | TextField | Full description |
| `image_url` | URLField(1024) | Primary image |
| `source_category` | CharField(255) | Original category |
| `materials` | CharField(255) | Material description |
| `product_weight` | FloatField | Weight in lbs |
| `country_of_origin` | CharField(64) | Country of origin |

### Classification (4,999 results)
One-to-one mapping of product to taxonomy node with confidence scoring.

| Field | Type | Description |
|-------|------|-------------|
| `product` | OneToOneField | Linked product |
| `taxonomy_node` | FK(TaxonomyNode) | Assigned category |
| `confidence` | FloatField | Score 0.0–1.0 |
| `status` | CharField(20) | pending / auto_classified / needs_review / approved / rejected |
| `alternatives` | JSONField | Top 3 runner-up categories |
| `detected_attributes` | JSONField | Material, Color, Assembly, etc. |
| `needs_review` | BooleanField | Flagged for human review |

---

## Classification Algorithm

The classifier uses a **weighted keyword scoring** system to match products to taxonomy nodes.

### Text Assembly
All product fields are concatenated into a single search string:
```
product_name + description + bullets + source_category + source_subcategory + collection + materials
```

### Scoring Components

| Component | Weight | Method |
|-----------|--------|--------|
| **Keyword match** | 0.6 | Jaccard similarity: `\|text ∩ keywords\| / \|keywords\|` |
| **Product type hint** | 0.3 | Exact substring match in product text |
| **Node name match** | 0.2 | Exact substring match in product text |
| **Parent keywords** | 0.15 | Keyword scoring against parent node |
| **Grandparent keywords** | 0.05 | Keyword scoring against grandparent node |

Score is capped at 1.0. Best match wins.

### Decision Rules

- **Score < 0.1** → No match (status: `needs_review`)
- **Score 0.1–0.3** → Low confidence (flagged for review)
- **Score > 0.3** → Auto-classified
- **Missing description + no image** → Always flagged for review

### Detected Attributes

The classifier also extracts structured attributes:

| Attribute | Detection |
|-----------|-----------|
| Material | Keyword lookup (Wood, Metal, Fabric, Leather, etc.) |
| Color | First match from 16 color words |
| Assembly Required | Phrase matching |
| Weight | From product field |
| Country of Origin | From product field |

---

## Web Interface

### Dashboard (`/`)
- Stats cards: Total Products, Classified, Needs Review, Approved, Avg Confidence
- Status breakdown bar chart
- Top 10 categories bar chart
- Quick links to review flagged products

### Product List (`/products`)
- Search by name, SKU, or category
- Filter by classification status
- Sort by confidence, status, or product number
- Thumbnail images, color-coded confidence scores
- 200 results per page

### Product Detail (`/products/<id>`)
- Full product info with image
- Classification card with confidence progress bar
- Detected attributes panel
- Alternative categories with confidence scores
- Approve / Reject actions
- Source metadata (original category, collection, country, weight)

---

## API Endpoints

### REST API (Django mode)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/products/` | GET | List products (paginated, 50/page) |
| `/api/products/{id}/` | GET | Product detail |
| `/api/products/stats/` | GET | Product statistics |
| `/api/classifications/` | GET | List classifications |
| `/api/classifications/{id}/` | GET | Classification detail |
| `/api/classifications/{id}/approve/` | POST | Approve a classification |
| `/api/classifications/{id}/reject/` | POST | Reject a classification |
| `/api/classifications/{id}/reassign/` | POST | Reassign to different node |
| `/api/classifications/batch_approve/` | POST | Bulk approve by IDs |
| `/api/classifications/stats/` | GET | Classification statistics |

### JSON API (Flask/Production mode)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stats` | GET | `{total_products, classified, status_counts, avg_confidence}` |
| `/api/classifications` | GET | Top 50 classifications (JSON array) |

---

## Project Structure

```
shopify_classifier/
├── app.py                          # Flask production app (189 lines, self-contained)
├── manage.py                       # Django management script
├── requirements.txt                # flask, gunicorn
├── Procfile                        # Render/Heroku process definition
├── seed_chunk_*.json               # 20 JSON data chunks (4,999 products)
│
├── shopify_classifier/             # Django project config
│   ├── settings.py                 # Django settings (SQLite, DRF)
│   ├── urls.py                     # Root URL configuration
│   └── wsgi.py                     # WSGI application
│
└── core/                           # Main Django app
    ├── models.py                   # TaxonomyNode, Product, Classification
    ├── classifier.py               # NLP classification algorithm
    ├── taxonomy_data.py            # Hardcoded Shopify taxonomy (69 nodes)
    ├── api.py                      # DRF serializers + viewsets
    ├── views.py                    # Django template views
    ├── urls.py                     # URL routing
    ├── management/commands/
    │   ├── import_products.py      # Excel import command
    │   └── classify_products.py    # Bulk classification command
    └── templates/core/
        ├── base.html               # Base layout
        ├── dashboard.html          # Dashboard page
        ├── product_list.html       # Product list with filters
        └── product_detail.html     # Product detail page
```

---

## Local Development

### Prerequisites
- Python 3.13+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/niyas-adam/shopify-taxonomy-classifier
cd shopify-taxonomy-classifier

# Install dependencies
pip install django djangorestframework openpyxl flask gunicorn

# Run Django migrations
python manage.py migrate

# Import products (requires Product List.xlsx in project root)
python manage.py import_products "Product List.xlsx"

# Load taxonomy and classify all products
python manage.py classify_products --load-taxonomy

# Run Django dev server
python manage.py runserver
```

### Production Mode (Flask)

```bash
# The Flask app auto-seeds from seed_chunk_*.json on first run
python app.py
# or
gunicorn app:app --bind 0.0.0.0:8080
```

---

## Deployment (Render)

The app is deployed on Render's free tier:

1. **GitHub repo** pushed with all source + seed data
2. **Render auto-deploys** on push to `main`
3. **Build:** `pip install -r requirements.txt`
4. **Start:** `gunicorn app:app --bind 0.0.0.0:$PORT`
5. **First boot:** Flask auto-seeds 4,999 products from 20 JSON chunks
6. **Live at:** https://shopify-taxonomy-classifier.onrender.com

> **Note:** Render free tier spins down after 15 min of inactivity. First request after idle takes ~30s to wake up.

---

## Seed Data

The 4,999 products are pre-classified and exported as 20 JSON chunks (`seed_chunk_0.json` – `seed_chunk_19.json`). Each chunk contains:

- **250 products** (last chunk: 249)
- **69 taxonomy nodes** (duplicated across all chunks)
- **250 classifications** with confidence scores and alternatives

Total data size: ~15 MB across 20 files.

### Classification Results Summary

| Status | Count | Percentage |
|--------|-------|------------|
| Auto-classified | ~4,706 | 94.1% |
| Needs review | ~293 | 5.9% |
| **Total** | **4,999** | **100%** |

---

## Key Design Decisions

1. **Dual-stack architecture** — Django for development/admin, Flask for production (lighter, no ORM overhead)
2. **SQLite** — Simple, zero-config database; sufficient for 5K products
3. **JSON seed chunks** — Enables one-command deployment without Django or Excel dependency
4. **Keyword-based scoring** — No ML model required; deterministic, explainable, fast
5. **Confidence thresholds** — Automatic flagging of low-confidence classifications for human review
6. **Self-contained Flask app** — Single `app.py` with inline CSS, auto-seeding, no external templates

---

## License

Internal project — not licensed for distribution.