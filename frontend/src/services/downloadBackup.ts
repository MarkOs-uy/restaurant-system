import { getAuthHeaders } from "../api"

const API_URL =
  import.meta.env.VITE_API_URL ??
  "http://localhost:8000"

export async function downloadBackup(filename: string) {

  const response = await fetch(
    `${API_URL}/backups/download/${encodeURIComponent(filename)}`,
    {
      headers: getAuthHeaders()
    }
  )

  if (!response.ok) {
    throw new Error("No fue posible descargar el backup")
  }

  const blob = await response.blob()

  const url = window.URL.createObjectURL(blob)

  const link = document.createElement("a")

  link.href = url
  link.download = filename.split("/").pop() ?? filename

  document.body.appendChild(link)

  link.click()

  link.remove()

  window.URL.revokeObjectURL(url)
}