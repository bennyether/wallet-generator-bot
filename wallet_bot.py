import json
import logging
import os
import time
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
from bip_utils import (
    Bip39MnemonicGenerator, Bip39SeedGenerator,
    Bip44, Bip44Coins, Bip44Changes,
    Bip86, Bip86Coins
)
from eth_keys import keys
from eth_utils import to_checksum_address

# ========== KONFIGURASI ==========
API_TOKEN = 'ISI_TOKEN_BOT_ANDA'  # <-- GANTI DENGAN TOKEN DARI @BotFather
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

cooldown_users = {}  # Simpan user yang sedang cooldown
COOLDOWN_SECONDS = 3600  # 1 jam

# ========== GENERATE WALLET ==========
def generate_wallets(word_count: int):
    mnemonic = Bip39MnemonicGenerator().FromWordsNumber(word_count)
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()

    eth_wallet = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
    eth_priv_key = keys.PrivateKey(eth_wallet.PrivateKey().Raw().ToBytes())
    eth_address = to_checksum_address(eth_priv_key.public_key.to_address())

    btc_wallet = Bip86.FromSeed(seed_bytes, Bip86Coins.BITCOIN).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
    btc_address = btc_wallet.PublicKey().ToAddress()

    sol_wallet = Bip44.FromSeed(seed_bytes, Bip44Coins.SOLANA).Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(0)
    sol_address = sol_wallet.PublicKey().ToAddress()

    return {
        "mnemonic": str(mnemonic),
        "word_count": word_count,
        "addresses": {
            "ethereum": eth_address,
            "bitcoin_taproot": btc_address,
            "solana": sol_address
        }
    }

# ========== /start COMMAND ==========
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    now = time.time()

    if user_id in cooldown_users:
        elapsed = now - cooldown_users[user_id]
        if elapsed < COOLDOWN_SECONDS:
            remaining = int(COOLDOWN_SECONDS - elapsed)
            minutes = remaining // 60
            seconds = remaining % 60
            return await message.answer(f"⏳ Tunggu {minutes}m {seconds}s sebelum generate wallet baru.")

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton("12"), KeyboardButton("24"))
    await message.answer("🔐 Pilih jumlah kata untuk seed phrase:", reply_markup=keyboard)

# ========== PILIHAN 12/24 ==========
@dp.message_handler(lambda msg: msg.text in ["12", "24"])
async def handle_choice(message: types.Message):
    user_id = message.from_user.id
    now = time.time()

    if user_id in cooldown_users:
        elapsed = now - cooldown_users[user_id]
        if elapsed < COOLDOWN_SECONDS:
            remaining = int(COOLDOWN_SECONDS - elapsed)
            minutes = remaining // 60
            seconds = remaining % 60
            return await message.answer(f"⏳ Kamu masih dalam cooldown: {minutes}m {seconds}s")

    word_count = int(message.text)
    result = generate_wallets(word_count)
    mnemonic = result["mnemonic"]
    addresses = result["addresses"]

    # Kirim hasil
    reply = (
        f"✅ <b>Seed Phrase</b> ({word_count} kata):\n<code>{mnemonic}</code>\n\n"
        f"🪙 <b>Ethereum</b>: <code>{addresses['ethereum']}</code>\n"
        f"₿ <b>Bitcoin Taproot</b>: <code>{addresses['bitcoin_taproot']}</code>\n"
        f"⚡ <b>Solana</b>: <code>{addresses['solana']}</code>\n\n"
        f"⚠️ <b>Simpan seed phrase ini dengan sangat aman!</b>"
    )
    await bot.send_message(message.chat.id, reply)

    # Kirim file JSON
    filename = f"wallet_backup_{user_id}.json"
    with open(filename, "w") as f:
        json.dump(result, f, indent=4)
    await bot.send_document(message.chat.id, InputFile(filename), caption="🗂 Backup wallet kamu")
    os.remove(filename)

    # Kirim pesan transparansi
    transparansi = (
        "🔒 <b>Transparansi & Keamanan</b>\n\n"
        "✅ Seed phrase dan wallet hanya dibuat saat kamu minta.\n"
        "✅ Tidak ada data yang disimpan di server.\n"
        "✅ Tidak ada database, pelacakan, atau logging.\n"
        "✅ File backup langsung dihapus setelah dikirim.\n\n"
        "📌 <b>Hanya kamu</b> yang bisa melihat seed phrase ini.\n"
        "🛡 Jangan pernah bagikan ke siapa pun, termasuk developer bot ini."
    )
    await message.answer(transparansi)

    # Kirim link GitHub repo
    github_info = (
        "📂 <b>Kode sumber bot ini tersedia di GitHub:</b>\n"
        "🔗 <a href='https://github.com/bennyether/wallet-generator-bot'>github.com/bennyether/wallet-generator-bot</a>\n\n"
        "Silakan cek, pelajari, atau kontribusi. Transparansi adalah prioritas kami. 💡"
    )
    await message.answer(github_info, disable_web_page_preview=True)

    # Simpan cooldown
    cooldown_users[user_id] = now

# ========== JALANKAN BOT ==========
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
