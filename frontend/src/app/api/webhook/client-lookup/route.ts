import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function POST(req: Request) {
    try {
        const { email, cin } = await req.json();

        if (!email && !cin) {
            return NextResponse.json({ error: "Email or CIN required" }, { status: 400 });
        }

        const client = await prisma.client.findFirst({
            where: {
                OR: [
                    email ? { email: email } : {},
                    cin ? { cin: cin } : {},
                ]
            },
            include: {
                documents: true,
            }
        });

        if (!client) {
            return NextResponse.json({ error: "Client not found" }, { status: 404 });
        }

        return NextResponse.json(client);
    } catch (error) {
        console.error("Error in client-lookup:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
