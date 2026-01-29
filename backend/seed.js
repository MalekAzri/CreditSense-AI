const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();
const bcrypt = require('bcrypt');

async function main() {
    console.log('--- Starting Complete Database Seeding with Messaging ---');

    console.log('Cleaning up existing data...');
    // Delete in order to respect constraints
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

    const mark = await prisma.analyst.create({
        data: {
            nom: 'Zuckerberg',
            prenom: 'Mark',
            email: 'mark@creditsense.ai',
            password: hashedPass,
            role: 'analyst',
            bank: 'BNA',
            lastSeen: new Date()
        }
    });

    console.log('Creating test messages...');
    await prisma.analystMessage.create({
        data: {
            content: "Salut Malek, as-tu fini l'analyse du document BTS pour Sousse Tech ?",
            senderId: sarah.id,
            receiverId: malek.id,
            createdAt: new Date(Date.now() - 1000 * 60 * 30)
        }
    });

    await prisma.analystMessage.create({
        data: {
            content: "Presque Sarah, je vérifie encore les vecteurs CLIP. Ça semble valide.",
            senderId: malek.id,
            receiverId: sarah.id,
            createdAt: new Date(Date.now() - 1000 * 60 * 20)
        }
    });

    const clientsData = [
        {
            typeClient: 'individu',
            nom: 'Trabelsi',
            prenom: 'Sami',
            email: 'sami.trabelsi@email.com',
            compte_courant: '100020003000',
            duree_mois: 12,
            historique_credit: 'aucun crédit existant',
            objectif_credit: 'achat voiture',
            montant_credit: 12000,
            epargne: 5000,
            emploi: 'ingénieur',
            emploi_depuis: 5,
            taux_remboursement: 0.15,
            statut_personnel: 'célibataire',
            garants: 'aucun',
            residence_depuis: 3,
            patrimoine: 80000,
            age: 30,
            autres_credits: 'aucun',
            logement: 'propriétaire',
            nb_credits_banque: 1,
            personnes_a_charge: 0,
            telephone: '21698765432',
            travailleur_etranger: false,
            classe: 'bon client', // Résultat du module ML
            decision_ia: 'donner', // Résultat du module de score final
            decision_analyste: 'donner',
            difference_ia_analyste: false,
            emails: {
                create: [
                    {
                        subject: 'Demande de prêt automobile - Trabelsi Sami',
                        sender: 'sami.trabelsi@email.com',
                        body: 'Bonjour, je vous envoie ma CIN pour compléter ma demande de crédit pour ma nouvelle voiture. Merci de me tenir informé.',
                        status: 'received',
                        intention: 'envoi de documents',
                        confiance: 0.95,
                        ton_urgence: 40,
                        ton_stress: 10,
                        ton_serieux: 90,
                        extractedData: {
                            "Clean Text": "Demande de prêt automobile",
                            "Credit Type": "automobile",
                            "Amount": "12000 TND",
                            "Client Name": "Sami Trabelsi",
                            "Phone": "21698765432",
                            "CIN": "12345678",
                            "Reference": "REF-AUTO-001"
                        },
                        attachments: {
                            create: [
                                {
                                    type: 'CIN',
                                    url: 'd:/CreditSense Ai/module-verification-docs/docs/CIN.png',
                                    clientId: 0, // Placeholder
                                    statut: 'valide',
                                    clipScore: 0.98,
                                    ocrScore: 0.95
                                }
                            ]
                        }
                    }
                ]
            }
        },
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
            emploi: 'médecin',
            emploi_depuis: 8,
            taux_remboursement: 0.2,
            statut_personnel: 'marié',
            garants: 'conjoint',
            residence_depuis: 5,
            patrimoine: 150000,
            age: 35,
            autres_credits: 'un crédit immobilier',
            logement: 'propriétaire',
            nb_credits_banque: 2,
            personnes_a_charge: 2,
            telephone: '21655667788',
            travailleur_etranger: false,
            classe: 'bon client',
            decision_ia: 'donner',
            decision_analyste: 'donner',
            difference_ia_analyste: false,
            emails: {
                create: [
                    {
                        subject: 'Envoi de Passport - Amira Ben Mabrouk',
                        sender: 'amira.mabrouk@email.com',
                        body: 'Ci-joint mon passport pour la validation de mon dossier de crédit travaux. Cordialement.',
                        status: 'received',
                        intention: 'soumission de document officiel',
                        confiance: 0.98,
                        ton_urgence: 60,
                        ton_stress: 20,
                        ton_serieux: 95,
                        extractedData: {
                            "Clean Text": "Envoi de Passport pour validation",
                            "Credit Type": "travaux",
                            "Amount": "25000 TND",
                            "Client Name": "Amira Ben Mabrouk",
                            "Phone": "21655667788",
                            "CIN": "None",
                            "Reference": "None"
                        },
                        attachments: {
                            create: [
                                {
                                    type: 'PASSPORT',
                                    url: 'd:/CreditSense Ai/module-verification-docs/docs/test_passport_1.png',
                                    clientId: 0,
                                    statut: 'valide',
                                    clipScore: 0.92,
                                    ocrScore: 0.88
                                }
                            ]
                        }
                    }
                ]
            }
        },
        {
            typeClient: 'pme',
            nom: 'Sousse Tech Solutions',
            prenom: 'Mohamed Ali',
            email: 'contact@soussetech.com',
            compte_courant: '700080009000',
            duree_mois: 36,
            historique_credit: 'retards fréquents sur lignes de crédit',
            objectif_credit: 'expansion matériel informatique',
            montant_credit: 50000,
            epargne: 2000,
            emploi: 'chef d\'entreprise',
            emploi_depuis: 3,
            taux_remboursement: 0.35,
            statut_personnel: 'divorcé',
            garants: 'personne morale',
            residence_depuis: 2,
            patrimoine: 40000,
            age: 45,
            autres_credits: 'plusieurs crédits courts termes',
            logement: 'location',
            nb_credits_banque: 3,
            personnes_a_charge: 1,
            telephone: '21622334455',
            travailleur_etranger: false,
            classe: 'mauvais client',
            decision_ia: 'refuser',
            decision_analyste: 'donner',
            difference_ia_analyste: true,
            emails: {
                create: [
                    {
                        subject: 'URGENT: Demande de crédit BTS - Sousse Tech',
                        sender: 'contact@soussetech.com',
                        body: 'Nous avons besoin de ce crédit rapidement pour payer nos fournisseurs. Voici le formulaire rempli.',
                        status: 'received',
                        intention: 'demande urgente de fonds',
                        confiance: 0.65,
                        ton_urgence: 95,
                        ton_stress: 80,
                        ton_serieux: 70,
                        extractedData: {
                            "Clean Text": "URGENT: Demande de crédit BTS",
                            "Credit Type": "BTS",
                            "Amount": "50000 TND",
                            "Client Name": "Mohamed Ali",
                            "Phone": "21622334455",
                            "CIN": "None",
                            "Reference": "BTS-Sousse-2026"
                        },
                        attachments: {
                            create: [
                                {
                                    type: 'BTS_LOAN_APP',
                                    url: 'd:/CreditSense Ai/module-verification-docs/docs/bts_loan_app.png',
                                    clientId: 0,
                                    statut: 'valide',
                                    clipScore: 0.85,
                                    ocrScore: 0.82
                                },
                                {
                                    type: 'BTS_LOAN_APP',
                                    url: 'd:/CreditSense Ai/module-verification-docs/docs/test_loan_doc.png',
                                    clientId: 0,
                                    statut: 'en_attente',
                                    clipScore: 0.75,
                                    ocrScore: 0.71
                                }
                            ]
                        }
                    }
                ]
            }
        },
        {
            typeClient: 'individu',
            nom: 'Azri',
            prenom: 'Malek',
            email: 'malek.azri@insat.ucar.tn', // Requested test email
            compte_courant: '123456789012',
            duree_mois: 12,
            historique_credit: 'nouveau client',
            objectif_credit: 'consommation',
            montant_credit: 5000,
            epargne: 1000,
            emploi: 'ingénieur',
            emploi_depuis: 2,
            taux_remboursement: 0.1,
            statut_personnel: 'célibataire',
            garants: 'aucun',
            residence_depuis: 5,
            patrimoine: 10000,
            age: 25,
            autres_credits: 'aucun',
            logement: 'locataire',
            nb_credits_banque: 0,
            personnes_a_charge: 0,
            telephone: '21655555555',
            travailleur_etranger: false,
            classe: 'bon client',
            decision_ia: 'donner',
            decision_analyste: 'donner',
            difference_ia_analyste: false,
            emails: {
                create: [] // No emails initially
            }
        }
    ];

    for (const clientData of clientsData) {
        const { emails, ...clientFields } = clientData;
        const client = await prisma.client.create({
            data: clientFields
        });

        if (emails && emails.create) {
            for (const emailData of emails.create) {
                const { attachments, ...emailFields } = emailData;
                await prisma.email.create({
                    data: {
                        ...emailFields,
                        clientId: client.id,
                        attachments: attachments ? {
                            create: attachments.create.map(att => ({
                                ...att,
                                clientId: client.id
                            }))
                        } : undefined
                    }
                });
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
