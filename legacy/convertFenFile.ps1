param(
    [string]$InputFile = ".\startingPositions.txt",
    [string]$OutputFile = ".\startingPositions.xml"
)

# Create a new XML document and the root element.
[xml]$xmlDoc = New-Object System.Xml.XmlDocument
$root = $xmlDoc.CreateElement("positions")
$xmlDoc.AppendChild($root) | Out-Null

# Read all non-empty lines from the input text file.
$lines = Get-Content -Path $InputFile | Where-Object { $_ -ne "" }

$lineNumber = 1
foreach ($line in $lines) {
    # Create a <startingPosition> element.
    $startingPosition = $xmlDoc.CreateElement("startingPosition")
    
    # Create and append the <positionNumber> element.
    $positionNumber = $xmlDoc.CreateElement("positionNumber")
    $positionNumber.InnerText = $lineNumber
    $startingPosition.AppendChild($positionNumber) | Out-Null
    
    # Create and append the <fen> element.
    $fenElem = $xmlDoc.CreateElement("fen")
    $fenElem.InnerText = $line
    $startingPosition.AppendChild($fenElem) | Out-Null
    
    # Append the startingPosition element to the root.
    $root.AppendChild($startingPosition) | Out-Null
    $lineNumber++
}

# Save the XML document.
$xmlDoc.Save($OutputFile)
Write-Host "Converted $InputFile to $OutputFile"
