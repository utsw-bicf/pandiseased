import React from 'react';
import PropTypes from 'prop-types';
import { Panel, PanelBody } from '../libs/ui/panel';
import * as globals from './globals';
import { FacetList } from './search';
import { ViewControls } from './view_controls';
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faHospitalUser } from "@fortawesome/free-solid-svg-icons";
import { faVial } from "@fortawesome/free-solid-svg-icons";
import { faDna } from "@fortawesome/free-solid-svg-icons";
import { faDisease } from "@fortawesome/free-solid-svg-icons";
import { LineChart, Line } from 'recharts';
import SummaryChart from './summaryChart';


class SummaryBody extends React.Component {
    constructor(props) {
        super(props);
    }


    render() {
        const { context } = this.props;
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
        const data = [{name: 'Page A', uv: 400, pv: 2400, amt: 2400},
        {name: 'Page B', uv: 400, pv: 2400, amt: 2400},
        {name: 'Page C', uv: 200, pv: 2400, amt: 2400},
        {name: 'Page D', uv: 300, pv: 2400, amt: 2400},
        {name: 'Page E', uv: 100, pv: 2400, amt: 2400},
        {name: 'Page F', uv: 300, pv: 2400, amt: 2400}
        ];
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
                    <LineChart width={400} height={400} data={data}>
                        <Line type="monotone" dataKey="uv" stroke="#8884d8" />
                    </LineChart>

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
            <div>
            <header className="row">
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            </header>
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
            </div>
        );
    }
    return <h4>No results found</h4>;
};

Summary.propTypes = {
    context: PropTypes.object.isRequired, // Summary search result object
};

globals.contentViews.register(Summary, 'Summary');


