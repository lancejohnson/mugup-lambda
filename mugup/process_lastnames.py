import csv
import io
import json
from datetime import date, datetime

import boto3


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

    print("Execution started...")

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
