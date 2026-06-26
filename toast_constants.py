"""
Toast text whitelist — fallback layer for when CSS class regex + generic
keyword matching (success/error) in tools.py's _CLASSIFY_JS / _ARM_JS both
return 'unknown' (e.g. toast has no "berhasil/sukses/error" wording at all,
like "Lokasi Tersimpan" or app-specific business copy).

This is layer 3 in the resolution order:
  1. CSS class regex      (tools.py _CLASSIFY_JS/_ARM_JS, in-browser)
  2. Generic OK/ERR regex (tools.py _CLASSIFY_JS/_ARM_JS, in-browser)
  3. Exact/substring whitelist below (Python, post-hoc upgrade of 'unknown')

Only used when type == 'unknown' coming back from JS. Never overrides a
class-based success/error verdict — class detection is more reliable than
text matching across languages/phrasing variants.
"""

# Toasts containing these phrases (case-insensitive substring) are treated
# as FAILURE even with no error-style CSS class and no generic ERR keyword.
TOAST_FAILURE_PHRASES = [
    "gagal mengunggah dokumen", "password salah", "kata sandi salah",
    "email tidak terdaftar", "akun tidak ditemukan", "email atau password salah",
    "sesi telah berakhir", "sesi anda habis", "format file tidak didukung",
    "ukuran file terlalu besar", "data gagal disimpan", "gagal menyimpan perubahan",
    "kode voucher tidak valid", "kupon kedaluwarsa", "stok habis",
    "produk tidak tersedia", "jumlah item melebihi batas stok",
    "koneksi internet terputus", "tidak ada koneksi jaringan", "akses ditolak",
    "saldo tidak cukup", "metode pembayaran ditolak", "kartu kredit tidak valid",
    "pembayaran gagal",
    "incorrect password", "wrong password", "email not registered",
    "user not found", "invalid email or password", "invalid credentials",
    "session expired", "your session has timed out",
    "unsupported file format", "file size too large", "failed to upload document",
    "failed to save data", "invalid voucher code", "coupon expired",
    "out of stock", "product unavailable", "quantity exceeds available stock",
    "internet connection lost", "no network connection", "payment failed",
    "insufficient funds", "payment method declined", "invalid credit card",
    "access denied", "unauthorized access", "invalid token",
]

# Toasts containing these phrases are treated as SUCCESS even with no
# success-style CSS class and no generic OK keyword (e.g. no literal
# "berhasil"/"sukses" in the copy).
TOAST_SUCCESS_PHRASES = [
    "dokumen berhasil terunggah", "data berhasil disimpan", "pendaftaran sukses",
    "item added to cart", "checkout sukses", "lokasi tersimpan",
    "pendaftaran berhasil", "akun berhasil dibuat", "login berhasil",
    "selamat datang kembali", "masuk sukses", "reset password berhasil",
    "profil berhasil diperbarui", "perubahan data akun disimpan",
    "file berhasil diunggah", "unggah dokumen sukses", "dokumen berhasil dihapus",
    "file berhasil dihapus", "unduhan dimulai", "ekspor data berhasil",
    "perubahan berhasil disimpan", "simpan data sukses", "data berhasil dihapus",
    "penghapusan sukses", "item berhasil dihapus", "alamat berhasil ditambahkan",
    "produk berhasil ditambahkan ke keranjang", "berhasil masuk keranjang",
    "pembayaran berhasil", "transaksi sukses", "pesanan berhasil dibuat",
    "kode promo berhasil digunakan", "diskon diterapkan",
    "registration successful", "account created successfully", "sign up success",
    "login successful", "welcome back", "sign in success",
    "password reset successful", "password reset link sent",
    "profile updated successfully", "account changes saved",
    "document uploaded successfully", "file uploaded successfully", "upload success",
    "document deleted successfully", "file deleted successfully", "download started",
    "data export successful", "data saved successfully", "changes saved successfully",
    "save success", "data deleted successfully", "delete success",
    "item removed successfully", "location saved", "address added successfully",
    "order placed successfully", "payment successful", "transaction success",
    "promo code applied successfully", "discount applied",
    # App-specific (OSS/licensing demo) — keep separate from generic list above
    # so it's obvious these are domain phrases, not generic UI copy.
    "terdaftar & nib terbit", "dokumen ukl-upl diproses & terbit",
    "retribusi dibayar", "pbg terbit", "terkirim ke verifikator",
    "fiktif positif", "sertifikat standar terbit", "hasil uji lab diunggah",
    "pb umku terbit", "dokumen amdal diproses & terbit", "permohonan izin terkirim", "Good Job!"
]
