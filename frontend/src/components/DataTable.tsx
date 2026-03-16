interface Props {
  children: React.ReactNode
}

export default function DataTable({ children }: Props) {

  return (
    <table
      style={{
        width: "100%",
        borderCollapse: "collapse"
      }}
    >
      {children}
    </table>
  )
}