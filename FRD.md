# Functional Requirements Document (FRD)
## Shopify Product Taxonomy Classifier

---

## 1. Project Overview

| Field | Description |
|-------|-------------|
| **Project Name** | Shopify Product Taxonomy Classifier |
| **Version** | 1.0 |
| **Type** | Web Application / Prototype |
| **Backend** | Python 3.11+ / Flask 3.1.3 |
| **Database** | SQLite 3 |
| **Frontend** | HTML/CSS/JavaScript |

---

## 2. Problem Statement

Manual product categorization is slow, inconsistent, and doesn't scale for 10,000+ products. E-commerce teams need an automated system to classify products into Shopify's taxonomy with human review for uncertain cases.

---

## 3. Functional Requirements

### 3.1 Product Import

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-01 | Import products from CSV files | High | ✅ Done |
| FR-02 | Import products from XLSX files | High | ✅ Done |
| FR-03 | Auto-detect column mappings | High | ✅ Done |
| FR-04 | Extract brand from "Product Name by Brand" pattern | Medium | ✅ Done |
| FR-05 | Clear previous data on new import | Medium | ✅ Done |
| FR-06 | Show import progress and results | High | ✅ Done |

### 3.2 Classification Engine

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-07 | Classify products into 69 Shopify taxonomy nodes | High | ✅ Done |
| FR-08 | Use keyword-based scoring (no ML dependency) | High | ✅ Done |
| FR-09 | Support 15 root categories + 54 subcategories | High | ✅ Done |
| FR-10 | Direct category match (source_category) | High | ✅ Done |
| FR-11 | Parent boost scoring (+0.05) | Medium | ✅ Done |
| FR-12 | Return top 3 alternative categories | High | ✅ Done |

### 3.3 Attribute Detection

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-13 | Detect Color (26 color words) | High | ✅ Done |
| FR-14 | Detect Material (30+ material types) | High | ✅ Done |
| FR-15 | Detect Shape (6 shape keywords) | Medium | ✅ Done |
| FR-16 | Detect Style (25+ style keywords) | Medium | ✅ Done |
| FR-17 | Show detected attributes per product | High | ✅ Done |

### 3.4 Confidence Scoring

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-18 | Calculate confidence score (0.0-1.0) | High | ✅ Done |
| FR-19 | Auto-classify if confidence ≥ 0.4 | High | ✅ Done |
| FR-20 | Flag for review if confidence < 0.4 | High | ✅ Done |
| FR-21 | Color-coded confidence display | Medium | ✅ Done |

### 3.5 Manual Review

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-22 | Flag products needing manual review | High | ✅ Done |
| FR-23 | Show review reason | High | ✅ Done |
| FR-24 | Approve classification | High | ✅ Done |
| FR-25 | Reject classification | High | ✅ Done |
| FR-26 | Reclassify to different category | High | ✅ Done |
| FR-27 | Show alternative categories for selection | High | ✅ Done |

### 3.6 Batch Operations

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-28 | Bulk approve multiple products | High | ✅ Done |
| FR-29 | Bulk reject multiple products | High | ✅ Done |
| FR-30 | Bulk reclassify multiple products | High | ✅ Done |
| FR-31 | View import history | Medium | ✅ Done |

### 3.7 Error Handling

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-32 | Handle missing images without crashing | High | ✅ Done |
| FR-33 | Handle missing descriptions | High | ✅ Done |
| FR-34 | Handle invalid/missing data | High | ✅ Done |
| FR-35 | Continue batch on individual errors | High | ✅ Done |
| FR-36 | Log errors with traceback | Medium | ✅ Done |

### 3.8 Resume Capability

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-37 | Save import progress to checkpoint file | Medium | ✅ Done |
| FR-38 | Resume interrupted imports | Medium | ✅ Done |
| FR-39 | Skip already-processed products | Medium | ✅ Done |

### 3.9 Web Interface

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-40 | Dashboard with stats cards | High | ✅ Done |
| FR-41 | Status breakdown chart | Medium | ✅ Done |
| FR-42 | Top categories chart | Medium | ✅ Done |
| FR-43 | Products list with search/filter | High | ✅ Done |
| FR-44 | Product detail with classification | High | ✅ Done |
| FR-45 | Import page with file upload | High | ✅ Done |
| FR-46 | Batches page with import history | Medium | ✅ Done |
| FR-47 | Responsive design | Medium | ✅ Done |

### 3.10 REST API

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-48 | GET /api/stats - Dashboard statistics | High | ✅ Done |
| FR-49 | GET /api/products - List products | High | ✅ Done |
| FR-50 | GET /api/products/<id> - Product detail | High | ✅ Done |
| FR-51 | GET /api/classifications - List classifications | High | ✅ Done |
| FR-52 | PUT /api/classifications/<id> - Update classification | High | ✅ Done |
| FR-53 | POST /api/classifications/batch - Batch operations | High | ✅ Done |
| FR-54 | GET /api/taxonomy - List taxonomy nodes | Medium | ✅ Done |
| FR-55 | POST /api/import - Import via API | Medium | ✅ Done |

---

## 4. Data Model

### 4.1 Product Table

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| product_number | VARCHAR(100) | SKU |
| product_name | TEXT | Full product name |
| product_description | TEXT | Product description |
| image_url | VARCHAR(500) | Primary image URL |
| all_image_urls | TEXT | All image URLs (JSON) |
| source_category | VARCHAR(255) | Original category |
| source_subcategory | VARCHAR(255) | Original subcategory |
| materials | TEXT | Material description |
| brand | VARCHAR(255) | Brand name |
| product_type | VARCHAR(255) | Product type hint |

### 4.2 TaxonomyNode Table

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| shopify_id | VARCHAR(64) | Shopify taxonomy ID |
| name | VARCHAR(255) | Node name |
| level | SMALLINT | 0=root, 1=subcategory |
| parent_id | BIGINT | Parent node ID |
| keywords | TEXT | Matching keywords |
| attributes | TEXT | Expected attributes (JSON) |

### 4.3 Classification Table

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| product_id | BIGINT | Linked product |
| taxonomy_node_id | BIGINT | Assigned category |
| confidence | REAL | Score 0.0-1.0 |
| status | VARCHAR(20) | Classification status |
| alternatives | TEXT | Top 3 alternatives (JSON) |
| detected_attributes | TEXT | Detected attributes (JSON) |
| needs_review | BOOL | Flagged for review |
| review_reason | VARCHAR(255) | Why flagged |

---

## 5. Non-Functional Requirements

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| NFR-01 | Process 10,000+ products | High | ✅ Done |
| NFR-02 | No external API dependencies | High | ✅ Done |
| NFR-03 | Zero-config database (SQLite) | Medium | ✅ Done |
| NFR-04 | Single-file deployment | Medium | ✅ Done |
| NFR-05 | No-cache headers for fresh data | Medium | ✅ Done |

---

## 6. Deployment

| Component | Technology |
|-----------|------------|
| Hosting | Render / Heroku / Railway |
| Server | Gunicorn |
| Database | SQLite (file-based) |
| Version Control | GitHub |

---

## 7. Future Enhancements

| Enhancement | Priority |
|-------------|----------|
| Image classification (Google Vision API) | High |
| MariaDB/PostgreSQL support | Medium |
| User authentication | Medium |
| Background processing (Celery) | Medium |
| Batch export functionality | Low |

---

## 8. Assumptions

1. Product data is in CSV or XLSX format
2. Products have text descriptions for keyword matching
3. 10,000+ products can be processed in batches of 250
4. SQLite is sufficient for prototype scale
5. No external AI/API calls needed for classification

---

## 9. Risks

| Risk | Mitigation |
|------|------------|
| SQLite locking under heavy load | WAL mode enabled |
| Classification accuracy | Confidence threshold + manual review |
| Large file uploads | Batch processing (250 per batch) |
| Data loss on crash | Checkpoint/resume capability |

---

*Document Version: 1.0*
*Last Updated: September 2026*
