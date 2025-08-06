from bleak import BleakClient
from PIL import Image, ImageDraw, ImageFont

def create_text_image(text, font_path, font_size):
    if font_path:
        font = ImageFont.truetype(font_path, font_size)
    else:
        font = ImageFont.load_default(font_size)

    with Image.new("RGB", (1, 1), "white") as temp_img:
        temp_draw = ImageDraw.Draw(temp_img)
        text_width = temp_draw.textlength(text, font=font)

    img_width = int(text_width)
    img_height = 64

    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)

    draw.text((0, 32), text, font=font, fill="black", anchor="lm")

    return img


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
