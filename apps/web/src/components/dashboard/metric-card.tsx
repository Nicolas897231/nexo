import { CreditCard, PiggyBank, TrendingDown, TrendingUp } from "lucide-react";
import { formatMoney, type MoneyString } from "@/lib/money";

const icons = {
  success: TrendingUp,
  danger: TrendingDown,
  primary: PiggyBank,
  purple: CreditCard,
};

export function MetricCard({
  label,
  value,
  tone,
  delta,
}: {
  label: string;
  value: MoneyString;
  tone: keyof typeof icons;
  delta: string;
}) {
  const Icon = icons[tone];
  return (
    <article className={`card metric-card ${tone === "success" ? "success" : ""}`}>
      <div className="metric-row">
        <span className="metric-icon" style={{ background: `var(--${tone === "primary" ? "primary" : tone})` }}>
          <Icon size={26} />
        </span>
        <div>
          <p className="muted" style={{ margin: 0 }}>{label}</p>
          <p className={`metric-value ${tone}-text`}>{formatMoney(value)}</p>
          <p className={`${tone}-text small`} style={{ margin: 0 }}>↗ {delta}</p>
        </div>
      </div>
    </article>
  );
}
