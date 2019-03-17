CREATE TABLE article_term_idf (
  article_id uuid REFERENCES articles (id),
  term_id uuid REFERENCES terms_list (term_id),
  idf double precision
);

ALTER TABLE article_term ADD UNIQUE (article_id, term_id);