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

CSS = "*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;background:#f5f5f5;color:#333}.nb{background:#1a1a2e;color:white;padding:1rem 2rem;display:flex;align-items:center;gap:2rem}.nb a{color:#a0a0c0;text-decoration:none;font-size:.9rem}.nb a:hover,.nb a.on{color:white}.nb b{font-size:1.1rem;margin-right:2rem}.wr{max-width:1400px;margin:0 auto;padding:1.5rem}.cds{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;margin-bottom:1.5rem}.cd{background:white;border-radius:8px;padding:1.2rem;box-shadow:0 1px 3px rgba(0,0,0,.08)}.cd h3{font-size:.8rem;color:#888;text-transform:uppercase;letter-spacing:.5px;margin-bottom:.3rem}.cd .v{font-size:1.8rem;font-weight:700}table{width:100%;border-collapse:collapse;background:white;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.08)}th,td{padding:.7rem 1rem;text-align:left;border-bottom:1px solid #eee;font-size:.85rem}th{background:#f8f9fa;font-weight:600;color:#555}tr:hover{background:#f8f9fa}.btn{display:inline-block;padding:6px 14px;border-radius:6px;border:none;cursor:pointer;font-size:.8rem;font-weight:500;text-decoration:none}.bp{background:#007bff;color:white}.bsu{background:#28a745;color:white}.bda{background:#dc3545;color:white}.bse{background:#6c757d;color:white}.sb{display:flex;gap:.5rem;margin-bottom:1rem;flex-wrap:wrap}.sb input,.sb select{padding:6px 12px;border:1px solid #ddd;border-radius:6px;font-size:.85rem}.sb input{flex:1;min-width:200px}.cw{font-weight:600;color:#28a745}.cm{font-weight:600;color:#ffc107}.cl{font-weight:600;color:#dc3545}.pi{width:50px;height:50px;object-fit:cover;border-radius:4px}.dg{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem}.ds{background:white;border-radius:8px;padding:1.2rem;box-shadow:0 1px 3px rgba(0,0,0,.08)}.ds h3{margin-bottom:.8rem;font-size:.95rem;color:#333}.ar{display:flex;justify-content:space-between;padding:.3rem 0;border-bottom:1px solid #f0f0f0;font-size:.85rem}.ai{padding:.5rem 0;border-bottom:1px solid #f5f5f5;font-size:.85rem}.pbar{height:6px;background:#eee;border-radius:3px;margin-top:.5rem;overflow:hidden}.pfill{height:100%;border-radius:3px;transition:width .3s}.cbar{display:flex;align-items:center;gap:.5rem;margin-bottom:.4rem;font-size:.8rem}.cbarf{height:16px;background:linear-gradient(90deg,#667eea,#764ba2);border-radius:3px;min-width:2px}.bsg{background:#28a745;color:white;padding:2px 8px;border-radius:4px;font-size:.75rem}.bwy{background:#ffc107;color:#333;padding:2px 8px;border-radius:4px;font-size:.75rem}.bdr{background:#dc3545;color:white;padding:2px 8px;border-radius:4px;font-size:.75rem}.binf{background:#17a2b8;color:white;padding:2px 8px;border-radius:4px;font-size:.75rem}@media(max-width:768px){.dg{grid-template-columns:1fr}.nb{flex-wrap:wrap;padding:.8rem 1rem}.cds{grid-template-columns:repeat(2,1fr)}}"

def pg(title, body):
    n = "<nav class='nb'><b>Shopify Taxonomy Classifier</b>"
    n += "<a href='/' class='on'>Dashboard</a>" if "Dashboard" in title else "<a href='/'>Dashboard</a>"
    n += "<a href='/products' class='on'>Products</a>" if "Products" in title and "Detail" not in title else "<a href='/products'>Products</a>" if "Detail" not in title else "<a href='/products'>Products</a>"
    n += "<a href='/api/stats' target='_blank'>API</a></nav>"
    return f"<!DOCTYPE html><html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1.0'><title>{title}</title><style>{CSS}</style></head><body>{n}<div class='wr'>{body}</div></body></html>"

def badge(status):
    m = {"approved":"bsg","needs_review":"bwy","rejected":"bdr"}
    return f"<span class='{m.get(status,"binf")}'>{status}</span>"

def confcls(c):
    return "cw" if c>=0.7 else ("cm" if c>=0.4 else "cl")

@app.route("/")
def dashboard():
    db = gdb()
    total = db.execute("SELECT COUNT(*) FROM core_product").fetchone()[0]
    classified = db.execute("SELECT COUNT(*) FROM core_classification").fetchone()[0]
    nr = db.execute("SELECT COUNT(*) FROM core_classification WHERE needs_review=1").fetchone()[0]
    ap = db.execute("SELECT COUNT(*) FROM core_classification WHERE status='approved'").fetchone()[0]
    ac = db.execute("SELECT AVG(confidence) FROM core_classification").fetchone()[0] or 0
    sc = dict(db.execute("SELECT status, COUNT(*) FROM core_classification GROUP BY status").fetchall())
    tc = db.execute("SELECT t.name, COUNT(*) as c FROM core_classification cl JOIN core_taxonomynode t ON cl.taxonomy_node_id=t.id GROUP BY t.name ORDER BY c DESC LIMIT 10").fetchall()
    db.close()
    s = "<h2 style='margin-bottom:1rem'>Dashboard</h2><div class='cds'>"
    s += f"<div class='cd'><h3>Total Products</h3><div class='v'>{total}</div></div>"
    s += f"<div class='cd'><h3>Classified</h3><div class='v'>{classified}</div></div>"
    s += f"<div class='cd'><h3>Needs Review</h3><div class='v' style='color:#ffc107'>{nr}</div></div>"
    s += f"<div class='cd'><h3>Approved</h3><div class='v' style='color:#28a745'>{ap}</div></div>"
    s += f"<div class='cd'><h3>Avg Confidence</h3><div class='v'>{ac:.1%}</div></div></div>"
    s += "<div class='dg'><div class='ds'><h3>Status Breakdown</h3>"
    for st, c in sc.items():
        w = max(c*150//max(total,1),2)
        s += f"<div class='cbar'><span style='width:130px'>{st}</span><div class='cbarf' style='width:{w}px'></div><span>{c}</span></div>"
    s += "</div><div class='ds'><h3>Top Categories</h3>"
    mx = tc[0][1] if tc else 1
    for nm, c in tc:
        w = max(c*150//mx,2)
        s += f"<div class='cbar'><span style='width:180px'>{nm}</span><div class='cbarf' style='width:{w}px'></div><span>{c}</span></div>"
    s += "</div></div><div style='margin-top:1.5rem'><a href='/products?status=needs_review' class='btn bwy' style='text-decoration:none'>Review Flagged</a> <a href='/products' class='btn bse' style='text-decoration:none;margin-left:.5rem'>View All</a></div>"
    return pg("Dashboard - Shopify Taxonomy Classifier", s)

@app.route("/products")
def product_list():
    db = gdb()
    st = request.args.get("status","")
    q = request.args.get("q","")
    query = "SELECT cl.*, p.product_number, p.product_name, p.image_url, p.source_category, t.name as tax_name FROM core_classification cl JOIN core_product p ON cl.product_id=p.id LEFT JOIN core_taxonomynode t ON cl.taxonomy_node_id=t.id WHERE 1=1"
    params = []
    if st: query += " AND cl.status=?"; params.append(st)
    if q: query += " AND (p.product_name LIKE ? OR p.product_number LIKE ? OR p.source_category LIKE ?)"; params.extend([f"%{q}%"]*3)
    query += " ORDER BY cl.confidence DESC LIMIT 200"
    rows = db.execute(query, params).fetchall()
    db.close()
    opts = ""
    for s2,l in [("pending","Pending"),("auto_classified","Auto Classified"),("needs_review","Needs Review"),("approved","Approved"),("rejected","Rejected")]:
        sel = "selected" if s2==st else ""
        opts += f"<option value='{s2}' {sel}>{l}</option>"
    s = "<h2 style='margin-bottom:1rem'>Product Classifications</h2>"
    s += f"<form class='sb' method='get'><input type='text' name='q' placeholder='Search...' value='{q}'><select name='status'><option value=''>All Status</option>{opts}</select><button type='submit' class='btn bp'>Filter</button></form>"
    s += "<table><thead><tr><th>Image</th><th>Product #</th><th>Name</th><th>Category</th><th>Confidence</th><th>Status</th><th></th></tr></thead><tbody>"
    for r in rows:
        img_url = r["image_url"] or ""
        img = f"<img src='{img_url}' class='pi' loading='lazy' onerror=\"this.style.display='none'\">" if img_url else ""
        nm = (r["product_name"] or "-")[:60]
        s += f"<tr><td>{img}</td><td><code>{r['product_number']}</code></td><td>{nm}</td><td>{r['tax_name'] or '-'}</td><td><span class='{confcls(r['confidence'])}'>{r['confidence']*100:.1f}%</span></td><td>{badge(r['status'])}</td><td><a href='/products/{r['id']}' class='btn bp'>View</a></td></tr>"
    s += "</tbody></table>"
    return pg("Products - Classifier", s)

@app.route("/products/<int:cid>")
def product_detail(cid):
    db = gdb()
    r = db.execute("SELECT cl.*, p.product_number, p.product_name, p.product_description, p.image_url, p.source_category, p.source_subcategory, p.collection_name, p.materials, p.product_dimensions, p.product_weight, p.country_of_origin, p.model_number, t.name as tax_name FROM core_classification cl JOIN core_product p ON cl.product_id=p.id LEFT JOIN core_taxonomynode t ON cl.taxonomy_node_id=t.id WHERE cl.id=?", [cid]).fetchone()
    if not r: db.close(); return "Not found", 404
    alts = json.loads(r["alternatives"]) if r["alternatives"] else []
    attrs = json.loads(r["detected_attributes"]) if r["detected_attributes"] else {}
    db.close()
    c = r["confidence"]; cc = confcls(c); cp = f"{c*100:.1f}%"
    bg = "#28a745" if c>=0.7 else ("#ffc107" if c>=0.4 else "#dc3545")
    img_url = r["image_url"] or ""
    img = f"<img src='{img_url}' style='max-width:200px;max-height:200px;border-radius:8px' onerror=\"this.style.display='none'\">" if img_url else ""
    desc = (r["product_description"] or "")[:300]
    mat = f"<p style='font-size:.8rem;color:#666;margin-top:.3rem'>Materials: {r['materials']}</p>" if r["materials"] else ""
    dim = f"<p style='font-size:.8rem;color:#666'>Dimensions: {(r['product_dimensions'] or '')[:80]}</p>" if r["product_dimensions"] else ""
    ah = "".join(f"<div class='ar'><span>{k}</span><strong>{v}</strong></div>" for k,v in attrs.items()) or "<p style='color:#888;font-size:.85rem'>None detected.</p>"
    al = "".join(f"<div class='ai'><strong>{a['name']}</strong> <span style='color:#888;font-size:.8rem'>{a.get('path','')}</span> <span class='{confcls(a['confidence'])}'>{a['confidence']*100:.1f}%</span></div>" for a in alts)
    als = f"<div class='ds' style='margin-top:1rem'><h3>Alternatives</h3>{al}</div>" if al else ""
    wt = f"{r['product_weight']} lbs" if r["product_weight"] else "-"
    src = f"{r['source_category'] or '-'} > {r['source_subcategory'] or '-'}"
    s = "<div style='margin-bottom:1rem'><a href='/products' style='color:#007bff;text-decoration:none;font-size:.85rem'>&larr; Back</a></div>"
    s += "<div style='display:flex;gap:1.5rem;align-items:flex-start;flex-wrap:wrap'>"
    s += f"<div style='flex:2;min-width:300px'><div class='ds'><div style='display:flex;gap:1rem;align-items:flex-start'>{img}<div><h3 style='margin-bottom:.3rem'>{r['product_name'] or ''}</h3><p style='color:#888;font-size:.85rem'>{r['product_number']} | {r['model_number'] or ''}</p><p style='font-size:.85rem;margin-top:.5rem'>{desc}</p>{mat}{dim}</div></div></div></div>"
    s += f"<div style='flex:1;min-width:280px'>"
    s += f"<div class='ds'><h3>Classification</h3><div class='ar'><span>Category</span><strong>{r['tax_name'] or 'Unclassified'}</strong></div><div class='ar'><span>Confidence</span><span class='{cc}'>{cp}</span></div><div class='ar'><span>Status</span>{badge(r['status'])}</div><div class='pbar'><div class='pfill' style='width:{c*100:.0f}%;background:{bg}'></div></div></div>"
    s += f"<div class='ds' style='margin-top:1rem'><h3>Detected Attributes</h3>{ah}</div>"
    s += als
    s += f"<div class='ds' style='margin-top:1rem'><h3>Actions</h3>"
    s += f"<form method='post' action='/products/{cid}/approve' style='display:inline'><button class='btn bsu'>Approve</button></form> "
    s += f"<form method='post' action='/products/{cid}/reject' style='display:inline'><button class='btn bda'>Reject</button></form></div>"
    s += f"<div class='ds' style='margin-top:1rem'><h3>Product Info</h3>"
    s += f"<div class='ar'><span>Source</span><span>{src}</span></div>"
    s += f"<div class='ar'><span>Collection</span><span>{r['collection_name'] or '-'}</span></div>"
    s += f"<div class='ar'><span>Country</span><span>{r['country_of_origin'] or '-'}</span></div>"
    s += f"<div class='ar'><span>Weight</span><span>{wt}</span></div></div></div></div>"
    return pg(f"{r['product_number']} - Detail", s)

@app.route("/products/<int:cid>/approve", methods=["POST"])
def approve(cid):
    db = gdb(); db.execute("UPDATE core_classification SET status='approved', needs_review=0 WHERE id=?", [cid]); db.commit(); db.close()
    return redirect(f"/products/{cid}")

@app.route("/products/<int:cid>/reject", methods=["POST"])
def reject(cid):
    db = gdb(); db.execute("UPDATE core_classification SET status='rejected' WHERE id=?", [cid]); db.commit(); db.close()
    return redirect(f"/products/{cid}")

@app.route("/api/stats")
def api_stats():
    db = gdb()
    t = db.execute("SELECT COUNT(*) FROM core_product").fetchone()[0]
    cl = db.execute("SELECT COUNT(*) FROM core_classification").fetchone()[0]
    sc = dict(db.execute("SELECT status, COUNT(*) FROM core_classification GROUP BY status").fetchall())
    ac = db.execute("SELECT AVG(confidence) FROM core_classification").fetchone()[0] or 0
    db.close()
    return jsonify({"total_products":t,"classified":cl,"status_counts":sc,"avg_confidence":round(ac,3)})

@app.route("/api/classifications")
def api_classifications():
    db = gdb()
    rows = db.execute("SELECT cl.id, p.product_number, p.product_name, t.name as taxonomy, cl.confidence, cl.status, cl.needs_review FROM core_classification cl JOIN core_product p ON cl.product_id=p.id LEFT JOIN core_taxonomynode t ON cl.taxonomy_node_id=t.id ORDER BY cl.confidence DESC LIMIT 50").fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))