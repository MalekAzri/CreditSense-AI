const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();
const bcrypt = require('bcrypt');
const path = require('path');

async function main() {
    console.log('--- Starting Demo V2 Database Seeding ---');

    console.log('Cleaning up existing data...');
    await prisma.vocal.deleteMany({});
    await prisma.document.deleteMany({});
    await prisma.email.deleteMany({});
    await prisma.analystMessage.deleteMany({});
    await prisma.analyst.deleteMany({});
    await prisma.client.deleteMany({});

    console.log('Creating Test Analysts...');
    const hashedPass = await bcrypt.hash('password123', 10);

    const malek = await prisma.analyst.create({
        data: {
            nom: 'Azri',
            prenom: 'Malek',
            email: 'malek@creditsense.ai',
            password: hashedPass,
            role: 'admin',
            bank: 'BIAT',
            lastSeen: new Date()
        }
    });

    const sarah = await prisma.analyst.create({
        data: {
            nom: 'Connor',
            prenom: 'Sarah',
            email: 'sarah.connor@creditsense.ai',
            password: hashedPass,
            role: 'analyst',
            bank: 'BIAT',
            lastSeen: new Date(Date.now() - 1000 * 60 * 5)
        }
    });

    // Mock data for documents
    // Paths are absolute as requested for Windows
    const docsBase = 'd:/CreditSense Ai/module-verification-docs/docs/';

    const clientsData = [
        {
            typeClient: 'individu',
            nom: 'Ben Mabrouk',
            prenom: 'Amira',
            email: 'amira.mabrouk@email.com',
            compte_courant: '400050006000',
            duree_mois: 24,
            historique_credit: 'crédit en cours remboursé normalement',
            objectif_credit: 'travaux maison',
            montant_credit: 25000,
            epargne: 12000,
            emploi: 'Médecin spécialiste',
            emploi_depuis: 8,
            taux_remboursement: 0.2,
            statut_personnel: 'marié',
            garants: 'conjoint',
            residence_depuis: 5,
            patrimoine: 250000,
            age: 35,
            autres_credits: 'un crédit immobilier',
            logement: 'propriétaire',
            nb_credits_banque: 2,
            personnes_a_charge: 2,
            telephone: '21655667788',
            travailleur_etranger: false,
            classe: null, // Pending ML
            emails: [
                {
                    subject: 'Soumission documents officiels - Amira Ben Mabrouk',
                    sender: 'amira.mabrouk@email.com',
                    body: 'Monsieur le conseiller,\n\nComme convenu lors de notre entretien, je vous transmets mon passeport pour la validation finale de mon prêt travaux.\n\nBien respectueusement,\nDr. Amira Ben Mabrouk',
                    intention: 'soumission de document officiel',
                    ton_serieux: 98,
                    attachments: [
                        { type: 'PASSPORT', url: docsBase + 'test_passport_1.png', clipScore: 0.94, ocrScore: 0.91, statut: 'valide' }
                    ]
                }
            ]
        },
        {
            typeClient: 'pme',
            nom: 'Sousse Tech Solutions',
            prenom: 'Mohamed Ali',
            email: 'contact@soussetech.com',
            compte_courant: '700080009000',
            duree_mois: 36,
            historique_credit: 'retards fréquents sur lignes de crédit',
            objectif_credit: 'Expansion matériel informatique',
            montant_credit: 50000,
            epargne: 2000,
            emploi: 'Directeur Général',
            emploi_depuis: 3,
            taux_remboursement: 0.35,
            statut_personnel: 'marié',
            garants: 'personne morale',
            residence_depuis: 2,
            patrimoine: 40000,
            age: 42,
            autres_credits: 'Ligne de découvert active',
            logement: 'location (bureau)',
            nb_credits_banque: 3,
            personnes_a_charge: 1,
            telephone: '21622334455',
            travailleur_etranger: false,
            classe: null, // Pending ML
            emails: [
                {
                    subject: 'Demande de crédit BTS - Sousse Tech Solutions',
                    sender: 'contact@soussetech.com',
                    body: 'Bonjour,\n\nNous souhaitons solliciter un financement BTS pour l’acquisition de nouveaux serveurs. Vous trouverez ci-joint le formulaire de demande.\n\nCordialement,\nMohamed Ali - CEO',
                    intention: 'demande de fonds entreprise',
                    ton_stress: 40,
                    ton_serieux: 85,
                    attachments: [
                        { type: 'BTS_LOAN_APP', url: docsBase + 'bts_loan_app.png', clipScore: 0.88, ocrScore: 0.82, statut: 'en_attente' },
                        { type: 'Facture', url: docsBase + 'Facture.pdf_page_1.png', clipScore: 0.70, ocrScore: 0.65, statut: 'en_attente' }
                    ]
                }
            ]
        },
        {
            typeClient: 'individu',
            nom: 'Azri',
            prenom: 'Malek',
            email: 'malek.azri@insat.ucar.tn',
            compte_courant: '123456789012',
            duree_mois: 12,
            historique_credit: 'nouveau client',
            objectif_credit: 'Prêt consommation personnel',
            montant_credit: 7500,
            epargne: 3000,
            emploi: 'Software Architect',
            emploi_depuis: 4,
            taux_remboursement: 0.12,
            statut_personnel: 'célibataire',
            garants: 'aucun',
            residence_depuis: 5,
            patrimoine: 15000,
            age: 26,
            autres_credits: 'aucun',
            logement: 'appartement privé',
            nb_credits_banque: 0,
            personnes_a_charge: 0,
            telephone: '21655555555',
            travailleur_etranger: false,
            classe: null,
            emails: [
                {
                    subject: 'Question concernant les taux actuels',
                    sender: 'malek.azri@insat.ucar.tn',
                    body: 'Bonjour, je souhaiterais connaître vos taux pour un prêt consommation sur 12 mois. Merci.',
                    intention: 'demande information',
                    ton_serieux: 90
                }
            ]
        },
        {
            typeClient: 'individu',
            nom: 'Belhadj',
            prenom: 'Yassine',
            email: 'yassine.belhadj@email.tn',
            compte_courant: '888899990000',
            duree_mois: 18,
            historique_credit: 'historique impeccable',
            objectif_credit: 'Achat de matériel électroménager',
            montant_credit: 4500,
            epargne: 1500,
            emploi: 'Comptable Senior',
            emploi_depuis: 10,
            taux_remboursement: 0.08,
            statut_personnel: 'marié',
            residence_depuis: 12,
            patrimoine: 120000,
            age: 45,
            autres_credits: 'aucun',
            logement: 'propriétaire',
            nb_credits_banque: 1,
            personnes_a_charge: 3,
            telephone: '21620202020',
            travailleur_etranger: false,
            classe: null,
            emails: [
                {
                    subject: 'Dossier complet pour crédit consommation - Yassine Belhadj',
                    sender: 'yassine.belhadj@email.tn',
                    body: 'Messieurs,\n\nJe vous adresse l’intégralité des pièces pour mon dossier de crédit. Vous y trouverez ma CIN ainsi qu’une facture récente.\n\nSalutations,\nYassine Belhadj',
                    intention: 'envoi dossier complet',
                    ton_serieux: 99,
                    attachments: [
                        { type: 'CIN', url: docsBase + 'test_cin_1.png', clipScore: 0.99, ocrScore: 0.98, statut: 'valide' },
                        { type: 'DOMICILE', url: docsBase + 'Facture.pdf_page_1.png', clipScore: 0.95, ocrScore: 0.92, statut: 'valide' }
                    ]
                }
            ]
        },
        {
            typeClient: 'pme',
            nom: 'Carthage Construction Ltd',
            prenom: 'Omar',
            email: 'omar.benali@carthage-const.com',
            compte_courant: '554433221100',
            duree_mois: 60,
            historique_credit: 'Incident de paiement en 2024',
            objectif_credit: 'Achat grue de chantier',
            montant_credit: 150000,
            epargne: 15000,
            emploi: 'Fondateur',
            emploi_depuis: 15,
            taux_remboursement: 0.45,
            statut_personnel: 'marié',
            residence_depuis: 15,
            patrimoine: 800000,
            age: 50,
            autres_credits: 'Crédit bail actif',
            logement: 'propriétaire',
            nb_credits_banque: 2,
            personnes_a_charge: 4,
            telephone: '21671000888',
            travailleur_etranger: false,
            classe: null,
            emails: [
                {
                    subject: 'Demande urgente de financement - Carthage Construction',
                    sender: 'omar.benali@carthage-const.com',
                    body: 'Nous avons besoin d’une réponse rapide pour l’acquisition de notre nouveau matériel de levage. Voici nos documents financiers.\n\nOmar Ben Ali',
                    intention: 'demande urgente',
                    ton_stress: 85,
                    ton_serieux: 75,
                    attachments: [
                        { type: 'BTS_LOAN_APP', url: docsBase + 'test_loan_doc.png', clipScore: 0.42, ocrScore: 0.45, statut: 'en_attente' }
                    ]
                }
            ]
        }
    ];

    for (const clientData of clientsData) {
        const { emails, ...clientFields } = clientData;
        const client = await prisma.client.create({
            data: clientFields
        });

        if (emails) {
            for (const emailData of emails) {
                const { attachments, ...emailFields } = emailData;
                const email = await prisma.email.create({
                    data: {
                        ...emailFields,
                        clientId: client.id,
                        status: 'processed'
                    }
                });

                if (attachments) {
                    for (const att of attachments) {
                        await prisma.document.create({
                            data: {
                                ...att,
                                clientId: client.id,
                                emailId: email.id
                            }
                        });
                    }
                }
            }
        }
        console.log(`Created client: ${client.nom} ${client.prenom || ''} (ID: ${client.id})`);
    }

    console.log('--- Seeding Completed Successfully ---');
}

main()
    .catch((e) => {
        console.error('Error during seeding:', e);
        process.exit(1);
    })
    .finally(async () => {
        await prisma.$disconnect();
    });
