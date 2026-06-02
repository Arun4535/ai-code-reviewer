"use client";

import Link from "next/link";
import { BarChart3, GitPullRequest, History, Settings } from "lucide-react";

const nav = [
  { href: "/", label: "Dashboard", icon: BarChart3 },
  { href: "/", label: "Review", icon: GitPullRequest },
  { href: "/history", label: "History", icon: History },
  { href: "/settings", label: "Settings", icon: Settings }
];

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-line bg-white px-4 py-5 lg:block">
        <div className="mb-8 text-lg font-semibold text-ink">AI Code Reviewer</div>
        <nav className="space-y-1">
          {nav.map((item) => (
            <Link key={item.label} href={item.href} className="flex items-center gap-3 rounded-md px-3 py-2 text-sm text-slate-700 hover:bg-slate-100">
              <item.icon size={18} />
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="lg:pl-64">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">{children}</div>
      </main>
    </div>
  );
}
