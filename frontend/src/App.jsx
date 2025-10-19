import { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = '/api/v1'

function App() {
  const [voices, setVoices] = useState([])
  const [selectedVoice, setSelectedVoice] = useState(null)
  const [textInput, setTextInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState(null)
  const [generatedAudio, setGeneratedAudio] = useState(null)

  // New voice form
  const [showNewVoiceForm, setShowNewVoiceForm] = useState(false)
  const [newVoiceName, setNewVoiceName] = useState('')
  const [newVoiceDescription, setNewVoiceDescription] = useState('')
  const [audioFile, setAudioFile] = useState(null)

  useEffect(() => {
    fetchVoices()
  }, [])

  const fetchVoices = async () => {
    try {
      const response = await axios.get(`${API_BASE}/voices/`)
      setVoices(response.data)
    } catch (error) {
      console.error('Error fetching voices:', error)
      showMessage('Error loading voices', 'error')
    }
  }

  const createVoiceProfile = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const response = await axios.post(`${API_BASE}/voices/`, {
        name: newVoiceName,
        description: newVoiceDescription
      })

      // Upload audio sample if provided
      if (audioFile) {
        const formData = new FormData()
        formData.append('file', audioFile)
        await axios.post(`${API_BASE}/voices/${response.data.id}/upload-sample`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      }

      showMessage('Voice profile created successfully!', 'success')
      setNewVoiceName('')
      setNewVoiceDescription('')
      setAudioFile(null)
      setShowNewVoiceForm(false)
      fetchVoices()
    } catch (error) {
      console.error('Error creating voice:', error)
      showMessage('Error creating voice profile', 'error')
    } finally {
      setLoading(false)
    }
  }

  const generateAudio = async (e) => {
    e.preventDefault()
    if (!textInput.trim()) {
      showMessage('Please enter some text to generate', 'error')
      return
    }

    setLoading(true)
    try {
      const response = await axios.post(`${API_BASE}/voices/generate`, {
        text: textInput,
        voice_profile_id: selectedVoice?.id || null
      })

      setGeneratedAudio(response.data)
      showMessage('Audio generated successfully!', 'success')
    } catch (error) {
      console.error('Error generating audio:', error)
      showMessage('Error generating audio', 'error')
    } finally {
      setLoading(false)
    }
  }

  const showMessage = (text, type) => {
    setMessage({ text, type })
    setTimeout(() => setMessage(null), 5000)
  }

  return (
    <div className="container">
      <div className="header">
        <h1>Voice Cloner</h1>
        <p>Create and manage custom voice profiles</p>
      </div>

      {message && (
        <div className={`alert alert-${message.type}`}>
          {message.text}
        </div>
      )}

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2>Voice Profiles</h2>
          <button
            className="btn"
            onClick={() => setShowNewVoiceForm(!showNewVoiceForm)}
          >
            {showNewVoiceForm ? 'Cancel' : '+ New Voice'}
          </button>
        </div>

        {showNewVoiceForm && (
          <form onSubmit={createVoiceProfile} style={{ marginTop: '20px', padding: '20px', background: '#f8f9fa', borderRadius: '8px' }}>
            <div className="form-group">
              <label>Voice Name</label>
              <input
                type="text"
                value={newVoiceName}
                onChange={(e) => setNewVoiceName(e.target.value)}
                required
                placeholder="e.g., Morgan Freeman"
              />
            </div>
            <div className="form-group">
              <label>Description (optional)</label>
              <textarea
                value={newVoiceDescription}
                onChange={(e) => setNewVoiceDescription(e.target.value)}
                placeholder="Describe this voice..."
              />
            </div>
            <div className="form-group">
              <label>Audio Sample (optional)</label>
              <input
                type="file"
                accept="audio/*"
                onChange={(e) => setAudioFile(e.target.files[0])}
              />
            </div>
            <button type="submit" className="btn" disabled={loading}>
              {loading ? 'Creating...' : 'Create Voice Profile'}
            </button>
          </form>
        )}

        <div className="voice-list">
          {voices.length === 0 ? (
            <p style={{ gridColumn: '1 / -1', textAlign: 'center', color: '#999' }}>
              No voice profiles yet. Create one to get started!
            </p>
          ) : (
            voices.map(voice => (
              <div
                key={voice.id}
                className={`voice-item ${selectedVoice?.id === voice.id ? 'selected' : ''}`}
                onClick={() => setSelectedVoice(voice)}
              >
                <h3>{voice.name}</h3>
                {voice.description && <p>{voice.description}</p>}
                <small style={{ opacity: 0.6 }}>
                  {voice.is_trained ? 'Trained' : 'Not trained'}
                </small>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="card">
        <h2>Generate Audio</h2>
        <form onSubmit={generateAudio}>
          <div className="form-group">
            <label>Selected Voice</label>
            <input
              type="text"
              value={selectedVoice ? selectedVoice.name : 'None (Default voice)'}
              readOnly
              style={{ background: '#f8f9fa' }}
            />
          </div>
          <div className="form-group">
            <label>Text to Speech</label>
            <textarea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Enter the text you want to convert to speech..."
              required
            />
          </div>
          <button type="submit" className="btn" disabled={loading}>
            {loading ? 'Generating...' : 'Generate Speech'}
          </button>
        </form>

        {generatedAudio && (
          <div style={{ marginTop: '20px', padding: '20px', background: '#f8f9fa', borderRadius: '8px' }}>
            <h3>Generated Audio</h3>
            <p style={{ marginBottom: '10px', color: '#666' }}>
              <strong>Text:</strong> {generatedAudio.text_input}
            </p>
            <audio className="audio-player" controls src={generatedAudio.audio_path}>
              Your browser does not support the audio element.
            </audio>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
