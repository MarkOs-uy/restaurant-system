import { API_URL } from "../api"

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/health`)
    if (!response.ok) {
      return false
    }
    const data = await response.json()
    return data.status === "ok"
  } catch {
    return false
  }
}

export async function waitForServer(
  timeout = 60000,
  interval = 2000
): Promise<boolean> {
  const deadline = Date.now() + timeout
  while (Date.now() < deadline) {
    if (await checkHealth()) {
      return true
    }
    await new Promise(resolve =>
      setTimeout(resolve, interval)
    )
  }
  return false
}