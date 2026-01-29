
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
    const email = "malek.azri@insat.ucar.tn";
    const namePartial = "Malek";

    console.log(`Looking for client matching "${namePartial}"...`);

    // 1. Find the client first
    const client = await prisma.client.findFirst({
        where: {
            AND: [
                { nom: { contains: "Azri" } },
                { prenom: { contains: "Malek" } }
            ]
        }
    });

    if (client) {
        // 2. Update by ID
        const updated = await prisma.client.update({
            where: { id: client.id },
            data: { email: email }
        });
        console.log(`Successfully updated client: ${updated.nom} ${updated.prenom} (ID: ${updated.id}) with email ${email}`);
    } else {
        console.log("No client found matching 'Malek Azri'. Creating one for test...");

        // Create if not exists (fallback)
        // Note: 'cin' is likely unique, so we provide a random one for testing
        const randomCin = Math.floor(10000000 + Math.random() * 90000000).toString();

        const newClient = await prisma.client.create({
            data: {
                nom: "Azri",
                prenom: "Malek",
                email: email,
                cin: randomCin,
                typeClient: "individu",
                classe: "bon client"
            }
        });
        console.log(`Created new test client: ${newClient.nom} ${newClient.prenom} (ID: ${newClient.id}, CIN: ${newClient.cin})`);
    }
}

main()
    .catch(e => {
        console.error(e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
