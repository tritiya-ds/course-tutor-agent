import { Link, NavLink } from "react-router-dom";
import type { ReactNode } from "react";
import { Show, UserButton } from "@clerk/react";
import { Activity, BookOpen, ChevronRight, FlaskConical, GraduationCap, ShieldCheck } from "lucide-react";

const navItems = [
  { to: "/", label: "Tutor Workspace", icon: BookOpen, testId: "nav-tutor-workspace" },
  { to: "/quiz", label: "Formative Quiz", icon: GraduationCap, testId: "nav-formative-quiz" },
  { to: "/instructor", label: "Control Tower", icon: ShieldCheck, testId: "nav-control-tower" },
  { to: "/evaluation", label: "Evaluation", icon: FlaskConical, testId: "nav-evaluation" },
];

export default function AppShell({ children, eyebrow }: { children: ReactNode; eyebrow: string }) {
  return (
    <div className="min-h-svh bg-[#0b0d11] text-[#f4f6fb] noise-grid" data-testid="app-shell">
      <header className="sticky top-0 z-50 border-b border-white/10 bg-[#0b0d11]/90 px-4 py-3.5 backdrop-blur-xl lg:px-8" data-testid="app-header">
        <div className="mx-auto flex max-w-[1500px] items-center justify-between gap-5">
          <Link to="/" className="flex min-w-fit items-center gap-3" data-testid="brand-home-link">
            <span className="flex h-9 w-9 items-center justify-center rounded-lg border border-blue-400/30 bg-blue-500/10 text-blue-300 shadow-[0_0_20px_rgba(59,130,246,.12)]"><Activity size={18} /></span>
            <span className="hidden leading-none sm:block"><span className="block font-heading text-sm font-semibold tracking-[0.12em] text-white">GROUNDED // TUTOR</span><span className="mt-1 block font-mono text-[9px] uppercase tracking-[0.18em] text-slate-500">course intelligence studio</span></span>
          </Link>
          <nav className="hidden items-center gap-1 lg:flex" aria-label="Primary navigation" data-testid="primary-navigation">
            {navItems.map(({ to, label, icon: Icon, testId }) => (
              <NavLink key={to} to={to} end={to === "/"} data-testid={testId} className={({ isActive }) => `group flex items-center gap-2 rounded-md px-3 py-2 text-xs font-medium ${isActive ? "bg-blue-500/12 text-blue-300" : "text-slate-400 hover:bg-white/[.04] hover:text-slate-200"}`}>
                <Icon size={14} /><span>{label}</span>
              </NavLink>
            ))}
          </nav>
          <div className="flex items-center gap-2" data-testid="header-actions">
            <span className="hidden items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/5 px-3 py-1.5 font-mono text-[10px] uppercase tracking-wider text-emerald-300 xl:flex" data-testid="rag-status-pill"><span className="h-1.5 w-1.5 animate-pulse-orbit rounded-full bg-emerald-400" /> hybrid RAG · strict</span>
            <span className="hidden rounded-full border border-amber-400/20 bg-amber-400/5 px-3 py-1.5 font-mono text-[10px] uppercase tracking-wider text-amber-200 md:block" data-testid="role-badge">STUDENT VIEW</span>
            <Show when="signed-out"><Link to="/sign-in" className="rounded-md border border-white/10 px-3 py-2 text-xs font-medium text-slate-300 hover:border-blue-400/40 hover:text-white" data-testid="header-sign-in-link">Sign in</Link></Show>
            <Show when="signed-in"><span data-testid="header-user-button"><UserButton /></span></Show>
          </div>
        </div>
        <div className="mx-auto mt-3 flex max-w-[1500px] items-center gap-2 overflow-x-auto lg:hidden" data-testid="mobile-navigation">
          {navItems.map(({ to, label, testId }) => <NavLink key={to} to={to} end={to === "/"} data-testid={`${testId}-mobile`} className={({ isActive }) => `whitespace-nowrap rounded-md px-2 py-1.5 text-[11px] ${isActive ? "bg-blue-500/15 text-blue-300" : "text-slate-500"}`}>{label}</NavLink>)}
        </div>
      </header>
      <main className="mx-auto max-w-[1500px] px-4 py-7 lg:px-8 lg:py-10" data-testid="page-content">
        <div className="mb-8 flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.2em] text-slate-500" data-testid="page-eyebrow"><span className="text-blue-400">/</span>{eyebrow}<ChevronRight size={12} className="text-slate-700" /><span className="text-slate-600">CS-101 · 2025 cohort</span></div>
        {children}
      </main>
    </div>
  );
}