# PowerShell 脚本测试配置文件编码

# 测试不同编码方式读取文件

$file_path = "settings.txt"

Write-Host "测试1: 使用 Get-Content (默认编码)"
Write-Host "================================="
Get-Content $file_path
Write-Host ""

Write-Host "测试2: 使用 UTF-8 编码"
Write-Host "================================="
Get-Content -Path $file_path -Encoding UTF8
Write-Host ""

Write-Host "测试3: 使用 Unicode 编码"
Write-Host "================================="
Get-Content -Path $file_path -Encoding Unicode
Write-Host ""

Write-Host "测试4: 使用 OEM 编码"
Write-Host "================================="
Get-Content -Path $file_path -Encoding OEM
Write-Host ""

Write-Host "测试5: 使用默认编码并设置输出编码"
Write-Host "================================="
[console]::OutputEncoding = [System.Text.Encoding]::UTF8
Get-Content $file_path
Write-Host ""

Write-Host "文件编码信息:"
Write-Host "================================="
$bytes = [System.IO.File]::ReadAllBytes($file_path)
$utf8 = [System.Text.Encoding]::UTF8
$unicode = [System.Text.Encoding]::Unicode

Write-Host "文件大小: $($bytes.Length) 字节"
Write-Host "前20字节: $([System.BitConverter]::ToString($bytes[0..19]))"

# 检查BOM标记
if ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
    Write-Host "检测到 UTF-8 BOM 标记"
} elseif ($bytes[0] -eq 0xFF -and $bytes[1] -eq 0xFE) {
    Write-Host "检测到 Unicode BOM 标记"
} elseif ($bytes[0] -eq 0xFE -and $bytes[1] -eq 0xFF) {
    Write-Host "检测到 Big Endian Unicode BOM 标记"
} else {
    Write-Host "未检测到 BOM 标记"
}