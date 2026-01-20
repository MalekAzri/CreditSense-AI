"use client";

import { useAuth } from "@/components/providers/AuthProvider";
import { LoginView } from "@/components/views/LoginView";
import { DashboardView } from "@/components/views/DashboardView";

export default function Home() {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <DashboardView /> : <LoginView />;
}
