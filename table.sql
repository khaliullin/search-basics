CREATE TABLE students (
  id SERIAL PRIMARY KEY,
  name VARCHAR(32),
  surname VARCHAR(32),
  mygroup VARCHAR(32)
);

CREATE TABLE articles (
  id SERIAL PRIMARY KEY,
  title VARCHAR(256),
  keywords VARCHAR(256),
  content TEXT,
  url VARCHAR(128),
  student_id INT REFERENCES students(id)
);
