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
export async function PATCH(
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

    const body = await req.json();

    // Only allow specific fields to be updated for now
    const allowedFields = ["statut_dossier", "classe", "decision_ia", "decision_analyste"];
    const updateData: any = {};

    for (const field of allowedFields) {
      if (body[field] !== undefined) {
        updateData[field] = body[field];
      }
    }

    if (Object.keys(updateData).length === 0) {
      return NextResponse.json({ error: "No valid fields to update" }, { status: 400 });
    }

    // Use raw query to bypass Prisma Client sync issues for newer fields
    if (updateData.statut_dossier !== undefined || updateData.decision_ia !== undefined || updateData.classe !== undefined) {
      if (updateData.statut_dossier !== undefined) {
        await prisma.$executeRawUnsafe(`UPDATE Client SET statut_dossier = ? WHERE id = ?`, updateData.statut_dossier, clientId);
      }
      if (updateData.decision_ia !== undefined) {
        await prisma.$executeRawUnsafe(`UPDATE Client SET decision_ia = ? WHERE id = ?`, updateData.decision_ia, clientId);
      }
      if (updateData.classe !== undefined) {
        await prisma.$executeRawUnsafe(`UPDATE Client SET classe = ? WHERE id = ?`, updateData.classe, clientId);
      }

      // Update remaining fields if any (like decision_analyste) using normal prisma
      const remainingFields = { ...updateData };
      delete remainingFields.statut_dossier;
      delete remainingFields.decision_ia;
      delete remainingFields.classe;

      if (Object.keys(remainingFields).length > 0) {
        await prisma.client.update({
          where: { id: clientId },
          data: remainingFields,
        });
      }

      const updatedClient = await prisma.client.findUnique({ where: { id: clientId } });
      return NextResponse.json(updatedClient);
    }

    const updatedClient = await prisma.client.update({
      where: { id: clientId },
      data: updateData,
    });

    return NextResponse.json(updatedClient);
  } catch (error) {
    console.error("Error updating client:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}
