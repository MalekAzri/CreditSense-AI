import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/lib/auth";

export async function GET(req: Request) {
    try {
        const session = await getServerSession(authOptions);
        if (!session?.user?.email) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        const { searchParams } = new URL(req.url);
        const targetId = searchParams.get("targetId");

        if (!targetId) {
            return NextResponse.json({ error: "Target analyst ID is required" }, { status: 400 });
        }

        const currentUser = await prisma.analyst.findUnique({
            where: { email: session.user.email },
        });

        if (!currentUser) {
            return NextResponse.json({ error: "User not found" }, { status: 404 });
        }

        // Récupérer les messages entre les deux analystes
        const messages = await prisma.analystMessage.findMany({
            where: {
                OR: [
                    { senderId: currentUser.id, receiverId: parseInt(targetId) },
                    { senderId: parseInt(targetId), receiverId: currentUser.id },
                ],
            },
            orderBy: { createdAt: "asc" },
        });

        return NextResponse.json(messages);
    } catch (error) {
        console.error("Error fetching messages:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}

export async function POST(req: Request) {
    try {
        const session = await getServerSession(authOptions);
        if (!session?.user?.email) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        const { targetId, content } = await req.json();

        if (!targetId || !content) {
            return NextResponse.json({ error: "Target ID and content are required" }, { status: 400 });
        }

        const currentUser = await prisma.analyst.findUnique({
            where: { email: session.user.email },
        });

        if (!currentUser) {
            return NextResponse.json({ error: "User not found" }, { status: 404 });
        }

        const newMessage = await prisma.analystMessage.create({
            data: {
                content,
                senderId: currentUser.id,
                receiverId: parseInt(targetId),
            },
        });

        return NextResponse.json(newMessage, { status: 201 });
    } catch (error) {
        console.error("Error sending message:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
