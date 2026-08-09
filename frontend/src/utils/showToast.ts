import toast from "react-hot-toast"

// ---------------------------------------------------------------------------------------------
// Muestra un mensaje de error mediante una notificación toast.
// ---------------------------------------------------------------------------------------------
export function showToast(message: string): void {
    toast.error(message, {
        duration: 4000
    })
}