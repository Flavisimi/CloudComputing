
INSERT INTO categories (name) VALUES
('Constitutional'),
('Criminal'),
('Civil'),
('Administrative'),
('Fiscal'),
('Labor'),
('Environmental'),
('Commercial'),
('Health'),
('Education');

INSERT INTO tags (name) VALUES
('urgent'),
('reform'),
('national'),
('EU'),
('temporary'),
('taxation'),
('public'),
('private'),
('digital'),
('infrastructure');

INSERT INTO laws (title, description, category_id, status, promulgation_date, metadata)
SELECT
    'Law #' || gs,
    'Description for law #' || gs,
    c.id,
    (ARRAY['draft','active','repealed'])[1 + (gs % 3)],
    CURRENT_DATE - (gs * 30),
    jsonb_build_object('importance', gs, 'source', 'official_monitor')
FROM generate_series(1,10) gs
JOIN categories c ON c.name = (
    SELECT name FROM categories ORDER BY name LIMIT 1 OFFSET (gs-1)
);

INSERT INTO law_tags (law_id, tag_id)
SELECT l.id, t.id
FROM laws l
JOIN tags t ON (random() < 0.3)
LIMIT 20;

INSERT INTO articles (law_id, article_number)
SELECT l.id, 1
FROM laws l;

INSERT INTO article_versions (article_id, version, content)
SELECT a.id, v,
       'Content for article ' || a.article_number || ', version ' || v
FROM articles a
CROSS JOIN generate_series(1,2) v;

INSERT INTO amendments (article_id, amendment_text, amendment_date, approved)
SELECT
    a.id,
    'Amendment for article ' || a.article_number,
    CURRENT_DATE - 10,
    (random() > 0.5)
FROM articles a;

INSERT INTO article_references (from_article, to_article)
SELECT a1.id, a2.id
FROM articles a1
JOIN articles a2 ON a1.id <> a2.id
LIMIT 10;

INSERT INTO audit_log (entity_type, entity_id, action, payload)
SELECT
    'LAW',
    l.id,
    'CREATE',
    jsonb_build_object('title', l.title)
FROM laws l
LIMIT 10;