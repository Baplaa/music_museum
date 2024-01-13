import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://AZURE_VM_DNS/processing/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h2>Latest Stats</h2>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<td><strong># Albums:</strong> {stats['num_album_events']}</td>
						</tr>
                        <tr>
                            <td colspan="2"><strong>Max Album Count:</strong> {stats['max_album_events']}</td>
                        </tr>
						<tr>
                            <td><strong># Single Song:</strong> {stats['num_single_events']}</td>
						</tr>
                        <tr>
                            <td colspan="2"><strong>Max Single Song Count:</strong> {stats['max_single_events']}</td>
                        </tr>
					</tbody>
                </table>
                <h2>Last Updated</h2>
                {stats['last_datetime']}
            </div>
        )
    }
}
