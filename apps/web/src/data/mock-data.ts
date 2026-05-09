import type { MoneyString } from "@/lib/money";

export const kpis = [
  { label: "Ingresos del mes", value: "4250000.00", tone: "success", delta: "12% vs. mes anterior" },
  { label: "Egresos del mes", value: "2890000.00", tone: "danger", delta: "8% vs. mes anterior" },
  { label: "Ahorro disponible", value: "1360000.00", tone: "primary", delta: "18% vs. mes anterior" },
];

export const goals = [
  {
    name: "Ahorrar",
    type: "saving",
    target: "1360000.00",
    saved: "896000.00",
    progress: 66,
    status: "Viable",
    tone: "success",
    date: "30 dic 2025",
  },
  {
    name: "Vivir solo",
    type: "living-alone",
    target: "12000000.00",
    saved: "5600000.00",
    progress: 47,
    status: "Con ajustes",
    tone: "primary",
    date: "Oct 2026",
  },
  {
    name: "Comprar carro",
    type: "car",
    target: "45000000.00",
    saved: "21500000.00",
    progress: 48,
    status: "Con ajustes",
    tone: "purple",
    date: "Mar 2027",
  },
  {
    name: "Viajar",
    type: "travel",
    target: "6500000.00",
    saved: "2800000.00",
    progress: 43,
    status: "En riesgo",
    tone: "warning",
    date: "Jun 2026",
  },
];

export const movements: Array<{
  date: string;
  type: "income" | "expense";
  description: string;
  category: string;
  goal: string;
  method: string;
  amount: MoneyString;
  status: string;
}> = [
  { date: "30 jul 2025", type: "income", description: "Salario mensual", category: "Ingresos", goal: "Viaje a Europa", method: "Transferencia", amount: "2500000.00", status: "Completado" },
  { date: "29 jul 2025", type: "expense", description: "Supermercado", category: "Alimentacion", goal: "-", method: "Tarjeta debito", amount: "185400.00", status: "Completado" },
  { date: "28 jul 2025", type: "expense", description: "Transporte publico", category: "Transporte", goal: "-", method: "Tarjeta recargable", amount: "45000.00", status: "Completado" },
  { date: "27 jul 2025", type: "income", description: "Freelance - Diseno", category: "Ingresos", goal: "Fondo de emergencia", method: "Transferencia", amount: "750000.00", status: "Completado" },
  { date: "26 jul 2025", type: "expense", description: "Cena fuera", category: "Ocio", goal: "-", method: "Tarjeta credito", amount: "98000.00", status: "Completado" },
  { date: "25 jul 2025", type: "expense", description: "Netflix", category: "Servicios", goal: "-", method: "Tarjeta credito", amount: "34900.00", status: "Completado" },
  { date: "24 jul 2025", type: "income", description: "Venta de equipo", category: "Otros", goal: "Meta prioritaria", method: "Transferencia", amount: "420000.00", status: "Completado" },
  { date: "23 jul 2025", type: "expense", description: "Combustible", category: "Transporte", goal: "-", method: "Tarjeta debito", amount: "120000.00", status: "Pendiente" },
];

export const categoryDistribution = [
  ["Vivienda", "1150000.00", "39%"],
  ["Alimentacion", "620000.00", "21%"],
  ["Transporte", "430000.00", "15%"],
  ["Estilo de vida", "340000.00", "12%"],
  ["Servicios", "210000.00", "7%"],
  ["Otros", "140000.00", "5%"],
];

export const recommendations = [
  { title: "Arriendo recomendado", detail: "Basado en tu ingreso y gastos actuales", value: "$850.000 - $1.000.000", tone: "success" },
  { title: "Cuota maxima de carro", detail: "Para mantener tu salud financiera", value: "$450.000", tone: "primary" },
  { title: "Aumenta tu ahorro mensual", detail: "Podrias aumentar $120.000 mas al mes.", value: "Simular", tone: "purple" },
];
