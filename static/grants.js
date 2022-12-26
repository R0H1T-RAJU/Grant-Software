'use strict';


const e = React.createElement;


class Grants extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            grants: {},
            filter: "",
            grantStatusFilter: [],
            applicationStatusFilter: [],
            filteredGrants: {}
        };

        this.filterGrants = this.filterGrants.bind(this)
        this.showGrantInfo = this.showGrantInfo.bind(this)
        this.statusChange = this.statusChange.bind(this)
        this.grantStatusChange = this.grantStatusChange.bind(this)
        this.applicationStatusChange = this.applicationStatusChange.bind(this)
        this.searchChange = this.searchChange.bind(this)
    }

    statusChange(e, list, statusFilter) {
        var value = e.target.value
        var tempDict = {}
        if (e.target.checked) {
            var addFilter = list
            addFilter.push(value)
            tempDict[statusFilter] = addFilter
            this.setState(tempDict)
        }
        else {
            var removeFilter = list.filter(item => item != value)
            tempDict[statusFilter] = removeFilter
            this.setState(tempDict)
        }
        setTimeout(this.filterGrants, 100)
    }

    applicationStatusChange(e) {
        this.statusChange(e, this.state.applicationStatusFilter, 'applicationStatusFilter')
    }

    grantStatusChange(e) {
        this.statusChange(e, this.state.grantStatusFilter, 'grantStatusFilter')
    }

    componentDidMount() {
        fetch('/api/grants/')
            .then((response) => response.json())
            .then((data) => {
                this.setState({
                    grants: data,
                    filteredGrants: data
                })
            })
    }


    showGrantInfo() {
        loadGrantInfo()
    }


    filterGrants() {
        var filteredItems = {}
        for (let [x, y] of Object.entries(this.state['grants'])) {
            let grant = this.state['grants'][x]
            let name = grant['Name'].toUpperCase()
            let applicationStatus = grant['ApplicationStatus']
            let grantStatus = grant['GrantStatus']
            if (name.match(this.state.filter) && (this.state.grantStatusFilter.includes(grantStatus) || this.state.grantStatusFilter.length == 0) && (this.state.applicationStatusFilter.includes(applicationStatus) || this.state.applicationStatusFilter.length == 0)) {
                filteredItems[x] = y;
            }
        }
        this.setState({ filteredGrants: filteredItems })
    }

    searchChange(e) {
        this.setState({filter: e.target.value.toUpperCase()})
        setTimeout(this.filterGrants, 100)
    }


    checklist() {
        var checkList = document.getElementById('list1');
        var items = document.getElementById('items');
        if (items.classList.contains('visible')) {
            items.classList.remove('visible');
            items.style.display = "none";
        }
        else {
            items.classList.add('visible');
            items.style.display = "block";
        }

        items.onblur = function (evt) {
            items.classList.remove('visible');
        }
    }


    render() {
        return (
            <div style={{ position: 'relative' }}>
                <div>
                    <span><input onChange={this.searchChange} id='search' className="sort" type="text" placeholder="&#128270; Search"></input></span>
                    <span id="list1" className="dropdown-check-list" tabIndex="100">
                        <span onClick={this.checklist} className="anchor">Filter</span>
                        <ul  id="items" className="items">
                            <li><input onChange={this.grantStatusChange} value="Grant Open" type="checkbox" />Grant Open</li>
                            <li><input onChange={this.grantStatusChange} value='Grant Closed' type="checkbox" />Grant Closed</li>
                            <li><input onChange={this.grantStatusChange} value='None' type="checkbox" />None (Grant)</li>
                            <li><input onChange={this.applicationStatusChange} value='Applied' type="checkbox" />Applied</li>
                            <li><input onChange={this.applicationStatusChange} value='Rejected' type="checkbox" />Rejected</li>
                            <li><input onChange={this.applicationStatusChange} value='Accepted' type="checkbox" />Accepted</li>
                            <li><input onChange={this.applicationStatusChange} value='None' type="checkbox" />None (App)</li>

                        </ul>
                    </span>
                </div>

                <select style={{ marginTop: '40px' }} onClick={this.showGrantInfo} className="homeselect" name="grantid" id="grantList" size="6">
                    {Object.keys(this.state['filteredGrants']).map(x => <option className='homeoption' value={x}>{this.state['filteredGrants'][x]["Name"]}</option>)}
                </select>
            </div>
        )
    }
}

const domContainer = document.querySelector('#grantsAndFilter');
const root = ReactDOM.createRoot(domContainer);
root.render(<Grants/>);

