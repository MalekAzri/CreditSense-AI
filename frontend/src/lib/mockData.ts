export type LoanRequest = {
    id: string;
    applicant: string;
    source: "Gmail" | "WhatsApp" | "Outlook" | "Manual" | "Bank DB" | "CRM";
    amount: number;
    date: string;
    riskScore: number; // 0-100
    status: "Pending" | "Approved" | "Rejected" | "Needs Review";
    avatar?: string;
};

export const mockLoans: LoanRequest[] = [
    {
        id: "LN-2024-001",
        applicant: "Amine Ben Ali",
        source: "Gmail",
        amount: 25000,
        date: "2024-01-15",
        riskScore: 12, // Low risk
        status: "Approved",
    },
    {
        id: "LN-2024-002",
        applicant: "TechSolution SARL",
        source: "Outlook",
        amount: 150000,
        date: "2024-01-18",
        riskScore: 45, // Medium
        status: "Pending",
    },
    {
        id: "LN-2024-003",
        applicant: "Samia Tounsi",
        source: "WhatsApp",
        amount: 8000,
        date: "2024-01-19",
        riskScore: 89, // High risk
        status: "Needs Review",
    },
    {
        id: "LN-2024-004",
        applicant: "Golden Trade Co",
        source: "Bank DB",
        amount: 500000,
        date: "2024-01-20",
        riskScore: 32,
        status: "Pending",
    }
];

export type Integration = {
    id: string;
    name: string;
    type: "CRM" | "Email" | "Chat" | "Database" | "Custom";
    connected: boolean;
    lastSync?: string;
    icon?: string;
    apiKey?: string; // For custom
    endpoint?: string; // For custom
};

export const defaultIntegrations: Integration[] = [
    { id: "int_1", name: "Bank CRM Core", type: "CRM", connected: true, lastSync: "2 mins ago" },
    { id: "int_2", name: "Outlook Business", type: "Email", connected: true, lastSync: "10 mins ago" },
    { id: "int_3", name: "WhatsApp Business API", type: "Chat", connected: true, lastSync: "Live" },
    { id: "int_4", name: "Gmail Corporate", type: "Email", connected: false },
    { id: "int_5", name: "Oracle DB Internal", type: "Database", connected: true, lastSync: "1 hour ago" },
];

export type AnalysisResult = {
    loanId: string;
    summary: string;
    documents: {
        name: string;
        type: "PDF" | "Image";
        status: "Valid" | "Forged" | "Suspicious";
        confidence: number;
    }[];
    toneAnalysis: {
        source: "Audio Call" | "WhatsApp Voice" | "Email Text";
        sentiment: "Neutral" | "Stress" | "Deception" | "Confident";
        confidence: number;
        details: string;
    };
    recommendation: {
        decision: "Approve" | "Reject" | "Investigate";
        reason: string;
    };
};

export const mockAnalysis: Record<string, AnalysisResult> = {
    "LN-2024-003": {
        loanId: "LN-2024-003",
        summary: "Suspicious activity detected in provided ID documents and high stress levels in voice notes.",
        documents: [
            { name: "CIN_Recto.jpg", type: "Image", status: "Suspicious", confidence: 65 },
            { name: "Releve_Bancaire.pdf", type: "PDF", status: "Valid", confidence: 98 },
        ],
        toneAnalysis: {
            source: "WhatsApp Voice",
            sentiment: "Stress",
            confidence: 88,
            details: "Voice analysis detected micro-tremors associated with deception when discussing income sources.",
        },
        recommendation: {
            decision: "Investigate",
            reason: "Inconsistent documentation and potential deceptive behavior in communication.",
        },
    },
    "LN-2024-001": {
        loanId: "LN-2024-001",
        summary: "All sources verify stable income and valid identity.",
        documents: [
            { name: "CIN_Copie.pdf", type: "PDF", status: "Valid", confidence: 99 },
            { name: "Salary_Slip.pdf", type: "PDF", status: "Valid", confidence: 97 },
        ],
        toneAnalysis: {
            source: "Email Text",
            sentiment: "Confident",
            confidence: 95,
            details: "Communication is professional and consistent with provided data.",
        },
        recommendation: {
            decision: "Approve",
            reason: "Low risk score and validated documents.",
        },
    },
};
