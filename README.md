# String - Advanced Modular Hosting Tool

String is a professional-grade terminal hosting tool with built-in DNS, PHP support, and an advanced security suite.

## New Features (Modular Refactor)

- **Modular Architecture**: Core logic split into `dff/` module for better performance and organization.
- **PHP Integration**: Native support for `.php` files (requires PHP CLI on system).
- **Security Suite**: 
    - **Early Alert System**: Real-time detection of suspicious URL patterns (e.g., `.env`, `wp-admin`).
    - **DDoS Protection**: Per-IP rate limiting and request throttling enabled by default.
    - **DNS Traffic Handling**: Precise resolution for custom domains and subdomains.
- **Enhanced Admin Panel**: Sleek new design on port `1947` with a dedicated Security Alert sidebar.
- **Client-side Security**: Automatic JS injection for integrity checks (see `static/js/security.js`).

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. (Optional) Ensure `php` is in your system path for PHP site support.

## Usage

```bash
python main.py --path /your/project --domains "site.local, business.pk"
```

- `--path`: Project folder (contains `index.html` or `index.php`).
- `--domains`: Comma-separated list of domains to catch.
- `--webport`: (Optional) Default is 443 (HTTPS).
- `--panelport`: (Optional) Default is 1947.
- `--https / --no-https`: Enable or disable HTTPS (Default: Enabled).

## Supported Domain Extensions

String supports **any** domain extension you specify. Popular examples include:
- **Local**: `.local`, `.test`, `.dev`, `.home`
- **International**: `.pk`, `.st`, `.com`, `.net`, `.org`
- **Custom**: `.string`, `.server`, `.hub`, `.web`

*Note: Any text following the dot is valid as long as it is mapped correctly.*

## Global Accessibility (Other Devices)

To make your site accessible to other devices on your WiFi:
1.  **Free Port 53**: Windows often blocks DNS port 53. Run this in an **Admin CMD**:
    ```bash
    net stop SharedAccess
    ```
2.  **Point DNS**: Set the DNS server of your phone/laptop to the **Local IP** shown in the String terminal.

## Structure

- `main.py`: Entry point.
- `dff/`:
    - `server.py`: PHP/Static web engine.
    - `dns.py`: DNS resolution engine.
    - `security.py`: Alarms & DDoS protection logic.
- `static/js/security.js`: Client integrity script.
- `templates/`: Admin panel UI.

## Troubleshooting

- **Permissions**: DNS (port 53) and Web (port 80) require Administrator/Sudo.
- **PHP**: If `.php` fails, verify `php -v` works in your terminal.
