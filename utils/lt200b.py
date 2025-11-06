from bleak import BleakClient
from PIL import Image, ImageDraw, ImageFont

def create_text_image(text, font_path, font_size):
    if font_path:
        font = ImageFont.truetype(font_path, font_size)
    else:
        font = ImageFont.load_default(font_size)

    text_width, text_height = textsize(text, font)

    img_width = int(text_width)
    img_height = int(text_height)

    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)

    draw.multiline_text((0, img_height / 2), text, font=font, fill="black", anchor="lm") # align middle left anchored in the middle

    return img

def textsize(text, font):
    im = Image.new(mode="P", size=(0, 0))
    draw = ImageDraw.Draw(im)
    _, _, width, height = draw.textbbox((0, 0), text=text, font=font)
    return width, height

async def print_image(address, job):
    async with BleakClient(address) as client:
        # unsure if every device has the same uuid, so we search for it
        for service in client.services:
            first, second, _, _, _ = service.uuid.split('-')
            if first == 'be3dd650':
                uuid = second
                break

        for chunk in job:
            await client.write_gatt_char(f'be3dd651-{uuid}-42f1-99c1-f0f749dd0678', bytearray(chunk))
