"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { logout } from "@/lib/auth";
import type { User } from "@/lib/types";

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
}

interface SidebarProps {
  user: User;
}

function HomeIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
      <polyline points="9 22 9 12 15 12 15 22" />
    </svg>
  );
}

function HistoryIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </svg>
  );
}

function AnalyticsIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="20" x2="18" y2="10" />
      <line x1="12" y1="20" x2="12" y2="4" />
      <line x1="6" y1="20" x2="6" y2="14" />
    </svg>
  );
}

function ReportsIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
    </svg>
  );
}

function AdminIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </svg>
  );
}

function LogoutIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
      <polyline points="16 17 21 12 16 7" />
      <line x1="21" y1="12" x2="9" y2="12" />
    </svg>
  );
}

export function Sidebar({ user }: SidebarProps) {
  const pathname = usePathname();

  const navItems: NavItem[] = [
    { label: "Dashboard", href: "/dashboard", icon: <HomeIcon /> },
    { label: "History", href: "/dashboard/history", icon: <HistoryIcon /> },
    { label: "Analytics", href: "/dashboard/analytics", icon: <AnalyticsIcon /> },
    { label: "Reports", href: "/dashboard/reports", icon: <ReportsIcon /> },
  ];

  if (user.role === "Admin") {
    navItems.push({ label: "Admin", href: "/dashboard/admin", icon: <AdminIcon /> });
  }

  function isActive(href: string) {
    if (href === "/dashboard") return pathname === "/dashboard";
    return pathname.startsWith(href);
  }

  return (
    <aside className="fixed left-0 top-0 h-full w-60 flex flex-col z-30 bg-[hsl(230,30%,6%)] border-r border-white/[0.06]">
      {/* Logo */}
      <div className="px-6 py-5 border-b border-white/[0.06]">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500/20 to-blue-500/20 border border-violet-500/15">
            <span className="text-lg">🌌</span>
          </div>
          <div>
            <h1 className="text-sm font-semibold text-white tracking-tight">Mood Tracker</h1>
            <p className="text-[11px] text-white/40">Daily well-being</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const active = isActive(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                active
                  ? "bg-violet-500/15 text-violet-300 shadow-sm shadow-violet-500/10"
                  : "text-white/50 hover:bg-white/[0.04] hover:text-white/80"
              }`}
            >
              <span className={active ? "text-violet-400" : ""}>{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* User info + logout */}
      <div className="px-3 py-4 border-t border-white/[0.06] space-y-2">
        <div className="flex items-center gap-3 px-3 py-2.5 rounded-xl bg-white/[0.03]">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-violet-500/25 to-blue-500/25 text-violet-300 text-xs font-bold">
            {user.full_name?.charAt(0)?.toUpperCase() || "U"}
          </div>
          <div className="flex flex-col min-w-0">
            <span className="text-sm font-medium text-white/90 truncate">
              {user.full_name}
            </span>
            <span className="text-[11px] text-white/35">{user.role}</span>
          </div>
        </div>

        <button
          onClick={logout}
          className="flex w-full items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-white/40 hover:bg-red-500/10 hover:text-red-400 transition-all"
        >
          <LogoutIcon />
          Sign out
        </button>
      </div>
    </aside>
  );
}
