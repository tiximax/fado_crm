param(
  [string]$BackendUrl = "http://localhost:8000",
  [string]$Secret = "secret"
)

function QuotePlus([string]$s) {
  $enc = [System.Net.WebUtility]::UrlEncode($s)
  return $enc -replace '%20','+'
}

$params = [ordered]@{
  vnp_Version      = '2.1.0'
  vnp_Command      = 'pay'
  vnp_TmnCode      = 'demo'
  vnp_Amount       = '10000'
  vnp_CurrCode     = 'VND'
  vnp_TxnRef       = 'TESTPS'
  vnp_OrderInfo    = 'FADO Test Return'
  vnp_ResponseCode = '00'
  vnp_CreateDate   = '20250101000000'
}

# Build data string with quote_plus encoding and sorted keys
$items = $params.GetEnumerator() | Sort-Object Key
$pairs = @()
foreach ($it in $items) {
  $pairs += ("{0}={1}" -f $it.Key, (QuotePlus ([string]$it.Value)))
}
$data = [string]::Join('&', $pairs)

# Compute HMAC SHA512 in hex lower
$hmac = [System.Security.Cryptography.HMACSHA512]::new([Text.Encoding]::UTF8.GetBytes($Secret))
$hashBytes = $hmac.ComputeHash([Text.Encoding]::UTF8.GetBytes($data))
$sig = ([System.BitConverter]::ToString($hashBytes)).Replace('-', '').ToLower()

# Add signature and build query string (standard percent-encoding)
# Clone params into a new ordered dict and add signature
$qs = New-Object System.Collections.Specialized.OrderedDictionary
foreach ($it in ($params.GetEnumerator() | Sort-Object Key)) {
  $qs.Add($it.Key, $it.Value)
}
$qs['vnp_SecureHash'] = $sig
$qsPairs = @()
foreach ($kv in $qs.GetEnumerator()) {
  $qsPairs += ("{0}={1}" -f [System.Uri]::EscapeDataString($kv.Key), [System.Uri]::EscapeDataString([string]$kv.Value))
}
$query = [string]::Join('&', $qsPairs)

$url = "$BackendUrl/payments/return?$query"
Write-Host "URL: $url"

try {
  $resp = Invoke-WebRequest -UseBasicParsing $url -TimeoutSec 20
  Write-Host "StatusCode:" $resp.StatusCode
  Write-Output $resp.Content
} catch {
  Write-Host "Request failed:" $_.Exception.Message
  if ($_.Exception.Response) {
    $stream = $_.Exception.Response.GetResponseStream()
    if ($stream) {
      $reader = New-Object System.IO.StreamReader($stream)
      $body = $reader.ReadToEnd()
      Write-Output $body
    }
  }
  exit 1
}
