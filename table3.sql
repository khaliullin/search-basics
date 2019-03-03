CREATE TABLE terms_list (
  term_id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  term_text varchar(64) unique
);

CREATE TABLE article_term (
  article_id uuid REFERENCES articles (id),
  term_id uuid REFERENCES terms_list (term_id)
);

-- sorted index for term_text
CREATE index terms_list_index on terms_list (term_text);