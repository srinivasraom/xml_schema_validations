from pydantic import BaseModel, ValidationError, field_validator, model_validator
from typing import List
import xml.etree.ElementTree as ET

class Item(BaseModel):
    name: str

class ItemsWrapper(BaseModel):
    items: List[Item]

    @model_validator(mode="after")
    def check_max_occurs(self) -> "ItemsWrapper":
        if len(self.items) > 2:
            raise ValueError("Maximum of 2 <Item> elements allowed")
        return self

def validate_max_occurs(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    items = []
    for elem in root.findall('Item'):
        name = elem.attrib.get('name')
        items.append(Item(name=name))
    try:
        wrapper = ItemsWrapper(items=items)
        print("MaxOccurs Validation: Passed")
    except ValidationError as e:
        print("MaxOccurs Validation: Failed")
        print(e)

validate_max_occurs("items.xml")
