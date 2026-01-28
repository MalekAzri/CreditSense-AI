import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth/next";
import { authOptions } from "@/lib/auth";
import fs from "fs";
import path from "path";

export async function GET(req: NextRequest) {
    try {
        const session = await getServerSession(authOptions);
        if (!session) {
            return new NextResponse("Unauthorized", { status: 401 });
        }

        const { searchParams } = new URL(req.url);
        const filePath = searchParams.get("path");

        if (!filePath) {
            return new NextResponse("Path is required", { status: 400 });
        }

        // Security check: only allow files within the project directory
        // In this specific case, we'll allow paths that start with 'd:/CreditSense Ai'
        const normalizedPath = path.normalize(filePath).replace(/\\/g, "/");
        if (!normalizedPath.toLowerCase().startsWith("d:/creditsense ai")) {
            return new NextResponse("Access denied: Path outside project", { status: 403 });
        }

        if (!fs.existsSync(normalizedPath)) {
            return new NextResponse("File not found", { status: 404 });
        }

        const fileBuffer = fs.readFileSync(normalizedPath);
        const ext = path.extname(normalizedPath).toLowerCase();

        const contentTypes: Record<string, string> = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".pdf": "application/pdf",
        };

        return new NextResponse(fileBuffer, {
            headers: {
                "Content-Type": contentTypes[ext] || "application/octet-stream",
                "Cache-Control": "public, max-age=31536000, immutable",
            },
        });
    } catch (error) {
        console.error("Error serving document:", error);
        return new NextResponse("Internal Server Error", { status: 500 });
    }
}
