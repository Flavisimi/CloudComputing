-- ─────────────────────────────────────────────
-- TRUNCATE (reset complet)
-- ─────────────────────────────────────────────
TRUNCATE audit_log, article_references, amendments,
         article_versions, articles, law_tags,
         laws, tags, categories
RESTART IDENTITY CASCADE;

-- ─────────────────────────────────────────────
-- CATEGORIES
-- ─────────────────────────────────────────────
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

-- ─────────────────────────────────────────────
-- TAGS
-- ─────────────────────────────────────────────
INSERT INTO tags (name) VALUES
('civil-rights'),
('federal'),
('amendment'),
('landmark'),
('social-policy'),
('taxation'),
('environment'),
('healthcare'),
('labor-rights'),
('national-security'),
('education'),
('privacy'),
('immigration'),
('consumer-protection'),
('reform');

-- ─────────────────────────────────────────────
-- LAWS  (titluri reale SUA / UK — Wikipedia le cunoaște)
-- ─────────────────────────────────────────────
INSERT INTO laws (title, description, category_id, status, promulgation_date, metadata)
VALUES
-- 1
(
  'Civil Rights Act',
  'Landmark federal legislation that outlaws discrimination based on race, color, religion, sex, or national origin.',
  (SELECT id FROM categories WHERE name = 'Civil'),
  'active',
  '1964-07-02',
  '{"importance":"high","source":"US Congress","reference":"Public Law 88-352"}'
),
-- 2
(
  'Freedom of Information Act',
  'Federal law that grants the public the right to request access to records from any federal agency.',
  (SELECT id FROM categories WHERE name = 'Administrative'),
  'active',
  '1966-07-04',
  '{"importance":"high","source":"US Congress","reference":"5 U.S.C. § 552"}'
),
-- 3
(
  'Clean Air Act',
  'United States federal law designed to control air pollution on a national level.',
  (SELECT id FROM categories WHERE name = 'Environmental'),
  'active',
  '1970-12-31',
  '{"importance":"high","source":"US Congress","reference":"42 U.S.C. § 7401"}'
),
-- 4
(
  'Occupational Safety and Health Act',
  'US law that established the Occupational Safety and Health Administration to ensure safe working conditions.',
  (SELECT id FROM categories WHERE name = 'Labor'),
  'active',
  '1970-12-29',
  '{"importance":"high","source":"US Congress","reference":"29 U.S.C. § 651"}'
),
-- 5
(
  'Privacy Act',
  'Federal law that establishes a code of fair information practices governing the collection, maintenance, and use of personal information.',
  (SELECT id FROM categories WHERE name = 'Administrative'),
  'active',
  '1974-12-31',
  '{"importance":"high","source":"US Congress","reference":"5 U.S.C. § 552a"}'
),
-- 6
(
  'Americans with Disabilities Act',
  'Civil rights law that prohibits discrimination against individuals with disabilities in all areas of public life.',
  (SELECT id FROM categories WHERE name = 'Civil'),
  'active',
  '1990-07-26',
  '{"importance":"high","source":"US Congress","reference":"42 U.S.C. § 12101"}'
),
-- 7
(
  'Family and Medical Leave Act',
  'Federal law requiring covered employers to provide employees with job-protected and unpaid leave for family and medical reasons.',
  (SELECT id FROM categories WHERE name = 'Labor'),
  'active',
  '1993-02-05',
  '{"importance":"medium","source":"US Congress","reference":"29 U.S.C. § 2601"}'
),
-- 8
(
  'Health Insurance Portability and Accountability Act',
  'Legislation that provides data privacy and security provisions for safeguarding medical information.',
  (SELECT id FROM categories WHERE name = 'Health'),
  'active',
  '1996-08-21',
  '{"importance":"high","source":"US Congress","reference":"Public Law 104-191"}'
),
-- 9
(
  'No Child Left Behind Act',
  'Federal law reauthorizing the Elementary and Secondary Education Act, emphasizing standards-based education reform.',
  (SELECT id FROM categories WHERE name = 'Education'),
  'repealed',
  '2002-01-08',
  '{"importance":"medium","source":"US Congress","reference":"Public Law 107-110"}'
),
-- 10
(
  'USA PATRIOT Act',
  'Law dramatically expanding the surveillance and investigative powers of law enforcement agencies in the United States.',
  (SELECT id FROM categories WHERE name = 'National Security'),
  'active',
  '2001-10-26',
  '{"importance":"high","source":"US Congress","reference":"Public Law 107-56"}'
),
-- 11
(
  'Dodd-Frank Wall Street Reform and Consumer Protection Act',
  'Financial reform legislation passed in response to the 2008 financial crisis, introducing comprehensive regulation of financial markets.',
  (SELECT id FROM categories WHERE name = 'Commercial'),
  'active',
  '2010-07-21',
  '{"importance":"high","source":"US Congress","reference":"Public Law 111-203"}'
),
-- 12
(
  'Affordable Care Act',
  'Comprehensive health care reform law intended to increase health insurance quality and affordability.',
  (SELECT id FROM categories WHERE name = 'Health'),
  'active',
  '2010-03-23',
  '{"importance":"high","source":"US Congress","reference":"Public Law 111-148"}'
),
-- 13
(
  'Human Rights Act 1998',
  'UK Act of Parliament which incorporated the rights contained in the European Convention on Human Rights into UK law.',
  (SELECT id FROM categories WHERE name = 'Constitutional'),
  'active',
  '1998-11-09',
  '{"importance":"high","source":"UK Parliament","reference":"1998 c. 42"}'
),
-- 14
(
  'Data Protection Act 2018',
  'UK law that controls how personal information is used by organisations, businesses or the government.',
  (SELECT id FROM categories WHERE name = 'Administrative'),
  'active',
  '2018-05-23',
  '{"importance":"high","source":"UK Parliament","reference":"2018 c. 12"}'
),
-- 15
(
  'Equality Act 2010',
  'UK law that legally protects people from discrimination in the workplace and in wider society.',
  (SELECT id FROM categories WHERE name = 'Civil'),
  'active',
  '2010-04-08',
  '{"importance":"high","source":"UK Parliament","reference":"2010 c. 15"}'
);

-- ─────────────────────────────────────────────
-- LAW_TAGS
-- ─────────────────────────────────────────────
INSERT INTO law_tags (law_id, tag_id)
SELECT l.id, t.id FROM laws l, tags t
WHERE (l.title = 'Civil Rights Act'                                     AND t.name IN ('civil-rights','landmark','federal'))
   OR (l.title = 'Freedom of Information Act'                           AND t.name IN ('federal','reform'))
   OR (l.title = 'Clean Air Act'                                        AND t.name IN ('environment','federal','landmark'))
   OR (l.title = 'Occupational Safety and Health Act'                   AND t.name IN ('labor-rights','federal'))
   OR (l.title = 'Privacy Act'                                          AND t.name IN ('privacy','federal'))
   OR (l.title = 'Americans with Disabilities Act'                      AND t.name IN ('civil-rights','landmark','social-policy'))
   OR (l.title = 'Family and Medical Leave Act'                         AND t.name IN ('labor-rights','social-policy'))
   OR (l.title = 'Health Insurance Portability and Accountability Act'  AND t.name IN ('healthcare','privacy'))
   OR (l.title = 'No Child Left Behind Act'                             AND t.name IN ('education','federal','reform'))
   OR (l.title = 'USA PATRIOT Act'                                      AND t.name IN ('national-security','federal'))
   OR (l.title = 'Dodd-Frank Wall Street Reform and Consumer Protection Act' AND t.name IN ('commercial','reform','consumer-protection'))
   OR (l.title = 'Affordable Care Act'                                  AND t.name IN ('healthcare','social-policy','landmark','reform'))
   OR (l.title = 'Human Rights Act 1998'                                AND t.name IN ('civil-rights','landmark','amendment'))
   OR (l.title = 'Data Protection Act 2018'                             AND t.name IN ('privacy','reform'))
   OR (l.title = 'Equality Act 2010'                                    AND t.name IN ('civil-rights','landmark','social-policy'));

-- ─────────────────────────────────────────────
-- ARTICLES
-- ─────────────────────────────────────────────
INSERT INTO articles (law_id, article_number)
SELECT id, 1 FROM laws WHERE title = 'Civil Rights Act'
UNION ALL SELECT id, 2 FROM laws WHERE title = 'Civil Rights Act'
UNION ALL SELECT id, 3 FROM laws WHERE title = 'Civil Rights Act'
UNION ALL SELECT id, 1 FROM laws WHERE title = 'Clean Air Act'
UNION ALL SELECT id, 2 FROM laws WHERE title = 'Clean Air Act'
UNION ALL SELECT id, 1 FROM laws WHERE title = 'Affordable Care Act'
UNION ALL SELECT id, 2 FROM laws WHERE title = 'Affordable Care Act'
UNION ALL SELECT id, 3 FROM laws WHERE title = 'Affordable Care Act'
UNION ALL SELECT id, 1 FROM laws WHERE title = 'Americans with Disabilities Act'
UNION ALL SELECT id, 2 FROM laws WHERE title = 'Americans with Disabilities Act'
UNION ALL SELECT id, 1 FROM laws WHERE title = 'Human Rights Act 1998'
UNION ALL SELECT id, 2 FROM laws WHERE title = 'Human Rights Act 1998'
UNION ALL SELECT id, 1 FROM laws WHERE title = 'Data Protection Act 2018'
UNION ALL SELECT id, 1 FROM laws WHERE title = 'Equality Act 2010'
UNION ALL SELECT id, 2 FROM laws WHERE title = 'Equality Act 2010'
UNION ALL SELECT id, 1 FROM laws WHERE title = 'Health Insurance Portability and Accountability Act'
UNION ALL SELECT id, 1 FROM laws WHERE title = 'Dodd-Frank Wall Street Reform and Consumer Protection Act'
UNION ALL SELECT id, 1 FROM laws WHERE title = 'Privacy Act'
UNION ALL SELECT id, 1 FROM laws WHERE title = 'Freedom of Information Act'
UNION ALL SELECT id, 1 FROM laws WHERE title = 'USA PATRIOT Act';

-- ─────────────────────────────────────────────
-- ARTICLE VERSIONS
-- ─────────────────────────────────────────────
INSERT INTO article_versions (article_id, version, content)
SELECT a.id, 1, CASE
  WHEN l.title = 'Civil Rights Act' AND a.article_number = 1 THEN
    'Section 1. All persons within the jurisdiction of the United States shall have the same right in every State and Territory to make and enforce contracts, to sue, be parties, give evidence, and to the full and equal benefit of all laws and proceedings for the security of persons and property as is enjoyed by white citizens.'
  WHEN l.title = 'Civil Rights Act' AND a.article_number = 2 THEN
    'Section 2. It shall be unlawful to deny any person access to a place of public accommodation on account of race, color, religion, or national origin. Discrimination in public facilities is hereby prohibited across all states and territories.'
  WHEN l.title = 'Civil Rights Act' AND a.article_number = 3 THEN
    'Section 3. No person in the United States shall, on the ground of race, color, or national origin, be excluded from participation in, be denied the benefits of, or be subjected to discrimination under any program or activity receiving Federal financial assistance.'
  WHEN l.title = 'Clean Air Act' AND a.article_number = 1 THEN
    'Section 101. The purpose of this Act is to protect and enhance the quality of the Nation''s air resources so as to promote the public health and welfare and the productive capacity of its population.'
  WHEN l.title = 'Clean Air Act' AND a.article_number = 2 THEN
    'Section 109. The Administrator shall publish proposed regulations prescribing a national primary ambient air quality standard and a national secondary ambient air quality standard for each air pollutant for which criteria have been issued.'
  WHEN l.title = 'Affordable Care Act' AND a.article_number = 1 THEN
    'Section 1001. The purpose of this title is to provide affordable, quality health care for all Americans and reduce the growth in health care spending. No group health plan or health insurance issuer may impose lifetime limits on the dollar value of benefits for any participant or beneficiary.'
  WHEN l.title = 'Affordable Care Act' AND a.article_number = 2 THEN
    'Section 1201. A health insurance issuer offering group or individual health insurance coverage may not impose any preexisting condition exclusion with respect to such plan or coverage.'
  WHEN l.title = 'Affordable Care Act' AND a.article_number = 3 THEN
    'Section 1311. Each State shall, not later than January 1, 2014, establish an American Health Benefit Exchange for the State through which qualified individuals and qualified employers may purchase qualified health plans.'
  WHEN l.title = 'Americans with Disabilities Act' AND a.article_number = 1 THEN
    'Title I. No covered entity shall discriminate against a qualified individual on the basis of disability in regard to job application procedures, the hiring, advancement, or discharge of employees, employee compensation, job training, and other terms, conditions, and privileges of employment.'
  WHEN l.title = 'Americans with Disabilities Act' AND a.article_number = 2 THEN
    'Title II. No qualified individual with a disability shall, by reason of such disability, be excluded from participation in or be denied the benefits of the services, programs, or activities of a public entity, or be subjected to discrimination by any such entity.'
  WHEN l.title = 'Human Rights Act 1998' AND a.article_number = 1 THEN
    'Section 1. In this Act, the Convention rights means the rights and fundamental freedoms set out in Articles 2 to 12 and 14 of the Convention, Articles 1 to 3 of the First Protocol, and Article 1 of the Thirteenth Protocol, as read with Articles 16 to 18 of the Convention.'
  WHEN l.title = 'Human Rights Act 1998' AND a.article_number = 2 THEN
    'Section 3. So far as it is possible to do so, primary legislation and subordinate legislation must be read and given effect in a way which is compatible with the Convention rights. This section applies to primary legislation and subordinate legislation whenever enacted.'
  WHEN l.title = 'Data Protection Act 2018' AND a.article_number = 1 THEN
    'Section 1. This Act makes provision for the regulation of the processing of information relating to individuals, including the implementation in the United Kingdom of the GDPR. It extends the data protection regime to areas outside the scope of EU law, including national security and defence.'
  WHEN l.title = 'Equality Act 2010' AND a.article_number = 1 THEN
    'Section 4. The following characteristics are protected characteristics: age, disability, gender reassignment, marriage and civil partnership, pregnancy and maternity, race, religion or belief, sex, sexual orientation.'
  WHEN l.title = 'Equality Act 2010' AND a.article_number = 2 THEN
    'Section 39. An employer must not discriminate against a person in the arrangements the employer makes for deciding to whom to offer employment, as to the terms on which it offers employment, or by not offering employment. An employer must not victimise a job applicant.'
  WHEN l.title = 'Health Insurance Portability and Accountability Act' AND a.article_number = 1 THEN
    'Section 261. The Secretary of Health and Human Services shall adopt standards for transactions and data elements for financial and administrative transactions to enable health information to be exchanged electronically. Security standards shall ensure the integrity and confidentiality of health information.'
  WHEN l.title = 'Dodd-Frank Wall Street Reform and Consumer Protection Act' AND a.article_number = 1 THEN
    'Section 1. The purpose of this Act is to promote the financial stability of the United States by improving accountability and transparency in the financial system, to end too big to fail, to protect the American taxpayer by ending bailouts, and to protect consumers from abusive financial services practices.'
  WHEN l.title = 'Privacy Act' AND a.article_number = 1 THEN
    'Section 1. No agency shall disclose any record which is contained in a system of records by any means of communication to any person, or to another agency, except pursuant to a written request by, or with the prior written consent of, the individual to whom the record pertains.'
  WHEN l.title = 'Freedom of Information Act' AND a.article_number = 1 THEN
    'Section 1. Each agency shall make available to the public information about its organization, functions, rules and final opinions made in the adjudication of cases. Any person has the right to request access to federal agency records or information.'
  WHEN l.title = 'USA PATRIOT Act' AND a.article_number = 1 THEN
    'Section 206. The Foreign Intelligence Surveillance Court may grant orders authorizing roving surveillance that follows a target rather than being tied to a specific telephone line or computer. This provision allows intelligence agencies to monitor multiple communication devices used by a single suspect.'
  ELSE 'Article ' || a.article_number || ' of ' || l.title || ': provisions of this article shall apply to all relevant parties within the jurisdiction as defined by the parent legislation.'
END
FROM articles a
JOIN laws l ON l.id = a.law_id;

-- versiunea 2 pentru câteva articole cheie (history)
INSERT INTO article_versions (article_id, version, content)
SELECT a.id, 2,
  'Amended version of Article ' || a.article_number || ': ' ||
  av.content || ' [Amended to include updated enforcement mechanisms and expanded definitions as per the 2003 revision.]'
FROM articles a
JOIN laws l ON l.id = a.law_id
JOIN article_versions av ON av.article_id = a.id AND av.version = 1
WHERE l.title IN ('Civil Rights Act', 'Clean Air Act', 'Affordable Care Act');

-- ─────────────────────────────────────────────
-- AMENDMENTS
-- ─────────────────────────────────────────────
INSERT INTO amendments (article_id, amendment_text, amendment_date, approved)
SELECT a.id, am_text, am_date::date, approved
FROM articles a
JOIN laws l ON l.id = a.law_id
JOIN (VALUES
  ('Civil Rights Act',           1, 'Extended to cover sex-based discrimination in federally assisted education programs following Title IX guidance.',              '1972-06-23', true),
  ('Civil Rights Act',           2, 'Scope expanded to explicitly include pregnancy-related conditions as a protected characteristic under employment law.',        '1978-10-31', true),
  ('Civil Rights Act',           3, 'Clarification added regarding the applicability to digital platforms and online service providers.',                           '2021-03-15', false),
  ('Clean Air Act',              1, 'Amended to include greenhouse gas emissions as regulated air pollutants following Massachusetts v. EPA Supreme Court ruling.',  '2009-04-17', true),
  ('Clean Air Act',              2, 'Updated emission standards to reflect latest scientific consensus on particulate matter and nitrogen oxide thresholds.',        '2015-09-12', true),
  ('Affordable Care Act',        1, 'Individual mandate tax penalty reduced to zero dollars effective 2019.',                                                        '2017-12-22', true),
  ('Affordable Care Act',        2, 'Expanded Medicaid eligibility criteria to cover individuals up to 138 percent of the federal poverty level.',                  '2012-06-28', true),
  ('Affordable Care Act',        3, 'Clarification of essential health benefits to include mental health and substance use disorder services on equal footing.',     '2020-01-15', false),
  ('Americans with Disabilities Act', 1, 'ADA Amendments Act: Broadened the definition of disability to include episodic conditions and conditions in remission.',  '2008-09-25', true),
  ('Americans with Disabilities Act', 2, 'Web accessibility standards incorporated by reference to WCAG 2.1 Level AA for federal government websites.',             '2022-03-18', false),
  ('Human Rights Act 1998',      1, 'Interpretation updated following Supreme Court ruling on the extraterritorial application of Convention rights.',              '2007-06-13', true),
  ('Data Protection Act 2018',   1, 'Updated to reflect post-Brexit divergence from EU GDPR while maintaining adequacy standards for international data transfers.', '2021-01-01', true),
  ('Equality Act 2010',          1, 'Guidance issued clarifying that gender critical beliefs constitute a philosophical belief protected under the Act.',            '2021-06-10', false),
  ('Equality Act 2010',          2, 'Pay gap reporting obligations extended to organisations with 250 or more employees.',                                           '2017-04-05', true),
  ('USA PATRIOT Act',            1, 'Section 215 bulk telephone metadata collection programme ruled unlawful by Second Circuit Court of Appeals.',                  '2015-05-07', true)
) AS t(law_title, art_num, am_text, am_date, approved)
ON l.title = t.law_title AND a.article_number = t.art_num;

-- ─────────────────────────────────────────────
-- ARTICLE REFERENCES (cross-references între legi)
-- ─────────────────────────────────────────────
INSERT INTO article_references (from_article, to_article)
SELECT a1.id, a2.id
FROM articles a1
JOIN laws l1 ON l1.id = a1.law_id
JOIN articles a2
JOIN laws l2 ON l2.id = a2.law_id
ON (l1.title, a1.article_number, l2.title, a2.article_number) IN (
  ('Affordable Care Act',              2, 'Health Insurance Portability and Accountability Act', 1),
  ('Americans with Disabilities Act',  1, 'Civil Rights Act',                                   1),
  ('Americans with Disabilities Act',  2, 'Civil Rights Act',                                   2),
  ('Equality Act 2010',                1, 'Human Rights Act 1998',                              1),
  ('Equality Act 2010',                2, 'Human Rights Act 1998',                              2),
  ('Data Protection Act 2018',         1, 'Human Rights Act 1998',                              1),
  ('Dodd-Frank Wall Street Reform and Consumer Protection Act', 1, 'Freedom of Information Act', 1),
  ('USA PATRIOT Act',                  1, 'Privacy Act',                                        1)
);

-- ─────────────────────────────────────────────
-- AUDIT LOG
-- ─────────────────────────────────────────────
INSERT INTO audit_log (entity_type, entity_id, action, payload)
SELECT 'LAW', l.id, 'CREATE', jsonb_build_object('title', l.title, 'status', l.status)
FROM laws l;

INSERT INTO audit_log (entity_type, entity_id, action, payload)
SELECT 'LAW', l.id, 'UPDATE', jsonb_build_object('title', l.title, 'change', 'status updated')
FROM laws l
WHERE l.title IN ('No Child Left Behind Act', 'USA PATRIOT Act');