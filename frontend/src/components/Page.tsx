interface Props {
  title: string
  children: React.ReactNode
}

export default function Page({ title, children }: Props) {
  return (
    <div style={{ padding: 40 }}>

      <h1
        style={{
          marginBottom: 30,
          fontSize: 28
        }}
      >
        {title}
      </h1>

      {children}

    </div>
  )
}