import React from 'react';
import PropTypes from 'prop-types';
import queryString from 'query-string';
import url from 'url';
import * as encoding from '../libs/query_encoding';
import QueryString from '../libs/query_string';
import { Panel, PanelBody } from '../libs/ui/panel';
import { LabChart, CategoryChart, ExperimentDate, createBarChart } from './award';
import * as globals from './globals';
import { FacetList, ClearFilters } from './search';
import { getObjectStatuses, sessionToAccessLevel } from './status';
import { ViewControls } from './view_controls';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faHospitalUser } from "@fortawesome/free-solid-svg-icons";
import { faVial } from "@fortawesome/free-solid-svg-icons";
import { faDna } from "@fortawesome/free-solid-svg-icons";
import { faDisease } from "@fortawesome/free-solid-svg-icons";
import SummaryChart from "./summaryChart";


/**
 * Generate an array of data from one facet bucket for displaying in a chart, with one array entry
 * per experiment status. The order of the entries in the resulting array correspond to the order
 * of the statuses in `labels`.
 *
 * @param {array} buckets - Buckets for one facet returned in summary search results.
 * @param {array} labels - Experiment status labels.
 * @return {array} - Data extracted from buckets with an order of values corresponding to `labels`.
 */
function generateStatusData(buckets, labels) {
    // Fill the array to the proper length with zeroes to start with. Actual non-zero data will
    // overwrite the appropriate entries.
    const statusData = Array.from({ length: labels.length }, (() => 0));

    // Convert statusData to a form createBarChart understands.
    if (buckets && buckets.length > 0) {
        buckets.forEach((bucketItem) => {
            const statusIndex = labels.indexOf(bucketItem.key);
            if (statusIndex !== -1) {
                statusData[statusIndex] = bucketItem.doc_count;
            }
        });
    }
    return statusData;
}


// Column graph of experiment statuses.
class SummaryStatusChart extends React.Component {
    constructor() {
        super();
        this.chart = null;
        this.createChart = this.createChart.bind(this);
        this.updateChart = this.updateChart.bind(this);
    }

    componentDidMount() {
        if (this.props.totalStatusData) {
            this.createChart();
        }
    }

    componentDidUpdate() {
        if (this.props.totalStatusData) {
            if (this.chart) {
                this.updateChart(this.chart, this.props.statusData);
            } else {
                this.createChart();
            }
        } else if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    createChart() {
        const { statusData } = this.props;
        const accessLevel = sessionToAccessLevel(this.context.session, this.context.session_properties);
        const experimentStatuses = getObjectStatuses('Dataset', accessLevel);

        // Initialize data object to pass to createBarChart.
        const data = {
            whiteDataset: null,
            otherDataset: null,
            asianDataset: null,
            labels: experimentStatuses,
        };

        // Convert statusData to a form createBarChart understands.
        let facetData = statusData.find(facet => facet.key === 'white');
        data.whiteDataset = facetData ? generateStatusData(facetData.status.buckets, data.labels) : [];
        facetData = statusData.find(facet => facet.key === 'other');
        data.otherDataset = facetData ? generateStatusData(facetData.status.buckets, data.labels) : [];
        facetData = statusData.find(facet => facet.key === 'asian');
        data.asianDataset = facetData ? generateStatusData(facetData.status.buckets, data.labels) : [];

        // Generate colors to use for each replicate type.
        const colors = globals.replicateTypeColors.colorList(globals.replicateTypeList);

        createBarChart(this.chartId, data, colors, globals.replicateTypeList, 'Replication', this.props.linkUri, (uri) => { this.context.navigate(uri); })
            .then((chartInstance) => {
                // Save the created chart instance.
                this.chart = chartInstance;
            });
    }

    updateChart(chart, statusData) {
        const replicateTypeColors = globals.replicateTypeColors.colorList(globals.replicateTypeList);
        const accessLevel = sessionToAccessLevel(this.context.session, this.context.session_properties);
        const experimentStatuses = getObjectStatuses('Dataset', accessLevel);

        // For each replicate type, extract the data for each status to assign to the existing
        // chart's dataset.
        const datasets = [];
        globals.replicateTypeList.forEach((replicateType, replicateTypeIndex) => {
            const facetData = statusData.find(facet => facet.key === replicateType);
            if (facetData) {
                // Get an array of replicate data per status from the facet data.
                const data = generateStatusData(facetData.status.buckets, experimentStatuses);

                datasets.push({
                    backgroundColor: replicateTypeColors[replicateTypeIndex],
                    data,
                    label: replicateType,
                });
            }
        });

        // Update the chart data, then force a redraw of the chart and legend.
        chart.data.datasets = datasets;
        chart.data.labels = experimentStatuses;
        chart.update();
        document.getElementById(`${this.chartId}-legend`).innerHTML = chart.generateLegend();
    }

    render() {
        const { totalStatusData } = this.props;

        // Calculate a (hopefully) unique ID to put on the DOM elements.
        this.chartId = 'status-chart-experiments';

        return (
            <div className="award-charts__chart">
                <div className="award-charts__title">
                    Status
                </div>
                {totalStatusData ?
                    <div className="award-charts__visual">
                        <div id={this.chartId} className="award-charts__canvas">
                            <canvas id={`${this.chartId}-chart`} />
                        </div>
                        <div id={`${this.chartId}-legend`} className="award-charts__legend" />
                    </div>
                :
                    <div className="chart-no-data" style={{ height: this.wrapperHeight }}>No data to display</div>
                }
            </div>
        );
    }
}

SummaryStatusChart.propTypes = {
    statusData: PropTypes.array.isRequired, // Experiment status data from /summary/ search results
    totalStatusData: PropTypes.number.isRequired, // Number of items in statusData
    linkUri: PropTypes.string.isRequired, // URI of base link for each bar to link to
};

SummaryStatusChart.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
    navigate: PropTypes.func,
};


// Update all charts to resize themselves on print.
const printHandler = () => {
    Object.keys(window.Chart.instances).forEach((id) => {
        window.Chart.instances[id].resize();
    });
};


// Render the data for the summary in the main panel. Note that we use the charting components from
// awards.js for labs and categories, but not for the status chart. That's because the data gets
// retrieved so differently -- through multiple search requests in awards.js, but in its own
// property with this summary page. Might be good for a refactor later to share common code.

// "displayCharts" is an optional parameter which allows for display of subset of all possible charts
// Possible parameter values are "all", "donuts" or "area", and the default is "all"
class SummaryData extends React.Component {
    constructor() {
        super();
        this.mediaQueryInfo = null;
    }

    componentDidMount() {
        if (window.matchMedia) {
            this.mediaQueryInfo = window.matchMedia('print');
            this.mediaQueryInfo.addListener(printHandler);
        }

        // In case matchMedia doesn't work (e.g. FF and IE).
        window.onbeforeprint = printHandler;
        window.onafterprint = printHandler;
    }

    componentWillUnmount() {
        if (this.mediaQueryInfo) {
            this.mediaQueryInfo.removeListener(printHandler);
            this.mediaQueryInfo = null;
        }
    }

    render() {
        const { context } = this.props;

        // Find the labs and assay facets in the search results.
        const labFacet = context.facets.find(facet => facet.field === 'lab.title');
        let labs = labFacet ? labFacet.terms : null;
        const assayFacet = context.facets.find(facet => facet.field === 'assay_title');
        let assays = assayFacet ? assayFacet.terms : null;

        const filteredOutLabs = context.filters.filter(c => c.field === 'lab.title!');
        const filteredOutAssays = context.filters.filter(c => c.field === 'assay_title!');

        // Filter the assay list if any assay facets have been selected so that the assay graph will be
        // filtered accordingly. Find assay_title filters. Same applies to the lab filters.
        if (context.filters && context.filters.length > 0) {
            const assayTitleFilters = context.filters.filter(filter => filter.field === 'assay_title');
            if (assayTitleFilters.length > 0) {
                const assayTitleFilterTerms = assayTitleFilters.map(filter => filter.term);
                assays = assays.filter(assayItem => assayTitleFilterTerms.indexOf(assayItem.key) !== -1);
            }
            const labFilters = context.filters.filter(filter => filter.field === 'lab.title');
            if (labFilters.length > 0) {
                const labFilterTerms = labFilters.map(filter => filter.term);
                labs = labs.filter(labItem => labFilterTerms.indexOf(labItem.key) !== -1);
            }
        }

        // Get the status data with a process completely different from the others because it comes
        // in its own property in the /summary/ context. Start by getting the name of the property
        // that contains the status data, as well as the number of items within it.
        const statusProp = context.matrix.y.group_by[0];
        const statusSection = context.matrix.y[statusProp];
        const statusDataCount = context.total;
        const statusData = statusSection.buckets;

        // Collect selected facet terms to add to the base linkUri.
        let searchQuery = '';
        if (context.filters && context.filters.length > 0) {
            searchQuery = context.filters.map(filter => `${filter.field}=${encoding.encodedURIComponentOLD(filter.term)}`).join('&');
        }
        const linkUri = `/matrix/?${searchQuery}`;
        const displayCharts = this.props.displayCharts;

        return (
            <div className="summary-content__data">
                {(displayCharts === 'all' || displayCharts === 'donuts') ?
                    <div className="summary-content__snapshot">
                        {labs ? <LabChart labs={labs} linkUri={linkUri} ident="experiments" filteredOutLabs={filteredOutLabs} /> : null}
                        {assays ? <CategoryChart categoryData={assays} categoryFacet="assay_title" title="Assay" linkUri={linkUri} ident="assay" filteredOutAssays={filteredOutAssays} /> : null}
                        {statusDataCount ? <SummaryStatusChart statusData={statusData} totalStatusData={statusDataCount} linkUri={linkUri} ident="status" /> : null}
                    </div>
                : null}
                {(displayCharts === 'all' || displayCharts === 'area') ?
                    <div className="summary-content__statistics">
                        <ExperimentDate experiments={context} panelCss="summary-content__panel" panelHeadingCss="summary-content__panel-heading" />
                    </div>
                : null}
            </div>
        );
    }
}

SummaryData.propTypes = {
    context: PropTypes.object.isRequired, // Summary search result object
    displayCharts: PropTypes.string, // Optional property that allows display of subset of charts
};

SummaryData.defaultProps = {
    displayCharts: 'all',
};

class SummaryBody extends React.Component {
    constructor(props) {
        super(props);
        const searchQuery = url.parse(this.props.context['@id']).search;
        const terms = queryString.parse(searchQuery);


    }


    render() {
        const { context } = this.props;
        const searchQuery = url.parse(this.props.context['@id']).search;
        const query = new QueryString(searchQuery);
        const nonPersistentQuery = query.clone();
        nonPersistentQuery.deleteKeyValue('?type');
        let numOfKidneySamples = 0;
        let numOfTumorgraftSample = 0

        let facets = context.facets;
        let anatomic_site = facets.filter(obj => {
            return obj.field === "biospecimen.anatomic_site"
          })
        if (anatomic_site && anatomic_site.length > 0){
            let terms = anatomic_site[0].terms;
            let result = terms.filter(obj => {
                return obj.key === "Kidney, NOS"
            })
            if (result && result.length > 0) {
                numOfKidneySamples = result[0].doc_count;
            }
        }
        let species = facets.filter(obj => {
            return obj.field === "biospecimen.species"
          })
        if (species && species.length > 0){
            let terms = species[0].terms;
            let result = terms.filter(obj => {
                return obj.key === "Mouse"
            })
            if (result && result.length > 0) {
                numOfTumorgraftSample = result[0].doc_count;
            }
        }
        
        let totalContainerStyle = {
            display: "flex",
            justifyContent: "space-between"
        };
        let totalLabelStyle ={
            minWidth: "25%"
        };
        let numberStyle = {
            fontSize: "80px",
            minWidth: "50%"
        }
        let noteStyle = {
            fontSize: "20px"
        }
        return (
            <div className="summary-header">
                <div className="summary-header__title_control">
                    <div className="summary-header__title">
                        <h1>{this.props.context.title}</h1>
                    </div>
                </div>
                <div className="summary-controls">
                    <div style={totalContainerStyle}>
                        
                        <label style={totalLabelStyle}>
                            <ul style={{ listStyleType: "none" }}>
                            <li><span style={numberStyle}>{context.total}</span><span>&nbsp;</span><span>&nbsp;</span><FontAwesomeIcon icon={faHospitalUser} size="4x" /></li>
                            <li><span style={noteStyle}>Patients</span></li>
                            </ul>
                        </label>

                        <label style={totalLabelStyle}>
                            <ul style={{ listStyleType: "none" }}>
                            <li><span style={numberStyle}>{numOfKidneySamples}</span><span>&nbsp;</span><span>&nbsp;</span><FontAwesomeIcon icon={faVial} size="4x" /></li>
                            <li><span style={noteStyle}>Patients with Primary Kidney Samples</span></li>
                            </ul>
                        </label>

                        <label style={totalLabelStyle}>
                            <ul style={{ listStyleType: "none" }}>
                            <li><span style={numberStyle}>{numOfTumorgraftSample}</span><span>&nbsp;</span><span>&nbsp;</span><FontAwesomeIcon icon={faDisease} size="4x" /></li>
                            <li><span style={noteStyle}>Patients with Tumorgraft Samples</span></li>
                            </ul>
                        </label>

                        <label style={totalLabelStyle}>
                            <ul style={{ listStyleType: "none" }}>
                            <li><span style={numberStyle}>0</span><span>&nbsp;</span><span>&nbsp;</span><FontAwesomeIcon icon={faDna} size="4x" /></li>
                            <li><span style={noteStyle}>Patients with Genomics Data</span></li>
                            </ul>
                        </label>


                        
                    </div>
                    <SummaryChart chartId="summaryChart" data={context} ></SummaryChart>

                </div>
            </div>
        );
    }
}

SummaryBody.propTypes = {
    context: PropTypes.object.isRequired, // Summary search result object
};

SummaryBody.contextTypes = {
    navigate: PropTypes.func,
    location_href: PropTypes.string,
};

// Render the entire summary page based on summary search results.
const Summary = (props) => {
    const { context } = props;
    const itemClass = globals.itemClass(context, 'view-item');


    if (context.total) {
        return (
            <Panel addClasses={itemClass}>
                <PanelBody>
                    <div className="search-results">
                        <div className="search-results__facets">
                            <FacetList context={context} facets={context.facets} filters={context.filters} searchBase={context.searchBase} docTypeTitleSuffix="summary" />
                        </div>
                        <div className="search-results__report-list">
                            <h4>Showing results</h4>
                            <div className="results-table-control">
                                <div className="results-table-control__main">
                                    <ViewControls results={context} />
                                </div>  
                            </div>
                            <SummaryBody context={context} />

                        </div>
                    </div>
                </PanelBody>
            </Panel>

        );
    }
    return <h4>No results found</h4>;
};

Summary.propTypes = {
    context: PropTypes.object.isRequired, // Summary search result object
};

globals.contentViews.register(Summary, 'Summary');
