from collimator import data
db = 'postgres://hopper@localhost:5432/hopper'
with data._connect(db) as conn:
    for count, in data._execute(conn, 'SELECT count(*) FROM samples WHERE cleave_result IS NOT NULL AND skip IS NULL'):
        print(f'skip IS NULL: {count}')
    for count, in data._execute(conn, "SELECT count(*) FROM samples WHERE cleave_result IS NOT NULL AND skip = ''"):
        print(f"skip IS '': {count}")
    for count, in data._execute(conn, "SELECT count(*) FROM samples WHERE cleave_result IS NOT NULL AND (skip IS NULL OR skip = '')"):
        print(f"total trainable: {count}")
