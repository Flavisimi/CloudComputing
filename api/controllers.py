from router import route
from db import get_db
from http_utils import json_response, error_response
import json
import psycopg2
from datetime import datetime

PAGE_SIZE = 5

LAWS_SORT_FIELDS = {"title", "created_at", "status", "promulgation_date"}
ARTICLES_SORT_FIELDS = {"article_number", "created_at"}
AMENDMENTS_SORT_FIELDS = {"amendment_date", "approved"}

def paginate(query, params, query_params, sort_fields, default_sort="created_at"):
    try:
        page = int(query_params.get("page", 1))
        if page < 1:
            raise ValueError
    except ValueError:
        return None, error_response(400, "Invalid 'page' parameter", "Must be a positive integer")

    sort = query_params.get("sort", default_sort)
    order = query_params.get("order", "asc").lower()

    if sort not in sort_fields:
        return None, error_response(400, f"Invalid 'sort' field: '{sort}'",
                                    f"Allowed: {', '.join(sorted(sort_fields))}")
    if order not in ("asc", "desc"):
        return None, error_response(400, "Invalid 'order' parameter", "Must be 'asc' or 'desc'")

    offset = (page - 1) * PAGE_SIZE
    full_query = f"{query} ORDER BY {sort} {order.upper()} LIMIT %s OFFSET %s"
    return (full_query, params + [PAGE_SIZE, offset], page), None


#Laws

@route("PUT", r"/laws/(?P<id>[a-f0-9\-]+)")
def replace_law(body, query_params, id):
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return error_response(400, "Invalid JSON body")

    if not data.get("title") or not isinstance(data["title"], str) or not data["title"].strip():
        return error_response(422, "Missing or invalid field: 'title'", "Title is required for PUT")

    status = data.get("status")
    if status not in ("draft", "active", "repealed"):
        return error_response(422, "Invalid or missing 'status'", "Allowed: draft, active, repealed")

    description = data.get("description", None)
    metadata = data.get("metadata", {})

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM laws WHERE id = %s AND deleted_at IS NULL", (id,))
    except psycopg2.errors.InvalidTextRepresentation:
        return error_response(400, "Invalid UUID format")

    if not cur.fetchone():
        return error_response(404, "Law not found", f"No active law with id '{id}'")

    try:
        cur.execute("""
            UPDATE laws 
            SET title = %s, description = %s, status = %s, metadata = %s::jsonb, updated_at = NOW()
            WHERE id = %s
        """, (data["title"].strip(), description, status, json.dumps(metadata), id))
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        return error_response(500, "Database error", str(e))

    return json_response({"replaced": id})

@route("GET", r"/laws")
def get_laws(body, query_params):
    conn = get_db()
    cur = conn.cursor()

    filters = []
    params = []

    status_filter = query_params.get("status")
    if status_filter:
        if status_filter not in ("draft", "active", "repealed"):
            return error_response(400, "Invalid 'status' filter",
                                  "Allowed values: draft, active, repealed")
        filters.append("l.status = %s")
        params.append(status_filter)

    title_filter = query_params.get("title")
    if title_filter:
        filters.append("l.title ILIKE %s")
        params.append(f"%{title_filter}%")

    where = ("WHERE l.deleted_at IS NULL AND " + " AND ".join(filters)) if filters else "WHERE l.deleted_at IS NULL"

    base_query = f"""
        SELECT l.id, l.title, l.description, l.status, l.promulgation_date,
               l.metadata, l.created_at, COUNT(a.id) as article_count
        FROM laws l
        LEFT JOIN articles a ON l.id = a.law_id
        {where}
        GROUP BY l.id, l.title, l.description, l.status,
                 l.promulgation_date, l.metadata, l.created_at
    """

    result, err = paginate(base_query, params, query_params, LAWS_SORT_FIELDS)
    if err:
        return err

    full_query, all_params, page = result
    try:
        cur.execute(full_query, all_params)
    except Exception as e:
        return error_response(500, "Database error", str(e))

    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    return json_response({
        "page": page,
        "page_size": PAGE_SIZE,
        "results": [dict(zip(cols, r)) for r in rows]
    })


@route("POST", r"/laws")
def create_law(body, query_params):
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return error_response(400, "Invalid JSON body")

    if not data.get("title") or not isinstance(data["title"], str) or not data["title"].strip():
        return error_response(422, "Missing or invalid field: 'title'", "Must be a non-empty string")

    status = data.get("status", "draft")
    if status not in ("draft", "active", "repealed"):
        return error_response(422, "Invalid 'status'", "Allowed: draft, active, repealed")

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO laws(title, description, status, metadata)
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (data["title"].strip(), data.get("description"),
              status, json.dumps(data.get("metadata", {}))))
        law_id = cur.fetchone()[0]
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        return error_response(500, "Database error", str(e))

    return json_response({"law_id": law_id}, 201)


@route("GET", r"/laws/(?P<id>[a-f0-9\-]+)")
def get_law(body, query_params, id):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM laws WHERE id = %s AND deleted_at IS NULL", (id,))
    except psycopg2.errors.InvalidTextRepresentation:
        return error_response(400, "Invalid UUID format", f"'{id}' is not a valid UUID")

    row = cur.fetchone()
    if not row:
        return error_response(404, "Law not found", f"No law with id '{id}'")

    cols = [d[0] for d in cur.description]
    return json_response(dict(zip(cols, row)))


@route("PATCH", r"/laws/(?P<id>[a-f0-9\-]+)")
def update_law(body, query_params, id):
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return error_response(400, "Invalid JSON body")

    if not data:
        return error_response(422, "Empty patch body", "Provide at least one field to update")

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM laws WHERE id = %s AND deleted_at IS NULL", (id,))
    except psycopg2.errors.InvalidTextRepresentation:
        return error_response(400, "Invalid UUID format")

    if not cur.fetchone():
        return error_response(404, "Law not found", f"No law with id '{id}'")

    try:
        cur.execute(
            "UPDATE laws SET metadata = metadata || %s::jsonb, updated_at = NOW() WHERE id = %s",
            (json.dumps(data), id)
        )
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        return error_response(500, "Database error", str(e))

    return json_response({"updated": id})


@route("DELETE", r"/laws/(?P<id>[a-f0-9\-]+)")
def delete_law(body, query_params, id):
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM laws WHERE id = %s AND deleted_at IS NULL", (id,))
    except psycopg2.errors.InvalidTextRepresentation:
        return error_response(400, "Invalid UUID format")

    if not cur.fetchone():
        return error_response(404, "Law not found", f"No active law with id '{id}'")

    try:
        cur.execute("UPDATE laws SET deleted_at = NOW() WHERE id = %s", (id,))
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        return error_response(500, "Database error", str(e))

    return json_response({"deleted": id})


#Tags

@route("GET", r"/tags")
def get_all_tags(body, query_params):
    """Lista tuturor tag-urilor din sistem, cu numărul de legi asociate fiecăruia."""
    conn = get_db()
    cur = conn.cursor()

    search = query_params.get("search")
    params = []
    where = ""
    if search:
        where = "WHERE t.name ILIKE %s"
        params.append(f"%{search}%")

    cur.execute(f"""
        SELECT t.id, t.name, COUNT(lt.law_id) AS law_count
        FROM tags t
        LEFT JOIN law_tags lt ON lt.tag_id = t.id
        {where}
        GROUP BY t.id, t.name
        ORDER BY t.name ASC
    """, params)

    cols = [d[0] for d in cur.description]
    return json_response([dict(zip(cols, r)) for r in cur.fetchall()])


@route("POST", r"/laws/(?P<id>[a-f0-9\-]+)/tags")
def add_tag(body, query_params, id):
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return error_response(400, "Invalid JSON body")

    tag_name = data.get("name", "").strip()
    if not tag_name:
        return error_response(422, "Missing field: 'name'", "Tag name must be a non-empty string")

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM laws WHERE id = %s AND deleted_at IS NULL", (id,))
    except psycopg2.errors.InvalidTextRepresentation:
        return error_response(400, "Invalid UUID format")

    if not cur.fetchone():
        return error_response(404, "Law not found")

    try:
        cur.execute("INSERT INTO tags(name) VALUES(%s) ON CONFLICT DO NOTHING", (tag_name,))
        cur.execute("""
            INSERT INTO law_tags(law_id, tag_id)
            SELECT %s, id FROM tags WHERE name = %s
            ON CONFLICT DO NOTHING
        """, (id, tag_name))
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        return error_response(500, "Database error", str(e))

    return json_response({"tag_added": tag_name})


@route("GET", r"/laws/(?P<id>[a-f0-9\-]+)/tags")
def get_tags(body, query_params, id):
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM laws WHERE id = %s AND deleted_at IS NULL", (id,))
    except psycopg2.errors.InvalidTextRepresentation:
        return error_response(400, "Invalid UUID format")

    if not cur.fetchone():
        return error_response(404, "Law not found")

    cur.execute("""
        SELECT t.id, t.name FROM tags t
        JOIN law_tags lt ON lt.tag_id = t.id
        WHERE lt.law_id = %s
        ORDER BY t.name
    """, (id,))
    cols = [d[0] for d in cur.description]
    return json_response([dict(zip(cols, r)) for r in cur.fetchall()])


@route("DELETE", r"/laws/(?P<id>[a-f0-9\-]+)/tags/(?P<tag_name>[^/]+)")
def remove_tag(body, query_params, id, tag_name):
    """Elimină asocierea unui tag de pe o lege. Tag-ul în sine rămâne în sistem."""
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM laws WHERE id = %s AND deleted_at IS NULL", (id,))
    except psycopg2.errors.InvalidTextRepresentation:
        return error_response(400, "Invalid UUID format")

    if not cur.fetchone():
        return error_response(404, "Law not found")

    cur.execute("SELECT id FROM tags WHERE name = %s", (tag_name,))
    tag_row = cur.fetchone()
    if not tag_row:
        return error_response(404, "Tag not found", f"No tag named '{tag_name}'")

    try:
        cur.execute("""
            DELETE FROM law_tags WHERE law_id = %s AND tag_id = %s
        """, (id, tag_row[0]))
        if cur.rowcount == 0:
            conn.rollback()
            return error_response(404, "Association not found",
                                  f"Law does not have tag '{tag_name}'")
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        return error_response(500, "Database error", str(e))

    return json_response({"tag_removed": tag_name})


#Articles

@route("GET", r"/laws/(?P<law_id>[a-f0-9\-]+)/articles")
def get_law_articles(body, query_params, law_id):
    """Toate articolele unei legi (ultima versiune), cu paginare și sortare."""
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM laws WHERE id = %s AND deleted_at IS NULL", (law_id,))
    except psycopg2.errors.InvalidTextRepresentation:
        return error_response(400, "Invalid UUID format for law_id")

    if not cur.fetchone():
        return error_response(404, "Law not found")

    base_query = """
        WITH latest_versions AS (
            SELECT article_id, MAX(version) AS max_v
            FROM article_versions
            GROUP BY article_id
        )
        SELECT a.id, a.article_number, av.content, av.version, av.changed_at, a.created_at
        FROM articles a
        JOIN latest_versions lv ON lv.article_id = a.id
        JOIN article_versions av ON av.article_id = a.id AND av.version = lv.max_v
        WHERE a.law_id = %s AND a.deleted_at IS NULL
    """

    result, err = paginate(base_query, [law_id], query_params, ARTICLES_SORT_FIELDS, default_sort="article_number")
    if err:
        return err

    full_query, all_params, page = result
    try:
        cur.execute(full_query, all_params)
    except Exception as e:
        return error_response(500, "Database error", str(e))

    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    return json_response({
        "page": page,
        "page_size": PAGE_SIZE,
        "results": [dict(zip(cols, r)) for r in rows]
    })


@route("GET", r"/articles")
def get_articles(body, query_params):
    conn = get_db()
    cur = conn.cursor()

    filters = []
    params = []

    law_filter = query_params.get("law_id")
    if law_filter:
        filters.append("a.law_id = %s")
        params.append(law_filter)

    search_filter = query_params.get("search")
    if search_filter:
        filters.append("av.content ILIKE %s")
        params.append(f"%{search_filter}%")

    where_clause = "WHERE a.deleted_at IS NULL"
    if filters:
        where_clause += " AND " + " AND ".join(filters)

    base_query = f"""
        WITH latest_versions AS (
            SELECT article_id, MAX(version) as max_v
            FROM article_versions
            GROUP BY article_id
        )
        SELECT a.id, a.law_id, a.article_number, av.content, av.version, av.changed_at, a.created_at
        FROM articles a
        JOIN latest_versions lv ON lv.article_id = a.id
        JOIN article_versions av ON av.article_id = a.id AND av.version = lv.max_v
        {where_clause}
    """

    result, err = paginate(base_query, params, query_params, ARTICLES_SORT_FIELDS, default_sort="created_at")
    if err:
        return err

    full_query, all_params, page = result
    try:
        cur.execute(full_query, all_params)
    except psycopg2.errors.InvalidTextRepresentation:
        conn.rollback()
        return error_response(400, "Invalid UUID format", "Parametrul 'law_id' trebuie să fie un UUID valid.")
    except Exception as e:
        conn.rollback()
        return error_response(500, "Database error", str(e))

    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    return json_response({
        "page": page,
        "page_size": PAGE_SIZE,
        "results": [dict(zip(cols, r)) for r in rows]
    })


@route("POST", r"/laws/(?P<law_id>[a-f0-9\-]+)/articles")
def create_article(body, query_params, law_id):
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return error_response(400, "Invalid JSON body")

    if "article_number" not in data:
        return error_response(422, "Missing field: 'article_number'")
    if not isinstance(data["article_number"], int) or data["article_number"] < 1:
        return error_response(422, "Invalid 'article_number'", "Must be a positive integer")
    if not data.get("content", "").strip():
        return error_response(422, "Missing field: 'content'", "Must be a non-empty string")

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM laws WHERE id = %s AND deleted_at IS NULL", (law_id,))
    except psycopg2.errors.InvalidTextRepresentation:
        return error_response(400, "Invalid UUID format for law_id")

    if not cur.fetchone():
        return error_response(404, "Law not found", f"No active law with id '{law_id}'")

    try:
        cur.execute("""
            INSERT INTO articles(law_id, article_number)
            VALUES(%s, %s) RETURNING id
        """, (law_id, data["article_number"]))
        article_id = cur.fetchone()[0]
        cur.execute("""
            INSERT INTO article_versions(article_id, version, content)
            VALUES(%s, 1, %s)
        """, (article_id, data["content"].strip()))
        conn.commit()
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return error_response(409, "Article number already exists",
                              f"Law already has article #{data['article_number']}")
    except psycopg2.Error as e:
        conn.rollback()
        return error_response(500, "Database error", str(e))

    return json_response({"article_id": article_id}, 201)


@route("GET", r"/articles/(?P<id>[a-f0-9\-]+)")
def get_article(body, query_params, id):
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT a.id, a.article_number, av.content, av.version, av.changed_at
            FROM articles a
            JOIN article_versions av ON av.article_id = a.id
            WHERE a.id = %s AND a.deleted_at IS NULL
            ORDER BY av.version DESC LIMIT 1
        """, (id,))
    except psycopg2.errors.InvalidTextRepresentation:
        return error_response(400, "Invalid UUID format")

    row = cur.fetchone()
    if not row:
        return error_response(404, "Article not found", f"No article with id '{id}'")

    cols = [d[0] for d in cur.description]
    return json_response(dict(zip(cols, row)))


@route("PATCH", r"/articles/(?P<id>[a-f0-9\-]+)")
def version_article(body, query_params, id):
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return error_response(400, "Invalid JSON body")

    if not data.get("content", "").strip():
        return error_response(422, "Missing or empty field: 'content'")

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM articles WHERE id = %s AND deleted_at IS NULL", (id,))
    except psycopg2.errors.InvalidTextRepresentation:
        return error_response(400, "Invalid UUID format")

    if not cur.fetchone():
        return error_response(404, "Article not found")

    try:
        cur.execute("SELECT COUNT(*) FROM article_versions WHERE article_id = %s", (id,))
        v = cur.fetchone()[0] + 1
        cur.execute("""
            INSERT INTO article_versions(article_id, version, content)
            VALUES(%s, %s, %s)
        """, (id, v, data["content"].strip()))
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        return error_response(500, "Database error", str(e))

    return json_response({"new_version": v})


@route("DELETE", r"/articles/(?P<id>[a-f0-9\-]+)")
def delete_article(body, query_params, id):
    """Soft-delete un articol. Cascadează logic și amendamentele/referințele rămân în DB."""
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM articles WHERE id = %s AND deleted_at IS NULL", (id,))
    except psycopg2.errors.InvalidTextRepresentation:
        return error_response(400, "Invalid UUID format")

    if not cur.fetchone():
        return error_response(404, "Article not found", f"No active article with id '{id}'")

    try:
        cur.execute("UPDATE articles SET deleted_at = NOW() WHERE id = %s", (id,))
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        return error_response(500, "Database error", str(e))

    return json_response({"deleted": id})


@route("GET", r"/articles/(?P<id>[a-f0-9\-]+)/versions")
def versions(body, query_params, id):
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM articles WHERE id = %s AND deleted_at IS NULL", (id,))
    except psycopg2.errors.InvalidTextRepresentation:
        return error_response(400, "Invalid UUID format")

    if not cur.fetchone():
        return error_response(404, "Article not found")

    try:
        page = int(query_params.get("page", 1))
        if page < 1:
            raise ValueError
    except ValueError:
        return error_response(400, "Invalid 'page' parameter")

    offset = (page - 1) * PAGE_SIZE
    cur.execute("""
        SELECT version, content, changed_at FROM article_versions
        WHERE article_id = %s ORDER BY version
        LIMIT %s OFFSET %s
    """, (id, PAGE_SIZE, offset))

    cols = [d[0] for d in cur.description]
    return json_response({
        "page": page,
        "page_size": PAGE_SIZE,
        "results": [dict(zip(cols, r)) for r in cur.fetchall()]
    })


#Amendments

@route("PUT", r"/amendments/(?P<id>[a-f0-9\-]+)")
def replace_amendment(body, query_params, id):
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return error_response(400, "Invalid JSON body")

    if not data.get("text") or not str(data["text"]).strip():
        return error_response(422, "Missing or invalid field: 'text'")

    if not data.get("date"):
        return error_response(422, "Missing field: 'date'")

    try:
        datetime.strptime(data["date"], "%Y-%m-%d")
    except ValueError:
        return error_response(422, "Invalid 'date' format", "Expected YYYY-MM-DD")

    if "approved" not in data or not isinstance(data["approved"], bool):
        return error_response(422, "Missing or invalid field: 'approved'", "Must be a boolean")

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM amendments WHERE id = %s", (id,))
    except psycopg2.errors.InvalidTextRepresentation:
        return error_response(400, "Invalid UUID format")

    if not cur.fetchone():
        return error_response(404, "Amendment not found")

    try:
        cur.execute("""
                    UPDATE amendments
                    SET amendment_text = %s,
                        amendment_date = %s,
                        approved       = %s
                    WHERE id = %s
                    """, (data["text"].strip(), data["date"], data["approved"], id))
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        return error_response(500, "Database error", str(e))

    return json_response({"replaced": id})

@route("GET", r"/amendments")
def get_all_amendments(body, query_params):
    conn = get_db()
    cur = conn.cursor()

    filters = []
    params = []

    approved_filter = query_params.get("approved")
    if approved_filter is not None:
        if approved_filter.lower() not in ("true", "false"):
            return error_response(400, "Invalid 'approved' filter", "Must be 'true' or 'false'")
        filters.append("am.approved = %s")
        params.append(approved_filter.lower() == "true")

    where_clause = ""
    if filters:
        where_clause = "WHERE " + " AND ".join(filters)

    base_query = f"""
        SELECT am.id, am.article_id, am.amendment_text, am.amendment_date, am.approved,
               a.article_number, a.law_id, l.title AS law_title
        FROM amendments am
        JOIN articles a ON a.id = am.article_id
        JOIN laws l ON l.id = a.law_id
        {where_clause}
    """

    result, err = paginate(base_query, params, query_params, AMENDMENTS_SORT_FIELDS, default_sort="amendment_date")
    if err:
        return err

    full_query, all_params, page = result

    try:
        cur.execute(full_query, all_params)
    except Exception as e:
        return error_response(500, "Database error", str(e))

    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]

    return json_response({
        "page": page,
        "page_size": PAGE_SIZE,
        "results": [dict(zip(cols, r)) for r in rows]
    })

@route("POST", r"/articles/(?P<id>[a-f0-9\-]+)/amendments")
def amend(body, query_params, id):
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return error_response(400, "Invalid JSON body")

    if not data.get("text", "").strip():
        return error_response(422, "Missing field: 'text'")
    if not data.get("date"):
        return error_response(422, "Missing field: 'date'")

    try:
        datetime.strptime(data["date"], "%Y-%m-%d")
    except ValueError:
        return error_response(422, "Invalid 'date' format", "Expected YYYY-MM-DD")

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM articles WHERE id = %s AND deleted_at IS NULL", (id,))
    except psycopg2.errors.InvalidTextRepresentation:
        return error_response(400, "Invalid UUID format")

    if not cur.fetchone():
        return error_response(404, "Article not found")

    try:
        cur.execute("""
            INSERT INTO amendments(article_id, amendment_text, amendment_date)
            VALUES(%s, %s, %s) RETURNING id
        """, (id, data["text"].strip(), data["date"]))
        amendment_id = cur.fetchone()[0]
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        return error_response(500, "Database error", str(e))

    return json_response({"amendment_id": amendment_id}, 201)


@route("GET", r"/articles/(?P<id>[a-f0-9\-]+)/amendments")
def get_amend(body, query_params, id):
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM articles WHERE id = %s AND deleted_at IS NULL", (id,))
    except psycopg2.errors.InvalidTextRepresentation:
        return error_response(400, "Invalid UUID format")

    if not cur.fetchone():
        return error_response(404, "Article not found")

    approved_filter = query_params.get("approved")
    params = [id]
    approved_clause = ""
    if approved_filter is not None:
        if approved_filter.lower() not in ("true", "false"):
            return error_response(400, "Invalid 'approved' filter", "Must be 'true' or 'false'")
        approved_clause = "AND approved = %s"
        params.append(approved_filter.lower() == "true")

    try:
        page = int(query_params.get("page", 1))
        if page < 1:
            raise ValueError
    except ValueError:
        return error_response(400, "Invalid 'page' parameter")

    offset = (page - 1) * PAGE_SIZE
    params += [PAGE_SIZE, offset]

    cur.execute(f"""
        SELECT id, amendment_text, amendment_date, approved
        FROM amendments WHERE article_id = %s {approved_clause}
        ORDER BY amendment_date DESC
        LIMIT %s OFFSET %s
    """, params)

    cols = [d[0] for d in cur.description]
    return json_response({
        "page": page,
        "page_size": PAGE_SIZE,
        "results": [dict(zip(cols, r)) for r in cur.fetchall()]
    })


@route("GET", r"/amendments/(?P<id>[a-f0-9\-]+)")
def get_amendment(body, query_params, id):
    """Returnează un amendament specific după id-ul său."""
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT am.id, am.article_id, am.amendment_text, am.amendment_date, am.approved,
                   a.article_number, a.law_id
            FROM amendments am
            JOIN articles a ON a.id = am.article_id
            WHERE am.id = %s
        """, (id,))
    except psycopg2.errors.InvalidTextRepresentation:
        return error_response(400, "Invalid UUID format")

    row = cur.fetchone()
    if not row:
        return error_response(404, "Amendment not found", f"No amendment with id '{id}'")

    cols = [d[0] for d in cur.description]
    return json_response(dict(zip(cols, row)))


@route("PATCH", r"/amendments/(?P<id>[a-f0-9\-]+)")
def update_amendment(body, query_params, id):
    """Actualizează textul și/sau statusul de aprobare al unui amendament."""
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return error_response(400, "Invalid JSON body")

    if not data:
        return error_response(422, "Empty patch body", "Provide 'approved' (bool) and/or 'text' (string)")

    allowed = {"approved", "text"}
    unknown = set(data.keys()) - allowed
    if unknown:
        return error_response(422, f"Unknown fields: {', '.join(unknown)}", f"Allowed fields: {', '.join(allowed)}")

    if "approved" in data and not isinstance(data["approved"], bool):
        return error_response(422, "Invalid 'approved'", "Must be a boolean (true/false)")

    if "text" in data and not str(data["text"]).strip():
        return error_response(422, "Invalid 'text'", "Must be a non-empty string")

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM amendments WHERE id = %s", (id,))
    except psycopg2.errors.InvalidTextRepresentation:
        return error_response(400, "Invalid UUID format")

    if not cur.fetchone():
        return error_response(404, "Amendment not found")

    set_clauses = []
    params = []
    if "approved" in data:
        set_clauses.append("approved = %s")
        params.append(data["approved"])
    if "text" in data:
        set_clauses.append("amendment_text = %s")
        params.append(data["text"].strip())
    params.append(id)

    try:
        cur.execute(f"""
            UPDATE amendments SET {', '.join(set_clauses)} WHERE id = %s
        """, params)
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        return error_response(500, "Database error", str(e))

    return json_response({"updated": id})


@route("DELETE", r"/amendments/(?P<id>[a-f0-9\-]+)")
def delete_amendment(body, query_params, id):
    """Șterge permanent un amendament (hard delete — amendamentele nu au deleted_at)."""
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id, approved FROM amendments WHERE id = %s", (id,))
    except psycopg2.errors.InvalidTextRepresentation:
        return error_response(400, "Invalid UUID format")

    row = cur.fetchone()
    if not row:
        return error_response(404, "Amendment not found")

    if row[1]:  # approved == True
        return error_response(409, "Cannot delete approved amendment",
                              "Approved amendments are immutable. Set approved=false first if needed.")

    try:
        cur.execute("DELETE FROM amendments WHERE id = %s", (id,))
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        return error_response(500, "Database error", str(e))

    return json_response({"deleted": id})


#Ref

@route("POST", r"/articles/(?P<id>[a-f0-9\-]+)/references")
def add_ref(body, query_params, id):
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return error_response(400, "Invalid JSON body")

    to_id = data.get("to", "").strip()
    if not to_id:
        return error_response(422, "Missing field: 'to'", "Target article UUID required")

    if id == to_id:
        return error_response(422, "Self-reference not allowed", "An article cannot reference itself")

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM articles WHERE id = %s AND deleted_at IS NULL", (id,))
        if not cur.fetchone():
            return error_response(404, "Source article not found")
        cur.execute("SELECT id FROM articles WHERE id = %s AND deleted_at IS NULL", (to_id,))
        if not cur.fetchone():
            return error_response(404, "Target article not found", f"No article with id '{to_id}'")
    except psycopg2.errors.InvalidTextRepresentation:
        return error_response(400, "Invalid UUID format")

    try:
        cur.execute("""
            INSERT INTO article_references(from_article, to_article)
            VALUES(%s, %s)
        """, (id, to_id))
        conn.commit()
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return error_response(409, "Reference already exists")
    except psycopg2.Error as e:
        conn.rollback()
        return error_response(500, "Database error", str(e))

    return json_response({"reference_added": True}, 201)


@route("GET", r"/articles/(?P<id>[a-f0-9\-]+)/references")
def refs(body, query_params, id):
    """Referințele outgoing: articolele la care face referință acest articol."""
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM articles WHERE id = %s AND deleted_at IS NULL", (id,))
    except psycopg2.errors.InvalidTextRepresentation:
        return error_response(400, "Invalid UUID format")

    if not cur.fetchone():
        return error_response(404, "Article not found")

    cur.execute("""
        SELECT ar.to_article, a.article_number, a.law_id
        FROM article_references ar
        JOIN articles a ON a.id = ar.to_article
        WHERE ar.from_article = %s
    """, (id,))
    cols = [d[0] for d in cur.description]
    return json_response([dict(zip(cols, r)) for r in cur.fetchall()])


@route("GET", r"/articles/(?P<id>[a-f0-9\-]+)/references/incoming")
def refs_incoming(body, query_params, id):
    """Referințele incoming: ce alte articole fac referință la acest articol."""
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM articles WHERE id = %s AND deleted_at IS NULL", (id,))
    except psycopg2.errors.InvalidTextRepresentation:
        return error_response(400, "Invalid UUID format")

    if not cur.fetchone():
        return error_response(404, "Article not found")

    cur.execute("""
        SELECT ar.from_article, a.article_number, a.law_id
        FROM article_references ar
        JOIN articles a ON a.id = ar.from_article
        WHERE ar.to_article = %s
    """, (id,))
    cols = [d[0] for d in cur.description]
    return json_response([dict(zip(cols, r)) for r in cur.fetchall()])


@route("DELETE", r"/articles/(?P<id>[a-f0-9\-]+)/references/(?P<to_id>[a-f0-9\-]+)")
def delete_ref(body, query_params, id, to_id):
    """Șterge o referință specifică între două articole."""
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("""
            DELETE FROM article_references WHERE from_article = %s AND to_article = %s
        """, (id, to_id))
    except psycopg2.errors.InvalidTextRepresentation:
        return error_response(400, "Invalid UUID format")

    if cur.rowcount == 0:
        conn.rollback()
        return error_response(404, "Reference not found",
                              f"No reference from '{id}' to '{to_id}'")

    conn.commit()
    return json_response({"deleted": True})


#Stats

@route("GET", r"/stats/laws-per-category")
def stats1(body, query_params):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.name, COUNT(l.id) AS total
        FROM categories c
        LEFT JOIN laws l ON l.category_id = c.id AND l.deleted_at IS NULL
        GROUP BY c.name
        ORDER BY c.name
    """)
    cols = [d[0] for d in cur.description]
    return json_response([dict(zip(cols, r)) for r in cur.fetchall()])


@route("GET", r"/stats/most-amended-laws")
def stats2(body, query_params):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT l.title, COUNT(am.id) AS total
        FROM laws l
        JOIN articles a ON a.law_id = l.id
        JOIN amendments am ON am.article_id = a.id
        WHERE l.deleted_at IS NULL
        GROUP BY l.title
        ORDER BY total DESC
        LIMIT 5
    """)
    cols = [d[0] for d in cur.description]
    return json_response([dict(zip(cols, r)) for r in cur.fetchall()])


@route("GET", r"/stats/articles-count")
def stats3(body, query_params):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS total FROM articles WHERE deleted_at IS NULL")
    return json_response({"total": cur.fetchone()[0]})


@route("GET", r"/stats/amendments-per-year")
def stats4(body, query_params):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT EXTRACT(YEAR FROM amendment_date)::int AS year, COUNT(*) AS total
        FROM amendments
        GROUP BY 1
        ORDER BY 1
    """)
    cols = [d[0] for d in cur.description]
    return json_response([dict(zip(cols, r)) for r in cur.fetchall()])


#Audit

@route("GET", r"/audit")
def audit(body, query_params):
    conn = get_db()
    cur = conn.cursor()

    try:
        page = int(query_params.get("page", 1))
        if page < 1:
            raise ValueError
    except ValueError:
        return error_response(400, "Invalid 'page' parameter")

    entity_type = query_params.get("entity_type")
    action_filter = query_params.get("action")

    filters = []
    params = []
    if entity_type:
        filters.append("entity_type = %s")
        params.append(entity_type.upper())
    if action_filter:
        filters.append("action = %s")
        params.append(action_filter.upper())

    where = ("WHERE " + " AND ".join(filters)) if filters else ""
    offset = (page - 1) * PAGE_SIZE
    params += [PAGE_SIZE, offset]

    cur.execute(f"""
        SELECT * FROM audit_log
        {where}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """, params)

    cols = [d[0] for d in cur.description]
    return json_response({
        "page": page,
        "page_size": PAGE_SIZE,
        "results": [dict(zip(cols, r)) for r in cur.fetchall()]
    })


#Bulk

@route("POST", r"/bulk/laws")
def bulk(body, query_params):
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return error_response(400, "Invalid JSON body")

    if not isinstance(data, list):
        return error_response(422, "Expected a JSON array of law objects")
    if len(data) == 0:
        return error_response(422, "Array must not be empty")
    if len(data) > 100:
        return error_response(422, "Bulk limit exceeded", "Max 100 laws per request")

    errors = []
    for i, law in enumerate(data):
        if not isinstance(law, dict):
            errors.append(f"Item {i}: must be an object")
        elif not law.get("title", "").strip():
            errors.append(f"Item {i}: missing or empty 'title'")

    if errors:
        return error_response(422, "Validation failed", errors)

    conn = get_db()
    cur = conn.cursor()
    try:
        for law in data:
            cur.execute(
                "INSERT INTO laws(title, description) VALUES(%s, %s)",
                (law["title"].strip(), law.get("description"))
            )
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        return error_response(500, "Database error", str(e))

    return json_response({"bulk_inserted": len(data)}, 201)