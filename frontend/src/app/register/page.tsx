"use client";

import { RegisterView } from "@/components/views/RegisterView";
import { useAuth } from "@/components/providers/AuthProvider";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function RegisterPage() {
    const { status } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (status === "authenticated") {
            router.push("/");
        }
    }, [status, router]);

    if (status === "loading" || status === "authenticated") return null;

    return <RegisterView />;
}
