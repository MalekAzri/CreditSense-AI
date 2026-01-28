"use client";

import { LoginView } from "@/components/views/LoginView";
import { useAuth } from "@/components/providers/AuthProvider";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function LoginPage() {
    const { isAuthenticated, status } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (status === "authenticated") {
            router.push("/");
        }
    }, [status, router]);

    if (status === "loading" || status === "authenticated") return null;

    return <LoginView />;
}
