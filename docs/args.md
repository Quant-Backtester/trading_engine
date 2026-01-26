# useful command line arguments


### Trading Logic

#### Cash
--cash `int`

this set the portfolio cash
example:
```bash
python main.py --cash 100000
```

#### DataSource

- `db`
  - `--host`  the host of the database, by default it is localhost
  - `--port` the port of the database, by default it is `5432` (the default for SQL)

example:
```bash
python main.py db --host localhost --port 5432
```

- `csv`
  - `path` (the path of the csv file)

example:
```bash
python main.py csv --path ./data/TSLA.csv
```


### Extra

#### Memory Profiler (under development)
- this is used to trace the memory allocation on the heap.
- To enable, run:
```bash
python main.py --profile_memory
```