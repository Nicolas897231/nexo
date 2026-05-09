import type { ReactNode } from "react";

export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <section className="card pad" style={{ display: "grid", minHeight: 320, placeItems: "center", textAlign: "center" }}>
      <div>
        <h1>{title}</h1>
        <p className="muted">{description}</p>
        {action ? <div style={{ marginTop: 20 }}>{action}</div> : null}
      </div>
    </section>
  );
}
