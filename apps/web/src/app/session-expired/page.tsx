import Link from "next/link";
import { EmptyState } from "@/components/ui/empty-state";

export default function SessionExpiredPage() {
  return (
    <main className="page">
      <EmptyState title="Sesion expirada" description="Por seguridad, vuelve a iniciar sesion para continuar." action={<Link className="btn primary" href="/login">Iniciar sesion</Link>} />
    </main>
  );
}
