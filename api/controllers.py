from router import route
from db import get_db
from http_utils import json_response
import json
from datetime import datetime

@route("GET", r"/laws")
def get_laws(body):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT l.*, COUNT(a.id) as article_count
        FROM laws l
        LEFT JOIN articles a ON l.id = a.law_id
        WHERE l.deleted_at IS NULL
        GROUP BY l.id
    """)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    return json_response([dict(zip(cols,r)) for r in rows])

@route("POST", r"/laws")
def create_law(body):
    data = json.loads(body)
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO laws(title, description, metadata)
        VALUES (%s,%s,%s) RETURNING id
    """, (data["title"], data.get("description"),
          json.dumps(data.get("metadata",{}))))
    law_id = cur.fetchone()[0]
    conn.commit()
    return json_response({"law_id": law_id},201)

@route("GET", r"/laws/(?P<id>[a-f0-9\-]+)")
def get_law(body,id):
    conn=get_db();cur=conn.cursor()
    cur.execute("SELECT * FROM laws WHERE id=%s",(id,))
    row=cur.fetchone()
    return json_response(row if row else {"error":"not found"},200)

@route("PATCH", r"/laws/(?P<id>[a-f0-9\-]+)")
def update_law(body,id):
    data=json.loads(body)
    conn=get_db();cur=conn.cursor()
    cur.execute("UPDATE laws SET metadata=metadata||%s::jsonb WHERE id=%s",
                (json.dumps(data),id))
    conn.commit()
    return json_response({"updated":id})

@route("DELETE", r"/laws/(?P<id>[a-f0-9\-]+)")
def delete_law(body,id):
    conn=get_db();cur=conn.cursor()
    cur.execute("UPDATE laws SET deleted_at=NOW() WHERE id=%s",(id,))
    conn.commit()
    return json_response({"deleted":id})

@route("POST", r"/laws/(?P<id>[a-f0-9\-]+)/tags")
def add_tag(body,id):
    data=json.loads(body)
    conn=get_db();cur=conn.cursor()
    cur.execute("INSERT INTO tags(name) VALUES(%s) ON CONFLICT DO NOTHING",
                (data["name"],))
    cur.execute("""
        INSERT INTO law_tags(law_id,tag_id)
        SELECT %s,id FROM tags WHERE name=%s
        ON CONFLICT DO NOTHING
    """,(id,data["name"]))
    conn.commit()
    return json_response({"tag_added":data["name"]})

@route("GET", r"/laws/(?P<id>[a-f0-9\-]+)/tags")
def get_tags(body,id):
    conn=get_db();cur=conn.cursor()
    cur.execute("""
        SELECT t.name FROM tags t
        JOIN law_tags lt ON lt.tag_id=t.id
        WHERE lt.law_id=%s
    """,(id,))
    return json_response([r[0] for r in cur.fetchall()])

@route("POST", r"/laws/(?P<law_id>[a-f0-9\-]+)/articles")
def create_article(body,law_id):
    data=json.loads(body)
    conn=get_db();cur=conn.cursor()
    cur.execute("""
        INSERT INTO articles(law_id,article_number)
        VALUES(%s,%s) RETURNING id
    """,(law_id,data["article_number"]))
    article_id=cur.fetchone()[0]
    cur.execute("""
        INSERT INTO article_versions(article_id,version,content)
        VALUES(%s,1,%s)
    """,(article_id,data["content"]))
    conn.commit()
    return json_response({"article_id":article_id},201)

@route("GET", r"/articles/(?P<id>[a-f0-9\-]+)")
def get_article(body,id):
    conn=get_db();cur=conn.cursor()
    cur.execute("""
        SELECT a.id,av.content,av.version
        FROM articles a
        JOIN article_versions av ON av.article_id=a.id
        WHERE a.id=%s
        ORDER BY av.version DESC LIMIT 1
    """,(id,))
    return json_response(cur.fetchone())

@route("PATCH", r"/articles/(?P<id>[a-f0-9\-]+)")
def version_article(body,id):
    data=json.loads(body)
    conn=get_db();cur=conn.cursor()
    cur.execute("SELECT COUNT(*) FROM article_versions WHERE article_id=%s",(id,))
    v=cur.fetchone()[0]+1
    cur.execute("""
        INSERT INTO article_versions(article_id,version,content)
        VALUES(%s,%s,%s)
    """,(id,v,data["content"]))
    conn.commit()
    return json_response({"new_version":v})

@route("GET", r"/articles/(?P<id>[a-f0-9\-]+)/versions")
def versions(body,id):
    conn=get_db();cur=conn.cursor()
    cur.execute("""
        SELECT version,content FROM article_versions
        WHERE article_id=%s ORDER BY version
    """,(id,))
    return json_response(cur.fetchall())

@route("POST", r"/articles/(?P<id>[a-f0-9\-]+)/amendments")
def amend(body,id):
    data=json.loads(body)
    conn=get_db();cur=conn.cursor()
    cur.execute("""
        INSERT INTO amendments(article_id,amendment_text,amendment_date)
        VALUES(%s,%s,%s)
    """,(id,data["text"],data["date"]))
    conn.commit()
    return json_response({"amended":id})

@route("GET", r"/articles/(?P<id>[a-f0-9\-]+)/amendments")
def get_amend(body,id):
    conn=get_db();cur=conn.cursor()
    cur.execute("SELECT amendment_text FROM amendments WHERE article_id=%s",(id,))
    return json_response(cur.fetchall())

@route("POST", r"/articles/(?P<id>[a-f0-9\-]+)/references")
def add_ref(body,id):
    data=json.loads(body)
    conn=get_db();cur=conn.cursor()
    cur.execute("""
        INSERT INTO article_references(from_article,to_article)
        VALUES(%s,%s)
    """,(id,data["to"]))
    conn.commit()
    return json_response({"reference_added":True})

@route("GET", r"/articles/(?P<id>[a-f0-9\-]+)/references")
def refs(body,id):
    conn=get_db();cur=conn.cursor()
    cur.execute("""
        SELECT to_article FROM article_references
        WHERE from_article=%s
    """,(id,))
    return json_response(cur.fetchall())

@route("GET", r"/stats/laws-per-category")
def stats1(body):
    conn=get_db();cur=conn.cursor()
    cur.execute("""
        SELECT c.name,COUNT(l.id)
        FROM categories c
        LEFT JOIN laws l ON l.category_id=c.id
        GROUP BY c.name
    """)
    return json_response(cur.fetchall())

@route("GET", r"/stats/most-amended-laws")
def stats2(body):
    conn=get_db();cur=conn.cursor()
    cur.execute("""
        SELECT l.title,COUNT(am.id) total
        FROM laws l
        JOIN articles a ON a.law_id=l.id
        JOIN amendments am ON am.article_id=a.id
        GROUP BY l.title ORDER BY total DESC LIMIT 5
    """)
    return json_response(cur.fetchall())

@route("GET", r"/stats/articles-count")
def stats3(body):
    conn=get_db();cur=conn.cursor()
    cur.execute("SELECT COUNT(*) FROM articles")
    return json_response(cur.fetchone())

@route("GET", r"/stats/amendments-per-year")
def stats4(body):
    conn=get_db();cur=conn.cursor()
    cur.execute("""
        SELECT EXTRACT(YEAR FROM amendment_date),COUNT(*)
        FROM amendments GROUP BY 1
    """)
    return json_response(cur.fetchall())

@route("GET", r"/audit")
def audit(body):
    conn=get_db();cur=conn.cursor()
    cur.execute("SELECT * FROM audit_log ORDER BY created_at DESC LIMIT 50")
    return json_response(cur.fetchall())

@route("POST", r"/bulk/laws")
def bulk(body):
    data=json.loads(body)
    conn=get_db();cur=conn.cursor()
    for law in data:
        cur.execute("INSERT INTO laws(title) VALUES(%s)",(law["title"],))
    conn.commit()
    return json_response({"bulk_inserted":len(data)})