from io import BytesIO
import requests
from PIL import Image, ImageFont, ImageDraw

PADDING = 10

def parse_json_to_list(data):
    """
    This function takes the raw json data from the API call and returns the relavent feilds as a list.

    :return: A list such that index 0 is the image url, index 1 is the title, index 2 is the description
    """

    required_fields = ["url", "title", "explanation",]

    if not all(field in data for field in required_fields):
        raise AttributeError("Invalid data returned by the API!")

    return [data[field] for field in required_fields]

def get_wrapped_text(text, font, line_length):
    """
    This wraps text if it will exceed one line.
    This is stolen from stack overflow. I really didnt want to have to implement this.
    https://stackoverflow.com/a/67203353
    """
    
    lines = ['']
    for word in text.split():
        line = f'{lines[-1]} {word}'.strip()
        if font.getlength(line) <= line_length:
            lines[-1] = line
        else:
            lines.append(word)

    return '\n'.join(lines)

def recalulate_width_height(image, description, width, height):
    """
    This function calculates the new diemensions of all the elements to be placed on the sheet.
    """

    scale = min(float(width-10) / float(image.size[0]), float(height - 10) / float(image.size[1]))

    image_width, image_height = int(image.size[0] * scale), int(image.size[1] * scale)

    width, height = image_width + PADDING * 3, image_height + PADDING

    font = ImageFont.load_default(20)

    height += 20 + PADDING

    font = ImageFont.load_default(14)

    wrappedDescription = get_wrapped_text(description, font, width - 20)

    height += 20 * (wrappedDescription.count("\n") + 1) + PADDING

    return image_width, image_height, width, height


def create_image_sheet(image, title, description, width, height):
    """
    This function generates a sheet with the the title, image, and description.

    It uses Pillow (another cool library you can use for your final project) to manipulate the image data.

    This code is *not* the best (we have a lot of magic numbers), but it effectily lays out essentally a baseball card for the image of the day.
    """

    image_width, image_height, width, height = recalulate_width_height(image, description, width, height)

    sheet = Image.new("RGB", (width, height), (15, 15, 15))

    drawer = ImageDraw.Draw(sheet)

    font = ImageFont.load_default(20)

    leftPlacement = (width-10) // 2 - font.getlength(title) // 2 + 10
    drawer.text((leftPlacement, 10), title, align="center", font=font, fill=(255, 255, 255))

    image = image.resize((image_width, image_height))
    sheet.paste(image, (width //2 - image_width//2, 55))

    font = ImageFont.load_default(14)

    drawer.multiline_text((10, 65 + image_height), get_wrapped_text(description, font, width - 20), align="center", font=font, fill=(200, 200, 200))

    return sheet


def get_image_of_the_day():
    """
    We will write this function together!

    This function will make a call to NASA's image of the day API and returns the data from the API call.
    """
    endpoint = "https://api.nasa.gov/planetary/apod" 
    api_key = "DEMO_KEY"

    res = requests.get(f"{endpoint}?api_key={api_key}")

    parsed = parse_json_to_list(res.json())

    return parsed

def download_image(image_url):
    """
    We will write this function together!

    This function will take the image URL returned by the NASA api, and download it.

    This is similar to some file IO that you have already down but it is instead grabbing the image file file from the interest.
    
    Finally, the raw response should be returned

    """

    res = requests.get(image_url)

    return BytesIO(res.content)

if __name__ == "__main__":
    res = get_image_of_the_day()

    image_data = download_image(res[0])

    combined_image = create_image_sheet(Image.open(image_data), res[1], res[2], 500, 500)

    combined_image.save("output.png")
