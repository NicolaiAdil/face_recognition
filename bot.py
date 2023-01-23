from discord_webhook import DiscordWebhook, DiscordEmbed
from confidential import TOKEN, WEBHOOK_URL
from datetime import datetime

def send_image(image: str, number: int) -> None:
    webhook = DiscordWebhook(url=WEBHOOK_URL)

    with open("unknown.jpg", "rb") as f:
        webhook.add_file(file=f.read(), filename='unknown.jpg')

    embed = DiscordEmbed(title='Intruder', description=f'{number} intruder(s) spotted {datetime.now()}', color='03b2f8')
    webhook.add_embed(embed)


    response = webhook.execute()