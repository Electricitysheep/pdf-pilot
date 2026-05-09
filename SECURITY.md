# Security Policy

## Supported Versions

| Version | Supported |
| --- | --- |
| 0.2.x | Yes |
| 0.1.x | No |

## Reporting a Vulnerability

If you discover a security vulnerability in pdf_pilot, please report it responsibly:

1. **Do NOT open a public issue** for security vulnerabilities
2. Email: [your-email@example.com](mailto:your-email@example.com)
3. Alternatively, use GitHub's [private vulnerability reporting](https://github.com/Electricitysheep/pdf-pilot/security/advisories/new)

We will respond within 48 hours and aim to release a fix within 7 days for confirmed vulnerabilities.

## Security Best Practices

When using pdf_pilot:

- **Never process untrusted PDFs** in environments with access to sensitive data
- **Use sandboxed environments** for processing unknown PDF sources
- **Keep dependencies updated** — run `pip install --upgrade pdf-pilot` regularly
- **Validate PDF sources** before processing in production pipelines
