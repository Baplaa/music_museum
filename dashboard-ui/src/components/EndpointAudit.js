import React, { useEffect, useState } from 'react'
import '../App.css';

export default function EndpointAudit(props) {
    const [isLoaded, setIsLoaded] = useState(false);
    const [log, setLog] = useState(null);
    const [error, setError] = useState(null)
    const [index, setIndex] = useState(null);
	const rand_val = Math.floor(Math.random() * 100);

    const getAudit = () => {
        fetch(`http://AZURE_VM_DNS/audit_log/${props.endpoint}?index=${rand_val}`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Audit Results for " + props.endpoint)
                setLog(result);
                setIndex(rand_val);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
	useEffect(() => {
		const interval = setInterval(() => getAudit(), 4000);
		return() => clearInterval(interval);
    }, [getAudit]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){             
        return (
            <div>
                <h3>{props.endpoint}-{index}</h3>
                <pre style={{ whiteSpace: 'pre-wrap', overflowWrap: 'break-word' }}>
                    {Object.keys(log).map((key, index, keysArray) => (
                        <div key={index}>
                            <strong>{key}:</strong>
                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                            <div style={{ marginLeft: '20px' }}>
                                {JSON.stringify(log[key], null, 2)}
                            </div>
                            {index < keysArray.length - 1 ? <br /> : null}
                        </div>
                    ))}
                </pre>
            </div>
        )
    }
}
