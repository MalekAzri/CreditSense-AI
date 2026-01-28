"use client";

import "./globals.css";
import { AuthProvider, useAuth } from "@/components/providers/AuthProvider";
import { Header } from "@/components/layout/Header";
import { usePathname } from "next/navigation";

// Separate component to use hooks (useAuth, usePathname)
function AppLayoutContent({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, logout } = useAuth();
  const pathname = usePathname();

  return (
    <html lang="en" className="dark">
      <body className="antialiased min-h-screen bg-[#0B0E14] text-slate-50 selection:bg-indigo-500/30">
        <Header isAuthenticated={isAuthenticated} onLogout={logout} />

        <main className={isAuthenticated ? "pt-24 px-4 sm:px-8 max-w-7xl mx-auto" : "h-screen w-full"}>
          {children}
        </main>
      </body>
    </html>
  );
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <AuthProvider>
      <AppLayoutContent>{children}</AppLayoutContent>
    </AuthProvider>
  );
}
