import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import url from 'url';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../libs/ui/modal';
import { Panel, PanelBody } from '../libs/ui/panel';
import { FetchedData, Param } from './fetched';
import * as globals from './globals';
import { FacetList } from './search';
import { ViewControls } from './view_controls';

class Report extends React.Component {
    constructor(props, context) {
        super(props, context);

        // Set initial React state.
        const parsedUrl = url.parse(context.location_href, true);
        const from = parseInt(parsedUrl.query.from, 10) || 0;
        const size = parseInt(parsedUrl.query.limit, 10) || 25;
        this.state = {
            from,
            size,
            to: from + size,
            more: [],
            selectorOpen: false, // True if column selector modal is open
        };

        // Bind this to non-React methods.
        this.setSort = this.setSort.bind(this);
        this.setColumnState = this.setColumnState.bind(this);
        this.loadMore = this.loadMore.bind(this);
        this.handleSelectorClick = this.handleSelectorClick.bind(this);
        this.closeSelector = this.closeSelector.bind(this);
    }

    componentWillReceiveProps(nextProps, nextContext) {
        // reset pagination when filter is changed
        if (nextContext.location_href !== this.context.location_href) {
            const parsedUrl = url.parse(this.context.location_href, true);
            const from = parseInt(parsedUrl.query.from, 10) || 0;
            const size = parseInt(parsedUrl.query.limit, 10) || 25;
            this.setState({
                from,
                to: from + size,
                more: [],
            });
        }
    }

    componentWillUnmount() {
        if (this.state.request) this.state.request.abort();
    }

    setSort(sort) {
        const parsedUrl = url.parse(this.context.location_href, true);
        parsedUrl.query.sort = sort;
        delete parsedUrl.search;
        this.context.navigate(url.format(parsedUrl));
    }

    setColumnState(newColumns) {
        // Gets called when the user clicks the Select button in the ColumnSelector modal.
        // `newColumns` has the same format as `columns` returned from `columnChoices`, but
        // `newColumns` has the user's chosen columns from the modal, while `columns` has the
        // columns selected by the query string.
        const parsedUrl = url.parse(this.context.location_href, true);
        parsedUrl.query.field = Object.keys(newColumns).filter(columnPath => newColumns[columnPath].visible);
        delete parsedUrl.search;
        this.context.navigate(url.format(parsedUrl));
    }

    loadMore() {
        if (this.state.request) {
            this.state.request.abort();
        }
        const parsedUrl = url.parse(this.context.location_href, true);
        parsedUrl.query.from = this.state.to;
        delete parsedUrl.search;
        const request = this.context.fetch(url.format(parsedUrl), {
            headers: { Accept: 'application/json' },
        });
        request.then((response) => {
            if (!response.ok) throw response;
            return response.json();
        }).catch(globals.parseAndLogError.bind(undefined, 'loadMore')).then((data) => {
            this.setState({
                more: this.state.more.concat(data['@graph']),
                request: null,
            });
        });

        this.setState({
            request,
            to: this.state.to + this.state.size,
        });
    }

    handleSelectorClick() {
        // Handle click on the column selector button by opening the modal.
        this.setState({ selectorOpen: true });
    }

    closeSelector() {
        // Close the column selector modal.
        this.setState({ selectorOpen: false });
    }

    render() {
        const parsedUrl = url.parse(this.context.location_href, true);
        if (parsedUrl.pathname.indexOf('/report') !== 0) return false; // avoid breaking on re-render when navigate changes href before context is changed
        const context = this.props.context;
        let searchBase = parsedUrl.search || '';
        searchBase += searchBase ? '&' : '?';

        const type = parsedUrl.query.type;
        const schema = this.props.schemas[type];
        let queryFields = parsedUrl.query.field;
        if (typeof queryFields === 'string') {
            queryFields = [queryFields];
        }
        const columns = columnChoices(schema, queryFields);

        // Compose download-TSV link.
        const downloadTsvPath = `/report.tsv${parsedUrl.path.slice(parsedUrl.pathname.length)}`;

        /* eslint-disable jsx-a11y/click-events-have-key-events, jsx-a11y/no-static-element-interactions */
        return (
            <Panel>
                <PanelBody>
                    <div className="search-results">
                        <div className="search-results__facets">
                            <FacetList context={context} facets={context.facets} filters={context.filters} searchBase={searchBase} docTypeTitleSuffix="report" />
                        </div>
                        <div className="search-results__report-list">
                            <h4>Showing results {this.state.from + 1} to {Math.min(context.total, this.state.to)} of {context.total}</h4>
                            <div className="results-table-control">
                                <div className="results-table-control__main">
                                    <ViewControls results={context} />
                                    <button className="btn btn-info btn-sm" title="Choose columns" onClick={this.handleSelectorClick}>
                                        <i className="icon icon-columns" /> Columns
                                    </button>
                                    <a className="btn btn-info btn-sm" href={downloadTsvPath} data-bypass data-test="download-tsv">Download TSV</a>
                                </div>
                            </div>
                            <Table context={context} more={this.state.more} columns={columns} setSort={this.setSort} />
                            {this.state.to < context.total ?
                                <button className="btn btn-info btn-sm" onClick={this.loadMore}>Load more</button>
                            : null}
                        </div>
                        {this.state.selectorOpen ?
                            <ColumnSelector
                                columns={columns}
                                setColumnState={this.setColumnState}
                                closeSelector={this.closeSelector}
                            />
                        : null}
                    </div>
                </PanelBody>
            </Panel>
        );
        /* eslint-enable jsx-a11y/click-events-have-key-events, jsx-a11y/no-static-element-interactions */
    }
}

Report.propTypes = {
    context: PropTypes.object.isRequired,
    schemas: PropTypes.object, // Actually required, but comes from a GET request.
};

Report.defaultProps = {
    schemas: null,
};

Report.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
    fetch: PropTypes.func,
};


const ReportLoader = props => (
    <FetchedData>
        <Param name="schemas" url="/profiles/" />
        <Report context={props.context} />
    </FetchedData>
);

ReportLoader.propTypes = {
    context: PropTypes.object.isRequired,
};

globals.contentViews.register(ReportLoader, 'Report');

