import os
import nest_asyncio, asyncio
from telethon import TelegramClient

nest_asyncio.apply()

# Identifiants API chargés depuis Render (Environment Variables)
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
phone = os.getenv("PHONE")
target_channel = int(os.getenv("TARGET_CHANNEL"))

# Session Telethon
client = TelegramClient("session_betmines_vip", api_id, api_hash)

def format_vip_message(text):
    lines = text.split("\n")
    championnat = ""
    minute_equipes = ""
    prediction = ""
    cotes = []
    stats = []

    for line in lines:
        line = line.strip()
        if "🏆" in line:
            championnat = line.replace("🏆", "").replace("*", "").strip()
        elif "🆚" in line or "🟧" in line:
            minute_equipes = line.replace("*", "").strip()
        elif "Résultat souhaité" in line or "Prédiction VIP" in line:
            prediction = line.replace("Résultat souhaité", "").replace("Prédiction VIP", "").replace("🎯", "").strip()
        elif "Pre-Match Odd" in line and "1X2" not in line:
            parts = line.split(":")
            if len(parts) == 2:
                label, value = parts
                cotes.append(f"{label.strip()}: **{value.strip()}**")
        elif "Live Odd bet365" in line:
            parts = line.split(":")
            if len(parts) == 2:
                label, value = parts
                cotes.append(f"{label.strip()}: **{value.strip()}**")
        elif "Possession" in line:
            stats.append(f"Possession: **{line.split(':')[1].strip()}**")
        elif any(x in line for x in ["Buts", "Corners", "Tirs cadrés", "Tirs non cadrés"]):
            if "Tirs au but" not in line:  # supprimer tirs au but
                parts = line.split(":")
                if len(parts) == 2:
                    label, value = parts
                    stats.append(f"{label.strip()}: **{value.strip()}**")

    # Format Markdown
    msg = "🚨 **ALERTE VIP EN DIRECT** 🚨\n\n"
    msg += f"🏆 **{championnat}**\n"
    msg += f"⚽️ {minute_equipes}\n\n"
    msg += f"🎯 **Prédiction VIP** : **{prediction}**\n\n"

    if cotes:
        msg += "💰 Cotes principales\n"
        for c in cotes:
            msg += f"{c}\n"
        msg += "\n"

    if stats:
        msg += "📌 Statistiques clés\n"
        for s in stats:
            msg += f"{s}\n"

    msg += "\n💡 *Conseil VIP* : Misez toujours entre **7 à 10%** de votre capital."
    return msg

async def main():
    await client.start(phone)
    print("✅ Connecté")

    # Message de test au démarrage
    await client.send_message(target_channel, "✅ Bot démarré et connecté avec succès !")
    print("✅ Message de test envoyé")

    betmines_entity = await client.get_entity("@BetMines_live_bot")
    last_id = None

    while True:
        # Vérifie les derniers messages toutes les 20 secondes
        messages = await client.get_messages(betmines_entity, limit=1)
        if messages:
            msg = messages[0]
            if msg.id != last_id and msg.text and msg.text.startswith("💎  Un but dans le match"):
                formatted = format_vip_message(msg.text)
                await client.send_message(target_channel, formatted, parse_mode="Markdown")
                print("✅ Nouveau message VIP envoyé")
                last_id = msg.id

        await asyncio.sleep(20)

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
