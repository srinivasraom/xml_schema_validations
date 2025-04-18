from pydantic import BaseModel, ValidationError, Field, model_validator
from typing import List, Dict, Any
import xml.etree.ElementTree as ET
import json


class XmlElement(BaseModel):
    tag: str
    attributes: Dict[str, str]


class XmlWrapper(BaseModel):
    elements: List[XmlElement]
    config: Dict[str, Any]  # JSON cardinal config loaded at runtime

    @model_validator(mode="after")
    def validate_cardinal_rules(self) -> "XmlWrapper":
        from collections import defaultdict

        # Group by tag name
        grouped: Dict[str, List[XmlElement]] = defaultdict(list)
        for el in self.elements:
            grouped[el.tag].append(el)

        for tag, rules in self.config.items():
            items = grouped.get(tag, [])
            count = len(items)

            max_occurs = rules.get("maxOccurs")
            if max_occurs is not None and count > max_occurs:
                raise ValueError(f"<{tag}> appears {count} times (max allowed: {max_occurs})")

            required_attrs = rules.get("attributes", [])
            for idx, el in enumerate(items, start=1):
                for attr in required_attrs:
                    if attr not in el.attributes:
                        raise ValueError(f"<{tag}> #{idx} missing required attribute '{attr}'")

        return self


def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r") as f:
        return json.load(f)


def parse_xml_elements(xml_file: str) -> List[XmlElement]:
    tree = ET.parse(xml_file)
    root = tree.getroot()
    elements = []
    for child in root:
        elements.append(XmlElement(tag=child.tag, attributes=child.attrib))
    return elements


def validate_with_pydantic(xml_path: str, config_path: str):
    config = load_config(config_path)
    elements = parse_xml_elements(xml_path)

    try:
        wrapper = XmlWrapper(elements=elements, config=config)
        print("✅ XML is valid according to cardinal config.")
    except ValidationError as e:
        print("❌ Validation Error:")
        print(e)


# Run the validator
if __name__ == "__main__":
    validate_with_pydantic("items.xml", "cardinal_config.json")
