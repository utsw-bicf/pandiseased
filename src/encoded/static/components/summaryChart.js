import React from 'react';

class SummaryChart extends React.Component {

    constructor(props) {
        super(props);
    
        this.data = this.props.data;
        this.state = {
          count: 0
        };
        this.plotlyConfig = {
          displayModeBar: true,
          displaylogo: false,
          modeBarButtonsToRemove: [
                  "sendDataToCloud",
                  "editInChartStudio",
                  "select2d",
                  "lasso2d",
                  "hoverClosestCartesian",
                  "hoverCompareCartesian",
                  "toggleSpikelines",
                  "autoScale2d"
          ],
          responsive: true
        };
    }

    render() {
        return (
          <div>
            <header>
              <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            </header>
            <div className="flex-container" >
    
              <div className="chart-main" >
                <div id={this.props.chartId}  >
    
                </div>
              </div>
            </div>
          </div>)
    
    }

    drawChart() {
        var data = [{
            values: [19, 26, 55],
            labels: ['Residential', 'Non-Residential', 'Utility'],
            type: 'pie'
          }];
          
          var layout = {
            height: 400,
            width: 500
        };
        
        this.plotly.newPlot(this.props.chartId, data, layout, this.plotlyConfig);
        

    }

    componentDidMount() {
      if(typeof window.Plotly !== "undefined"){
        this.plotly = window.Plotly;

        this.drawChart();
      }
      else{
        this.setState({ count: this.state.count + 1 })
      }
    }


  
}

export default SummaryChart;


