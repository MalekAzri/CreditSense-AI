"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useRouter } from "next/navigation";

interface AuthContextType {
    isAuthenticated: boolean;
    login: () => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const router = useRouter();

    // Persist auth state for dev convenience
    useEffect(() => {
        const stored = localStorage.getItem("auth_token");
        if (stored) setIsAuthenticated(true);
    }, []);

    const login = () => {
        localStorage.setItem("auth_token", "demo_token");
        setIsAuthenticated(true);
        router.push("/");
    };

    const logout = () => {
        localStorage.removeItem("auth_token");
        setIsAuthenticated(false);
        router.push("/");
    };

    return (
        <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}
