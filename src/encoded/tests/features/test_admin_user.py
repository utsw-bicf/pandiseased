import pytest
from pytest_bdd import scenarios

pytestmark = [
    pytest.mark.bdd,
    pytest.mark.usefixtures('index_workbook', 'admin_user'),
]


scenarios(
    'forms.feature',
    'page.feature',
    strict_gherkin=False,
)
