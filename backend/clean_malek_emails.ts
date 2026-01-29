import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function cleanEmails() {
    const emailToMatch = 'malek.azri@insat.ucar.tn';

    console.log(`Cleaning emails from: ${emailToMatch}...`);

    const deleted = await prisma.email.deleteMany({
        where: {
            sender: {
                contains: emailToMatch
            }
        }
    });

    console.log(`Successfully deleted ${deleted.count} emails.`);
}

cleanEmails()
    .catch((e) => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
