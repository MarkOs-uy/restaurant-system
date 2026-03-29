// src/services/healthMonitor.ts

import { logout } from "./auth.ts"

let interval: any = null
let fails = 0

export function startHealthMonitor() {

  if (interval) return

  interval = setInterval(async () => {

    const api = localStorage.getItem("API_URL")
    if (!api) return

    try {

      const res = await fetch(`${api}/health`)

      if (!res.ok) throw new Error()

      fails = 0

    } catch {

      fails++

      if (fails >= 3) {

        console.warn("Server unreachable")

        logout()

      }

    }

  }, 5000)

}