import { actorId } from "./lib/api";
import AuthGate from "./components/AuthGate";
import Dashboard from "./components/Dashboard";

export default function App() {
  const hasUser = !!actorId();
  return (
    <main className="min-h-screen bg-gradient-to-br from-white to-slate-100 text-slate-900">
      <div className="mx-auto w-full max-w-5xl p-6">
        {hasUser ? (
          <Dashboard />
        ) : (
          <AuthGate onAuth={() => location.reload()} />
        )}
      </div>
    </main>
  );
}
