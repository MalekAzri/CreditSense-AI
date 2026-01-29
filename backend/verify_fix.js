const { PrismaClient } = require('@prisma/client')
const prisma = new PrismaClient()

async function main() {
    try {
        const emails = await prisma.email.findMany({
            take: 1
        })
        console.log('Successfully queried Email table. Count:', emails.length)
        if (emails.length > 0) {
            console.log('Sample email keys:', Object.keys(emails[0]))
        }
    } catch (e) {
        console.error('Error querying Email table:', e)
    } finally {
        await prisma.$disconnect()
    }
}

main()
