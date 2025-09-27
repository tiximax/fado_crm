# Set backend URL to target custom port
$env:BACKEND_URL = 'http://127.0.0.1:8000'

# Run only VNPay-related tests with list reporter
npm run test -- --reporter=list --grep 'VNPay'
