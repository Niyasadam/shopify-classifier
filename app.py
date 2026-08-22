import os
import sqlite3
import json
import glob
from flask import Flask, request, jsonify, redirect

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "db.sqlite3")

SCHEMA = """
CREATE TABLE IF NOT EXISTS core_product (id INTEGER PRIMARY KEY,product_number VARCHAR(100),product_name TEXT,product_description TEXT,image_url VARCHAR(500),all_image_urls TEXT,source_category VARCHAR(255),source_subcategory VARCHAR(255),collection_name VARCHAR(255),materials TEXT,product_dimensions TEXT,product_weight REAL,country_of_origin VARCHAR(100),product_url VARCHAR(500),model_number VARCHAR(100),bullets TEXT);
CREATE TABLE IF NOT EXISTS core_taxonomynode (id INTEGER PRIMARY KEY,shopify_id VARCHAR(64) UNIQUE,name VARCHAR(255),level SMALLINT,keywords TEXT,product_type_hint VARCHAR(255),parent_id BIGINT);
CREATE TABLE IF NOT EXISTS core_classification (id INTEGER PRIMARY KEY,confidence REAL,status VARCHAR(20),alternatives TEXT,detected_attributes TEXT,needs_review BOOL,review_reason VARCHAR(255),classified_at DATETIME,reviewed_at DATETIME,reviewer_notes TEXT,product_id BIGINT,taxonomy_node_id BIGINT);
"""

def init_db():
    need = False
    if not os.path.exists(DB): need = True
    else:
        try:
            c = sqlite3.connect(DB)
            if c.execute("SELECT COUNT(*) FROM core_product").fetchone()[0] == 0: need = True
            c.close()
        except: need = True
    if not need: return
    print("Seeding database...")
    c = sqlite3.connect(DB)
    c.executescript(SCHEMA)
    chunks = sorted(glob.glob(os.path.join(BASE_DIR, "seed_chunk_*.json")))
    if not chunks: c.close(); return
    prods, nodes, cls = [], None, []
    for p in chunks:
        d = json.load(open(p))
        prods.extend(d["products"]); cls.extend(d["classifications"])
        if nodes is None: nodes = d["taxonomy_nodes"]
    cur = c.cursor()
    for n in nodes:
        cur.execute("INSERT OR IGNORE INTO core_taxonomynode VALUES (?,?,?,?,?,?,?)",(n["id"],n["shopify_id"],n["name"],n["level"],n.get("keywords",""),n.get("product_type_hint",""),n.get("parent_id")))
    for p in prods:
        cur.execute("INSERT OR IGNORE INTO core_product VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(p["id"],p.get("product_number"),p.get("product_name"),p.get("product_description"),p.get("image_url"),p.get("all_image_urls"),p.get("source_category"),p.get("source_subcategory"),p.get("collection_name"),p.get("materials"),p.get("product_dimensions"),p.get("product_weight"),p.get("country_of_origin"),p.get("product_url"),p.get("model_number"),p.get("bullets")))
    for cl in cls:
        cur.execute("INSERT OR IGNORE INTO core_classification VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",(cl["id"],cl["confidence"],cl["status"],cl.get("alternatives"),cl.get("detected_attributes"),cl["needs_review"],cl.get("review_reason"),cl.get("classified_at"),cl.get("reviewed_at"),cl.get("reviewer_notes"),cl["product_id"],cl.get("taxonomy_node_id")))
    c.commit(); c.close()
    print(f"Seeded {len(prods)} products, {len(nodes)} nodes, {len(cls)} classifications")

init_db()

def gdb():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c

def pg(title, body):
    css = open(os.path.join(BASE_DIR,"static")).read() if False else ""
    return body

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
