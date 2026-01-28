import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/lib/auth";

export async function GET(
  req: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const session = await getServerSession(authOptions);

    if (!session?.user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { id } = await params;
    const rawId = id;
    const idMatch = rawId.match(/(\d+)$/);
    const clientId = idMatch ? parseInt(idMatch[1]) : parseInt(rawId);

    if (isNaN(clientId)) {
      return NextResponse.json({ error: "Invalid client ID" }, { status: 400 });
    }

    const client = await prisma.client.findUnique({
      where: { id: clientId },
      include: {
        documents: true,
        emails: true,
        vocaux: true,
      },
    });

    if (!client) {
      return NextResponse.json({ error: "Client not found" }, { status: 404 });
    }

    // Format for frontend
    const formattedClient = {
      ...client,
      id: `LN-2026-${client.id.toString().padStart(3, "0")}`,
      dbId: client.id,
      clientType: client.typeClient === "individu" ? "Individu" : "PME",
      applicant: `${client.prenom || ""} ${client.nom || ""}`.trim(),
    };

    return NextResponse.json(formattedClient);
  } catch (error) {
    console.error("Error fetching client details:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}
