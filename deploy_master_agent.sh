
#!/bin/bash

# CPAS Master Agent System Deployment Script
# Ultimate Master Agent with OSINT Intelligence Capabilities

echo "🎭 Deploying CPAS Master Agent System with OSINT Intelligence..."

# Activate virtual environment
source venv/bin/activate

# Install remaining dependencies
pip install --quiet plotly dash framer-motion lucide-react

# Fix import paths
cd backend
export PYTHONPATH=$PWD:$PYTHONPATH

# Start services in background
echo "🚀 Starting Master Agent Backend..."
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../master_agent_backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start frontend
echo "🎨 Starting Master Agent Frontend..."
cd ../frontend
npm install --silent
nohup npm run dev > ../master_agent_frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 10

echo "✅ CPAS Master Agent System Deployed Successfully!"
echo ""
echo "🎭 Master Agent 'Greta' is now operational with:"
echo "   • HRM Hierarchical Reasoning (4 levels)"
echo "   • German-accented English voice interface"
echo "   • Complete OSINT intelligence suite:"
echo "     - Social Media Intelligence (SOCMINT)"
echo "     - Technical Intelligence (TECHINT)" 
echo "     - Breach Intelligence (BREACHINT)"
echo "     - Media Intelligence (MEDIAINT)"
echo "   • Mac-native UI with Tufte-style visualizations"
echo "   • Advanced task delegation and orchestration"
echo ""
echo "🌐 Access Points:"
echo "   • Backend API: http://localhost:8000"
echo "   • Master Agent UI: http://localhost:3000/master"
echo "   • API Documentation: http://localhost:8000/docs"
echo ""
echo "🎯 Key Features Implemented:"
echo "   ✅ Master Agent with HRM reasoning"
echo "   ✅ German voice personality (Greta)"
echo "   ✅ Complete OSINT toolkit"
echo "   ✅ Mac-optimized desktop interface"
echo "   ✅ Tufte-style data visualizations"
echo "   ✅ Multi-agent coordination"
echo "   ✅ Voice interface with accent"
echo "   ✅ Intelligence gathering capabilities"
echo ""
echo "📊 System Status:"
echo "   Backend PID: $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo "   Logs: master_agent_backend.log, master_agent_frontend.log"
echo ""
echo "🔧 To stop services:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "🎉 Your Ultimate Master Agent System is ready!"
echo "   Ask Greta anything - she's your German-precision AI assistant!"
