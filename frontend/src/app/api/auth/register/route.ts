import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import bcrypt from "bcrypt";

export async function POST(req: Request) {
    try {
        const { nom, prenom, email, password, bank } = await req.json();

        if (!nom || !prenom || !email || !password || !bank) {
            return NextResponse.json(
                { error: "Tous les champs sont obligatoires." },
                { status: 400 }
            );
        }

        // Vérifier si l'analyste existe déjà
        const existingAnalyst = await prisma.analyst.findUnique({
            where: { email },
        });

        if (existingAnalyst) {
            return NextResponse.json(
                { error: "Cet email est déjà utilisé." },
                { status: 400 }
            );
        }

        // Hasher le mot de passe
        const hashedPassword = await bcrypt.hash(password, 10);

        // Créer l'analyste
        const analyst = await prisma.analyst.create({
            data: {
                nom,
                prenom,
                email,
                password: hashedPassword,
                bank,
                role: "analyst", // Par défaut
            },
        });

        return NextResponse.json(
            { message: "Compte créé avec succès.", analystId: analyst.id },
            { status: 201 }
        );
    } catch (error) {
        console.error("Erreur lors de l'inscription:", error);
        return NextResponse.json(
            { error: "Une erreur interne est survenue." },
            { status: 500 }
        );
    }
}
