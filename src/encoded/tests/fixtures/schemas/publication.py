import pytest


@pytest.fixture
def publication_0_0():
    return{
        'title': "Fake paper"
    }


@pytest.fixture
def publication_1(publication_0_0):
    item = publication_0_0.copy()
    item.update({
        'schema_version': '1',
        'references': ['PMID:25409824'],
    })
    return item


@pytest.fixture
def publication_4():
    return {
        'title': 'Fake paper',
        'schema_version': '4'
    }


@pytest.fixture
def publication_5(publication_0_0):
    item = publication_0_0.copy()
    item.update({
        'schema_version': '5',
        'status': 'in preparation'
    })
    return item


@pytest.fixture
def publication_6(testapp, lab, award):
    item = {
        'title': "Test publication with publication data",
        'award': award['@id'],
        'lab': lab['@id'],
    }
    return testapp.post_json('/publication', item, status=201).json['@graph'][0]


@pytest.fixture
def publication(testapp, lab, award):
    item = {
        # upgrade/shared.py has a REFERENCES_UUID mapping.
        'uuid': '8312fc0c-b241-4cb2-9b01-1438910550ad',
        'title': "Test publication",
        'award': award['@id'],
        'lab': lab['@id'],
        'identifiers': ["doi:10.1214/11-AOAS466"],
    }
    return testapp.post_json('/publication', item).json['@graph'][0]


@pytest.fixture
def publication_7(testapp, lab, award):
    item = {
        'title': "Test publication with incorrect date_published",
        'award': award['@id'],
        'lab': lab['@id'],
        'date_published': '3/30/20'
        }
    return item


@pytest.fixture
def publication_8(root, testapp, lab, award, publication_6,
                  functional_characterization_experiment,
                  experiment_1, base_reference, annotation_dataset
                  ):
    item = publication_6.copy()
    item.update({
        'datasets': [
            experiment_1['@id'],
            functional_characterization_experiment['@id'],
            base_reference['@id'],
            annotation_dataset['@id'],
            ]
        })
    return item
