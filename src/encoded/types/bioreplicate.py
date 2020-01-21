from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
    paths_filtered_by_status,
)
import re


@collection(
    name='bioreplicates',
    unique_key='uuid',
    properties={
        'title': 'Bioreplicates',
        'description': 'Bioreplicates used or available',
    })
class Bioreplicate(Item):
    item_type = 'bioreplicate'
    schema = load_schema('encoded:schemas/bioreplicate.json')
    name_key = 'uuid'
    rev = {
        
    }
    embedded = [

    ]
    audit_inherit = [
    ]
    set_status_up = [
      
    ]
    set_status_down = []