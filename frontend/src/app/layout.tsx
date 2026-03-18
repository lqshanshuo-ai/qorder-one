import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Content Creator Platform",
  description: "Automated content creation pipeline for short video production",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen">
        <div className="flex">
          <Sidebar />
          <main className="flex-1 p-6 ml-56">{children}</main>
        </div>
      </body>
    </html>
  );
}

function Sidebar() {
  const links = [
    { href: "/", label: "Dashboard", icon: "📊" },
    { href: "/topics", label: "Topics", icon: "💡" },
    { href: "/pipeline", label: "Pipeline", icon: "⚙️" },
    { href: "/videos", label: "Videos", icon: "🎬" },
    { href: "/analytics", label: "Analytics", icon: "📈" },
  ];

  return (
    <aside className="fixed left-0 top-0 h-screen w-56 border-r border-[var(--card-border)] bg-[var(--card)] p-4 flex flex-col">
      <div className="mb-8 px-2">
        <h1 className="text-lg font-bold text-[var(--accent)]">Creator Platform</h1>
        <p className="text-xs text-[var(--text-secondary)]">Content Automation</p>
      </div>
      <nav className="flex flex-col gap-1">
        {links.map((link) => (
          <a
            key={link.href}
            href={link.href}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm hover:bg-[var(--background)] transition-colors"
          >
            <span>{link.icon}</span>
            <span>{link.label}</span>
          </a>
        ))}
      </nav>
    </aside>
  );
}
