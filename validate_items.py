from lxml import etree

# Load schema
with open("items.xsd", "rb") as f:
    schema_root = etree.XML(f.read())
schema = etree.XMLSchema(schema_root)

# Parse XML
with open("items.xml", "rb") as f:
    xml_doc = etree.XML(f.read())

# Validate
is_valid = schema.validate(xml_doc)
print("Schema Valid:", is_valid)
if not is_valid:
    print(schema.error_log)
