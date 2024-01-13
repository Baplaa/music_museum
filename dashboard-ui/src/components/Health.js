import React, { useEffect, useState } from 'react'
import '../App.css';

export default function HealthChecks() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [services, setChecks] = useState({});
    const [error, setError] = useState(null)

	const getChecks = () => {
	
        fetch(`http://AZURE_VM_DNS/health/check`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Health Checks")
                setChecks(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getChecks(), 20000);
		return() => clearInterval(interval);
    }, [getChecks]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h2>Latest Health Checks</h2>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<td><strong>Receiver:</strong> {services['receiver']}</td>
						</tr>
                        <tr>
                            <td colspan="2"><strong>Storage:</strong> {services['storage']}</td>
                        </tr>
						<tr>
                            <td><strong>Processing:</strong> {services['processing']}</td>
						</tr>
                        <tr>
                            <td colspan="2"><strong>Audit:</strong> {services['audit']}</td>
                        </tr>
					</tbody>
                </table>
                <h2>Last Updated</h2>
                {services['last_datetime']}
            </div>
        )
    }
}
