# tabwatch

> Browser extension backend that tracks and reports time spent per domain with weekly digest emails.

## Installation

```bash
pip install tabwatch
```

Or install from source:

```bash
git clone https://github.com/yourname/tabwatch.git && cd tabwatch && pip install -e .
```

## Usage

Start the local backend server:

```bash
tabwatch serve --port 8080
```

The browser extension connects to the server and logs tab activity. Browsing data is aggregated per domain and stored locally.

Configure your weekly digest email in `config.yaml`:

```yaml
digest:
  email: you@example.com
  schedule: "every monday at 08:00"
  smtp_host: smtp.gmail.com
```

Then run the scheduler alongside the server:

```bash
tabwatch serve &
tabwatch scheduler start
```

You can also query your stats directly from the CLI:

```bash
tabwatch report --last 7d
# Domain              Time Spent
# github.com          4h 32m
# news.ycombinator.com 1h 14m
# youtube.com         0h 47m
```

## Configuration

| Key | Default | Description |
|-----|---------|-------------|
| `server.port` | `8080` | Port for the backend server |
| `digest.schedule` | `weekly` | Frequency of email digests |
| `storage.path` | `~/.tabwatch/db` | Local database path |

## License

MIT © [yourname](https://github.com/yourname)