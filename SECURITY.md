# Security Policy

`sql-to-dax` parses SQL text and emits DAX text. It does not execute SQL or DAX.

## Supported Versions

Security fixes are provided for the latest released minor version once releases begin.

## Reporting a Vulnerability

Use GitHub private vulnerability reporting once enabled for the repository. Until then, do not disclose suspected vulnerabilities publicly before maintainers have had a reasonable chance to respond.

## Security Notes

- Do not execute untrusted SQL or generated DAX as part of translation.
- Metadata files are parsed as TOML using the Python standard library.
- Unsupported or ambiguous constructs should raise `UnsupportedSqlError` rather than falling back to string rewriting.
