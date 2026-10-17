# ShellInABox & transports — reference

Background for driving a web terminal with `ssh2web`. You rarely need the
protocol details (the client handles them), but they help when something behaves
oddly or you must recognize which kind of terminal you are facing.

## Recognizing the terminal type

`--transport auto` (default) fetches the landing page and picks a transport:

| terminal | wire protocol | ssh2web status |
|---|---|---|
| **ShellInABox** (Shell In A Box) | HTTP POST (AJAX terminal) | ✅ implemented, tested against the live product |
| **ttyd** / **gotty** | WebSocket | detected and reported clearly; **not driven yet** |

If `auto` sees a WebSocket-only terminal it says so instead of failing
obscurely — treat that as "wrong tool", not a bug. Do not force
`--transport shellinabox` against a WebSocket terminal.

## ShellInABox protocol, in one table

| step | request |
|---|---|
| new session | `POST /?` — `width=W&height=H&rooturl=<url>` → `{"session":…,"data":…}` |
| read output | `POST /?` — `width=W&height=H&session=<sid>` → same JSON |
| type keys | `POST /?` — `…&session=<sid>&keys=<hex>` (`"id\n"` → `69640a`) |

Two quirks the client handles for you:

- A key POST is answered with a plain HTML page titled `OK` (not JSON).
- A poll with no output **long-polls ~30 s** — an empty poll is normal and is
  **never** an error or a reason to retry aggressively.

## How a command is delimited

`ssh2web` types:

```sh
{ <your command> ; } 2>&1 ; echo __SSH2WEB_<nonce>__$?
```

The `{ … }` group keeps stdout/stderr interleaved in order; the marker + `$?`
carries the exit status. The first transcript line (prompt + echo of the typed
line) is dropped, ANSI escapes are stripped, and everything before the marker is
the command's output. This is why the remote exit code becomes ssh2web's own.

## Exit codes

| code | meaning |
|---|---|
| *n* | the remote command's exit status |
| 2 | bad configuration / cancelled password prompt |
| 3 | authentication failed |
| 4 | transport error (unreachable, protocol, session lost) |
| 124 | command timed out (no end-marker within the command timeout) |

## Useful flags

- `--transport {auto,shellinabox}` — default `auto`.
- `--json` — `{"stdout": …, "exit_code": …}` for chaining.
- `--resolve HOST:IP` — pin DNS (split-horizon / broken client resolver), like
  `curl --resolve`.
- `--insecure` — skip TLS verification; prefer `--cacert <bundle>`.
- `--rbash-escape` — break a restricted-shell `PATH` jail by overwriting a
  writable `PATH` entry (e.g. `~/bin/dig`). Intrusive and host-mutating —
  authorized targets only.
- `-i` interactive REPL · `--raw` no output cleaning · `--no-login` ·
  `--command-timeout` / `--login-timeout` · `--retries` · `-o FILE` · `-q`.

## Credentials & config

Precedence: **CLI flag > `SSH2WEB_*` env > config file**. Config file locations:
`./ssh2web.ini`, `~/.config/ssh2web/config.ini`, `/etc/ssh2web.ini`:

```ini
[ssh2web]
url = https://host/
user = alice
password = s3cret
insecure = true
transport = auto
```

Keep a password out of shell history: a `chmod 600` config file, a
`--password-file`, or the environment — not `-p` on the command line.

## Troubleshooting

- **Hangs then exits 124** — the end-marker never arrived: the command may be
  interactive or long-running; raise `--command-timeout`, or run it backgrounded.
- **Exit 3** — login failed: check credentials, `--no-login` only if the terminal
  drops you straight to a shell.
- **Exit 4 right away** — unreachable or not ShellInABox: verify the URL, try
  `--resolve`, confirm the transport with `auto`.
- **Garbled output** — try `--raw` to see the untouched transcript, or widen the
  terminal with the client's width/height (some tools wrap at the terminal size).
