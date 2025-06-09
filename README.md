# Wallet Generator Bot

Telegram bot untuk menghasilkan wallet Ethereum, Bitcoin Taproot, dan Solana dari seed phrase BIP39. Termasuk sistem rate-limit 1 jam, transparansi keamanan, dan kirim file JSON.

## Fitur
- Pilih 12 atau 24 kata
- Generate alamat ETH, BTC (Taproot), dan SOL
- File backup .json langsung dikirim & dihapus
- Tidak ada penyimpanan data
- Rate limit 1 jam per pengguna

## Jalankan
pip install -r requirements.txt
python wallet_bot.py

## Token
Masukkan token bot di variabel `API_TOKEN` di dalam script.

aiogram==2.25
bip-utils
eth-keys
eth-utils
