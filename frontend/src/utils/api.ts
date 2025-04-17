// filepath: g:\Projekte\timedesk\frontend\src\utils\api.ts

/**
 * Wrapper für fetch, der die Cookie-basierte Authentifizierung handhabt
 */
export async function fetchWithAuth(url: string, options: RequestInit = {}) {
  // Optionen klonen, um das Original nicht zu verändern
  const requestOptions = { ...options }

  // Headers hinzufügen, falls nicht vorhanden
  if (!requestOptions.headers) {
    requestOptions.headers = {}
  }

  // credentials option hinzufügen für Cookie-Übertragung
  requestOptions.credentials = 'include'

  try {
    // Anfrage ausführen
    let response = await fetch(url, requestOptions)

    // Bei 401 (Unauthorized) versuchen, das Token zu aktualisieren
    if (response.status === 401) {
      try {
        const errorData = await response.json()

        if (errorData.msg === 'Token has expired') {
          // Token-Aktualisierung versuchen
          const refreshRes = await fetch('https://chronixly.com/api/refresh', {
            method: 'POST',
            credentials: 'include',
          })

          if (refreshRes.ok) {
            // Original-Anfrage wiederholen
            return fetch(url, requestOptions)
          }
        }
      } catch (e) {
        // Wenn JSON nicht geparst werden kann oder etwas anderes schief geht, mit der fehlgeschlagenen Antwort fortfahren
      }
    }

    return response
  } catch (error) {
    // Bei Netzwerkfehlern protokollieren und erneut werfen
    console.error('API-Anfrage fehlgeschlagen:', error)
    throw error
  }
}
