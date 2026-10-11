# codex-skills

`skills` — a small CLI for scaffolding, validating, and cataloguing agent
skills (Codex, Claude, opencode). One format, one validator, no lock-in.

A skill is a directory with a `SKILL.md` whose frontmatter carries at least
`name` and `description`. That's the whole contract.

## Install

```sh
python3 -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
```

## Usage

```sh
skills new my-skill            # scaffold a new skill directory
skills list                    # catalog all skills under the current tree
skills validate                # validate every SKILL.md frontmatter
skills doctor                  # check the local environment for optional features
```

## Development

```sh
make test
```

`skills doctor` is informational: it checks whether a user session bus is
reachable (used by `skills watch` for in-place reload hints) and reports
which optional features are available. It should be run from a normal login
shell.

## License

MIT