    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE laws (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    category_id UUID REFERENCES categories(id),
    status TEXT CHECK(status IN ('draft','active','repealed')) DEFAULT 'draft',
    promulgation_date DATE,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    law_id UUID REFERENCES laws(id) ON DELETE CASCADE,
    article_number INT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP,
    UNIQUE(law_id, article_number)
);

CREATE TABLE article_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
    version INT NOT NULL,
    content TEXT NOT NULL,
    changed_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(article_id, version)
);

CREATE TABLE amendments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
    amendment_text TEXT,
    amendment_date DATE,
    approved BOOLEAN DEFAULT FALSE
);

CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE law_tags (
    law_id UUID REFERENCES laws(id) ON DELETE CASCADE,
    tag_id UUID REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY(law_id, tag_id)
);

CREATE TABLE article_references (
    from_article UUID REFERENCES articles(id) ON DELETE CASCADE,
    to_article UUID REFERENCES articles(id) ON DELETE CASCADE,
    PRIMARY KEY(from_article, to_article)
);

CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type TEXT,
    entity_id UUID,
    action TEXT,
    payload JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);