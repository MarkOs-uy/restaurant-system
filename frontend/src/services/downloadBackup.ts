import { API_URL, getAuthHeaders } from "../api"

// ---------------------------------------------------------------------------------------------
// Descarga un archivo de backup desde el backend autenticado.
// Recibe el nombre del archivo y fuerza la descarga en el navegador.
// ---------------------------------------------------------------------------------------------
export async function downloadBackup(
    filename: string
): Promise<void> {

    const response = await fetch(
        `${API_URL}/backups/download/${encodeURIComponent(filename)}`,
        {
            headers: getAuthHeaders()
        }
    )

    if (!response.ok) {
        throw new Error(
            "No fue posible descargar el backup"
        )
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