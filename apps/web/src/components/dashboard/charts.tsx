import { formatMoney } from "@/lib/money";

export function BalanceChart() {
  return (
    <svg className="chart-line" viewBox="0 0 620 210" role="img" aria-label="Evolucion de saldo">
      <defs>
        <linearGradient id="lineFill" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="#075ff7" stopOpacity="0.24" />
          <stop offset="100%" stopColor="#075ff7" stopOpacity="0.02" />
        </linearGradient>
      </defs>
      {[40, 85, 130, 175].map((y) => (
        <line key={y} x1="20" x2="600" y1={y} y2={y} stroke="#e4ebf6" />
      ))}
      <path d="M20 170 C95 140 150 150 215 112 S330 120 395 86 S500 78 600 52 L600 190 L20 190 Z" fill="url(#lineFill)" />
      <path d="M20 170 C95 140 150 150 215 112 S330 120 395 86 S500 78 600 52" fill="none" stroke="#075ff7" strokeWidth="5" />
      {["Semana 1", "Semana 2", "Semana 3", "Semana 4"].map((label, index) => (
        <text key={label} x={35 + index * 150} y="205" fill="#536587" fontSize="14">{label}</text>
      ))}
    </svg>
  );
}

export function CategoryDonut({
  total = "0.00",
  items = [],
}: {
  total?: string;
  items?: [string, string, string][];
}) {
  const rows = items.length ? items : [["Sin datos", "0.00", "0%"] as [string, string, string]];
  return (
    <div style={{ display: "flex", gap: 24, alignItems: "center", flexWrap: "wrap" }}>
      <div className="donut">
        <strong>{formatMoney(total)}</strong>
      </div>
      <div className="grid" style={{ gap: 10, minWidth: 220 }}>
        {rows.map(([label, value, percent]) => (
          <div key={label} style={{ display: "flex", justifyContent: "space-between", gap: 20 }}>
            <span>{label}</span>
            <strong>{formatMoney(value)} - {percent}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}

export function SavingsBars({ values = [20, 35, 42, 55] }: { values?: number[] }) {
  return (
    <div className="bar-chart" aria-label="Ahorro mensual">
      {values.map((height, index) => (
        <span className="bar" key={index} style={{ height: `${Math.max(height, 8)}%` }} />
      ))}
    </div>
  );
}
