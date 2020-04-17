import csv
import boto3
from datetime import date, datetime
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
            "microwave_mug": "imgs/microwave_mug.png",
            "size_example": "imgs/size_example.png",
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

        # resize left_mug_image
        mug_resize = 0.5
        new_mug_w = int(ceil(left_mug_img.size[0] * mug_resize))
        new_mug_h = int(ceil(left_mug_img.size[1] * mug_resize))
        new_mug_size = (new_mug_w, new_mug_h)
        small_mug_img = left_mug_img.copy().resize((new_mug_size), Image.ANTIALIAS)

        # paste onto microwave_mug_img
        microwave_mug_file = load_file_from_s3(
            bucket=INPUT_BUCKET, key=TEMPLATE_IMG_KEYS["microwave_mug"]
        )
        microwave_mug_img = Image.open(microwave_mug_file)
        microwave_mug_img.paste(small_mug_img, (440, 45), small_mug_img)
        lastname["microwave_mug"] = microwave_mug_img

        # paste onto size_example_img
        size_example_file = load_file_from_s3(
            bucket=INPUT_BUCKET, key=TEMPLATE_IMG_KEYS["size_example"]
        )
        size_example_img = Image.open(size_example_file)
        size_example_img.paste(small_mug_img, (440, 45), small_mug_img)
        lastname["size_example"] = size_example_img
        lastname_with_renders = lastname

        return lastname_with_renders

    def upload_mug_to_s3(lastname):
        today_str = str(date.today())
        images_to_upload_names = {
            "left_mug": lastname["left_mug"],
            "right_mug": lastname["right_mug"],
            "microwave_mug": lastname["microwave_mug"],
            "size_example": lastname["size_example"],
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

    rendered_lastname = render_mug(event)
    uploaded_lastname = upload_mug_to_s3(rendered_lastname)
    amazon_ready_lastname = {
        "item_name": uploaded_lastname["item_name"],
        "keywords": uploaded_lastname["keywords"],
        "left_mug_url": uploaded_lastname["left_mug_url"],
        "right_mug_url": uploaded_lastname["right_mug_url"],
        "microwave_mug_url": uploaded_lastname["microwave_mug_url"],
        "size_example_url": uploaded_lastname["size_example_url"],
    }
    return json.dumps({"amazon_ready_lastname": amazon_ready_lastname})


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

    def create_amazon_upload_file(*, uploaded_mugs_dicts, output_bucket, s3_client):
        print("Format dict for csv printing")
        formatted_dicts = []
        today_str = date.today().strftime("%Y%m%d")

        for i, slogan_dict in enumerate(uploaded_mugs_dicts):
            try:
                formatted_dict = {}
                formatted_dict["feed_product_type"] = "kitchen"
                formatted_dict["item_sku"] = f"{today_str}-{i}"
                formatted_dict["brand_name"] = "Gifts On Demand"
                formatted_dict["item_name"] = slogan_dict["item_name"]
                formatted_dict["external_product_id"] = ""
                formatted_dict["external_product_id_type"] = "UPC"
                formatted_dict["item_type"] = "novelty-coffee-mugs"
                formatted_dict["standard_price"] = 19.95
                formatted_dict["quantity"] = 99
                formatted_dict["main-image-url"] = slogan_dict["left_mug_url"]
                formatted_dict["other-image-url1"] = slogan_dict["right_mug_url"]
                formatted_dict["other-image-url2"] = slogan_dict["microwave_mug_url"]
                formatted_dict["other-image-url3"] = slogan_dict["size_example_url"]
                formatted_dict["other-image-url4"] = ""
                formatted_dict["other-image-url5"] = ""
                formatted_dict["other-image-url6"] = ""
                formatted_dict["other-image-url7"] = ""
                formatted_dict["other-image-url8"] = ""
                formatted_dict["swatch-image-url"] = ""
                formatted_dict["parent_child"] = ""
                formatted_dict["parent_sku"] = ""
                formatted_dict["relationship_type"] = ""
                formatted_dict["variation_theme"] = ""
                formatted_dict["update_delete"] = ""
                formatted_dict["product_description"] = ""
                formatted_dict["manufacturer"] = ""
                formatted_dict["part_number"] = ""
                formatted_dict["model"] = ""
                formatted_dict["closure_type"] = ""
                formatted_dict[
                    "bullet_point1"
                ] = "High quality mug makes the perfect gift for everyone."  # noqa:E501
                formatted_dict[
                    "bullet_point2"
                ] = "Printed on only the highest quality mugs. The print will never fade no matter how many times it is washed."  # noqa:E501
                formatted_dict["bullet_point3"] = "Packaged, and shipped from the USA."
                formatted_dict["bullet_point4"] = "Dishwasher and Microwave safe."
                formatted_dict[
                    "bullet_point5"
                ] = "Shipped in a custom made styrofoam package to ensure it arrives perfect. GUARANTEED."  # noqa:E501
                formatted_dict["target_audience_base"] = ""
                formatted_dict["catalog_number"] = ""
                formatted_dict["specific_uses_keywords1"] = ""
                formatted_dict["specific_uses_keywords2"] = ""
                formatted_dict["specific_uses_keywords3"] = ""
                formatted_dict["specific_uses_keywords4"] = ""
                formatted_dict["specific_uses_keywords5"] = ""
                formatted_dict["target_audience_keywords1"] = ""
                formatted_dict["target_audience_keywords2"] = ""
                formatted_dict["target_audience_keywords3"] = ""
                formatted_dict["thesaurus_attribute_keywords1"] = ""
                formatted_dict["thesaurus_attribute_keywords2"] = ""
                formatted_dict["thesaurus_attribute_keywords3"] = ""
                formatted_dict["thesaurus_attribute_keywords4"] = ""
                formatted_dict["thesaurus_subject_keywords1"] = ""
                formatted_dict["thesaurus_subject_keywords2"] = ""
                formatted_dict["thesaurus_subject_keywords3"] = ""
                formatted_dict["generic_keywords"] = slogan_dict["keywords"]
                formatted_dict["platinum_keywords1"] = ""
                formatted_dict["platinum_keywords2"] = ""
                formatted_dict["platinum_keywords3"] = ""
                formatted_dict["platinum_keywords4"] = ""
                formatted_dict["platinum_keywords5"] = ""
                formatted_dict["country_as_labeled"] = ""
                formatted_dict["fur_description"] = ""
                formatted_dict["occasion"] = ""
                formatted_dict["number_of_pieces"] = ""
                formatted_dict["scent_name"] = ""
                formatted_dict["included_components"] = ""
                formatted_dict["color_name"] = "white"
                formatted_dict["color_map"] = ""
                formatted_dict["size_name"] = ""
                formatted_dict["material_type"] = ""
                formatted_dict["style_name"] = ""
                formatted_dict["power_source_type"] = ""
                formatted_dict["wattage"] = ""
                formatted_dict["special_features1"] = ""
                formatted_dict["special_features2"] = ""
                formatted_dict["special_features3"] = ""
                formatted_dict["special_features4"] = ""
                formatted_dict["special_features5"] = ""
                formatted_dict["pattern_name"] = ""
                formatted_dict["lithium_battery_voltage"] = ""
                formatted_dict["compatible_devices1"] = ""
                formatted_dict["compatible_devices2"] = ""
                formatted_dict["compatible_devices3"] = ""
                formatted_dict["compatible_devices4"] = ""
                formatted_dict["compatible_devices5"] = ""
                formatted_dict["compatible_devices6"] = ""
                formatted_dict["compatible_devices7"] = ""
                formatted_dict["compatible_devices8"] = ""
                formatted_dict["compatible_devices9"] = ""
                formatted_dict["compatible_devices10"] = ""
                formatted_dict["wattage_unit_of_measure"] = ""
                formatted_dict["included_features"] = ""
                formatted_dict["lithium_battery_voltage_unit_of_measure"] = ""
                formatted_dict["length_range"] = ""
                formatted_dict["shaft_style_type"] = ""
                formatted_dict["specification_met"] = ""
                formatted_dict["breed_recommendation"] = ""
                formatted_dict["directions"] = ""
                formatted_dict["number_of_sets"] = ""
                formatted_dict["blade_edge_type"] = ""
                formatted_dict["blade_material_type"] = ""
                formatted_dict["material_composition"] = ""
                formatted_dict["mfg_maximum"] = ""
                formatted_dict["mfg_minimum"] = ""
                formatted_dict["website_shipping_weight"] = ""
                formatted_dict["website_shipping_weight_unit_of_measure"] = ""
                formatted_dict["item_shape"] = ""
                formatted_dict["item_display_length_unit_of_measure"] = ""
                formatted_dict["item_display_width_unit_of_measure"] = ""
                formatted_dict["item_display_height_unit_of_measure"] = ""
                formatted_dict["item_display_length"] = ""
                formatted_dict["item_display_width"] = ""
                formatted_dict["item_display_depth"] = ""
                formatted_dict["item_display_height"] = ""
                formatted_dict["item_display_diameter"] = ""
                formatted_dict["item_display_weight"] = ""
                formatted_dict["item_display_weight_unit_of_measure"] = ""
                formatted_dict["volume_capacity_name"] = 11
                formatted_dict["volume_capacity_name_unit_of_measure"] = "ounces"
                formatted_dict["item_height"] = ""
                formatted_dict["item_length"] = ""
                formatted_dict["item_width"] = ""
                formatted_dict["size_map"] = ""
                formatted_dict["weight_recommendation_unit_of_measure"] = ""
                formatted_dict["width_range"] = ""
                formatted_dict["maximum_weight_recommendation"] = ""
                formatted_dict["item_dimensions_unit_of_measure"] = ""
                formatted_dict["fulfillment_center_id"] = ""
                formatted_dict["package_height"] = ""
                formatted_dict["package_width"] = ""
                formatted_dict["package_length"] = ""
                formatted_dict["package_dimensions_unit_of_measure"] = ""
                formatted_dict["package_weight"] = ""
                formatted_dict["package_weight_unit_of_measure"] = ""
                formatted_dict["energy_efficiency_image_url"] = ""
                formatted_dict["warranty_description"] = ""
                formatted_dict["cpsia_cautionary_statement"] = ""
                formatted_dict["cpsia_cautionary_description"] = ""
                formatted_dict["fabric_type"] = ""
                formatted_dict["import_designation"] = ""
                formatted_dict["legal_compliance_certification_metadata"] = ""
                formatted_dict["legal_compliance_certification_expiration_date"] = ""
                formatted_dict["item_volume"] = ""
                formatted_dict["item_volume_unit_of_measure"] = ""
                formatted_dict["specific_uses_for_product"] = ""
                formatted_dict["country_string"] = ""
                formatted_dict["country_of_origin"] = ""
                formatted_dict["legal_disclaimer_description"] = ""
                formatted_dict["usda_hardiness_zone1"] = ""
                formatted_dict["usda_hardiness_zone2"] = ""
                formatted_dict["are_batteries_included"] = ""
                formatted_dict["item_weight"] = ""
                formatted_dict["batteries_required"] = ""
                formatted_dict["battery_type1"] = ""
                formatted_dict["battery_type2"] = ""
                formatted_dict["battery_type3"] = ""
                formatted_dict["item_weight_unit_of_measure"] = ""
                formatted_dict["number_of_batteries1"] = ""
                formatted_dict["number_of_batteries2"] = ""
                formatted_dict["number_of_batteries3"] = ""
                formatted_dict["lithium_battery_energy_content"] = ""
                formatted_dict["lithium_battery_packaging"] = ""
                formatted_dict["lithium_battery_weight"] = ""
                formatted_dict["number_of_lithium_ion_cells"] = ""
                formatted_dict["number_of_lithium_metal_cells"] = ""
                formatted_dict["battery_cell_composition"] = ""
                formatted_dict["battery_weight"] = ""
                formatted_dict["battery_weight_unit_of_measure"] = ""
                formatted_dict["lithium_battery_energy_content_unit_of_measure"] = ""
                formatted_dict["lithium_battery_weight_unit_of_measure"] = ""
                formatted_dict["supplier_declared_dg_hz_regulation1"] = ""
                formatted_dict["supplier_declared_dg_hz_regulation2"] = ""
                formatted_dict["supplier_declared_dg_hz_regulation3"] = ""
                formatted_dict["supplier_declared_dg_hz_regulation4"] = ""
                formatted_dict["supplier_declared_dg_hz_regulation5"] = ""
                formatted_dict["hazmat_united_nations_regulatory_id"] = ""
                formatted_dict["safety_data_sheet_url"] = ""
                formatted_dict["lighting_facts_image_url"] = ""
                formatted_dict["flash_point"] = ""
                formatted_dict["external_testing_certification1"] = ""
                formatted_dict["external_testing_certification2"] = ""
                formatted_dict["external_testing_certification3"] = ""
                formatted_dict["external_testing_certification4"] = ""
                formatted_dict["external_testing_certification5"] = ""
                formatted_dict["external_testing_certification6"] = ""
                formatted_dict["ghs_classification_class1"] = ""
                formatted_dict["ghs_classification_class2"] = ""
                formatted_dict["ghs_classification_class3"] = ""
                formatted_dict["california_proposition_65_compliance_type"] = ""
                formatted_dict["california_proposition_65_chemical_names1"] = ""
                formatted_dict["california_proposition_65_chemical_names2"] = ""
                formatted_dict["california_proposition_65_chemical_names3"] = ""
                formatted_dict["california_proposition_65_chemical_names4"] = ""
                formatted_dict["california_proposition_65_chemical_names5"] = ""
                formatted_dict["merchant_shipping_group_name"] = ""
                formatted_dict["list_price"] = ""
                formatted_dict["map_price"] = ""
                formatted_dict["product_site_launch_date"] = ""
                formatted_dict["merchant_release_date"] = ""
                formatted_dict["condition_type"] = ""
                formatted_dict["restock_date"] = ""
                formatted_dict["fulfillment_latency"] = ""
                formatted_dict["condition_note"] = ""
                formatted_dict["product_tax_code"] = ""
                formatted_dict["sale_price"] = ""
                formatted_dict["sale_from_date"] = ""
                formatted_dict["sale_end_date"] = ""
                formatted_dict["item_package_quantity"] = ""
                formatted_dict["max_aggregate_ship_quantity"] = ""
                formatted_dict["offering_can_be_gift_messaged"] = ""
                formatted_dict["offering_can_be_giftwrapped"] = ""
                formatted_dict["is_discontinued_by_manufacturer"] = ""
                formatted_dict["max_order_quantity"] = ""
                formatted_dict["number_of_items"] = ""
                formatted_dict["offering_start_date"] = ""
                formatted_dict["offering_end_date"] = ""

                formatted_dicts.append(formatted_dict)
            except Exception as e:
                error_msg = f"{e}. {slogan_dict['slogan']}"
                print(error_msg)

        print("Write listing information to txt file")
        amazon_data = [
            [
                "TemplateType=fptcustom",
                "Version=2020.0324",
                "TemplateSignature=S0lUQ0hFTg==",
                "The top 3 rows are for Amazon.com use only. Do not modify or delete the top 3 rows.",  # noqa:E501
                "",
                "",
                "",
                "",
                "",
                "",
                "Images",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "Variation",
                "",
                "",
                "",
                "Basic",
                "",
                "",
                "",
                "",
                "",
                "Discovery",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "Product Enrichment",
                "",
                "",
                "",
                "",
                "",
                "Dimensions",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "Fulfillment",
                "",
                "",
                "",
                "",
                "",
                "",
                "Compliance",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "Offer",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
            [
                "Product Type",
                "Seller SKU",
                "Brand Name",
                "Product Name",
                "Product ID",
                "Product ID Type",
                "Item Type Keyword",
                "Standard Price",
                "Quantity",
                "Main Image URL",
                "Other Image URL1",
                "Other Image URL2",
                "Other Image URL3",
                "Other Image URL4",
                "Other Image URL5",
                "Other Image URL6",
                "Other Image URL7",
                "Other Image URL8",
                "Swatch Image URL",
                "Parentage",
                "Parent SKU",
                "Relationship Type",
                "Variation Theme",
                "Update Delete",
                "Product Description",
                "Manufacturer",
                "Manufacturer Part Number",
                "model",
                "closure_type",
                "Key Product Features",
                "Key Product Features",
                "Key Product Features",
                "Key Product Features",
                "Key Product Features",
                "Target Audience",
                "Catalog Number",
                "Used For1 - Used For3",
                "Used For1 - Used For3",
                "Used For1 - Used For3",
                "Used For1 - Used For3",
                "Used For1 - Used For3",
                "Target Audience",
                "Target Audience",
                "Target Audience",
                "Other Attributes",
                "Other Attributes",
                "Other Attributes",
                "Other Attributes",
                "Subject Matter",
                "Subject Matter",
                "Subject Matter",
                "Search Terms",
                "Platinum Keywords",
                "Platinum Keywords",
                "Platinum Keywords",
                "Platinum Keywords",
                "Platinum Keywords",
                "Country/Region as Labeled",
                "Fur Description",
                "Occasion",
                "Number of Pieces",
                "Scent",
                "Included Components",
                "Color",
                "Color Map",
                "Size",
                "Material Type",
                "Style Name",
                "Power Source",
                "Wattage",
                "Additional Features",
                "Additional Features",
                "Additional Features",
                "Additional Features",
                "Additional Features",
                "Pattern",
                "Lithium Battery Voltage",
                "Compatible Devices",
                "Compatible Devices",
                "Compatible Devices",
                "Compatible Devices",
                "Compatible Devices",
                "Compatible Devices",
                "Compatible Devices",
                "Compatible Devices",
                "Compatible Devices",
                "Compatible Devices",
                "Wattage Unit of Measure",
                "included_features",
                "Lithium Battery Voltage Unit of Measure",
                "Length Range",
                "shaft_style_type",
                "Specification Met",
                "breed_recommendation",
                "directions",
                "Number of Sets",
                "Blade Type",
                "Blade Material Type",
                "Material Composition",
                "Maximum Age Recommendation",
                "Minimum Age Recommendation",
                "Shipping Weight",
                "Website Shipping Weight Unit Of Measure",
                "Shape",
                "Display Length Unit Of Measure",
                "Item Display Width Unit Of Measure",
                "Item Display Height Unit Of Measure",
                "Item Display Length",
                "Item Display Width",
                "Item Display Depth",
                "Item Display Height",
                "Item Display Diameter",
                "Item Display Weight",
                "Item Display Weight Unit Of Measure",
                "Volume",
                "Volume Capacity Name Unit Of Measure",
                "Item Height",
                "Item Length",
                "Item Width",
                "Size Map",
                "Weight Recommendation Unit Of Measure",
                "Width Range",
                "maximum_weight_recommendation",
                "Item Dimensions Unit Of Measure",
                "Fulfillment Center ID",
                "Package Height",
                "Package Width",
                "Package Length",
                "Package Dimensions Unit Of Measure",
                "Package Weight",
                "Package Weight Unit Of Measure",
                "Energy Guide Label",
                "Manufacturer Warranty Description",
                "Cpsia Warning",
                "CPSIA Warning Description",
                "Fabric Type",
                "Import Designation",
                "Please provide the Executive Number (EO) required for sale into California.",  # noqa:E501
                "Please provide the expiration date of the EO Number.",
                "Volume",
                "item_volume_unit_of_measure",
                "Specific Uses For Product",
                "Country/Region of Origin",
                "Country/Region of Origin",
                "Legal Disclaimer",
                "USDA Hardiness Zone",
                "USDA Hardiness Zone",
                "Batteries are Included",
                "Item Weight",
                "Is this product a battery or does it utilize batteries?",
                "Battery type/size",
                "Battery type/size",
                "Battery type/size",
                "item_weight_unit_of_measure",
                "Number of batteries",
                "Number of batteries",
                "Number of batteries",
                "Watt hours per battery",
                "Lithium Battery Packaging",
                "Lithium content (grams)",
                "Number of Lithium-ion Cells",
                "Number of Lithium Metal Cells",
                "Battery composition",
                "Battery weight (grams)",
                "battery_weight_unit_of_measure",
                "lithium_battery_energy_content_unit_of_measure",
                "lithium_battery_weight_unit_of_measure",
                "Applicable Dangerous Goods Regulations",
                "Applicable Dangerous Goods Regulations",
                "Applicable Dangerous Goods Regulations",
                "Applicable Dangerous Goods Regulations",
                "Applicable Dangerous Goods Regulations",
                "UN number",
                "Safety Data Sheet (SDS) URL",
                "Lighting Facts Label",
                "Flash point (°C)?",
                "external_testing_certification1",
                "external_testing_certification2",
                "external_testing_certification3",
                "external_testing_certification4",
                "external_testing_certification5",
                "external_testing_certification6",
                "Categorization/GHS pictograms (select all that apply)",
                "Categorization/GHS pictograms (select all that apply)",
                "Categorization/GHS pictograms (select all that apply)",
                "California Proposition 65 Warning Type",
                "California Proposition 65 Chemical Names",
                "Additional Chemical Name1",
                "Additional Chemical Name2",
                "Additional Chemical Name3",
                "Additional Chemical Name4",
                "Shipping-Template",
                "Manufacturer's Suggested Retail Price",
                "Minimum Advertised Price",
                "Launch Date",
                "Release Date",
                "Item Condition",
                "Restock Date",
                "Handling Time",
                "Offer Condition Note",
                "Product Tax Code",
                "Sale Price",
                "Sale Start Date",
                "Sale End Date",
                "Package Quantity",
                "Max Aggregate Ship Quantity",
                "Offering Can Be Gift Messaged",
                "Is Gift Wrap Available",
                "Is Discontinued by Manufacturer",
                "Max Order Quantity",
                "Number of Items",
                "Offering Release Date",
                "Stop Selling Date",
            ],
        ]
        now_str = datetime.now().strftime("%Y%m%d%H%M")

        # IO object must accept strings
        csv_buffer = io.StringIO()

        keys = formatted_dicts[0].keys()
        writer = csv.writer(csv_buffer, delimiter="\t")
        writer.writerows(amazon_data)
        dict_writer = csv.DictWriter(csv_buffer, keys, delimiter="\t")
        dict_writer.writeheader()
        dict_writer.writerows(formatted_dicts)

        # S3 put_object expects bytes obj
        # https://stackoverflow.com/a/45700716/1723469
        csv_bytes = io.BytesIO(csv_buffer.getvalue().encode())

        today_str = str(date.today())

        s3_file_path = f"inventory_files/amazon_data_{now_str}.txt"

        s3_client.put_object(
            Bucket=output_bucket,
            Key=s3_file_path,
            Body=csv_bytes,
            ContentType="text/plain",
            ACL="public-read",
        )

        return f"https://{output_bucket}.s3.amazonaws.com/{s3_file_path}"

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

    amazon_ready_lastnames = []  # list of dicts including mug urls
    for lastname in lastnames:
        event_payload = {
            "lastname": lastname,
            "input_bucket": INPUT_BUCKET,
            "output_bucket": event["output_bucket"],
        }
        invoke_response = lambda_client.invoke(
            FunctionName="mugup-dev-render-and-upload-lastname-mug",
            InvocationType="RequestResponse",
            Payload=json.dumps(event_payload),
        )
        string_response = invoke_response["Payload"].read().decode("utf-8")
        # Quest: why did I have to load this twice?  Essentially
        # that would mean we're getting back a json inside a
        # string inside a str
        parsed_response = json.loads(json.loads(string_response))
        amazon_ready_lastnames.append(parsed_response["amazon_ready_lastname"])

    amazon_upload_file_url = create_amazon_upload_file(
        uploaded_mugs_dicts=amazon_ready_lastnames,
        output_bucket=event["output_bucket"],
        s3_client=s3_client,
    )

    return json.dumps(amazon_upload_file_url)


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
