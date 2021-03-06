import React from 'react';
import PropTypes from 'prop-types';
import { Panel, PanelBody, PanelHeading } from '../libs/ui/panel';
import * as globals from './globals';
import { ItemAccessories } from './objectutils';
import { Breadcrumbs } from './navigation';
import Status from './status';
import CollapsiblePanel from './collapsiblePanel';
import { PanelLookup } from './objectutils';
import GenomicsTable from './genomicsTable';
import IHCTable from './ihcTable';



class Biospecimen extends React.Component {
    constructor(props) {
        super(props);


    }
    createSurgeryTable(){
        const context = this.props.context;
        let list = []
        if (context.surgery && context.surgery.surgery_procedure) {
            for(let i = 0; i < context.surgery.surgery_procedure.length; i++){
                list.push(<div data-test="surgery.surgery_procedure"><dt>Surgery Procedure</dt><dd>{context.surgery.surgery_procedure[i].procedure_type}</dd> </div>)
            }
        }

        return list
      }

      createPathTable(){
        const context = this.props.context;
        let list = []
        if (context.surgery && context.surgery.pathology_report) {

            for(let i = 0; i < context.surgery.pathology_report.length; i++){
                list.push(<div className="row" style={{ borderTop: "1px solid #151313" }}></div>)
                list.push(<div data-test="surgery.pathology_report"><dt>Pathology Report</dt><dd><a href={context.surgery.pathology_report[i]['@id']}>{context.surgery.pathology_report[i].accession}</a></dd> </div>)
                list.push(<div data-test="surgery.pathology_report"><dt>Histologic Subtype</dt><dd>{context.surgery.pathology_report[i].histology}</dd> </div>)
                if (context.surgery.pathology_report[i].t_stage) {
                    list.push(<div data-test="surgery.pathology_report"><dt>pT Stage</dt><dd>{context.surgery.pathology_report[i].t_stage}</dd> </div>)
                }
                if (context.surgery.pathology_report[i].n_stage) {
                    list.push(<div data-test="surgery.pathology_report"><dt>pN Stage</dt><dd>{context.surgery.pathology_report[i].n_stage}</dd> </div>)
                }
                if (context.surgery.pathology_report[i].m_stage) {
                    list.push(<div data-test="surgery.pathology_report"><dt>pM Stage</dt><dd>{context.surgery.pathology_report[i].m_stage}</dd> </div>)
                }
                if (context.surgery.pathology_report[i].ajcc_version){
                    list.push(<div data-test="surgery.pathology_report"><dt>AJCC Version</dt><dd>{context.surgery.pathology_report[i].ajcc_version}</dd> </div>)
                }


            }
        }

        return list
      }


    render() {
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'view-item');
        // Set up breadcrumbs
        const crumbs = [
            { id: 'Biospecimens' },
            { id: <i>{context.accession}</i> },
        ];
        const crumbsReleased = (context.status === 'released');
        let hasGenomics =false;
        if (Object.keys(this.props.context.biolibrary).length > 0) {
            hasGenomics = true;
        }
        let hasIHC=false;
        if (Object.keys(this.props.context.ihc).length > 0) {
            hasIHC = true;
          }
        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <Breadcrumbs root="/search/?type=Biospecimen" crumbs={crumbs} crumbsReleased={crumbsReleased} />
                        <h2>{context.accession}</h2>
                    </div>

                </header>

                <Panel>
                    <PanelBody addClasses="panel__split">
                        <div className="panel__split-element">
                            <div className="panel__split-heading panel__split-heading--experiment">
                                <h4>Specimen Information</h4>
                            </div>

                            <dl className="key-value">
                                <div data-test="status">
                                    <dt>Status</dt>
                                    <dd><Status item={context} inline /></dd>
                                </div>
                                <div data-test="openspecimen_id">
                                    <dt>OpenSpecimen ID</dt>
                                    <dd>{context.openspecimen_id}</dd>
                                </div>
                                <div data-test="specimen_label">
                                    <dt>Specimen Label</dt>
                                    <dd>{context.specimen_label}</dd>
                                </div>
                                <div data-test="patient">
                                    <dt>Patient</dt>
                                    <dd><a href={context.patient}>{context.patient.split("/")[2]}</a></dd>
                                </div>
                                <div data-test="collection_date">
                                    <dt>Collection Date</dt>
                                    <dd>{context.collection_date}</dd>
                                </div>
                                <div data-test="sample_type">
                                    <dt>Sample Type</dt>
                                    <dd>{context.sample_type}</dd>
                                </div>

                                <div data-test="tissue_derivatives">
                                    <dt>Tissue Derivatives</dt>
                                    <dd>{context.tissue_derivatives}</dd>
                                </div>
                                <div data-test="species">
                                    <dt>Species</dt>
                                    <dd>{context.species}</dd>
                                </div>
                                {context.originated_from && <div data-test="originated_from">
                                    <dt>Originated From</dt>
                                    <dd><a href={context.originated_from}>{context.originated_from.split("/")[2]}</a></dd>
                                </div>}
                                {context.tissue_type && <div data-test="tissue_type">
                                    <dt>Specimen Pathological Type</dt>
                                    <dd>{context.tissue_type}</dd>
                                </div>}
                                {context.anatomic_site && <div data-test="anatomic_site">
                                    <dt>Anatomic Site</dt>
                                    <dd>{context.anatomic_site}</dd>
                                </div>}
                                {context.primary_site && <div data-test="primary_site">
                                    <dt>Primary Site</dt>
                                    <dd>{context.primary_site}</dd>
                                </div>}
                                <div data-test="specimen_lineage">
                                    <dt>Specimen Lineage</dt>
                                    <dd>{context.specimen_lineage}</dd>
                                </div>
                                <div data-test="activity_status">
                                    <dt>Activity Status</dt>
                                    <dd>{context.activity_status}</dd>
                                </div>
                            </dl>
                        </div>

                        <div className="panel__split-element">
                            <div className="panel__split-heading panel__split-heading--experiment">
                                <h4>Case Diagnosis</h4>
                            </div>
                            {context.surgery && <dl className="key-value">
                                {context.surgery && <div data-test="surgery">
                                    <dt>Surgery</dt>
                                    <dd><a href={context.surgery['@id']}>{context.surgery.accession}</a></dd>
                                </div>}
                                {this.createPathTable()}
                            </dl>}
                        </div>
                    </PanelBody>
                </Panel>
                {/* { hasGenomics && <GenomicsTable data={context.biolibrary} tableTitle="Genomics for this specimen"></GenomicsTable>} */}
                {hasIHC&&<IHCTable data={context.ihc} tableTitle="IHC Assay Staining Results"></IHCTable>}

                {false &&
                    <div>
                        {PanelLookup({ context: context.patient, biospecimen: context })}
                    </div>}


            </div>
        )
    }
}

globals.contentViews.register(Biospecimen, 'Biospecimen');
