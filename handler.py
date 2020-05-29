import csv
import boto3
from datetime import date
import io
import json
from math import ceil
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont
from botocore.vendored import requests


def render_and_upload_lastname_mug(event, context):
    def load_file_from_s3(*, bucket, key):
        s3_client = boto3.client("s3")
        buffer_file = io.BytesIO()
        s3_client.download_fileobj(bucket, key, buffer_file)
        # Why do I have to do this seek operation?
        # https://stackoverflow.com/a/58006156/1723469
        buffer_file.seek(0)
        return buffer_file

    def render_mug(event):
        def check_first_char_is_vowel(lastname):
            vowels = ["a", "e", "i", "o", "u"]
            return lastname[0].lower() in vowels

        def draw_lastname(lastname_to_write, img):
            draw = ImageDraw.Draw(img)
            INPUT_BUCKET = "giftsondemand-input"
            FONT_S3_KEY = "fonts/angelina.ttf"

            font_file = load_file_from_s3(bucket=INPUT_BUCKET, key=FONT_S3_KEY)
            font = ImageFont.truetype(font_file, 310)

            # Find starting x coordinate to center text
            text_width, text_height = draw.textsize(lastname_to_write, font)
            img_width, img_height = img.size
            starting_x = (img_width - text_width) / 2
            draw.text(
                xy=(starting_x, 1050),
                text=lastname_to_write,
                fill=(88, 89, 91, 255),
                font=font,
            )
            return img

        def transform_lastname(original_img):
            def solve_quadratic_coeffs(point_1, point_2, point_3):
                points = np.array([point_1, point_2, point_3])
                x = points[:, 0]
                y = points[:, 1]
                z = np.polyfit(x, y, 2)
                return z

            def plot_deflected_point(x, a, b, height):
                return int(a * x ** 2 + b * x + height)

            def plot_alpha_point(x, d, e, f):
                return d * x ** 2 + e * x + f

            original_pixel = original_img.load()

            # The new image will be tallest on the bottom and in
            # the middle of the line.  So new height should be the
            # original height plus the new y value at the bottom of
            # the old image.
            original_w = original_img.size[0]
            original_h = original_img.size[1]

            # Quadratic for deflection found by fitting 3 points
            mid_x = original_w / 2
            deflection = 0.075
            mid_y = original_h * deflection

            # Deflection eqn coeffs
            a, b, c = solve_quadratic_coeffs(
                point_1=(0, 0), point_2=(mid_x, mid_y), point_3=(original_w, 0)
            )
            new_h = int(ceil(plot_deflected_point(mid_x, a, b, original_h)))
            new_img = Image.new("RGBA", (original_w, new_h), (255, 255, 255, 0))

            # Alpha (opacity) eqn found by fitting 3 points
            d, e, f = solve_quadratic_coeffs(
                point_1=(0, 0.8), point_2=(original_w / 4, 0.9), point_3=(mid_x, 0.95)
            )

            for x in range(original_w):  # cols
                if x < mid_x:
                    alpha_value = int(ceil(plot_alpha_point(x, d, e, f) * 255))
                else:
                    reflected_x = 2 * mid_x - x
                    alpha_value = int(
                        ceil(plot_alpha_point(reflected_x, d, e, f) * 255)
                    )
                for y in range(original_h):  # rows
                    current_pixel = original_pixel[x, y]
                    if current_pixel != (255, 255, 255, 0) and current_pixel != (
                        0,
                        0,
                        0,
                        0,
                    ):  # noqa:E501
                        new_pixel = (
                            current_pixel[0],
                            current_pixel[1],
                            current_pixel[2],
                            alpha_value,
                        )
                        new_pixel_y = plot_deflected_point(x, a, b, y)
                        try:
                            new_img.putpixel((x, new_pixel_y), new_pixel)
                        except Exception as e:
                            print(e)
                            continue

            return new_img

        INPUT_BUCKET = event["input_bucket"]
        lastname = event["lastname"]

        TEMPLATE_IMG_KEYS = {
            "lastname_template_consonant": "imgs/mug_template_feminine_its_a_surname_thing.png",
            "lastname_template_vowel": "imgs/mug_template_feminine_its_a_surname_thing_vowel.png",
            "left_mug": "imgs/mug_left_large.png",
            "right_mug": "imgs/mug_right_large.png",
        }

        lastname_to_write = lastname["lastname"]
        if check_first_char_is_vowel(lastname_to_write):
            LASTNAME_TEMPLATE_IMG_KEY = TEMPLATE_IMG_KEYS["lastname_template_vowel"]
        else:
            LASTNAME_TEMPLATE_IMG_KEY = TEMPLATE_IMG_KEYS["lastname_template_consonant"]
        lastname_img_template_file = load_file_from_s3(
            bucket=INPUT_BUCKET, key=LASTNAME_TEMPLATE_IMG_KEY
        )
        template_img = Image.open(lastname_img_template_file)

        lastname_img = draw_lastname(lastname_to_write, template_img)
        transformed_img = transform_lastname(lastname_img)

        # Calculate the new size starting with final size.
        STARTING_W, STARTING_H = template_img.size
        FINAL_W = 1372
        lastname_resize_factor = FINAL_W / STARTING_W
        size = (
            int(ceil(STARTING_W * lastname_resize_factor)),
            int(ceil(STARTING_H * lastname_resize_factor)),
        )
        transformed_img = transformed_img.resize(size, Image.ANTIALIAS)

        # paste onto left_mug_img
        left_mug_file = load_file_from_s3(
            bucket=INPUT_BUCKET, key=TEMPLATE_IMG_KEYS["left_mug"]
        )
        left_mug_img = Image.open(left_mug_file)
        left_mug_img.paste(transformed_img, (600, 180), transformed_img)
        lastname["left_mug"] = left_mug_img

        # paste onto right_mug_img
        right_mug_file = load_file_from_s3(
            bucket=INPUT_BUCKET, key=TEMPLATE_IMG_KEYS["right_mug"]
        )
        right_mug_img = Image.open(right_mug_file)
        right_mug_img.paste(transformed_img, (-20, 180), transformed_img)
        lastname["right_mug"] = right_mug_img

        lastname_with_renders = lastname

        return lastname_with_renders

    def upload_mug_to_s3(lastname):
        today_str = str(date.today())
        images_to_upload_names = {
            "left_mug": lastname["left_mug"],
            "right_mug": lastname["right_mug"],
        }

        s3 = boto3.client("s3")

        BUCKET = event["output_bucket"]

        for img_name, pil_img in images_to_upload_names.items():
            in_mem_file = io.BytesIO()
            s3_img_path = f"{today_str}/{lastname['name']}_{img_name}.png"
            pil_img.save(in_mem_file, format="PNG")
            in_mem_file.seek(0)

            s3.put_object(
                Bucket=BUCKET,
                Key=s3_img_path,
                Body=in_mem_file,
                ContentType="image/png",
                ACL="public-read",
            )
            # Example finished AWS S3 URL
            # https://giftsondemand.s3.amazonaws.com/2020-01-07/10_r.png
            aws_url = f"https://{BUCKET}.s3.amazonaws.com/{s3_img_path}"
            lastname[f"{img_name}_url"] = aws_url
            lastname_with_mug_urls = lastname

        return lastname_with_mug_urls

    def create_bigcommerce_product(lastname):
        def check_first_char_is_vowel(lastname):
            vowels = ["a", "e", "i", "o", "u"]
            return lastname[0].lower() in vowels

        payload = {
            "name": f"{lastname['lastname']} Ladies/Women Coffee Mug Gift - It's a {lastname['lastname']} Thing. You Wouldn't Understand Coffee Mug",
            "price": "19.95",
            "categories": [25],
            "weight": 13,
            "type": "physical",
            "description": "<ul><li>High quality mug makes the perfect gift for everyone.</li><li>Printed on durable ceramic. The print will never fade no matter how many times it is washed.</li><li>Packaged, and shipped from the USA.</li><li>Dishwasher and Microwave safe.</li><li>Shipped in a custom made styrofoam package to ensure it arrives perfect. GUARANTEED.</ul>",
            "is_free_shipping": True,
            "warranty": "If you're unhappy with this product, just return it and we'll refund your money OR give you a replacement mug.  We'll pay the return shipping!",
            "meta_description": "Here's the meta description",
            "meta_keywords": [
                f"gifts for {lastname['lastname']} woman",
                f"gift for {lastname['lastname']} last name",
                f"coffee mug {lastname['lastname']}",
                f"coffee cup {lastname['lastname']}",
                f"gifts for {lastname['lastname']} surname",
                f"aunt {lastname['lastname']} gift",
                f"cousin {lastname['lastname']} gift",
                f"mom {lastname['lastname']} gift",
                f"grandma {lastname['lastname']} gift",
                f"niece {lastname['lastname']} gift",
                f"mother {lastname['lastname']} gift",
            ],
            "images": [
                {
                    "is_thumbnail": True,
                    "sort_order": 1,
                    "description": f"Left Mug - {lastname['lastname']} Ladies/Women Coffe Mug Gift - It's an {lastname['lastname']} Thing. You Wouldn't Understand Coffee Mug",
                    "image_url": lastname["left_mug_url"],
                },
                {
                    "is_thumbnail": False,
                    "sort_order": 2,
                    "description": f"Right Mug - {lastname['lastname']} Ladies/Women Coffe Mug Gift - It's an {lastname['lastname']} Thing. You Wouldn't Understand Coffee Mug",
                    "image_url": lastname["right_mug_url"],
                },
            ],
        }

        if check_first_char_is_vowel(lastname["lastname"]):
            payload["name"] = f"{lastname['lastname']} Ladies/Women Coffe Mug Gift - It's an {lastname['lastname']} Thing. You Wouldn't Understand Coffee Mug"

        BIGCOMMERCE_STORE_HASH = os.environ.get("BIGCOMMERCE_STORE_HASH", "")
        PRODUCT_CREATION_URL = f"https://api.bigcommerce.com/stores/{BIGCOMMERCE_STORE_HASH}/v3/catalog/products"
        headers = {
            "X-Auth-Token": os.environ.get("BIGCOMMERCE_ACCESS_TOKEN", ""),
            "X-Auth-Client": os.environ.get("BIGCOMMERCE_CLIENT_ID", ""),
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        print(f"Headers: {headers}")
        print(f"Payload: {payload}")
        print(f"Product Creation URL: {PRODUCT_CREATION_URL}")
        resp = requests.post(PRODUCT_CREATION_URL, json.dumps(payload), headers=headers)
        print(resp.content)

    rendered_lastname = render_mug(event)
    uploaded_lastname = upload_mug_to_s3(rendered_lastname)
    create_bigcommerce_product(uploaded_lastname)


def process_lastnames(event, context):
    def clean_whitespace(string):
        string_split = string.split()
        return " ".join(string_split)

    def validate_lastname(lastname):
        char_len = len(lastname) < 16
        not_blank = lastname != ""
        passed_both_tests = char_len and not_blank
        return passed_both_tests

    def format_lastname(idx, lastname):
        today = date.today().strftime("%Y%m%d")
        lastname["lastname"] = clean_whitespace(lastname["lastname"])
        lastname["niche"] = (
            clean_whitespace(lastname["niche"]).replace(" ", "-").lower()
        )
        # Add two because we're not counting headers or 0.
        lastname["row"] = idx + 2
        lastname["name"] = f"{lastname['niche']}_{lastname['row']}_{today}"
        return lastname

    # Expect event to be something like:
    # {
    #     "lastnames_csv_key": "input_csv/input.csv",
    #     "input_bucket": "giftsondemand-input",
    #     "output_bucket": "giftsondemand",
    # }

    lambda_client = boto3.client("lambda")
    s3_client = boto3.client("s3")
    INPUT_BUCKET = event["input_bucket"]
    LASTNAMES_CSV_KEY = event["lastnames_csv_key"]

    buffer_file = io.BytesIO()
    s3_client.download_fileobj(INPUT_BUCKET, LASTNAMES_CSV_KEY, buffer_file)
    # Quest: Why do I have to do this seek operation?
    # https://stackoverflow.com/a/58006156/1723469
    buffer_file.seek(0)
    text_wrapper = io.TextIOWrapper(buffer_file)
    reader = csv.DictReader(text_wrapper)
    lastnames = [
        format_lastname(idx, lastname)
        for idx, lastname in enumerate(reader)
        if validate_lastname(lastname)
    ]

    for lastname in lastnames:
        event_payload = {
            "lastname": lastname,
            "input_bucket": INPUT_BUCKET,
            "output_bucket": event["output_bucket"],
        }
        lambda_client.invoke(
            FunctionName="mugup-dev-render-and-upload-lastname-mug",
            InvocationType="Event",
            Payload=json.dumps(event_payload),
        )

    return json.dumps({"message": "Successfully started!"})


if __name__ == "__main__":
    test_lastnames = [
        {
            "lastname": "Abcdefghijklmno",
            "niche": "Aardvark",
            "item_name": "Novelty Mugs For Aardvark Animal Lovers - Coffee Cup Ideas For Pet Owners",
            "keywords": "Birthday, Anniversary, Wedding, Graduation, Holiday, Coworkers, Boss, Friends",
        },
        {
            "lastname": "Jefferson",
            "niche": "Abyssinian",
            "item_name": "Novelty Mugs For Abyssinian Animal Lovers - Coffee Cup Ideas For Pet Owners",
            "keywords": "Birthday, Anniversary, Wedding, Graduation, Holiday, Coworkers, Boss, Friends",
        },
    ]

    data = {"lastnames": test_lastnames}
    context = ""
    process_lastnames(data, context)
