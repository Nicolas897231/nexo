export const currencyOptions = [
  { value: "COP", label: "COP - Peso colombiano" },
  { value: "USD", label: "USD - Dolar estadounidense" },
  { value: "EUR", label: "EUR - Euro" },
  { value: "MXN", label: "MXN - Peso mexicano" },
  { value: "PEN", label: "PEN - Sol peruano" },
  { value: "CLP", label: "CLP - Peso chileno" },
];

export const paydayOptions = [
  { value: "monthly_15", label: "Mensual - dia 15", frequency: "monthly", paydays: [15] },
  { value: "monthly_30", label: "Mensual - dia 30", frequency: "monthly", paydays: [30] },
  { value: "biweekly_15_30", label: "Quincenal - dias 15 y 30", frequency: "biweekly", paydays: [15, 30] },
  { value: "biweekly_1_15", label: "Quincenal - dias 1 y 15", frequency: "biweekly", paydays: [1, 15] },
] as const;

export function getPaydayOption(frequency?: string | null, paydays?: number[] | null) {
  const normalized = [...(paydays ?? [])].sort((a, b) => a - b).join(",");
  return (
    paydayOptions.find(
      (option) => option.frequency === frequency && option.paydays.join(",") === normalized,
    )?.value ?? "biweekly_15_30"
  );
}

export const paymentMethods = [
  { value: "cash", label: "Efectivo" },
  { value: "debit_card", label: "Tarjeta debito" },
  { value: "credit_card", label: "Tarjeta credito" },
  { value: "bank_transfer", label: "Transferencia bancaria" },
  { value: "nequi", label: "Nequi" },
  { value: "daviplata", label: "Daviplata" },
  { value: "pse", label: "PSE" },
  { value: "automatic_debit", label: "Debito automatico" },
];
