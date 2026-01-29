-- CreateTable
CREATE TABLE `Client` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `typeClient` VARCHAR(191) NOT NULL,
    `nom` VARCHAR(191) NULL,
    `prenom` VARCHAR(191) NULL,
    `compte_courant` VARCHAR(191) NULL,
    `duree_mois` INTEGER NULL,
    `historique_credit` VARCHAR(191) NULL,
    `objectif_credit` VARCHAR(191) NULL,
    `montant_credit` DOUBLE NULL,
    `epargne` DOUBLE NULL,
    `emploi` VARCHAR(191) NULL,
    `emploi_depuis` INTEGER NULL,
    `taux_remboursement` DOUBLE NULL,
    `statut_personnel` VARCHAR(191) NULL,
    `garants` VARCHAR(191) NULL,
    `residence_depuis` INTEGER NULL,
    `patrimoine` DOUBLE NULL,
    `age` INTEGER NULL,
    `autres_credits` VARCHAR(191) NULL,
    `logement` VARCHAR(191) NULL,
    `nb_credits_banque` INTEGER NULL,
    `personnes_a_charge` INTEGER NULL,
    `telephone` VARCHAR(191) NULL,
    `travailleur_etranger` BOOLEAN NULL,
    `classe` VARCHAR(191) NULL,
    `decision_ia` VARCHAR(191) NULL,
    `decision_analyste` VARCHAR(191) NULL,
    `difference_ia_analyste` BOOLEAN NULL,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `Document` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `clientId` INTEGER NOT NULL,
    `emailId` INTEGER NULL,
    `type` VARCHAR(191) NOT NULL,
    `url` VARCHAR(191) NOT NULL,
    `ocrScore` DOUBLE NULL,
    `clipScore` DOUBLE NULL,
    `statut` VARCHAR(191) NULL,
    `commentaire` VARCHAR(191) NULL,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `Email` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `clientId` INTEGER NOT NULL,
    `subject` VARCHAR(191) NOT NULL,
    `body` VARCHAR(191) NOT NULL,
    `sentAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `status` VARCHAR(191) NULL,
    `intention` VARCHAR(191) NULL,
    `confiance` DOUBLE NULL,
    `ton_estime` VARCHAR(191) NULL,

    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `Vocal` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `clientId` INTEGER NOT NULL,
    `url` VARCHAR(191) NOT NULL,
    `type` VARCHAR(191) NULL,
    `duration` INTEGER NULL,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),

    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `Analyst` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `nom` VARCHAR(191) NOT NULL,
    `prenom` VARCHAR(191) NOT NULL,
    `email` VARCHAR(191) NOT NULL,
    `password` VARCHAR(191) NOT NULL,
    `role` VARCHAR(191) NOT NULL DEFAULT 'analyst',
    `bank` VARCHAR(191) NULL,
    `lastSeen` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    UNIQUE INDEX `Analyst_email_key`(`email`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `AnalystMessage` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `content` TEXT NOT NULL,
    `senderId` INTEGER NOT NULL,
    `receiverId` INTEGER NOT NULL,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `read` BOOLEAN NOT NULL DEFAULT false,

    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- AddForeignKey
ALTER TABLE `Document` ADD CONSTRAINT `Document_clientId_fkey` FOREIGN KEY (`clientId`) REFERENCES `Client`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `Document` ADD CONSTRAINT `Document_emailId_fkey` FOREIGN KEY (`emailId`) REFERENCES `Email`(`id`) ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `Email` ADD CONSTRAINT `Email_clientId_fkey` FOREIGN KEY (`clientId`) REFERENCES `Client`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `Vocal` ADD CONSTRAINT `Vocal_clientId_fkey` FOREIGN KEY (`clientId`) REFERENCES `Client`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `AnalystMessage` ADD CONSTRAINT `AnalystMessage_senderId_fkey` FOREIGN KEY (`senderId`) REFERENCES `Analyst`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `AnalystMessage` ADD CONSTRAINT `AnalystMessage_receiverId_fkey` FOREIGN KEY (`receiverId`) REFERENCES `Analyst`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;
