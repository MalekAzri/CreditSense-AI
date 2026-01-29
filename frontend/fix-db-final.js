const { PrismaClient } = require('@prisma/client');
const bcrypt = require('bcrypt');
const prisma = new PrismaClient();

async function fixDb() {
    try {
        console.log('--- Fixing Database Records ---');

        // 1. Ensure Analyst exists (to fix heartbeat)
        const email = 'malek.azri@gmail.com';
        const hashedPassword = await bcrypt.hash('password123', 10);

        const analyst = await prisma.analyst.upsert({
            where: { email },
            update: {},
            create: {
                nom: 'Azri',
                prenom: 'Malek',
                email,
                password: hashedPassword,
                role: 'admin',
                bank: 'BIAT'
            }
        });
        console.log(`[OK] Analyst verified: ${analyst.email} (ID: ${analyst.id})`);

        // 2. Ensure Client exists (for email test)
        const clientEmail = 'malek.azri@insat.ucar.tn';
        const client = await prisma.client.upsert({
            where: { email: clientEmail },
            update: {},
            create: {
                typeClient: 'individu',
                nom: 'Azri',
                prenom: 'Malek',
                email: clientEmail,
                montant_credit: 150000,
                duree_mois: 24,
                objectif_credit: 'Crédit Immobilier',
                classe: 'bon client',
                decision_ia: 'en_attente',
                decision_analyste: 'en_attente'
            }
        });
        console.log(`[OK] Client verified: ${client.email} (ID: ${client.id})`);

        console.log('--- DB Fix Complete ---');
    } catch (error) {
        console.error('[ERROR] DB Fix failed:', error);
    } finally {
        await prisma.$disconnect();
    }
}

fixDb();
