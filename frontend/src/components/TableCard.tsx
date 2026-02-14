interface Props {
  number: number
  occupied: boolean
  onClick: () => void
}

export default function TableCard({ number, occupied, onClick }: Props) {
  return (
    <div
      onClick={onClick}
      style={{
        cursor: "pointer",
        backgroundColor: occupied ? "#ff6b6b" : "#51cf66",
        padding: 20,
        borderRadius: 12,
        textAlign: "center",
        fontSize: 20,
        fontWeight: "bold"
      }}
    >
      Mesa {number}
    </div>
  )
}
