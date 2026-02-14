type Props = {
  number: number
  status: "libre" | "ocupada"
  orderStatus: string | null
}

export default function TableCard({ number, status, orderStatus }: Props) {

  const getColor = () => {
    if (status === "libre") return "#2ecc71" // verde

    switch (orderStatus) {
      case "OPEN":
        return "#f1c40f"
      case "SENT":
        return "#3498db"
      case "IN_PROGRESS":
        return "#e67e22"
      case "READY":
        return "#9b59b6"
      default:
        return "#e74c3c"
    }
  }

  return (
    <div
      style={{
        backgroundColor: getColor(),
        borderRadius: 12,
        padding: 20,
        color: "white",
        fontSize: 22,
        fontWeight: "bold",
        textAlign: "center",
        cursor: "pointer",
        transition: "0.2s"
      }}
    >
      Mesa {number}
      <div style={{ fontSize: 14, marginTop: 10 }}>
        {status === "libre" ? "Libre" : orderStatus}
      </div>
    </div>
  )
}
