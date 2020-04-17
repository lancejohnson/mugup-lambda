import boto3
from datetime import date
import io
import json
from math import ceil
import numpy as np
from PIL import Image, ImageDraw, ImageFont


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
        def draw_slogan(slogan_to_write, img):
            draw = ImageDraw.Draw(img)
            INPUT_BUCKET = "giftsondemand-input"
            FONT_S3_KEY = "fonts/angelina.ttf"

            font_file = load_file_from_s3(bucket=INPUT_BUCKET, key=FONT_S3_KEY)
            font = ImageFont.truetype(font_file, 310)

            # Find starting x coordinate to center text
            text_width, text_height = draw.textsize(slogan_to_write, font)
            img_width, img_height = img.size
            starting_x = (img_width - text_width) / 2
            draw.text(
                xy=(starting_x, 1050),
                text=slogan_to_write,
                fill=(88, 89, 91, 255),
                font=font,
            )
            return img

        def transform_slogan(original_img):
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

        slogan = event["slogan"]
        template_img_keys = {
            "slogan_template": "imgs/mug_template_feminine_its_a_surname_thing.png",
            "left_mug": "imgs/mug_left_large.png",
            "right_mug": "imgs/mug_right_large.png",
            "microwave_mug": "imgs/microwave_mug.png",
            "size_example": "imgs/size_example.png",
        }

        INPUT_BUCKET = "giftsondemand-input"

        slogan_to_write = slogan["slogan"]
        SLOGAN_TEMPLATE_IMG_KEY = template_img_keys["slogan_template"]
        slogan_img_template_file = load_file_from_s3(
            bucket=INPUT_BUCKET, key=SLOGAN_TEMPLATE_IMG_KEY
        )
        template_img = Image.open(slogan_img_template_file)

        slogan_img = draw_slogan(slogan_to_write, template_img)
        transformed_img = transform_slogan(slogan_img)

        # Calculate the new size starting with final size.
        STARTING_W, STARTING_H = template_img.size
        FINAL_W = 1372
        slogan_resize_factor = FINAL_W / STARTING_W
        size = (
            int(ceil(STARTING_W * slogan_resize_factor)),
            int(ceil(STARTING_H * slogan_resize_factor)),
        )
        transformed_img = transformed_img.resize(size, Image.ANTIALIAS)

        # paste onto left_mug_img
        left_mug_file = load_file_from_s3(
            bucket=INPUT_BUCKET, key=template_img_keys["left_mug"]
        )
        left_mug_img = Image.open(left_mug_file)
        left_mug_img.paste(transformed_img, (600, 180), transformed_img)
        slogan["left_mug"] = left_mug_img

        # paste onto right_mug_img
        right_mug_file = load_file_from_s3(
            bucket=INPUT_BUCKET, key=template_img_keys["right_mug"]
        )
        right_mug_img = Image.open(right_mug_file)
        right_mug_img.paste(transformed_img, (-20, 180), transformed_img)
        slogan["right_mug"] = right_mug_img

        # resize left_mug_image
        mug_resize = 0.5
        new_mug_w = int(ceil(left_mug_img.size[0] * mug_resize))
        new_mug_h = int(ceil(left_mug_img.size[1] * mug_resize))
        new_mug_size = (new_mug_w, new_mug_h)
        small_mug_img = left_mug_img.copy().resize((new_mug_size), Image.ANTIALIAS)

        # paste onto microwave_mug_img
        microwave_mug_file = load_file_from_s3(
            bucket=INPUT_BUCKET, key=template_img_keys["microwave_mug"]
        )
        microwave_mug_img = Image.open(microwave_mug_file)
        microwave_mug_img.paste(small_mug_img, (440, 45), small_mug_img)
        slogan["microwave_mug"] = microwave_mug_img

        # paste onto size_example_img
        size_example_file = load_file_from_s3(
            bucket=INPUT_BUCKET, key=template_img_keys["size_example"]
        )
        size_example_img = Image.open(size_example_file)
        size_example_img.paste(small_mug_img, (440, 45), small_mug_img)
        slogan["size_example"] = size_example_img
        slogan_with_renders = slogan

        return slogan_with_renders

    def upload_mug_to_s3(slogan):
        today_str = str(date.today())
        images_to_upload_names = {
            "left_mug": slogan["left_mug"],
            "right_mug": slogan["right_mug"],
            "microwave_mug": slogan["microwave_mug"],
            "size_example": slogan["size_example"],
        }

        s3 = boto3.client("s3")

        BUCKET = event["BUCKET"]

        for img_name, pil_img in images_to_upload_names.items():
            in_mem_file = io.BytesIO()
            s3_img_path = f"{today_str}/{slogan['slogan']}_its_a_surname_thing_feminine_{img_name}.png"
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
            slogan[f"{img_name}_url"] = aws_url
            slogan_with_mug_urls = slogan

        return slogan_with_mug_urls

    rendered_slogan = render_mug(event)
    uploaded_slogan = upload_mug_to_s3(rendered_slogan)
    amazon_ready_slogan = {
        "item_name": uploaded_slogan["item_name"],
        "keywords": uploaded_slogan["keywords"],
        "left_mug_url": uploaded_slogan["left_mug_url"],
        "right_mug_url": uploaded_slogan["right_mug_url"],
        "microwave_mug_url": uploaded_slogan["microwave_mug_url"],
        "size_example_url": uploaded_slogan["size_example_url"],
    }
    return json.dumps({"amazon_ready_slogan": amazon_ready_slogan})


def process_surname_slogans(event, context):
    client = boto3.client("lambda")

    slogans = event["slogans"]

    amazon_ready_slogans = []  # list of dicts including mug urls
    for slogan in slogans[:1]:
        event_payload = {
            "slogan": slogan,
            "BUCKET": "giftsondemand",
        }
        invoke_response = client.invoke(
            FunctionName="mugup-dev-render-and-upload-lastname-mug",
            InvocationType="RequestResponse",
            Payload=json.dumps(event_payload),
        )
        string_response = invoke_response["Payload"].read().decode("utf-8")
        parsed_response = json.loads(string_response)
        amazon_ready_slogans.append(parsed_response)

    return json.dumps(amazon_ready_slogans)


if __name__ == "__main__":
    test_slogans = [
        {
            "slogan": "Abcdefghijklmno",
            "niche": "Aardvark",
            "item_name": "Novelty Mugs For Aardvark Animal Lovers - Coffee Cup Ideas For Pet Owners",
            "keywords": "Birthday, Anniversary, Wedding, Graduation, Holiday, Coworkers, Boss, Friends",
        },
        {
            "slogan": "Jefferson",
            "niche": "Abyssinian",
            "item_name": "Novelty Mugs For Abyssinian Animal Lovers - Coffee Cup Ideas For Pet Owners",
            "keywords": "Birthday, Anniversary, Wedding, Graduation, Holiday, Coworkers, Boss, Friends",
        },
    ]

    data = {"slogans": test_slogans}
    context = ""
    process_surname_slogans(data, context)
