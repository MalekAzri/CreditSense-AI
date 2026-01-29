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

        const unmatchedEmails = await prisma.email.findMany({
            where: {
                clientId: { equals: null }
            },
            orderBy: {
                sentAt: "desc"
            }
        });

        return NextResponse.json(unmatchedEmails);
    } catch (error) {
        console.error("Error fetching unmatched emails:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
