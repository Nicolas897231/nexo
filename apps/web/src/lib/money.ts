export type MoneyString = `${number}.${number}` | string;

const moneyPattern = /^\d+(\.\d{1,2})?$/;

export function normalizeMoney(input: string): MoneyString {
  const cleaned = input.trim();
  if (!cleaned) return "0.00";
  if (cleaned.includes(",")) {
    const [whole, cents = ""] = cleaned.split(",");
    const wholeDigits = whole.replace(/[^\d]/g, "") || "0";
    return `${wholeDigits}.${cents.replace(/[^\d]/g, "").padEnd(2, "0").slice(0, 2)}`;
  }
  const wholeDigits = cleaned.replace(/[^\d]/g, "") || "0";
  return `${wholeDigits}.00`;
}

export function isValidMoneyString(value: string, options: { allowZero?: boolean } = {}) {
  if (!moneyPattern.test(value)) return false;
  const [whole, cents = "00"] = value.split(".");
  const normalized = BigInt(whole + cents.padEnd(2, "0").slice(0, 2));
  return options.allowZero ? normalized >= 0n : normalized > 0n;
}

export function formatMoney(value: MoneyString, currency = "COP") {
  const [whole, cents = "00"] = value.split(".");
  const number = Number(`${whole}.${cents.slice(0, 2)}`);
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(number);
}

export function percentLabel(value: string) {
  return `${Math.round(Number(value) * 100)}%`;
}
