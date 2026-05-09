export function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

export function monthRangeLabel() {
  return "1 jul 2025 - 31 jul 2025";
}
