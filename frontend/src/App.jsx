import { useEffect, useState } from 'react'
import Dashboard from './Dashboard'
import './index.css'

function App() {
  const [fleetName, setFleetName] = useState(null)

  useEffect(() => {
    let storedFleet = localStorage.getItem('fleet_name')
    if (!storedFleet) {
      storedFleet = window.prompt("Welcome to SmartPath. Please enter your Fleet/Company Name:")
      if (!storedFleet) storedFleet = "Default Fleet"
      localStorage.setItem('fleet_name', storedFleet)
    }
    setFleetName(storedFleet)
  }, [])

  if (!fleetName) return null

  return (
    <div className="app-container">
      <header>
        <div className="logo">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{color: 'var(--accent)'}}><path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/></svg>
          SmartPath
        </div>
        <div className="fleet-badge">Fleet: {fleetName}</div>
      </header>
      <Dashboard fleetName={fleetName} />
    </div>
  )
}

export default App
