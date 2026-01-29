import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function checkDuplicates() {
    const emails = await prisma.email.findMany({
        orderBy: { createdAt: 'desc' },
        take: 20
    });

    console.log("Last 10 emails:");
    emails.forEach(e => {
        console.log(`ID: ${e.id} | Subject: ${e.subject} | MsgID: ${e.messageId} | Created: ${e.createdAt}`);
    });
}

checkDuplicates()
    .catch(console.error)
    .finally(() => prisma.$disconnect());
