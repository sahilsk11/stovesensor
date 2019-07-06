class StoveCenter extends React.Component {
    constructor(props) {
        super(props);
        this.state = { temperature: "73", status: "ON" }
    }

    render() {
        return (
            <div className="full-size-container">
                <div className="row">
                    <div className="column col-md-6">
                        <div class="col-container">
                            <StoveIcon status={this.state.status} />
                            <h1 className="title status">stove is {this.state.status.toLowerCase()}</h1>
                        </div>
                    </div>
                    <div className="column col-md-6 right-column">
                        <RecentActivityContainer />
                    </div>
                </div>
            </div >
        );
    }

}

class PieChart extends React.Component {
    constructor(props) {
        super(props);
        this.canvasRef = React.createRef();
    }

    createChartData() {
        return {
            datasets: [{
                data: [15, 15, , 15, 15, 15, 15, 15],
                backgroundColor: ['#D6D6D6', '#7DD7FF', '#4CB8F2', '#4CBBF5', '#FBCD50', '#FA9D38', '#F85B47', '#F14232']
            }],

            // These labels appear in the legend and in the tooltips when hovering different arcs
            labels: [
                'Normal range (60° - 80°)',
                'Medium range (80° - 100°)',
                'Current Temperature',
                'High (100° - 200°)'
            ]
        }
    }

    createChartOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            legend: {
                display: false,
            },
            title: {
                display: false,
            },
            cutoutPercentage: 50,
            rotation: 3 * Math.PI,
            circumference: Math.PI,
            animation: {
                animateScale: true
            }
        }
    }

    componentDidMount() {
        this.myChart = new Chart(this.canvasRef.current, {
            type: 'pie',
            data: this.createChartData(),
            options: this.createChartOptions(),
        });
    }

    render() {
        return (
            <div className="chart-container">
                <div className="circle-container">
                    <canvas ref={this.canvasRef} />
                </div>
                <PieChartNeedle />
            </div>
        );
    }
}

class PieChartNeedle extends React.Component {
    constructor(props) {
        super(props);
        this.canvasRef = React.createRef();
    }

    createChartData() {
        return {
            datasets: [{
                data: [70, 5, 27],
                backgroundColor: ['rgba(0, 0, 0, 0)', 'rgba(0, 0, 0, 0.8)', 'rgba(0, 0, 0, 0)'],
                borderColor: 'rgba(0, 0, 0, 0)'
            }],

            // These labels appear in the legend and in the tooltips when hovering different arcs
            labels: [
                '',
                '73',
            ]
        }
    }

    createChartOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    top: 0
                }
            },
            legend: {
                display: false,
            },
            title: {
                display: false,
            },
            cutoutPercentage: 40,
            rotation: 3 * Math.PI,
            circumference: Math.PI
        }
    }

    componentDidMount() {
        this.myChart = new Chart(this.canvasRef.current, {
            type: 'pie',
            data: this.createChartData(),
            options: this.createChartOptions(),
        });
    }

    render() {
        return (
            <div className="needle-container">
                <div>
                    <canvas ref={this.canvasRef} />
                </div>
            </div>
        );
    }
}

class RecentActivityContainer extends React.Component {
    constructor(props) {
        super(props);
    }

    renderEntry(state, time, temperature) {
        let stateClass = "data state-data";
        if (state === "ON") {
            stateClass += " on-color";
        }
        return (
            <tr className="entry">
                <td className={stateClass}>{state}</td>
                <td className="data state-center">{temperature} °F</td>
                <td className="data state-center">{time}</td>
            </tr>
        );
    }

    render() {
        return (
            <div>
                <h1 className="title">Recent Activity</h1>
                <table className="activity-table">
                    <tbody>
                        {this.renderEntry("OFF", "06/01/19 7:10AM", "73")}
                        {this.renderEntry("ON", "06/01/19 7:10AM", "73")}
                        {this.renderEntry("OFF", "06/01/19 7:10AM", "73")}
                        {this.renderEntry("OFF", "06/01/19 7:10AM", "73")}
                        {this.renderEntry("OFF", "06/01/19 7:10AM", "73")}
                        {this.renderEntry("OFF", "06/01/19 7:10AM", "73")}
                    </tbody>
                </table>
            </div>
        )
    }
}



class StoveIcon extends React.Component {
    constructor(props) {
        super(props);
    }

    renderFlame() {
        if (this.props.status == "ON") {
            return (
                <div>
                    <img src="img/flame.gif" className="flame" />
                    <img src="img/flame.gif" className="flame flame-rt" />
                </div>
            );
        } else {
            return "";
        }
    }

    renderSmile() {
        if (this.props.status == "ON") {
            return (
                <img src="img/on.png" className="stove-face" />
            );
        } else {
            return (
                <img src="img/smile.png" className="stove-face" />
            )
        }
    }

    render() {
        return (
            <div className="icon-container">
                <img src="img/stove.svg" className="stove-img" />
                {this.renderFlame()}
                {this.renderSmile()}
            </div>
        )
    }
}
//https://boingboing.net/2018/09/13/tool-to-create-pixel-art-parti.html

ReactDOM.render(
    <StoveCenter />,
    document.getElementById("content-container")
);