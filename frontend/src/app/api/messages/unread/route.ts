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

        const currentUserId = parseInt((session.user as any).id);

        if (isNaN(currentUserId)) {
            return NextResponse.json({ error: "Invalid User ID" }, { status: 400 });
        }

        const unreadCount = await prisma.analystMessage.count({
            where: {
                receiverId: currentUserId,
                read: false
            }
        });

        return NextResponse.json({ count: unreadCount });
    } catch (error) {
        console.error("Error fetching unread count:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
