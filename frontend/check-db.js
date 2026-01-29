const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function checkDb() {
    try {
        const analysts = await prisma.analyst.findMany();
        console.log('Analysts found:', analysts.length);
        analysts.forEach(a => console.log(` - ${a.email} (${a.prenom} ${a.nom})`));

        const clientsWithEmails = await prisma.client.findMany({
            include: { emails: true }
        });
        console.log('Clients with emails found:', clientsWithEmails.length);

        // Check if 'ton_estime' field exists in first email found
        for (const client of clientsWithEmails) {
            if (client.emails && client.emails.length > 0) {
                console.log('Sample email fields:', Object.keys(client.emails[0]));
                break;
            }
        }

    } catch (error) {
        console.error('Error during DB check:', error);
    } finally {
        await prisma.$disconnect();
    }
}

checkDb();
