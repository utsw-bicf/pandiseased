from snovault.attachment import ItemWithAttachment
from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from pyramid.traversal import find_root
from .base import (
    Item,
    paths_filtered_by_status,
    ALLOW_CURRENT,
    DELETED,
)


def includeme(config):
    config.scan()
    config.add_request_method(lambda request: set(), '_set_status_changed_paths', reify=True)
    config.add_request_method(lambda request: set(), '_set_status_considered_paths', reify=True)


@collection(
    name='labs',
    unique_key='lab:name',
    properties={
        'title': 'Labs',
        'description': 'Listing of ENCODE DCC labs',
    })
class Lab(Item):
    item_type = 'lab'
    schema = load_schema('encoded:schemas/lab.json')
    name_key = 'name'
    embedded = ['awards']


@collection(
    name='awards',
    unique_key='award:name',
    properties={
        'title': 'Awards (Grants)',
        'description': 'Listing of awards (aka grants)',
    })
class Award(Item):
    item_type = 'award'
    schema = load_schema('encoded:schemas/award.json')
    name_key = 'name'
    embedded = ['pi.lab']
    STATUS_ACL = {
        'current': ALLOW_CURRENT,
        'deleted': DELETED,
        'replaced': DELETED,
        'disabled': ALLOW_CURRENT
    }



@collection(
    name='sources',
    unique_key='source:name',
    properties={
        'title': 'Sources',
        'description': 'Listing of sources and vendors for ENCODE material',
    })
class Source(Item):
    item_type = 'source'
    schema = load_schema('encoded:schemas/source.json')
    name_key = 'name'

@collection(
    name='documents',
    properties={
        'title': 'Documents',
        'description': 'Listing of Biosample Documents',
    })
class Document(ItemWithAttachment, Item):
    item_type = 'document'
    schema = load_schema('encoded:schemas/document.json')
    embedded = ['lab', 'award', 'submitted_by']


@collection(
    name='platforms',
    unique_key='platform:term_id',
    properties={
        'title': 'Platforms',
        'description': 'Listing of Platforms',
    })
class Platform(Item):
    item_type = 'platform'
    schema = load_schema('encoded:schemas/platform.json')
    name_key = 'term_id'

    @calculated_property(schema={
        "title": "Title",
        "type": "string",
    })
    def title(self, term_name):
        return term_name


@collection(
    name='publications',
    unique_key='publication:identifier',
    properties={
        'title': 'Publications',
        'description': 'Publication pages',
    })
class Publication(Item):
    item_type = 'publication'
    schema = load_schema('encoded:schemas/publication.json')
    rev = {
        
    }

    def unique_keys(self, properties):
        keys = super(Publication, self).unique_keys(properties)
        if properties.get('identifiers'):
            keys.setdefault('alias', []).extend(properties['identifiers'])
        return keys

    @calculated_property(condition='date_published', schema={
        "title": "Publication year",
        "type": "integer",
    })
    def publication_year(self, date_published):
        likely_year = date_published[:4]
        if likely_year.isdigit():
            return int(date_published[:4])
        else:
            return None




@collection(
    name='software',
    unique_key='software:name',
    properties={
        'title': 'Software',
        'description': 'Software pages',
    })
class Software(Item):
    item_type = 'software'
    schema = load_schema('encoded:schemas/software.json')
    name_key = 'name'
    embedded = [
        'references',
        'versions'
    ]
    rev = {
        'versions': ('SoftwareVersion', 'software')
    }

    @calculated_property(schema={
        "title": "Versions",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "SoftwareVersion",
        },
    })
    def versions(self, request, versions):
        return paths_filtered_by_status(request, versions)


@collection(
    name='software-versions',
    properties={
        'title': 'Software version',
        'description': 'Software version pages',
    })
class SoftwareVersion(Item):
    item_type = 'software_version'
    schema = load_schema('encoded:schemas/software_version.json')
    embedded = ['software', 'software.references']

    def __ac_local_roles__(self):
        # Use lab/award from parent software object for access control.
        properties = self.upgrade_properties()
        root = find_root(self)
        software = root.get_by_uuid(properties['software'])
        return software.__ac_local_roles__()

