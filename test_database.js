const { PrismaClient } = require('@prisma/client');

// Set environment variables
process.env.DATABASE_URL = `postgresql://postgres.wjtyfgibnylvlgeusrxf:${process.env.SUPABASE_PASSWORD}@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres?pgbouncer=true`;

const prisma = new PrismaClient();

async function testDatabase() {
  console.log('🚀 Testing Supabase database connection...\n');

  try {
    // Test connection
    await prisma.$connect();
    console.log('✅ Successfully connected to Supabase database!\n');

    // Create a test user
    const sessionId = `test-session-${Date.now()}`;
    const user = await prisma.user.create({
      data: {
        sessionId: sessionId,
        name: 'Test Student',
        email: 'test@example.com',
        bio: 'Testing the database connection',
        preferences: { theme: 'dark', notifications: true }
      }
    });
    console.log('✅ Created test user:', {
      id: user.id,
      name: user.name,
      sessionId: user.sessionId
    });

    // Create a test chat message
    const chatMessage = await prisma.chatMessage.create({
      data: {
        userId: user.id,
        role: 'user',
        content: 'Hello, can you help me study for my exam?',
        metadata: { capability: 'chat' }
      }
    });
    console.log('✅ Created test chat message:', chatMessage.id);

    // Create a test quiz
    const quiz = await prisma.quiz.create({
      data: {
        userId: user.id,
        topic: 'Mathematics',
        difficulty: 'medium',
        questions: {
          questions: [
            {
              question: 'What is 2 + 2?',
              options: ['3', '4', '5', '6'],
              correct: 1
            }
          ]
        }
      }
    });
    console.log('✅ Created test quiz:', quiz.id);

    // Create a test calendar event
    const event = await prisma.calendarEvent.create({
      data: {
        userId: user.id,
        title: 'Math Exam',
        description: 'Calculus final exam',
        date: new Date('2025-11-15'),
        time: '14:00',
        eventType: 'exam'
      }
    });
    console.log('✅ Created test calendar event:', event.id);

    // Create test analytics data
    const analytics = await prisma.analyticsData.create({
      data: {
        userId: user.id,
        metricType: 'study_hours',
        value: 2.5,
        date: new Date(),
        metadata: { subject: 'Mathematics' }
      }
    });
    console.log('✅ Created test analytics data:', analytics.id);

    // Query data to verify relationships
    const userWithData = await prisma.user.findUnique({
      where: { id: user.id },
      include: {
        chatMessages: true,
        quizzes: true,
        events: true,
        analytics: true
      }
    });
    
    console.log('\n📊 Database Statistics:');
    console.log(`- Chat Messages: ${userWithData.chatMessages.length}`);
    console.log(`- Quizzes: ${userWithData.quizzes.length}`);
    console.log(`- Calendar Events: ${userWithData.events.length}`);
    console.log(`- Analytics Records: ${userWithData.analytics.length}`);

    // Clean up test data
    console.log('\n🧹 Cleaning up test data...');
    await prisma.user.delete({
      where: { id: user.id }
    });
    console.log('✅ Test data cleaned up successfully');

    console.log('\n🎉 All database tests passed successfully!');
    console.log('📝 Your Supabase database is fully configured and ready to use.');

  } catch (error) {
    console.error('❌ Database test failed:', error);
    process.exit(1);
  } finally {
    await prisma.$disconnect();
  }
}

testDatabase();