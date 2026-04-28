import { useState, useEffect } from 'react'
import axios from 'axios'
import { ArrowRight, Route, ShieldAlert, Navigation, Loader2 } from 'lucide-react'

const Dashboard = ({ fleetName }) => {
  const [routeInput, setRouteInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [currentShipment, setCurrentShipment] = useState(null)
  const [history, setHistory] = useState([])

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`http://localhost:5000/api/shipments?user_id=${fleetName}`)
      setHistory(res.data.reverse())
      if (res.data.length > 0 && !currentShipment) {
        setCurrentShipment(res.data[0])
      }
    } catch (err) {
      console.error("Failed to fetch history", err)
    }
  }

  useEffect(() => {
    fetchHistory()
  }, [fleetName])

  const handleOptimize = async (e) => {
    e.preventDefault()
    if (!routeInput) return
    setLoading(true)
    try {
      const res = await axios.post('http://localhost:5000/api/shipments', {
        user_id: fleetName,
        route: routeInput,
        timestamp: new Date().toISOString()
      })
      setCurrentShipment(res.data)
      fetchHistory()
      setRouteInput('')
    } catch (err) {
      console.error(err)
      alert("Error optimizing route")
    } finally {
      setLoading(false)
    }
  }

  const getRiskClass = (score) => {
    if (score > 60) return 'risk-high'
    if (score > 30) return 'risk-medium'
    return 'risk-low'
  }

  return (
    <div className="dashboard-grid">
      <div className="sidebar">
        <div className="glass-panel">
          <h2 style={{marginBottom: '1.5rem', fontSize: '1.2rem', display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
            <Navigation size={20} /> New Shipment
          </h2>
          <form onSubmit={handleOptimize}>
            <div className="input-group">
              <label>Enter Route (comma separated)</label>
              <input 
                type="text" 
                placeholder="e.g. Surat, Nashik, Mumbai" 
                value={routeInput}
                onChange={(e) => setRouteInput(e.target.value)}
              />
            </div>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? <Loader2 className="spinner" size={20} /> : <Route size={20} />}
              {loading ? 'Analyzing Risks...' : 'Optimize Route'}
            </button>
          </form>
        </div>

        <div className="glass-panel" style={{marginTop: '2rem'}}>
          <h2 style={{marginBottom: '1rem', fontSize: '1.2rem'}}>Recent Shipments</h2>
          <div className="history-list">
            {history.slice(0, 5).map((item, idx) => (
              <div 
                key={idx} 
                className={`history-item ${getRiskClass(item.ai_result?.risk_score || 0)}`}
                onClick={() => setCurrentShipment(item)}
                style={{cursor: 'pointer'}}
              >
                <div style={{fontSize: '0.9rem', marginBottom: '0.3rem'}}>{item.original_route && item.original_route.length > 0 ? `${item.original_route[0]} to ${item.original_route[item.original_route.length-1]}` : 'Unknown Route'}</div>
                <div style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>Risk: {item.ai_result?.risk_score || 'N/A'}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="main-content">
        {currentShipment ? (
          <div className={`glass-panel ${getRiskClass(currentShipment.ai_result?.risk_score || 0)}`} style={{transition: 'all 0.5s ease'}}>
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start'}}>
              <div>
                <h1 style={{fontSize: '2rem', marginBottom: '0.5rem'}}>Route Analysis</h1>
                <p style={{color: 'var(--text-muted)'}}>Risk Score: <strong style={{color: 'inherit', fontSize: '1.2rem'}}>{currentShipment.ai_result?.risk_score || 0}/100</strong></p>
              </div>
              {currentShipment.ai_result?.risk_score > 60 && (
                <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'var(--risk-red-bg)', padding: '0.8rem 1.2rem', borderRadius: '8px', color: 'var(--risk-red-text)'}}>
                  <ShieldAlert />
                  <strong>Critical Alert: {currentShipment.ai_result?.affected_location} blocked</strong>
                </div>
              )}
            </div>

            <div className="route-display">
              <div className="route-card">
                <h3><Route size={18} /> Original Route</h3>
                <div className="city-list">
                  {currentShipment.original_route && Array.isArray(currentShipment.original_route) && currentShipment.original_route.map((city, idx) => (
                    <div key={idx} className={`city-item ${currentShipment.ai_result?.affected_location === city ? 'blocked-city' : ''}`}>
                      <div className="city-dot"></div>
                      <span className="city-name">{city}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="route-card">
                <h3><ArrowRight size={18} /> AI-Optimized Route</h3>
                <div className="city-list">
                  {currentShipment.ai_result?.suggested_route && Array.isArray(currentShipment.ai_result.suggested_route) && currentShipment.ai_result.suggested_route.map((city, idx) => (
                    <div key={idx} className="city-item">
                      <div className="city-dot" style={{background: 'var(--risk-green-text)'}}></div>
                      <span className="city-name">{city}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {currentShipment.ai_result?.situation_analysis && (
              <div className="route-card" style={{marginTop: '1.5rem', marginBottom: '1.5rem', background: 'rgba(255,255,255,0.02)'}}>
                <h3 style={{display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem'}}><Navigation size={18} /> AI Situation Analysis & Suggestions</h3>
                <p style={{color: 'var(--text-muted)', lineHeight: '1.6'}}>
                  {typeof currentShipment.ai_result.situation_analysis === 'string' 
                    ? currentShipment.ai_result.situation_analysis 
                    : JSON.stringify(currentShipment.ai_result.situation_analysis)}
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="glass-panel" style={{height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', color: 'var(--text-muted)'}}>
            <Navigation size={48} style={{marginBottom: '1rem', opacity: 0.5}} />
            <h2>No shipment selected</h2>
            <p>Enter a route on the left to start autonomous analysis</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard
