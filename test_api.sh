echo "=== Testing Medical Appointment Scheduling Agent API ==="
echo ""

echo "1. Health Check:"
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""
echo ""

echo "2. Root Endpoint:"
curl -s http://localhost:8000/ | python3 -m json.tool
echo ""
echo ""

echo "3. Check Availability:"
tomorrow=$(date -d "tomorrow" +%Y-%m-%d)
curl -s "http://localhost:8000/api/calendly/availability?date=$tomorrow&appointment_type=consultation" | python3 -m json.tool
echo ""
echo ""

echo "4. Chat Endpoint (Test):"
curl -s -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}' | python3 -m json.tool
echo ""

echo "=== Tests Complete ==="

