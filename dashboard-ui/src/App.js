import logo from './logo.png';
import './App.css';

import EndpointAudit from './components/EndpointAudit'
import AppStats from './components/AppStats'
import HealthChecks from './components/Health';

function App() {

    const endpoints = ["album", "single_song"]

    const rendered_endpoints = endpoints.map((endpoint) => {
        return <EndpointAudit key={endpoint} endpoint={endpoint}/>
    })

    return (
        <div className="App">
            <div className='Processing'>
                <h1>Music Museum</h1>
                <img src={logo} className="App-logo" alt="logo" height="256px" width="256px"/>
                <AppStats/>
                <HealthChecks/>
            </div>
            <div className='Audit'>
                <h2>Audit Endpoints</h2>
                <div className='Endpoints'>
                    {rendered_endpoints}
                </div>
            </div>
        </div>
    );
}



export default App;
