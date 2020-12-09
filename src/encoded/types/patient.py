from pyramid.view import (
    view_config,
)
from pyramid.security import (
    Allow,
    Deny,
    Everyone,
)
from pyramid.traversal import find_root
from snovault import (
    calculated_property,
    collection,
    load_schema,
)
from .base import (
    Item,
    SharedItem,
    paths_filtered_by_status,
)
from snovault.resource_views import item_view_object
from snovault.util import expand_path
from collections import defaultdict
from datetime import datetime
import math


ONLY_ADMIN_VIEW_DETAILS = [
    (Allow, 'group.admin', ['view', 'view_details', 'edit']),
    (Allow, 'group.read-only-admin', ['view', 'view_details']),
    (Allow, 'remoteuser.INDEXER', ['view']),
    (Allow, 'remoteuser.EMBED', ['view']),
    (Deny, Everyone, ['view', 'view_details', 'edit']),
]

USER_ALLOW_CURRENT = [
    (Allow, Everyone, 'view'),
] + ONLY_ADMIN_VIEW_DETAILS

USER_DELETED = [
    (Deny, Everyone, 'visible_for_edit')
] + ONLY_ADMIN_VIEW_DETAILS

def group_values_by_lab(request, labs):
    values_by_key = defaultdict(list)
    for path in labs:
        properties = request.embed(path, '@@object?skip_calculated=true')
        values_by_key[properties.get('lab')].append(properties)
    return dict(values_by_key)


def group_values_by_vital(request, vitals):
    values_by_key = defaultdict(list)
    for path in vitals:
        properties = request.embed(path, '@@object?skip_calculated=true')
        values_by_key[properties.get('vital')].append(properties)
    return dict(values_by_key)


def supportive_med_frequency(request, supportive_medication):
    frequency_by_key = defaultdict(list)
    supportive_meds = []
    for path in supportive_medication:
        properties = request.embed(path, '@@object?skip_calculated=true')
        start_date = properties.get('start_date')
        frequency_by_key[properties.get('name')].append(start_date)

    for k, v in frequency_by_key.items():
        med_freq = {}
        med_freq['name'] = k
        med_freq['start_date'] = min(v)
        med_freq['frequency'] = len(v)
        supportive_meds.append(med_freq)
    return supportive_meds


def last_follow_up_date_fun(request, labs, vitals, germline,ihc, consent,radiation,medical_imaging,medication,supportive_medication,surgery, death_date):
    if death_date is not None:
        last_follow_up_date = death_date
    else:
        all_traced_dates=[]
        if len(vitals) > 0:
            for path in vitals:
                properties = request.embed(path, '@@object?skip_calculated=true')
                vital_dates=properties.get("date")
                all_traced_dates.append(vital_dates)
        if len(labs) > 0:
            for path in labs:
                properties = request.embed(path, '@@object?skip_calculated=true')
                lab_dates=properties.get("date")
                all_traced_dates.append(lab_dates)
        if len(surgery) > 0:
            for path in surgery:
                properties = request.embed(path, '@@object?skip_calculated=true')
                sur_dates=properties.get("date")
                all_traced_dates.append(sur_dates)
        if len(germline) > 0:
            for path in germline:
                properties = request.embed(path, '@@object?skip_calculated=true')
                ger_dates=properties.get("service_date")
                all_traced_dates.append(ger_dates)
        if len(ihc) > 0:
            for path in ihc:
                properties = request.embed(path, '@@object?skip_calculated=true')
                ihc_dates=properties.get("service_date")
                all_traced_dates.append(ihc_dates)
        if len(radiation) > 0:
            for path in radiation:
                properties = request.embed(path, '@@object?skip_calculated=true')
                if 'end_date' in properties:
                    rad_dates=properties.get("end_date")
                else:
                    rad_dates=properties.get("start_date")
                all_traced_dates.append(rad_dates)
        if len(medical_imaging) > 0:
            for path in medical_imaging:
                properties = request.embed(path, '@@object?skip_calculated=true')
                med_img_dates=properties.get("procedure_date")
                all_traced_dates.append(med_img_dates)
        if len(medication) > 0:
            for path in medication:
                properties = request.embed(path, '@@object?skip_calculated=true')
                med_dates=properties.get("end_date")
                all_traced_dates.append(med_dates)
        if len(supportive_medication) > 0:
            for path in supportive_medication:
                properties = request.embed(path, '@@object?skip_calculated=true')
                sup_med_dates=properties.get("start_date")
                all_traced_dates.append(sup_med_dates)

        if len(all_traced_dates) > 0:
            all_traced_dates.sort(key = lambda date: datetime.strptime(date, "%Y-%m-%d"))
            last_follow_up_date = all_traced_dates[-1]
        else:
            last_follow_up_date = "Not available"

    return last_follow_up_date

def getLabsAndVitalsRange(value, low, high, normal, lowRange, normalRange, highRange):
    if value <= low:
        if lowRange == "default":
            return "Below (Below " + str(low) + ")"
        else:
            return lowRange
    elif value >= high:
        if highRange == "default":
            return "Above (Above " + str(high) + ")"
        else:
            return highRange        
    else:
        if normalRange == "default":
            return "Normal Range (" + normal + ")"
        else: 
            return normalRange


@collection(
     name='patients',
     unique_key='accession',
     properties={
         'title': 'Patients',
         'description': 'Listing Patients',
})
class Patient(Item):
    item_type = 'patient'
    schema = load_schema('encoded:schemas/patient.json')
    name_key = 'accession'
    embedded = [
        'labs',
        'vitals',
        'germline',
        'ihc',
        'consent',
        'radiation',
        'medical_imaging',
        'medications',
        'supportive_medications',
        'surgery',
        'surgery.surgery_procedure',
        'surgery.pathology_report',
        'biospecimen']
    rev = {
        'labs': ('LabResult', 'patient'),
        'vitals': ('VitalResult', 'patient'),
        'germline': ('Germline', 'patient'),
        'ihc': ('Ihc', 'patient'),
        'consent': ('Consent', 'patient'),
        'radiation': ('Radiation', 'patient'),
        'medical_imaging': ('MedicalImaging', 'patient'),
        'medication': ('Medication', 'patient'),
        'supportive_medication': ('SupportiveMedication', 'patient'),
        'surgery': ('Surgery', 'patient'),
        'biospecimen': ('Biospecimen', 'patient')
    }
    set_status_up = []
    set_status_down = []

    @calculated_property(schema={
        "title": "Last Follow-up Date",
        "description": "Calculated last follow-up date,format as YYYY-MM-DD",
        "type": "string",
    })
    def last_follow_up_date(self, request, labs, vitals, germline,ihc, consent,radiation,medical_imaging,medication,supportive_medication,surgery, death_date=None):
        return last_follow_up_date_fun(request, labs, vitals, germline,ihc, consent,radiation,medical_imaging,medication,supportive_medication,surgery, death_date)


    @calculated_property( schema={
        "title": "Labs",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "LabResult",
        },
    })
    def labs(self, request, labs):
        return group_values_by_lab(request, labs)

    @calculated_property( schema={
        "title": "Vitals",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "VitalResult",
        },
    })
    def vitals(self, request, vitals):
        return group_values_by_vital(request, vitals)

    @calculated_property(schema={
        "title": "Germline Mutations",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Germline"
        },
    })
    def germline(self, request, germline):
        return paths_filtered_by_status(request, germline)



    @calculated_property(condition='germline', schema={
        "title": "Positive Germline Mutations",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def germline_summary(self, request, germline):
        germline_summary = []
        for mutation in germline:
            mutatation_object = request.embed(mutation, '@@object')
            if mutatation_object['significance'] in ['Positive', 'Variant', 'Positive and Variant']:
                mutation_summary = mutatation_object['target']
                germline_summary.append(mutation_summary)
        return germline_summary

    @calculated_property(schema={
        "title":"IHC result",
        "type":"array",
        "items":{
            "type":'string',
            "linkTo":'ihc'
        }
    })

    def ihc(self,request,ihc):
        return paths_filtered_by_status(request,ihc)


    @calculated_property(schema={
        "title": "Radiation Treatment",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Radiation"
        },
    })
    def radiation(self, request, radiation):
        return paths_filtered_by_status(request, radiation)

    @calculated_property(define=True, schema={
        "title": "Radiation Treatment Summary",
        "type": "string",
    })
    def radiation_summary(self, request, radiation=None):
        if len(radiation) > 0:
            radiation_summary = "Treatment Received"
        else:
            radiation_summary = "No Treatment Received"
        return radiation_summary

    @calculated_property(define=True, schema={
        "title": "Metastasis status ",
        "type": "string",
    })
    def metastasis_status(self, request, radiation=None, surgery=None):
        status = "No"
        if len(radiation) > 0:

            for radiation_record in radiation:
                radiation_object = request.embed(radiation_record, '@@object')
                #site mapping
                if radiation_object['site_general'] != "Kidney, right" and radiation_object['site_general'] != "Kidney, thrombus" and radiation_object['site_general'] != "Kidney, left" and radiation_object['site_general'] != "Retroperitoneum / renal bed, left" and radiation_object['site_general'] != "Retroperitoneum / renal bed, right":
                    status = "Yes"
        else:
            if len(surgery) > 0:
                for surgery_record in surgery:
                    surgery_object = request.embed(surgery_record, '@@object')
                    path_reports = surgery_object['pathology_report']
                    if len(path_reports) > 0:
                        for path_report in path_reports:
                            path_report_obj = request.embed(path_report, '@@object')
                            if path_report_obj['path_source_procedure'] == 'path_metasis':
                                status = "Yes"
        return status

    @calculated_property(define=True, schema={
        "title": "Vital Status",
        "type": "string",
    })
    def vital_status(self, request, death_date=None):
        if death_date is None:
            vital_status = "Alive"
        else:
            vital_status = "Deceased"
        return vital_status


    @calculated_property(schema={
        "title": "Medical Imaging",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "MedicalImaging"
        },
    })
    def medical_imaging(self, request, medical_imaging):
        return paths_filtered_by_status(request, medical_imaging)


    @calculated_property(schema={
        "title": "Consent",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Consent"
        },
    })
    def consent(self, request, consent):
        return paths_filtered_by_status(request, consent)

    @calculated_property( schema={
        "title": "Medications",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "Medication",
        },
    })
    def medications(self, request, medication):
        return paths_filtered_by_status(request, medication)

    @calculated_property(condition='medication', schema={
        "title": "Medication duration",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def medication_range(self, request, medication):

        for med in medication:
            medication_object = request.embed(med, '@@object')
            date_format="%Y-%m-%d"
            start_date=datetime.strptime(medication_object['start_date'],date_format )
            end_date=datetime.strptime(medication_object['end_date'],date_format )
            medication_duration=(end_date-start_date).days/30

            medication_range=[]
            if 0<=medication_duration<3:
                medication_range.append("0-3 months")
            elif 3<=medication_duration<6:
                medication_range.append("3-6 months")
            elif 6<=medication_duration<9:
                medication_range.append("6-9 months")
            elif 9<=medication_duration<12:
                medication_range.append("9-12 months")
            elif 12<=medication_duration<18:
                medication_range.append("12-18 months")
            elif 18<=medication_duration<24:
                medication_range.append("18-24 months")
            elif 24<=medication_duration<30:
                medication_range.append("24-30 months")
            elif 30<=medication_duration<36:
                medication_range.append("30-36 months")
            elif 36<=medication_duration<48:
                medication_range.append("36-48 months")
            else :
                medication_range.append("48+ months")
        return medication_range


    @calculated_property( schema={
        "title": "Supportive Medications",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "SupportiveMedication",
        },
    })
    def supportive_medications(self, request, supportive_medication):
        return supportive_med_frequency(request, supportive_medication)


    @calculated_property(schema={
        "title": "Biospecimen",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Biospecimen"
        },
    })

    def biospecimen(self, request, biospecimen):
        return paths_filtered_by_status(request, biospecimen)


    @calculated_property( schema={
        "title": "Surgeries",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "Surgery",
        },
    })

    def surgery(self, request, surgery):
        return paths_filtered_by_status(request, surgery)


    @calculated_property(define=True, schema={
            "title": "Surgery Treatment Summary",
            "type": "string",
        })
    def surgery_summary(self, request, surgery=None):
            if len(surgery) > 0:
                surgery_summary = "Yes"
            else:
                surgery_summary = "No"
            return surgery_summary



    @calculated_property(schema={
        "title": "Diagnosis",
        "description": "Infomation related to diagnosis",
        "type": "object",
        "additionalProperties": False,
        "properties":{
            "first_treatment_date": {
                "title": "Date of First Treatment",
                "type": "string",
            },
            "diagnosis_date": {
                "title": "Diagnosis Date",
                "description": "Date of Diagnosis",
                "type": "string",
            },
            "diagnosis_source": {
                "title": "Diagnosis Source",
                "description": "The source of the diagnosis date",
                "type": "string",
            },
            "age": {
                "title": "Diagnosis age",
                "description": "The age of diagnosis.",
                "type": "string",
                "pattern": "^((unknown)|([1-8]?\\d)|(90 or above))$"
            },
            "age_unit": {
                "title": "Diagnosis age unit",
                "type": "string",
                "default": "year",
                "enum": [
                    "year"
                ]
            },
            "age_range": {
                "title": "Age at Diagnosis",
                "type": "string"
            },
            "follow_up_duration_range": {
                "title": "Follow Up Duration",
                "type": "string"

            }

        },
    })
    def diagnosis(self, request, surgery, radiation, medication,labs, vitals,
                    germline,ihc, consent,medical_imaging,supportive_medication, diagnosis_date_tumor_registry=None, death_date=None):
        non_mets_dates = []
        mets_dates = []
        non_surgery_dates = []
        diagnosis_date = "Not available"
        diagnosis_source = "Not applicable"

        # if there is Path report for Nephretomy or biopsy
        if len(surgery) > 0:
            for surgery_record in surgery:
                surgery_object = request.embed(surgery_record, '@@object')
                surgery_path_report = surgery_object['pathology_report']
                for path_report in surgery_path_report:
                    path_report_obj = request.embed(path_report, '@@object')
                    if path_report_obj['path_source_procedure'] == "path_nephrectomy" or path_report_obj['path_source_procedure'] == "path_biopsy":
                        non_mets_dates.append(surgery_object['date'])
                    elif  path_report_obj['path_source_procedure'] == "path_metasis":
                        mets_dates.append(surgery_object['date'])

        if len(non_mets_dates) > 0 :
            non_mets_dates.sort(key = lambda date: datetime.strptime(date, '%Y-%m-%d'))
            diagnosis_date = non_mets_dates[0]
            diagnosis_source = "Pathology report"
        elif diagnosis_date_tumor_registry is not None:
            diagnosis_date = diagnosis_date_tumor_registry
            diagnosis_source = "Tumor registry"
        elif len(mets_dates) > 0:
            mets_dates.sort(key = lambda date: datetime.strptime(date, '%Y-%m-%d'))
            diagnosis_date = mets_dates[0]
            diagnosis_source = "Pathology report"
        elif len(medication) > 0 or len(radiation) > 0:
            diagnosis_source = "Medication or radiation treatment"
            for medication_record in medication:
                medication_object = request.embed(medication_record, '@@object')
                non_surgery_dates.append(medication_object['start_date'])
            for radiation_record in radiation:
                radiation_object = request.embed(radiation_record, '@@object')
                non_surgery_dates.append(radiation_object['start_date'])
            non_surgery_dates.sort(key = lambda date: datetime.strptime(date, '%Y-%m-%d'))
            diagnosis_date = non_surgery_dates[0]

        age_range = "Unknown"
        ageString = "Unknown"
        follow_up_duration_range = "Not available"

        if diagnosis_date is not "Not available":
            birth_date = datetime.strptime("1800-01-01", "%Y-%m-%d")
            end_date = datetime.strptime(diagnosis_date, "%Y-%m-%d")
            age = end_date.year - birth_date.year -  ((end_date.month, end_date.day) < (birth_date.month, birth_date.day))
            ageString = str(age)

            # For age of diagnosis if age is about 90
            # we make this a string to represent
            if age >= 90:
                ageString = "90 or above"

            if age >= 80:
                age_range = "80+"
            elif age >= 60:
                age_range = "60 - 79"
            elif age >= 40:
                age_range = "40 - 59"
            elif age >= 20:
                age_range = "20 - 39"
            else:
                age_range = "0 - 19"

            #Add follow up duration:
            follow_up_start_date = datetime.strptime(diagnosis_date,"%Y-%m-%d")
            last_follow_up_date = last_follow_up_date_fun(request, labs, vitals, germline,ihc, consent,radiation,medical_imaging,medication, supportive_medication, surgery, death_date)
            if last_follow_up_date != "Not available":
                follow_up_end_date = datetime.strptime(last_follow_up_date,"%Y-%m-%d")
                follow_up_duration = (follow_up_end_date-follow_up_start_date).days/365

                if follow_up_duration >= 5:
                    follow_up_duration_range = "> 5 year"
                elif follow_up_duration >= 3:
                    follow_up_duration_range = "3 - 5 year"
                elif follow_up_duration >= 1.5:
                    follow_up_duration_range = "1.5 - 3 year"
                else:
                    follow_up_duration_range = "0 - 1.5 year"


        treatment_dates = []
        first_treatment_date = "Not available"
        #Get the first_treatment_date
        if len(surgery) > 0:
            for surgery_record in surgery:
                surgery_object = request.embed(surgery_record, '@@object')
                treatment_dates.append(surgery_object['date'])
        if len(radiation) > 0:
                # add radiation dates
                for radiation_record in radiation:
                    radiation_object = request.embed(radiation_record, '@@object')
                    treatment_dates.append(radiation_object['start_date'])
        if len(medication) > 0:
            # add medication dates
            for medication_record in medication:
                medication_object = request.embed(medication_record, '@@object')
                treatment_dates.append(medication_object['start_date'])
        if len(treatment_dates) > 0:
            treatment_dates.sort(key = lambda date: datetime.strptime(date, '%Y-%m-%d'))
            first_treatment_date = treatment_dates[0]

        diagnosis = dict()
        diagnosis['diagnosis_date'] = diagnosis_date
        diagnosis['diagnosis_source'] = diagnosis_source
        diagnosis['age'] = ageString
        diagnosis['age_unit'] = "year"
        diagnosis['age_range'] = age_range
        diagnosis['follow_up_duration_range'] = follow_up_duration_range
        diagnosis['first_treatment_date'] = first_treatment_date

        return diagnosis


    @calculated_property(schema={
        "title": "Labs and Vitals",
        "description": "Infomation related to Biometrics and Blood Work Within 30 days prior to Date of Nephrectomy",
        "type": "object",
        "additionalProperties": False,
        "properties":{
            "first_Nephrectomy_date_string": {
                "title": "Date of First Nephrectomy",
                "type": "string"
            },
            "BMI": {
                "title": "BMI",
                "description": "Most recent BMI value Within 30 days prior to Date of Nephrectomy",
                "type": "string",
                "enum": [
                    'Underweight (<18.4)',
                    'Normal (18.5-24.9)',
                    'Overweight (25-29.9)',
                    'Obese (>30)'
                ]
            },
            "BMIValue": {
                "title": "BMI Value",
                "type": "number"
            },
            "BMIDate": {
                "title": "Date of BMI",
                "type": "string"
            },
            "BP_Systolic": {
                "title": "BP_Systolic",
                "description": "Most recent BP_Systolic value Within 30 days prior to Date of Nephrectomy",
                "type": "string",
                "enum": [
                    'Normal (Below 120 mmHg)',
                    'PreHypertension (121 - 139 mmHg)',
                    'Hypertension (Above 140 mmHg)'
                ]
            },
            "BP_SystolicValue": {
                "title": "BP_Systolic Value",
                "type": "number"
            },
            "BP_SystolicDate": {
                "title": "Date of BP_Systolic",
                "type": "string"
            },
            "BP_Diastolic": {
                "title": "BP_Diastolic",
                "description": "Most recent BP_Diastolic value Within 30 days prior to Date of Nephrectomy",
                "type": "string",
                "enum": [
                    'Normal (Below 80 mmHg)',
                    'PreHypertension (81 - 89)',
                    'Hypertension (Above 90)'
                ]
            },
            "BP_DiastolicValue": {
                "title": "BP_Diastolic Value",
                "type": "number"
            },
            "BP_DiastolicDate": {
                "title": "Date of BP_Diastolic",
                "type": "string"
            },
            "Hemoglobin": {
                "title": "Hemoglobin",
                "description": "Most recent Hemoglobin value Within 30 days prior to Date of Nephrectomy",
                "type": "string",
                "enum": [
                    'Below (9-12.3)',
                    'Normal (12.4-17.3 g/dL)',
                    'Above (Above 17.4)'
                ]
            },
            "HemoglobinValue": {
                "title": "Hemoglobin Value",
                "type": "number"
            },
            "HemoglobinDate": {
                "title": "Date of Hemoglobin",
                "type": "string"
            },
            "Platelets": {
                "title": "Platelets",
                "description": "Most recent Platelets value Within 30 days prior to Date of Nephrectomy",
                "type": "string",
                "enum": [
                    'Below (12-140)',
                    'Normal Range (140-450 10^3/ul)',
                    'Above (Above 450)'
                ]
            },
            "PlateletsValue": {
                "title": "Platelets Value",
                "type": "number"
            },
            "PlateletsDate": {
                "title": "Date of Platelets",
                "type": "string"
            },
            "WBC": {
                "title": "WBC",
                "description": "Most recent WBC value Within 30 days prior to Date of Nephrectomy",
                "type": "string",
                "enum": [
                    'Below (3.9)',
                    'Normal Range (4-10.9 10^3/ul)',
                    'Above (Above 11)'
                ]
            },
            "WBCValue": {
                "title": "WBC Value",
                "type": "number"
            },
            "WBCDate": {
                "title": "Date of WBC",
                "type": "string"
            },
            "Neutrophils": {
                "title": "Neutrophils",
                "description": "Most recent Neutrophils value Within 30 days prior to Date of Nephrectomy",
                "type": "string",
                "enum": [
                    'Below (1.4)',
                    'Normal Range (1.5-7.3 10^3/ul)',
                    'Above ( Above 7.4)'
                ]
            },
            "NeutrophilsValue": {
                "title": "Neutrophils Value",
                "type": "number"
            },
            "NeutrophilsDate": {
                "title": "Date of Neutrophils",
                "type": "string"
            },
            "Creatinine": {
                "title": "Creatinine",
                "description": "Most recent Creatinine value Within 30 days prior to Date of Nephrectomy",
                "type": "string",
                "enum": [
                    'Below (0.66)',
                    'Normal Range (0.67-1.16 mg/dL)',
                    'Above (Above 1.17)'
                ]
            },
            "CreatinineValue": {
                "title": "Creatinine Value",
                "type": "number"
            },
            "CreatinineDate": {
                "title": "Date of Creatinine",
                "type": "string"
            },
            "Calcium": {
                "title": "Calcium",
                "description": "Most recent Calcium value Within 30 days prior to Date of Nephrectomy",
                "type": "string",
                "enum": [
                    'Below (8.7)',
                    'Normal Range (8.8-10.1 mg/dL)',
                    'Above (Above 10.2)'
                ]
            },
            "CalciumValue": {
                "title": "Calcium Value",
                "type": "number"
            },
            "CalciumDate": {
                "title": "Date of Calcium",
                "type": "string"
            },
            "Albumin": {
                "title": "Albumin",
                "description": "Most recent Albumin value Within 30 days prior to Date of Nephrectomy",
                "type": "string",
                "enum": [
                    'Below (3.4)',
                    'Normal Range (3.5-5.2 g/dL)',
                    'Above (5.3)'
                ]
            },
            "AlbuminValue": {
                "title": "Albumin Value",
                "type": "number"
            },
            "AlbuminDate": {
                "title": "Date of Albumin",
                "type": "string"
            },
            "Sodium": {
                "title": "Sodium",
                "description": "Most recent Sodium value Within 30 days prior to Date of Nephrectomy",
                "type": "string",
                "enum": [
                    'Below (134)',
                    'Normal Range (135-145 mmol/L)',
                    'Above (146)'
                ]
            },
            "SodiumValue": {
                "title": "Sodium Value",
                "type": "number"
            },
            "SodiumDate": {
                "title": "Date of Sodium",
                "type": "string"
            },
            "LDH": {
                "title": "LDH",
                "description": "Most recent LDH value Within 30 days prior to Date of Nephrectomy",
                "type": "string",
                "enum": [
                    'Below (134)',
                    'Normal Range (135-225 U/L)',
                    'Above (225)'
                ]
            },
            "LDHValue": {
                "title": "LDH Value",
                "type": "number"
            },
            "LDHDate": {
                "title": "Date of LDH",
                "type": "string"
            }

        },
    })
    def labs_and_vitals(self, request, surgery,labs, vitals):
        nephrectomy_dates = []
        first_Nephrectomy_date_string = "Not Available"
        labs_and_vitals = {
            'first_Nephrectomy_date_string': "Not Available",
            'BMI': "Not Available",
            'BP_Systolic': "Not Available",
            'BP_Diastolic': "Not Available",
            'Hemoglobin': "Not Available",
            'Platelets': "Not Available",
            'WBC': "Not Available",
            'Neutrophils': "Not Available",
            'Creatinine': "Not Available",
            'Calcium': "Not Available",
            'Albumin': "Not Available",
            'Sodium': "Not Available",
            'LDH': "Not Available"
        }
        labs_and_vitals['first_Nephrectomy_date_string'] = first_Nephrectomy_date_string
        # find the first Nephrectomy 
        if len(surgery) > 0:
            for surgery_record in surgery:
                surgery_object = request.embed(surgery_record, '@@object')
                surgery_procedures = surgery_object['surgery_procedure']
                for surgery_procedure in surgery_procedures:
                    surgery_procedure_obj = request.embed(surgery_procedure, '@@object')
                    if surgery_procedure_obj['procedure_type'] == "Nephrectomy":
                        nephrectomy_dates.append(surgery_object['date'])
            #compare the date to get the first date if there is nephrectomy_dates
            if len(nephrectomy_dates)> 0:
                nephrectomy_dates.sort(key = lambda date: datetime.strptime(date, '%Y-%m-%d'))
                first_Nephrectomy_date_string = nephrectomy_dates[0]
                first_Nephrectomy_date = datetime.strptime(first_Nephrectomy_date_string, '%Y-%m-%d')
                labs_and_vitals['first_Nephrectomy_date_string'] = first_Nephrectomy_date_string

                #find dates Within 30 days prior to Date of Nephrectomy
                if len(labs)>0:             
                    albuminList = []                
                    calciumList = []
                    creatinineList = []
                    hemoglobinList = []
                    ldhList = []
                    neutrophilsList = []
                    plateletsList = []
                    sodiumList = []
                    wbcList = []

                    for path in labs:
                        properties = request.embed(path, '@@object?skip_calculated=true')
                        lab_date_string = properties.get("date")
                        #compare the date
                        lab_date = datetime.strptime(lab_date_string, '%Y-%m-%d')
                        if (first_Nephrectomy_date - lab_date).days < 30 and (first_Nephrectomy_date - lab_date).days >= 0:
                            lab_type = properties.get("lab")
                            lab_value = properties.get("value")
                            lab = {
                                "date": lab_date_string,
                                "value": lab_value
                            }
                            if lab_type == "ALBUMIN":
                                albuminList.append(lab)              
                            elif lab_type == "CALCIUM":
                                calciumList.append(lab)
                            elif lab_type == "CREATININE":
                                creatinineList.append(lab)
                            elif lab_type == "HEMOGLOBIN":
                                hemoglobinList.append(lab)
                            elif lab_type == "LACTATE_DE":
                                ldhList.append(lab)
                            elif lab_type == "NEUTROPHILS":
                                neutrophilsList.append(lab)
                            elif lab_type == "PLATELETS":
                                plateletsList.append(lab)
                            elif lab_type == "SODIUM":
                                sodiumList.append(lab)
                            else:
                                wbcList.append(lab)
                    if len(albuminList) > 0:
                        albuminList.sort(key = lambda lab: datetime.strptime(lab["date"], '%Y-%m-%d')) 
                        albuminLab = albuminList[-1]  
                        labs_and_vitals["Albumin"] = getLabsAndVitalsRange(albuminLab["value"], 3.4, 5.3, "3.5-5.2 g/dL", "default", "default", "default") 
                        labs_and_vitals["AlbuminValue"] = albuminLab["value"]
                        labs_and_vitals["AlbuminDate"] = albuminLab["date"]
                    if len(calciumList) > 0:
                        calciumList.sort(key = lambda lab: datetime.strptime(lab["date"], '%Y-%m-%d')) 
                        calciumLab = calciumList[-1]  
                        labs_and_vitals["Calcium"] = getLabsAndVitalsRange(calciumLab["value"], 8.7, 10.2, "8.8-10.1 mg/dL", "default", "default", "default")    
                        labs_and_vitals["CalciumValue"] = calciumLab["value"]
                        labs_and_vitals["CalciumDate"] = calciumLab["date"]
                    if len(creatinineList) > 0:
                        creatinineList.sort(key = lambda lab: datetime.strptime(lab["date"], '%Y-%m-%d')) 
                        creatinineLab = creatinineList[-1] 
                        labs_and_vitals["Creatinine"] = getLabsAndVitalsRange(creatinineLab["value"], 0.66, 1.17, "0.67-1.16 mg/dL", "default", "default", "default")
                        labs_and_vitals["CreatinineValue"] = creatinineLab["value"]
                        labs_and_vitals["CreatinineDate"] = creatinineLab["date"]
                    if len(hemoglobinList) > 0:
                        hemoglobinList.sort(key = lambda lab: datetime.strptime(lab["date"], '%Y-%m-%d')) 
                        hemoglobinLab = hemoglobinList[-1]
                        labs_and_vitals["Hemoglobin"] = getLabsAndVitalsRange(hemoglobinLab["value"], 12.3, 17.4, "12.4-17.3 g/dL", "default", "default", "default")
                        labs_and_vitals["HemoglobinValue"] = hemoglobinLab["value"]
                        labs_and_vitals["HemoglobinDate"] = hemoglobinLab["date"]
                    if len(ldhList) > 0:
                        ldhList.sort(key = lambda lab: datetime.strptime(lab["date"], '%Y-%m-%d')) 
                        ldhLab = ldhList[-1]
                        labs_and_vitals["LDH"] = getLabsAndVitalsRange(ldhLab["value"], 134, 225, "135-224 U/L", "default", "default", "default")
                        labs_and_vitals["LDHValue"] = ldhLab["value"]
                        labs_and_vitals["LDHDate"] = ldhLab["date"]
                    if len(neutrophilsList) > 0:
                        neutrophilsList.sort(key = lambda lab: datetime.strptime(lab["date"], '%Y-%m-%d')) 
                        neutrophilsLab = neutrophilsList[-1]
                        labs_and_vitals["Neutrophils"] = getLabsAndVitalsRange(neutrophilsLab["value"], 1.4, 7.4, "1.5-7.3 10^3/ul", "default", "default", "default")
                        labs_and_vitals["NeutrophilsValue"] = neutrophilsLab["value"]
                        labs_and_vitals["NeutrophilsDate"] = neutrophilsLab["date"]
                    if len(plateletsList) > 0:
                        plateletsList.sort(key = lambda lab: datetime.strptime(lab["date"], '%Y-%m-%d')) 
                        plateletsLab = plateletsList[-1]
                        labs_and_vitals["Platelets"] = getLabsAndVitalsRange(plateletsLab["value"], 139, 449, "140-450 10^3/ul", "default", "default", "default")
                        labs_and_vitals["PlateletsValue"] = plateletsLab["value"]
                        labs_and_vitals["PlateletsDate"] = plateletsLab["date"]
                    if len(sodiumList) > 0:
                        sodiumList.sort(key = lambda lab: datetime.strptime(lab["date"], '%Y-%m-%d')) 
                        sodiumLab = sodiumList[-1]
                        labs_and_vitals["Sodium"] = getLabsAndVitalsRange(sodiumLab["value"], 134, 146, "135-145 mmol/L", "default", "default", "default")
                        labs_and_vitals["SodiumValue"] = sodiumLab["value"]
                        labs_and_vitals["SodiumDate"] = sodiumLab["date"]
                    if len(wbcList) > 0:
                        wbcList.sort(key = lambda lab: datetime.strptime(lab["date"], '%Y-%m-%d')) 
                        wbcLab = wbcList[-1]
                        labs_and_vitals["WBC"] = getLabsAndVitalsRange(wbcLab["value"], 3.9, 11, "4-10.9 10^3/ul", "default", "default", "default")
                        labs_and_vitals["WBCValue"] = wbcLab["value"]
                        labs_and_vitals["WBCDate"] = wbcLab["date"]
                if len(vitals)>0 :
                    bmiList = []
                    bp_SystolicList = []
                    bp_DiastolicList = []
                    for path in vitals:
                        properties = request.embed(path, '@@object?skip_calculated=true')
                        vital_date_string = properties.get("date")
                        #compare the date
                        vital_date = datetime.strptime(vital_date_string, '%Y-%m-%d')
                        if (first_Nephrectomy_date - vital_date).days <30 and (first_Nephrectomy_date - vital_date).days >= 0:
                            vital_type = properties.get("vital")
                            vital_value = properties.get("value")
                            vital = {
                                "date": vital_date_string,
                                "value": vital_value
                            }

                            if vital_type == "BMI":
                                bmiList.append(vital)              
                            elif vital_type == "BP_DIAS":
                                bp_DiastolicList.append(vital)
                            elif vital_type == "BP_SYS":
                                bp_SystolicList.append(vital)    
                    if len(bmiList) > 0:     
                        bmiList.sort(key = lambda vital: datetime.strptime(vital["date"], '%Y-%m-%d')) 
                        bmiVital = bmiList[-1]
                        labs_and_vitals["BMIValue"] = bmiVital["value"]
                        labs_and_vitals["BMIDate"] = bmiVital["date"] 
                        if bmiVital["value"] <= 18.4:
                            labs_and_vitals["BMI"] = "Underweight (Below 18.4)"
                        elif bmiVital["value"] <= 24.9:
                            labs_and_vitals["BMI"] = "Normal (18.5-24.9)"
                        elif bmiVital["value"] <= 29.9:
                            labs_and_vitals["BMI"] = "Overweight (25-29.9)"
                        else:
                            labs_and_vitals["BMI"] = "Obese (Above 30)"
                    if len(bp_SystolicList) > 0:
                        bp_SystolicList.sort(key = lambda vital: datetime.strptime(vital["date"], '%Y-%m-%d')) 
                        bp_SystolicVital = bp_SystolicList[-1] 
                        labs_and_vitals["BP_Systolic"] = getLabsAndVitalsRange(bp_SystolicVital["value"], 120, 140, "121 - 139 mmHg", 'Normal (Below 120)', 'PreHypertension (121 - 139 mmHg)', 'Hypertension (Above 140)')
                        labs_and_vitals["BP_SystolicValue"] = bp_SystolicVital["value"]
                        labs_and_vitals["BP_SystolicDate"] = bp_SystolicVital["date"] 
                    if len(bp_DiastolicList) > 0:
                        bp_DiastolicList.sort(key = lambda vital: datetime.strptime(vital["date"], '%Y-%m-%d')) 
                        bp_DiastolicVital = bp_DiastolicList[-1]  
                        labs_and_vitals["BP_Diastolic"] = getLabsAndVitalsRange(bp_DiastolicVital["value"], 80, 90, "81 - 89 mmHg", 'Normal (Below 80)', 'PreHypertension (81 - 89 mmHg)', 'Hypertension (Above 90)')
                        labs_and_vitals["BP_DiastolicValue"] = bp_DiastolicVital["value"]
                        labs_and_vitals["BP_DiastolicDate"] = bp_DiastolicVital["date"] 

        return labs_and_vitals



    @calculated_property(schema={
        "title": "Metastasis",
        "description": "Infomation related to Metastasis",
        "type": "array",
        "items": {
            "title": "Metastasis Record",
            "type": "object",
            "additionalProperties": False,
            "properties":{
                "date": {
                    "title": "Date of Metastasis Record",
                    "description": "Date of Metastasis Record",
                    "type": "string"
                },
                "histology_proven": {
                    "title": "Histology Proven",
                    "type": "string"
                },
                "source": {
                    "title": "Source",
                    "description": "Source of the record",
                    "type": "string",
                    "enum": [
                        "Pathology report",
                        "Radiation treatment"
                    ]
                },
                "site": {
                    "title": "Metastasis Site",
                    "type": "string",
                    "enum": [
                        "Adrenal",
                        "Bone",
                        "Brain",
                        "Liver",
                        "Lung and pleura",
                        "Lymph node",
                        "Other"
                    ]
                }

            },
        }
    })
    def metastasis(self, request, surgery, radiation):
        records = []
        if len(surgery) > 0:
            for surgery_record in surgery:
                surgery_object = request.embed(surgery_record, '@@object')
                path_reports = surgery_object['pathology_report']
                if len(path_reports) > 0:
                    for path_report in path_reports:
                        path_report_obj = request.embed(path_report, '@@object')
                        if path_report_obj['path_source_procedure'] == 'path_metasis':
                            site = path_report_obj['metasis_details']['site']
                            if site == "Lung":
                                site = "Lung and pleura"
                            record = {
                                'date': path_report_obj['date'],
                                'source': 'Pathology report',
                                'site': site,
                                'histology_proven': 'Yes'
                            }
                            if record not in records:
                                records.append(record)
        if len(radiation) > 0 :
            for radiation_record in radiation:
                radiation_object = request.embed(radiation_record, '@@object')
                #site mapping
                if radiation_object['site_general'] == "Adrenal gland, left" or radiation_object['site_general'] == "Adrenal gland, right":
                    radiation_site = "Adrenal"
                elif radiation_object['site_general'] == "Spine" or radiation_object['site_general'] == "Bone":
                    radiation_site = "Bone"
                elif radiation_object['site_general'] == "Brain" or radiation_object['site_general'] == "Liver":
                    radiation_site = radiation_object['site_general']
                elif radiation_object['site_general'] == "Connective, subcutaneous and other soft tissues, NOS" or radiation_object['site_general'] == "Retroperitoneum & peritoneum" or radiation_object['site_general'] == "Connective, subcutaneous and other soft tissue, abdomen" or radiation_object['site_general'] == "Gastrointestine/ digestive system & spleen" or radiation_object['site_general'] == "Salivary gland":
                    radiation_site = "Other"
                elif radiation_object['site_general'] == "Lung, right" or radiation_object['site_general'] == "Lung, left" or radiation_object['site_general'] == "Lung":
                    radiation_site = "Lung and pleura"
                elif radiation_object['site_general'] == "Lymph node, NOS" or radiation_object['site_general'] == "Lymph node, intrathoracic" or radiation_object['site_general'] == "Lymph node, intra abdominal":
                    radiation_site = "Lymph node"

                record = {
                    'date': radiation_object['start_date'],
                    'source': 'Radiation treatment',
                    'site': radiation_site,
                    'histology_proven': 'No'
                }
                if record not in records:
                    records.append(record)

        return records


    matrix = {
        'y': {
            'facets': [
                'status',
                'sex',
                'race',
                'ethnicity',
                'surgery_summary',
                'radiation_summary',
                'medications.name',
                'surgery.surgery_procedure.surgery_type',
                'surgery.hospital_location',
                'surgery.pathology_report.tumor_size_range',
                'surgery.pathology_report.ajcc_p_stage',
                'surgery.pathology_report.n_stage',
                'surgery.pathology_report.m_stage',
                'surgery.pathology_report.ajcc_tnm_stage',
                'germline_summary',
                'ihc.antibody',
                'ihc.result',
            ],
            'group_by': ['race', 'sex'],
            'label': 'race',
        },
        'x': {
            'facets': [

                'surgery.pathology_report.histology',
            ],
            'group_by': 'surgery.pathology_report.histology',
            'label': 'histology',
        },
    }

    summary_data = {
        'y': {
            'facets': [

                'status',
                'sex',
                'race',
                'radiation_summary',

            ],
            'group_by': ['sex', 'radiation_summary'],
            'label': 'Sex',
        },
        'x': {
            'facets': [
                'race',
            ],
            'group_by': 'race',
            'label': 'Race',
        },
        'grouping': ['sex', 'status'],
    }



    @calculated_property(condition='surgery', schema={
        "title": "surgery procedure nephrectomy robotic assist",
        "type": "array",
        "items": {
            "type": "string",
        },
    })

    def sur_nephr_robotic_assist(self, request, surgery):

        sp_obj_array = []
        array=[]
        if surgery is not None:
            for so in surgery:
                so_object = request.embed(so, "@@object")
                sp_obj_array = so_object.get("surgery_procedure")

                if sp_obj_array is not None:
                    for spo in sp_obj_array:
                        sp_obj = request.embed(spo, "@@object")
                        sp_proc_type=sp_obj.get("procedure_type")
                        if sp_proc_type=="Nephrectomy":
                            sp_nephr_robotic=sp_obj.get("nephrectomy_details").get("robotic_assist")
                            array.append(sp_nephr_robotic)
                        else:
                            continue

        robotic_assist=[]

        for logic in array:
            if  logic is True:
                robotic_assist.append("Yes")
            else:
                robotic_assist.append("No")
        return robotic_assist


    @calculated_property(condition='surgery', schema={
        "title": "surgery pathology tumor size calculation",
        "type": "array",
        "items": {
            "type": "string",
        },
    })

    def sur_path_tumor_size(self, request, surgery):


        sp_obj_array = []
        array=[]
        if surgery is not None:
            for so in surgery:
                so_object = request.embed(so, "@@object")
                sp_obj_array = so_object.get("pathology_report")

                if sp_obj_array is not None:
                    for spo in sp_obj_array:
                        sp_obj = request.embed(spo, "@@object")
                        sp_tumor_size=sp_obj.get("tumor_size")

                        array.append(sp_tumor_size)

        tumor_size_range = []
        for tumor_size in array:
            if tumor_size is not None:
                if 0 <= tumor_size < 3:
                    tumor_size_range.append("0-3 cm")
                elif 3 <= tumor_size < 7:
                    tumor_size_range.append("3-7 cm")
                elif 7 <= tumor_size < 10:
                    tumor_size_range.append("7-10 cm")
                else:
                    tumor_size_range.append("10+ cm")
        return tumor_size_range


@collection(
    name='lab-results',
    properties={
        'title': 'Lab results',
        'description': 'Lab results pages',
    })
class LabResult(Item):
    item_type = 'lab_results'
    schema = load_schema('encoded:schemas/lab_results.json')
    embeded = []


@collection(
    name='vital-results',
    properties={
        'title': 'Vital results',
        'description': 'Vital results pages',
    })
class VitalResult(Item):
    item_type = 'vital_results'
    schema = load_schema('encoded:schemas/vital_results.json')
    embeded = []


@collection(
    name='germline',
    properties={
        'title': 'Germline Mutations',
        'description': 'Germline Mutation results pages',
    })
class Germline(Item):
    item_type = 'germline'
    schema = load_schema('encoded:schemas/germline.json')
    embeded = []


@collection(
    name='ihc',
    properties={
        'title': 'IHC results',
        'description': 'IHC results pages',
    })
class Ihc(Item):
    item_type = 'ihc'
    schema = load_schema('encoded:schemas/ihc.json')
    embeded = []

@collection(
    name='consent',
    properties={
        'title': 'Consent',
        'description': 'Consent results pages',
    })
class Consent(Item):
    item_type = 'consent'
    schema = load_schema('encoded:schemas/consent.json')
    embeded = []


@collection(
    name='radiation',
    properties={
        'title': 'Radiation treatment',
        'description': 'Radiation treatment results pages',
    })
class Radiation(Item):
    item_type = 'radiation'
    schema = load_schema('encoded:schemas/radiation.json')
    embeded = []

    @calculated_property(condition='dose', schema={
        "title": "Dosage per Fraction",
        "type": "number",
    })
    def dose_per_fraction(self, request, dose, fractions):
        dose_per_fraction = dose/fractions
        return dose_per_fraction

    @calculated_property(condition='dose', schema={
        "title": "Dosage range per fraction",
        "type": "string",

    })
    def dose_range(self, request, dose, fractions):
        dose_per_fraction = dose/fractions
        if dose_per_fraction < 2000:
            return "200 - 2000"
        elif dose_per_fraction < 4000:
            return "2000 - 4000"
        else:
            return "4000 - 6000"

    @calculated_property(condition='fractions', schema={
        "title": "Fractions range",
        "type": "string",

    })
    def fractions_range(self, request, fractions):

        if fractions < 5:
            return "1 - 5"
        elif fractions < 10:
            return "5 - 10"
        elif fractions < 15:
            return "10 - 15"
        else:
            return "15 and up"




@collection(
    name='medical_imaging',
    properties={
        'title': 'Medical imaging',
        'description': 'Medical imaging results pages',
    })
class MedicalImaging(Item):
    item_type = 'medical-imaging'
    schema = load_schema('encoded:schemas/medical_imaging.json')
    embeded = []


@collection(
    name='medication',
    properties={
        'title': 'Medications',
        'description': 'Medication results pages',
    })
class Medication(Item):
    item_type = 'medication'
    schema = load_schema('encoded:schemas/medication.json')
    embeded = []


@collection(
    name='supportive-medication',
    properties={
        'title': 'Supportive Medications',
        'description': 'Supportive Medication results pages',
    })
class SupportiveMedication(Item):
    item_type = 'supportive_medication'
    schema = load_schema('encoded:schemas/supportive_medication.json')
    embeded = []


@property
def __name__(self):
    return self.name()


@view_config(context=Patient, permission='view', request_method='GET', name='page')
def patient_page_view(context, request):
    if request.has_permission('view_details'):
        properties = item_view_object(context, request)
    else:
        item_path = request.resource_path(context)
        properties = request.embed(item_path, '@@object')
    for path in context.embedded:
        expand_path(request, properties, path)
    return properties


@view_config(context=Patient, permission='view', request_method='GET',
             name='object')
def patient_basic_view(context, request):
    properties = item_view_object(context, request)
    filtered = {}
    for key in ['@id', '@type', 'accession', 'uuid', 'sex', 'ethnicity', 'race', 'diagnosis', 'last_follow_up_date', 'status',  'ihc','labs', 'vitals', 'germline', 'germline_summary','radiation', 'radiation_summary', 'vital_status', 'medical_imaging',
                'medications','medication_range', 'supportive_medications', 'biospecimen', 'surgery_summary','sur_nephr_robotic_assist']:
        try:
            filtered[key] = properties[key]
        except KeyError:
            pass
    return filtered

