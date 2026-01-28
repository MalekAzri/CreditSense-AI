"use client";

import { SessionProvider, useSession, signOut } from "next-auth/react";
import { createContext, useContext, ReactNode, useEffect } from "react";

interface AuthContextType {
    isAuthenticated: boolean;
    status: "loading" | "authenticated" | "unauthenticated";
    user: any;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

function AuthProviderInner({ children }: { children: ReactNode }) {
    const { data: session, status } = useSession();

    useEffect(() => {
        if (status === "authenticated") {
            const updateLastSeen = () => fetch("/api/auth/heartbeat", { method: "POST" }).catch(() => { });
            updateLastSeen();
            const interval = setInterval(updateLastSeen, 1000 * 60 * 2); // Every 2 mins
            return () => clearInterval(interval);
        }
    }, [status]);

    const value = {
        isAuthenticated: status === "authenticated",
        status,
        user: session?.user,
        logout: () => signOut({ callbackUrl: "/" }),
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function AuthProvider({ children }: { children: ReactNode }) {
    return (
        <SessionProvider>
            <AuthProviderInner>{children}</AuthProviderInner>
        </SessionProvider>
    );
}

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
};
