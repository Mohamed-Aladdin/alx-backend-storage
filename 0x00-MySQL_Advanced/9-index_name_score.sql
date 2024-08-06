-- Creates a table with unique users.
CREATE INDEX idx_name_first_score ON names(name(1), score);
