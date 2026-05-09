"use client";

import { useId, useState } from "react";
import { formatMoney, normalizeMoney, type MoneyString } from "@/lib/money";

export function MoneyInput({
  label,
  value,
  onChange,
  hint,
}: {
  label: string;
  value: MoneyString;
  onChange: (value: MoneyString) => void;
  hint?: string;
}) {
  const id = useId();
  const [display, setDisplay] = useState(formatMoney(value));
  return (
    <label className="field" htmlFor={id}>
      <span>{label}</span>
      <input
        id={id}
        className="input"
        inputMode="numeric"
        value={display}
        onChange={(event) => {
          const normalized = normalizeMoney(event.target.value);
          onChange(normalized);
          setDisplay(formatMoney(normalized));
        }}
      />
      {hint ? <small className="muted">{hint}</small> : null}
    </label>
  );
}
