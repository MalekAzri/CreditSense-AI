import { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import { prisma } from "@/lib/prisma";
import bcrypt from "bcrypt";

// Extension des types NextAuth pour inclure le rôle
declare module "next-auth" {
    interface Session {
        user: {
            id: string;
            name?: string | null;
            email?: string | null;
            role?: string | null;
            bank?: string | null;
        };
    }
    interface User {
        role?: string | null;
        bank?: string | null;
    }
}

declare module "next-auth/jwt" {
    interface JWT {
        id?: string | null;
        role?: string | null;
        bank?: string | null;
    }
}

export const authOptions: NextAuthOptions = {
    providers: [
        CredentialsProvider({
            name: "Analyst Account",
            credentials: {
                email: { label: "Email", type: "text" },
                password: { label: "Password", type: "password" }
            },
            async authorize(credentials) {
                if (!credentials?.email || !credentials?.password) {
                    throw new Error("Missing credentials");
                }

                const analyst = await prisma.analyst.findUnique({
                    where: { email: credentials.email }
                });

                if (!analyst) {
                    throw new Error("No analyst found with this email");
                }

                // Utilisation de bcrypt pour comparer les mots de passe
                const isValid = await bcrypt.compare(credentials.password, analyst.password);

                if (!isValid) {
                    throw new Error("Incorrect password");
                }

                return {
                    id: analyst.id.toString(),
                    name: `${analyst.prenom} ${analyst.nom}`,
                    email: analyst.email,
                    role: analyst.role,
                    bank: analyst.bank,
                };
            }
        })
    ],
    callbacks: {
        async jwt({ token, user }) {
            if (user) {
                token.id = user.id;
                token.role = user.role;
                token.bank = user.bank;
            }
            return token;
        },
        async session({ session, token }) {
            if (session.user) {
                session.user.id = token.id as string;
                session.user.role = token.role;
                session.user.bank = token.bank;
            }
            return session;
        }
    },
    pages: {
        signIn: "/login",
    },
    session: {
        strategy: "jwt",
    },
    secret: process.env.NEXTAUTH_SECRET,
};
