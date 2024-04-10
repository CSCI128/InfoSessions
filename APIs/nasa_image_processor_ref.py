from io import BytesIO
import requests
from PIL import Image, ImageFont, ImageDraw

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

def create_image_sheet(image, title, description, width, height):
    # Compute the scale factor to preseve aspect ratio
    scale = min(float(width-10) / float(image.size[0]), float(height - 10) / float(image.size[1]))

    new_width, new_height = int(image.size[0] * scale), int(image.size[1] * scale)

    width, height = int(new_width * 1.5), int(new_height * 1.5)

    sheet = Image.new("RGB", (width, height), (5, 5, 5))
    drawer = ImageDraw.Draw(sheet)

    image = image.resize((new_width, new_height))

    font = ImageFont.load_default(27)

    drawer.multiline_text((10, 10), get_wrapped_text(title, font, width - 20), align="center", font=font, fill=(255, 255, 255))

    sheet.paste(image, (width//2 - new_width//2, 55))

    font = ImageFont.load_default(14)

    drawer.multiline_text((10, 65 + new_height), get_wrapped_text(description, font, width - 20), align="center", font=font, fill=(200, 200, 200))

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
