"""
Deterministic step bypasses — skips LLM entirely for known patterns.

Credential fill → fill bypass
  Format: "Mengisi/Isi Username|Email|Password → <value>"
  Returns (field_type, value); runner looks up selector from live elements.
  Falls back to LLM if no matching element found on the page.
  Examples:
    "Mengisi Username → admin@mail.com"  → ("username", "admin@mail.com")
    "Mengisi Password → secret"          → ("password", "secret")
    "Isi Email → user@example.com"       → ("email", "user@example.com")

VALID: → assert_text bypass
  Format: VALID: <context> → <expected_text>
  - expected = text AFTER "→"; if no "→", entire text after "VALID:"
  Examples:
    "VALID: Data Ditemukan → Annual Leave"  → expected="Annual Leave"
    "VALID: halaman berhasil dimuat"        → expected="halaman berhasil dimuat"

Verifikasi muncul: / Validasi muncul: → assert_toast bypass
  Format: "Verifikasi muncul: <text>" | "Validasi muncul: <text>"
  - expected_text = everything after the prefix (used as substring match in toast)
  - Bypasses LLM entirely; assert_toast polls the page immediately (no Ollama delay)
  Examples:
    "Verifikasi muncul: User berhasil dibuat"  → expected_text="User berhasil dibuat"
    "Validasi muncul: Data berhasil disimpan"  → expected_text="Data berhasil disimpan"

Halaman X / Menampilkan Halaman X → assert_url bypass
  Steps with a URL in the description are navigate steps, not assertions — excluded.
  Examples:
    "Halaman Dashboard"               → ("Dashboard", "dashboard")
    "Menampilkan Halaman My Request"  → ("My Request", "my-request")
    "Menampilkan Halaman Login https://..." → None  (navigate, not assertion)
"""

import re


def extract_credential_fill(step_description: str):
    """
    Returns (field_type, value) if step is a credential fill, else None.

    field_type: "username" | "email" | "password"
    value: the text to fill into the field

    Covered patterns (case-insensitive, separator → or -> or :):
      "Mengisi Username → value"
      "Mengisi Password → value"
      "Mengisi Email → value"
      "Isi Username → value"
      "Isi Password → value"
      "Isi Email → value"
    """
    s = step_description.strip()
    m = re.match(
        r'^(?:Mengisi|Isi)\s+(Username|Password|Email)\s*(?:→|->|:)\s*(.+)$',
        s, re.IGNORECASE
    )
    if m:
        field_type = m.group(1).lower()
        value = m.group(2).strip()
        return (field_type, value)
    return None


def extract_valid_assertion(step_description: str):
    """
    Returns (selector, expected_text) if step starts with VALID:, else None.
    selector is always "//body" (assert anywhere on the page).
    expected_text is the substring after "→" if present, else all text after "VALID:".
    """
    m = re.match(r"^VALID:\s*(.+)", step_description.strip(), re.IGNORECASE)
    if not m:
        return None
    text = m.group(1).strip()
    # Support both Unicode arrow → (U+2192) and ASCII arrow ->
    if "→" in text:
        expected = text.split("→", 1)[1].strip()
    elif "->" in text:
        expected = text.split("->", 1)[1].strip()
    else:
        expected = text
    return ("//body", expected)


def extract_toast_assertion(step_description: str):
    """
    Returns expected_text if step is a toast/notification verification, else None.

    Covered patterns (case-insensitive):
      "Verifikasi muncul: <text>"
      "Validasi muncul: <text>"

    The returned text is used as a substring match in assert_toast (contains check,
    case-insensitive), so passing a long sentence is fine — partial match works.
    """
    s = step_description.strip()
    m = re.match(r"^(?:Verifikasi|Validasi)\s+muncul\s*[:\s]\s*(.+)", s, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return None


def extract_page_assertion(step_description: str):
    """
    Returns (page_name, url_keyword) if step asserts "we are on page X", else None.

    Covered patterns (case-insensitive):
      "Halaman <Name>"
      "Menampilkan Halaman <Name>"

    Steps that contain a URL (e.g. "Menampilkan Halaman Login https://...") are
    NAVIGATE descriptions, not assertions — they return None so the LLM handles them.

    url_keyword = page_name lowercased with spaces replaced by hyphens, for use
    with assert_url (e.g. "My Request" → "my-request" to match /my-request in URL).

    Examples:
      "Halaman Dashboard"                            → ("Dashboard", "dashboard")
      "Menampilkan Halaman My Request"               → ("My Request", "my-request")
      "Menampilkan Halaman Login https://..."        → None
      "Klik Menu: Request Pada Sidebar"              → None
    """
    s = step_description.strip()
    if re.search(r'https?://', s):
        return None
    m = re.match(r'^(?:Menampilkan\s+)?Halaman\s+(.+)$', s, re.IGNORECASE)
    if m:
        page_name = m.group(1).strip()
        url_keyword = page_name.lower().replace(' ', '-')
        return (page_name, url_keyword)
    return None
