export type ClientType = "Individu" | "PME";
export type RiskClass = "Bon" | "Moyen" | "Mauvais";
export type Decision = "Oui" | "Non" | "En attente";
export type DocumentStatus = "Green" | "Yellow" | "Red";

export type LoanRequest = {
    id: string;
    applicant: string;
    clientType: ClientType;
    class: RiskClass;
    iaScore: number; // 0-100 (Risk level)
    iaRecommendation: "Oui" | "Non";
    analystDecision: Decision;
    creditAmount: number;
    duration: number; // months
    creditObjective: string;
    repaymentRate: number; // percentage
    age?: number | "-";
    employment?: string | "-";
    creditHistory: string;
    bankCreditsCount: number;
    housing: "Propriétaire" | "Locataire";
    documentStatus: DocumentStatus;
    documentsCount: { total: number; uploaded: number };
    date: string;
    source: string;
};

export const mockLoans: LoanRequest[] = [
    {
        id: "LN-2024-001",
        applicant: "Amine Ben Ali",
        clientType: "Individu",
        class: "Bon",
        iaScore: 12,
        iaRecommendation: "Oui",
        analystDecision: "Oui",
        creditAmount: 25000,
        duration: 24,
        creditObjective: "Achat voiture",
        repaymentRate: 15,
        age: 34,
        employment: "Ingénieur Software",
        creditHistory: "Aucun retard, 2 crédits soldés",
        bankCreditsCount: 0,
        housing: "Propriétaire",
        documentStatus: "Green",
        documentsCount: { total: 7, uploaded: 7 },
        date: "2024-01-15",
        source: "Gmail",
    },
    {
        id: "LN-2024-002",
        applicant: "TechSolution SARL",
        clientType: "PME",
        class: "Moyen",
        iaScore: 45,
        iaRecommendation: "Oui",
        analystDecision: "En attente",
        creditAmount: 150000,
        duration: 60,
        creditObjective: "Expansion parc machine",
        repaymentRate: 25,
        age: "-",
        employment: "-",
        creditHistory: "1 crédit en cours, quelques retards mineurs",
        bankCreditsCount: 1,
        housing: "Locataire",
        documentStatus: "Yellow",
        documentsCount: { total: 10, uploaded: 8 },
        date: "2024-01-18",
        source: "Outlook",
    },
    {
        id: "LN-2024-003",
        applicant: "Samia Tounsi",
        clientType: "Individu",
        class: "Mauvais",
        iaScore: 89,
        iaRecommendation: "Non",
        analystDecision: "En attente",
        creditAmount: 8000,
        duration: 12,
        creditObjective: "Consommation",
        repaymentRate: 45,
        age: 26,
        employment: "Freelance Design",
        creditHistory: "Historique de découverts fréquents",
        bankCreditsCount: 2,
        housing: "Locataire",
        documentStatus: "Red",
        documentsCount: { total: 7, uploaded: 5 },
        date: "2024-01-19",
        source: "WhatsApp",
    },
    {
        id: "LN-2024-004",
        applicant: "Golden Trade Co",
        clientType: "PME",
        class: "Bon",
        iaScore: 22,
        iaRecommendation: "Oui",
        analystDecision: "Oui",
        creditAmount: 500000,
        duration: 36,
        creditObjective: "Fonds de roulement",
        repaymentRate: 10,
        age: "-",
        employment: "-",
        creditHistory: "Excellent, forte croissance 3 ans",
        bankCreditsCount: 0,
        housing: "Propriétaire",
        documentStatus: "Green",
        documentsCount: { total: 10, uploaded: 10 },
        date: "2024-01-20",
        source: "Bank DB",
    }
];

export type DocumentCategory = "Identité" | "Demande" | "Financier" | "Domicile" | "Entreprise" | "Dirigeant";

export type DocumentInfo = {
    name: string;
    category: DocumentCategory;
    previewUrl: string;
    status: "Valide" | "Rejeté" | "En attente";
    ocrValidity: number; // percentage
    clipValidity: number; // percentage
    iaResult: string; // Summary summary
    comment?: string;
    uploadDate: string;
};

export type EmailInfo = {
    subject: string;
    snippet: string;
    date: string;
    sentiment: "Confiance" | "Neutre" | "Stress" | "Doute";
    confidence: number;
    fraudScore?: number; // Internal only for simulation
};

export type VocalInfo = {
    fileName: string;
    transcript: string;
    duration: string;
    emotion: "Calme" | "Stress" | "Nerveux" | "Deception";
    confidence: number;
    date: string;
};

export type FraudAlert = {
    type: "document" | "email" | "vocal";
    targetName: string;
    reason: string;
    metrics: {
        label1: string;
        value1: number | string;
        label2: string;
        value2: number | string;
    };
};

export type AnalysisResult = {
    loanId: string;
    finalDecision: "Oui" | "Non";
    score: number;
    class: RiskClass;
    riskLevel: "Faible" | "Modéré" | "Élevé";
    topFactors: {
        type: "positive" | "negative";
        text: string;
    }[];
    technicalDetails: {
        weights: Record<string, number>;
        fraudAlerts: FraudAlert[];
        confidence: number;
    };
    analystVsIa: {
        analystDecision: Decision;
        justification?: string;
    };
    documents: DocumentInfo[];
    emails: EmailInfo[];
    vocals: VocalInfo[];
    clientDetails: Record<string, any>;
};

export const mockAnalysis: Record<string, AnalysisResult> = {
    "LN-2024-001": {
        loanId: "LN-2024-001",
        finalDecision: "Oui",
        score: 12,
        class: "Bon",
        riskLevel: "Faible",
        topFactors: [
            { type: "positive", text: "Stabilité d'emploi élevée" },
            { type: "positive", text: "Patrimoine important" },
            { type: "positive", text: "Historique de crédit vierge" },
        ],
        technicalDetails: {
            weights: { "Stability": 0.4, "Assets": 0.3, "History": 0.3 },
            fraudAlerts: [],
            confidence: 98,
        },
        analystVsIa: {
            analystDecision: "Oui",
        },
        documents: [
            {
                name: "CIN_Amine.pdf",
                category: "Identité",
                previewUrl: "/api/placeholder/400/300",
                status: "Valide",
                ocrValidity: 100,
                clipValidity: 99,
                iaResult: "Cohérence parfaite, Aucune fraude détectée",
                uploadDate: "2024-01-15",
            },
            {
                name: "Demande_Credit.pdf",
                category: "Demande",
                previewUrl: "/api/placeholder/400/300",
                status: "Valide",
                ocrValidity: 98,
                clipValidity: 95,
                iaResult: "Signature validée, Montant cohérent",
                uploadDate: "2024-01-15",
            }
        ],
        emails: [
            {
                subject: "Demande de prêt immobilier - Amine Ben Ali",
                snippet: "Veuillez trouver ci-joint les documents requis pour mon dossier...",
                date: "2024-01-14",
                sentiment: "Confiance",
                confidence: 96
            }
        ],
        vocals: [
            {
                fileName: "vocal_intro.mp3",
                transcript: "Bonjour, je vous appelle pour confirmer l'envoi de mon dossier.",
                duration: "0:15",
                emotion: "Calme",
                confidence: 98,
                date: "2024-01-15"
            }
        ],
        clientDetails: {
            "Compte courant": "34,500 TND",
            "Épargne": "80,000 TND",
            "Patrimoine": "Appartement S+3",
            "Personnes à charge": "2",
            "Travailleur étranger": "Non",
            "Statut personnel": "Marié",
            "Résidence depuis": "5 ans",
            "Téléphone": "+216 22 333 444",
        }
    },
    "LN-2024-003": {
        loanId: "LN-2024-003",
        finalDecision: "Non",
        score: 89,
        class: "Mauvais",
        riskLevel: "Élevé",
        topFactors: [
            { type: "negative", text: "Taux de remboursement trop élevé (45%)" },
            { type: "negative", text: "Historique de découverts fréquents" },
            { type: "negative", text: "Épargne insuffisante" },
        ],
        technicalDetails: {
            weights: { "DebtRatio": 0.5, "Liquidity": 0.3, "Behavior": 0.2 },
            fraudAlerts: [
                {
                    type: "document",
                    targetName: "Facture_STEG.pdf",
                    reason: "Fraude potentielle : Adresse ne correspond pas à la demande",
                    metrics: { label1: "OCR Validity", value1: "45%", label2: "CLIP Validity", value2: "60%" }
                },
                {
                    type: "vocal",
                    targetName: "whatsapp_voice_001.mp3",
                    reason: "Le ton détecté indique une forte probabilité de tromperie sur les revenus",
                    metrics: { label1: "Emotion", value1: "Deception", label2: "Confiance IA", value2: "85%" }
                }
            ],
            confidence: 92,
        },
        analystVsIa: {
            analystDecision: "En attente",
        },
        documents: [
            {
                name: "CIN_Samia.jpg",
                category: "Identité",
                previewUrl: "/api/placeholder/400/300",
                status: "Valide",
                ocrValidity: 95,
                clipValidity: 92,
                iaResult: "Validité CIN confirmée",
                uploadDate: "2024-01-19",
            },
            {
                name: "Facture_STEG.pdf",
                category: "Domicile",
                previewUrl: "/api/placeholder/400/300",
                status: "Rejeté",
                ocrValidity: 45,
                clipValidity: 60,
                iaResult: "Fraude potentielle : Adresse ne correspond pas à la demande",
                comment: "Veuillez fournir un justificatif récent à la bonne adresse",
                uploadDate: "2024-01-19",
            }
        ],
        emails: [
            {
                subject: "Précisions sur mes revenus",
                snippet: "Je tiens à préciser que mes revenus freelance sont variables...",
                date: "2024-01-20",
                sentiment: "Stress",
                confidence: 82
            }
        ],
        vocals: [
            {
                fileName: "whatsapp_voice_001.mp3",
                transcript: "Euh, oui, je travaille à mon compte depuis trois ans environ...",
                duration: "0:45",
                emotion: "Deception",
                confidence: 85,
                date: "2024-01-20"
            }
        ],
        clientDetails: {
            "Compte courant": "-120 TND (Moyen)",
            "Épargne": "500 TND",
            "Patrimoine": "Aucun",
            "Personnes à charge": "0",
            "Travailleur étranger": "Non",
            "Statut personnel": "Célibataire",
            "Résidence depuis": "1 an",
            "Téléphone": "+216 55 666 777",
        }
    }
};

export type Integration = {
    id: string;
    name: string;
    type: "CRM" | "Email" | "Chat" | "Database" | "Custom";
    connected: boolean;
    lastSync?: string;
    icon?: string;
};

export const defaultIntegrations: Integration[] = [
    { id: "int_1", name: "Bank CRM Core", type: "CRM", connected: true, lastSync: "2 mins ago" },
    { id: "int_2", name: "Outlook Business", type: "Email", connected: true, lastSync: "10 mins ago" },
    { id: "int_3", name: "WhatsApp Business API", type: "Chat", connected: true, lastSync: "Live" },
    { id: "int_4", name: "Gmail Corporate", type: "Email", connected: false },
    { id: "int_5", name: "Oracle DB Internal", type: "Database", connected: true, lastSync: "1 hour ago" },
];
