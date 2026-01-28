import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/lib/auth";

export async function GET() {
    try {
        const session = await getServerSession(authOptions);

        if (!session?.user) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        const currentBank = (session as any).user.bank;

        const analysts = await prisma.analyst.findMany({
            where: {
                AND: [
                    { email: { not: session.user.email || "" } },
                    { bank: currentBank }
                ]
            },
            select: {
                id: true,
                nom: true,
                prenom: true,
                email: true,
                role: true,
                lastSeen: true,
            },
        });

        // Simple online check (within 5 minutes)
        const analystsWithStatus = analysts.map((analyst: any) => ({
            ...analyst,
            isOnline: new Date().getTime() - new Date(analyst.lastSeen).getTime() < 5 * 60 * 1000,
        }));

        return NextResponse.json(analystsWithStatus);
    } catch (error) {
        console.error("Error fetching analysts:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
