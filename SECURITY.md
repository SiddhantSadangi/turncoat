# Security

## Reporting a vulnerability

If you believe you’ve found a security issue, please **do not** open a public issue.

- **Email** the maintainers (or open a private security advisory on GitHub if the repo supports it) with a clear description and steps to reproduce.
- Allow time for a fix before any public disclosure.

## API keys and secrets

- Never commit `.streamlit/secrets.toml` or any file containing API keys.
- Keys entered in the Turncoat sidebar are stored only in Streamlit session state (in memory) and are not persisted by Turncoat.
