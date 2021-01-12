from botocore.exceptions import ClientError
from botocore.config import Config
from snovault import (
    AfterModified,
    BeforeModified,
    CONNECTION,
    calculated_property,
    collection,
    load_schema,
)
from snovault.schema_utils import schema_validator
from snovault.validation import ValidationFailure
from .base import (
    Item,
    paths_filtered_by_status
)
from pyramid.httpexceptions import (
    HTTPForbidden,
    HTTPTemporaryRedirect,
    HTTPNotFound,
)
from pyramid.response import Response
from pyramid.settings import asbool
from pyramid.traversal import traverse
from pyramid.view import view_config
from urllib.parse import (
    parse_qs,
    urlparse,
)
import base64
import boto3
import botocore
import datetime
import logging
import json
import pytz
import time

from encoded.upload_credentials import UploadCredentials


@collection(
    name='biofiles',
    unique_key='accession',
    properties={
        'title': 'Biofiles',
        'description': 'Listing of Files',
    })
class Biofile(Item):
    item_type = 'biofile'
    schema = load_schema('encoded:schemas/biofile.json')
    name_key = 'accession'
    rev = {
        'paired_with': ('Biofile', 'paired_with'),
        'bioquality_metrics': ('BioqualityMetric', 'bioquality_metric_of'),
        'superseded_by': ('Biofile', 'supersedes'),
    }
    embedded = [
        'platform',
        'award',
        'bioreplicate',
        'bioreplicate.bioexperiment',
        'bioreplicate.biolibrary',
        'submitted_by',
        'bioquality_metrics',
        'analysis_step_version.analysis_step',
        'analysis_step_version.analysis_step.pipelines',
        'analysis_step_version.software_versions',
        'analysis_step_version.software_versions.software',

    ]
    audit_inherit = [
        'analysis_step_version.analysis_step',
        'analysis_step_version.analysis_step.pipelines',
        'analysis_step_version.analysis_step.versions',
        'analysis_step_version.software_versions',
        'analysis_step_version.software_versions.software'
    ]
    set_status_up = [
        'bioquality_metrics',
        'platform',
        


    ]
    set_status_down = []
    public_s3_statuses = ['released', 'archived']
    private_s3_statuses = ['in progress', 'replaced', 'deleted', 'revoked']

    @calculated_property(schema={
        "title": "Superseded by",
        "description": "The file(s) that supersede this file (i.e. are more preferable to use).",
        "comment": "Do not submit. Values in the list are reverse links of a file that supersedes.",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "Biofile.supersedes",
        },
        "notSubmittable": True,
    })
    def superseded_by(self, request, superseded_by):
        return paths_filtered_by_status(request, superseded_by)

    @calculated_property(
        condition=lambda paired_end=None: paired_end == '1')
    def paired_with(self, root, request):
        paired_with = self.get_rev_links('paired_with')
        if not paired_with:
            return None
        item = root.get_by_uuid(paired_with[0])
        return request.resource_path(item)
    
    @calculated_property(schema={
        "title": "Output category",
        "description": "The overall catagory of the file content.",
        "comment": "Do not submit.  This field is calculated from output_type_output_category.",
        "type": "string",
        "enum": [
            "raw data",
            "alignment",
            "signal",
            "annotation",
            "quantification",
            "reference"
        ]
    })
    def output_category(self, output_type):
        return self.schema['output_type_output_category'].get(output_type)
    
    @calculated_property(schema={
        "title": "Read length units",
        "description": "The units for read length.",
        "comment": "Do not submit. This is a fixed value.",
        "type": "string",
        "enum": [
            "nt"
        ]
    })
    def read_length_units(self, read_length=None, mapped_read_length=None):
        if read_length is not None or mapped_read_length is not None:
            return "nt"

    @calculated_property(schema={
        "title": "QC Metric",
        "description": "The list of QC metric objects associated with this file.",
        "comment": "Do not submit. Values in the list are reverse links of a quality metric with this file in quality_metric_of field.",
        "type": "array",
        "items": {
            "type": ['string', 'object'],
            "linkFrom": "BioqualityMetric.bioquality_metric_of",
        },
        "notSubmittable": True,
    })
    def bioquality_metrics(self, request, bioquality_metrics):
        return paths_filtered_by_status(request, bioquality_metrics)

    @calculated_property(schema={
        "title": "Analysis step version",
        "description": "The step version of the pipeline from which this file is an output.",
        "comment": "Do not submit.  This field is calculated from step_run.",
        "type": "string",
        "linkTo": "AnalysisStepVersion"
    })
    def analysis_step_version(self, request, root, step_run=None):
        if step_run is None:
            return
        step_run_obj = traverse(root, step_run)['context']
        step_version_uuid = step_run_obj.__json__(request).get('analysis_step_version')
        if step_version_uuid is not None:
            return request.resource_path(root[step_version_uuid])

    @calculated_property(schema={
        "title": "Biological replicates",
        "description": "The biological replicate numbers associated with this file.",
        "comment": "Do not submit.  This field is calculated through the derived_from relationship back to the raw data.",
        "type": "array",
        "items": {
            "title": "Biological replicate number",
            "description": "The identifying number of each relevant biological replicate",
            "type": "integer",
        }
    })
    def biological_replicates(self, request, registry, root, replicate=None):
        if replicate is not None:
            replicate_obj = traverse(root, replicate)['context']
            replicate_biorep = replicate_obj.__json__(request)['biological_replicate_number']
            return [replicate_biorep]

        conn = registry[CONNECTION]
        derived_from_closure = property_closure(request, 'derived_from', self.uuid)
        dataset_uuid = self.__json__(request)['biodataset']
        obj_props = (conn.get_by_uuid(uuid).__json__(request) for uuid in derived_from_closure)
        replicates = {
            props['bioreplicate']
            for props in obj_props
            if props['biodataset'] == dataset_uuid and 'bioreplicate' in props
        }
        bioreps = {
            conn.get_by_uuid(uuid).__json__(request)['biological_replicate_number']
            for uuid in replicates
        }
        return sorted(bioreps)