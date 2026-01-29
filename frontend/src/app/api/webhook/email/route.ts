
import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function POST(req: Request) {
    try {
        const body = await req.json();
        const {
            subject,
            sender,
            content_text,
            extracted_data,
            similarity_results,
            auto_reply,
            status,
            metadata
        } = body;

        const messageId = metadata?.message_id;

        console.log(`[Webhook] Received email from: ${sender} - Subject: ${subject} - MsgID: ${messageId}`);

        // 0. Check for duplicates
        if (messageId) {
            const existing = await prisma.email.findUnique({
                where: { messageId }
            });
            if (existing) {
                console.log(`[Webhook] Email ${messageId} already exists. Skipping.`);
                return NextResponse.json({
                    success: true,
                    message: "Email already exists",
                    emailId: existing.id
                });
            }
        }

        // 1. Try to find client by email
        // Extract email from "Name <email@example.com>" format if needed
        let emailAddress = sender;
        const emailMatch = sender.match(/<([^>]+)>/);
        if (emailMatch) {
            emailAddress = emailMatch[1];
        }

        let client = await prisma.client.findFirst({
            where: {
                email: emailAddress
            }
        });

        // 2. Prepare Tone Analysis Data
        const toneData = similarity_results?.tone_estimation || {};

        // 3. Create Email Record
        const newEmail = await prisma.email.create({
            data: {
                subject: subject || "No Subject",
                sender: sender,
                body: content_text || "",
                status: status || "processed",

                // Link to client if found (clientId is optional now)
                clientId: client?.id || null, // Explicitly null if not found
                messageId: messageId,

                // AI Analysis
                intention: similarity_results?.top_intent,
                confiance: similarity_results?.confidence,

                // Tone (default to 0 if missing)
                ton_urgence: toneData.urgency || 0,
                ton_stress: toneData.stress || 0,
                ton_serieux: toneData.seriousness || 0,

                suggestion_reply: auto_reply,

                // Structured Data
                extractedData: extracted_data || {}
            }
        });

        if (client) {
            console.log(`[Webhook] Linked email ${newEmail.id} to Client ${client.id} (${client.nom})`);
        } else {
            console.log(`[Webhook] Email ${newEmail.id} is UNMATCHED (No client found for ${emailAddress})`);
        }

        return NextResponse.json({
            success: true,
            message: "Email processed and saved",
            emailId: newEmail.id,
            linkedClientId: client?.id || null
        });

    } catch (error: any) {
        console.error("[Webhook] Error processing email:", error);
        return NextResponse.json(
            { success: false, error: error.message },
            { status: 500 }
        );
    }
}
