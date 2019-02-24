CREATE TABLE words_porter (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4 (),
  term varchar(64),
  articles_id  uuid
);

CREATE TABLE  words_mystem (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4 (),
  term varchar(64),
  articles_id uuid
);
