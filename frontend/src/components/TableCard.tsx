interface Props {
  number: number
  color: string
  onClick: () => void
}

export default function TableCard({ number, color, onClick }: Props) {
  return (
    <div
      onClick={onClick}
      style={{
        background: color,
        padding: 30,
        textAlign: "center",
        fontSize: 24,
        fontWeight: "bold",
        cursor: "pointer",
        boxShadow: "0 3px 8px rgba(0,0,0,0.2)",
        borderRadius: "50%",
        height: 120,
        width: 120,
        display: "flex",
        alignItems: "center",
        justifyContent: "center"
      }}
    >
      Mesa {number}
    </div>
  )
}
