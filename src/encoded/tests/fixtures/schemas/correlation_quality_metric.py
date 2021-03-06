import pytest


@pytest.fixture
def correlation_quality_metric(testapp, analysis_step_run_bam, file_tsv_1_2, award, lab):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of': [file_tsv_1_2['@id']],
        'Pearson correlation': 0.1,
        'award': award['@id'],
        'lab': lab['@id']
    }

    return testapp.post_json('/correlation_quality_metric', item).json['@graph'][0]


@pytest.fixture
def spearman_correlation_quality_metric(testapp, analysis_step_run_bam, file_tsv_1_2, award, lab):
    item = {
        'step_run': analysis_step_run_bam['@id'],
        'quality_metric_of': [file_tsv_1_2['@id']],
        'Spearman correlation': 0.7,
        'award': award['@id'],
        'lab': lab['@id']
    }
    return testapp.post_json('/correlation_quality_metric', item).json['@graph'][0]
