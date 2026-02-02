import { useState } from "react";
import Register from "./Register";
import Login from "./Login";

export default function AuthGate({ onAuth }: { onAuth: () => void }) {
  const [mode, setMode] = useState<"register" | "login">("register");

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 text-slate-900">
      <div className="mx-auto w-full max-w-3xl px-4 py-12">
        {/* HERO z miejscem na gifa */}
        <div className="flex flex-col items-center gap-4">
          <img
            src="/cat.gif"
            alt="cat"
            className="h-24 w-24 rounded-full object-cover ring-2 ring-pink-200"
            onError={(e) => (e.currentTarget.style.display = "none")}
          />
          <h1 className="font-purr text-5xl font-black leading-tight tracking-tight">
            PurrTasks
          </h1>
          <p className="text-slate-500">
            {mode === "register"
              ? "Create your account"
              : "Sign in to continue"}
          </p>
        </div>

        {/* KARTA – stała szerokość dla obu widoków */}
        <div className="mx-auto mt-8 w-full max-w-xl rounded-2xl bg-white p-6 shadow">
          {mode === "register" ? (
            <Register onDone={onAuth} />
          ) : (
            <Login onDone={onAuth} />
          )}
        </div>

        {/* Przełącznik pod kartą – stała szerokość przycisków */}
        <div className="mt-4 flex justify-center">
          <div className="seg">
            <button
              className={`seg-item w-28 ${mode === "register" ? "seg-item-active" : ""}`}
              onClick={() => setMode("register")}
            >
              Register
            </button>
            <button
              className={`seg-item w-28 ${mode === "login" ? "seg-item-active" : ""}`}
              onClick={() => setMode("login")}
            >
              Login
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}
