import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/lib/auth";

export async function PATCH(
    request: Request,
    { params }: { params: Promise<{ id: string }> }
) {
    try {
        const session = await getServerSession(authOptions);

        if (!session?.user) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        const { id } = await params;
        const { clientId } = await request.json();

        if (!clientId) {
            return NextResponse.json({ error: "Client ID is required" }, { status: 400 });
        }

        const updatedEmail = await prisma.email.update({
            where: { id: parseInt(id) },
            data: { clientId: parseInt(clientId) }
        });

        return NextResponse.json(updatedEmail);
    } catch (error) {
        console.error("Error linking email:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
