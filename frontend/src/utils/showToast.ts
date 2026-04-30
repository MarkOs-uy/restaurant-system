import toast from "react-hot-toast"

export function showToast(message: string) {
    toast.error(message, {
    duration: 4000
    })
}