import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/lib/auth";

export async function GET(req: Request) {
    try {
        const session = await getServerSession(authOptions);

        if (!session?.user) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        const { searchParams } = new URL(req.url);
        const searchTerm = searchParams.get("search");

        let whereClause = {};
        if (searchTerm) {
            whereClause = {
                OR: [
                    { nom: { contains: searchTerm } },
                    { prenom: { contains: searchTerm } },
                    { email: { contains: searchTerm } },
                    // Support searching by formatted ID like "LN-2026-009"
                    ...(searchTerm.includes("LN-2026-") ? [{
                        id: parseInt(searchTerm.replace("LN-2026-", "")) || -1
                    }] : [])
                ]
            };
        }

        const clients = await prisma.client.findMany({
            where: whereClause,
            include: {
                documents: true,
                emails: true,
            },
            orderBy: {
                createdAt: "desc",
            },
        });

        // Transformer les données pour correspondre aux attentes du dashboard si nécessaire
        const formattedClients = clients.map((client: any) => {
            // Calculer le risque IA (moyenne des scores CLIP/OCR des documents si non spécifié)
            // Si pas encore de décision IA, le score est 0 (en attente) logic
            const iaScore = client.decision_ia === "donner" ? 15 : (client.decision_ia === "refuser" ? 85 : 0);

            return {
                id: `LN-2026-${client.id.toString().padStart(3, "0")}`,
                dbId: client.id,
                nom: client.nom,
                prenom: client.prenom,
                applicant: `${client.prenom || ""} ${client.nom || ""}`.trim(),
                email: client.email || "-",
                clientType: client.typeClient === "individu" ? "Individu" : "PME",
                class: client.classe === "bon client" ? "Bon" : (client.classe === "mauvais client" ? "Mauvais" : "N/A"), // Mapping vers les badges du dashboard
                iaScore: iaScore,
                iaRecommendation: client.decision_ia === "donner" ? "Oui" : (client.decision_ia === "refuser" ? "Non" : "En attente"),
                analystDecision: client.decision_analyste === "donner" ? "Oui" : client.decision_analyste === "refuser" ? "Non" : "En attente",
                creditAmount: client.montant_credit || 0,
                duration: client.duree_mois || 0,
                creditObjective: client.objectif_credit || "-",
                repaymentRate: Math.round((client.taux_remboursement || 0) * 100),
                age: client.age?.toString() || "-",
                employment: client.emploi || "-",
                creditHistory: client.historique_credit || "-",
                bankCreditsCount: client.nb_credits_banque || 0,
                housing: client.logement || "-",
                documentsCount: {
                    uploaded: client.documents.length,
                    total: 3, // Arbitraire pour l'affichage
                },
                documentStatus: client.documents.every((d: any) => d.statut === "valide") ? "Green" : "Yellow",
            };
        });

        return NextResponse.json(formattedClients);
    } catch (error) {
        console.error("Error fetching clients:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}

export async function POST(req: Request) {
    try {
        const session = await getServerSession(authOptions);
        if (!session?.user) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        const formData = await req.formData();
        const typeClient = formData.get("typeClient") as string;
        const nom = formData.get("nom") as string;
        const prenom = formData.get("prenom") as string;
        const montant_credit = parseInt(formData.get("montant_credit") as string || "0");
        const duree_mois = parseInt(formData.get("duree_mois") as string || "0");
        const objectif_credit = formData.get("objectif_credit") as string;
        const age = parseInt(formData.get("age") as string || "0");
        const emploi = formData.get("emploi") as string;
        const email = formData.get("email") as string;

        // Create the client
        const client = await prisma.client.create({
            data: {
                typeClient,
                nom,
                prenom,
                montant_credit,
                duree_mois,
                objectif_credit,
                age,
                emploi,
                email,
                classe: "nouveau", // Default
                decision_ia: "en_attente",
                decision_analyste: "en_attente",
            }
        });

        // Handle documents
        const docFields = [
            { key: "doc_ID", type: "CIN" },
            { key: "doc_BTS_APP", type: "BTS_LOAN_APP" },
            { key: "doc_FIN", type: "FINANCIER" },
        ];

        const { execSync } = require("child_process");
        const path = require("path");
        const fs = require("fs");

        for (const { key, type } of docFields) {
            const file = formData.get(key) as File;
            if (file && file.size > 0 && typeof file !== "string") {
                const buffer = Buffer.from(await file.arrayBuffer());
                const fileName = `${client.id}_${type}_${file.name}`;
                // Save in the module-verification-docs/docs folder
                const storagePath = path.join(process.cwd(), "..", "module-verification-docs", "docs", fileName);

                // Ensure directory exists
                const dir = path.dirname(storagePath);
                if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

                fs.writeFileSync(storagePath, buffer);

                // Create document record
                const doc = await prisma.document.create({
                    data: {
                        clientId: client.id,
                        type: type,
                        url: storagePath.replace(/\\/g, "/"),
                        statut: "en_attente",
                    }
                });

                // Trigger AI Verification if supported
                const supportedTypes = ["CIN", "PASSPORT", "BTS_LOAN_APP"];
                if (supportedTypes.includes(type)) {
                    try {
                        const scriptPath = path.join(process.cwd(), "..", "backend", "services", "document_verification.py");
                        // Execute python command
                        const command = `python "${scriptPath}" --path "${storagePath.replace(/\\/g, "/")}" --type "${type}"`;
                        const output = execSync(command).toString();
                        const result = JSON.parse(output);

                        if (result.statut && result.statut !== "erreur") {
                            await prisma.document.update({
                                where: { id: doc.id },
                                data: {
                                    statut: result.statut,
                                    ocrScore: result.ocrScore || 0,
                                    clipScore: result.clipScore || 0,
                                }
                            });
                        }
                    } catch (aiError) {
                        console.error(`AI Verification failed for doc ${doc.id}:`, aiError);
                    }
                }
            }
        }

        return NextResponse.json({ success: true, clientId: client.id });

    } catch (error) {
        console.error("Error creating client:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
