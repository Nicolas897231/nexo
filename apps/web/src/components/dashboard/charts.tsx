import { categoryDistribution } from "@/data/mock-data";
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
      <path d="M20 170 C80 120 115 165 160 92 S250 120 300 80 S395 96 445 54 S535 66 600 32 L600 190 L20 190 Z" fill="url(#lineFill)" />
      <path d="M20 170 C80 120 115 165 160 92 S250 120 300 80 S395 96 445 54 S535 66 600 32" fill="none" stroke="#075ff7" strokeWidth="5" />
      {["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul"].map((label, index) => (
        <text key={label} x={35 + index * 88} y="205" fill="#536587" fontSize="14">{label}</text>
      ))}
    </svg>
  );
}

export function CategoryDonut() {
  return (
    <div style={{ display: "flex", gap: 24, alignItems: "center", flexWrap: "wrap" }}>
      <div className="donut">
        <strong>{formatMoney("2890000.00")}</strong>
      </div>
      <div className="grid" style={{ gap: 10, minWidth: 220 }}>
        {categoryDistribution.map(([label, value, percent]) => (
          <div key={label} style={{ display: "flex", justifyContent: "space-between", gap: 20 }}>
            <span>{label}</span>
            <strong>{formatMoney(value)} · {percent}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}

export function SavingsBars() {
  const bars = [38, 48, 42, 64, 53, 70, 96];
  return (
    <div className="bar-chart" aria-label="Ahorro mensual">
      {bars.map((height, index) => (
        <span className="bar" key={index} style={{ height: `${height}%` }} />
      ))}
    </div>
  );
}
