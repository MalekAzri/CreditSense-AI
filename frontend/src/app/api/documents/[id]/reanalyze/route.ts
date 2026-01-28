import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/lib/auth";
import { execSync } from "child_process";
import path from "path";

export async function POST(
    req: Request,
    context: { params: Promise<{ id: string }> }
) {
    try {
        const session = await getServerSession(authOptions);
        if (!session?.user) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }

        const params = await context.params;
        const documentId = parseInt(params.id);

        // Get document details
        const document = await prisma.document.findUnique({
            where: { id: documentId }
        });

        if (!document) {
            return NextResponse.json({ error: "Document not found" }, { status: 404 });
        }

        // Check if document type is supported for AI verification
        const supportedTypes = ["CIN", "PASSPORT", "BTS_LOAN_APP"];
        if (!supportedTypes.includes(document.type)) {
            return NextResponse.json({
                error: "Document type not supported for AI verification"
            }, { status: 400 });
        }

        // Trigger AI Verification
        try {
            const scriptPath = path.join(process.cwd(), "..", "backend", "services", "document_verification.py");
            const documentPath = document.url;

            // Execute python command with stderr suppression for warnings
            const command = `python "${scriptPath}" --path "${documentPath.replace(/\\/g, "/")}" --type "${document.type}"`;
            const output = execSync(command, {
                timeout: 60000,
                encoding: 'utf-8',
                // Suppress stderr to avoid warnings mixing with JSON output
                stdio: ['pipe', 'pipe', 'ignore']
            }).toString().trim();

            // Extract JSON from output (in case there are any print statements before it)
            let jsonOutput = output;
            const jsonStartIndex = output.indexOf('{');
            const jsonEndIndex = output.lastIndexOf('}');

            if (jsonStartIndex !== -1 && jsonEndIndex !== -1) {
                jsonOutput = output.substring(jsonStartIndex, jsonEndIndex + 1);
            }

            const result = JSON.parse(jsonOutput);

            if (result.statut && result.statut !== "erreur") {
                // Update document with new scores
                const updatedDocument = await prisma.document.update({
                    where: { id: documentId },
                    data: {
                        statut: result.statut,
                        ocrScore: result.ocrScore || 0,
                        clipScore: result.clipScore || 0,
                    }
                });

                return NextResponse.json({
                    success: true,
                    document: updatedDocument,
                    verification: result
                });
            } else {
                return NextResponse.json({
                    success: false,
                    error: result.error || "Verification failed"
                }, { status: 500 });
            }
        } catch (aiError: any) {
            console.error(`AI Verification failed for doc ${documentId}:`, aiError);
            return NextResponse.json({
                success: false,
                error: aiError.message || "AI verification failed"
            }, { status: 500 });
        }

    } catch (error) {
        console.error("Error re-analyzing document:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
