<#
.SYNOPSIS
  Kullanilmayan import ve local degisken denetimi (Eclipse JDT / ecj ile).

.DESCRIPTION
  javac (mvn compile) su uyarilari URETMEZ:
    - "The import X is never used"                       (unusedImport)
    - "The value of the local variable X is not used"    (unusedLocal)
    - "Unnecessary @SuppressWarnings("X")"               (warningToken)
  Bu mesajlar VS Code Java (Eclipse JDT) derleyicisine aittir. Bu script ayni
  derleyiciyi (ecj) Lombok javaagent ile calistirir.

  IKI AYRI CIKTI - karistirma:
    * BULGU  (exit 1) : unusedImport, unusedLocal, gereksiz @SuppressWarnings.
                         Bunlar duzeltilmesi gereken gercek kod durumudur.
    * UYARI  (exit 0'da bile yazilir, kapiyi KIRMAZ):
                         unchecked / raw type. Bunlar derleyici/IDE uyarisidir
                         ve su an calisan kodu bozmadan temizlenemez; bkz.
                         rules/no-unused-code.md #4.2 "Calisan kodu bozma".

  Sahte gecis (vacuous pass) korumasi: once bilerek 3 bulgu + 1 uyari iceren
  bir CANARY dosyasi denetlenir. Canary'de 3 bulgu ve en az 1 uyari yakalanmazsa
  script FAIL verir (ecj hic calismadi / arguman hatali demektir) ve proje
  sonucuna guvenilmez.

  Exit: 0 = OK · 1 = bulgu var · 2 = ecj derleme hatasi · 3 = canary/arac hatasi

.EXAMPLE
  pwsh -NoProfile -File .agent/skills/musgoku/scripts/check-unused.ps1
  pwsh -NoProfile -File .agent/skills/musgoku/scripts/check-unused.ps1 -MainOnly
#>
param(
    [switch]$MainOnly,
    [string]$EcjVersion = "3.38.0"
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path "$PSScriptRoot\..\..\..\..").Path
Set-Location $root

# `java` PATH'te eski bir JDK olabilir (bu makinede Java 8). ecj 21 bytecode
# istedigi icin UnsupportedClassVersionError -> canary 0 bulgu -> yalan FAIL.
# JAVA_HOME verilmisse onu kullan.
$javaExe = "java"
if ($env:JAVA_HOME) {
    $candidate = Join-Path $env:JAVA_HOME "bin\java.exe"
    if (Test-Path $candidate) { $javaExe = $candidate }
}

$m2 = (mvn -B -q help:evaluate "-Dexpression=settings.localRepository" -DforceStdout | Out-String).Trim()
if (-not $m2 -or -not (Test-Path $m2)) { $m2 = Join-Path $env:USERPROFILE ".m2\repository" }
$ecjJar = Join-Path $m2 "org\eclipse\jdt\ecj\$EcjVersion\ecj-$EcjVersion.jar"
if (-not (Test-Path $ecjJar)) {
    Write-Host "ecj $EcjVersion indiriliyor..."
    mvn -B -q dependency:get "-Dartifact=org.eclipse.jdt:ecj:$EcjVersion" | Out-Null
    if (-not (Test-Path $ecjJar)) { throw "ecj indirilemedi: $ecjJar" }
}

# Lombok surumunu pom.xml'deki annotationProcessorPaths'ten oku
$lombokVersion = ([xml](Get-Content pom.xml -Raw)).project.build.plugins.plugin |
    ForEach-Object { $_.configuration.annotationProcessorPaths.path } |
    Where-Object { $_.artifactId -eq "lombok" } | Select-Object -First 1 -ExpandProperty version
$lombokJar = Join-Path $m2 "org\projectlombok\lombok\$lombokVersion\lombok-$lombokVersion.jar"
if (-not (Test-Path $lombokJar)) { throw "Lombok jar bulunamadi: $lombokJar" }

# Test scope classpath (main + test bagimliliklari)
$cpFile = Join-Path $env:TEMP "musgoku-unused-cp.txt"
mvn -B -q dependency:build-classpath "-Dmdep.includeScope=test" "-Dmdep.outputFile=$cpFile" | Out-Null
if (-not (Test-Path $cpFile)) { throw "Classpath uretilemedi (mvn dependency:build-classpath)" }
$cp = (Get-Content $cpFile -Raw).Trim()

# ⛔ Maven, ARTIK BULUNAMAYAN bir artifact icin classpath'e `.pom` yolunu
#    yazar. ECJ bu yolu jar sanip acmaya calisir ve TUM classpath'i dusurur:
#    "Failed to init Classpath for jar file ... .pom / zip END header not found"
#    -> sonuc "cannot be resolved to a type" sahte hatalari + guvenilmez bulgu.
#    Gozlenen: ticari lisansli veya ayri depoda duran bazi artifact'lar Maven
#    Central'da YOK; Maven yalnizca `.pom` yolunu cozuyor. Ayni durum, repo
#    eklenmesi unutulmus bir bagimlilik icin de gorulur.
# Cozum: classpath'ten `.jar` ile bitmeyen girdileri ayikla VE raporla.
$cpEntries = @($cp -split ';' | Where-Object { $_ -and (Test-Path $_) })
$cpJars = @($cpEntries | Where-Object { $_ -like '*.jar' })
$cpSkipped = @($cpEntries | Where-Object { $_ -notlike '*.jar' })
if ($cpSkipped.Count -gt 0) {
    Write-Host ("[WARN] {0} classpath girdisi .jar degil, ECJ'den cikarildi (bozuk/eksik artifact):" -f $cpSkipped.Count) -ForegroundColor Yellow
    $cpSkipped | ForEach-Object { Write-Host "       $_" -ForegroundColor DarkYellow }
    Write-Host "       Bu bir DENETIM ARACI sorunudur, kod hatası değil. Düzeltme: bagimlilik Kaldirilmalı ya da dogru repo/surum eklenmeli." -ForegroundColor DarkYellow
}
if ($cpJars.Count -eq 0) { throw "Classpath'te hic jar yok — denetim calistirilamaz" }
$cp = ($cpJars -join ';')

# ecj'yi calistirir; bulgulari, uyarilari, hata sayisini ve log yolunu dondurur.
# Onemli: once BULGU deseni denenir, tutmazsa UYARI deseni. Boylece
# "Unnecessary @SuppressWarnings("unchecked")" mesaji (icinde "unchecked" gecer)
# yanlislikla hem bulgu hem uyari olarak iki kez sayilmaz.
$FindingPattern = 'is never used|is not used|Unnecessary @SuppressWarnings'
$NoticePattern  = 'unchecked|raw type'

function Invoke-Ecj([string[]]$Sources, [string]$LogFile) {
    & $javaExe "-javaagent:$lombokJar=ECJ" -jar $ecjJar `
        -21 -encoding UTF-8 -proceedOnError -d none `
        -warn:unusedImport,unusedLocal,warningToken,unchecked `
        -cp "$lombokJar;$cp" @Sources 2>&1 | Out-File $LogFile -Encoding utf8
    $log = @(Get-Content $LogFile)
    $findings = @()
    $notices = @()
    for ($i = 0; $i -lt $log.Count; $i++) {
        if ($log[$i] -match '^\d+\. WARNING in (.+) \(at line (\d+)\)') {
            $file = $Matches[1].Replace("$root\", ""); $line = $Matches[2]
            $window = $log[($i + 1)..([Math]::Min($i + 4, $log.Count - 1))]
            $msg = ($window | Where-Object { $_ -match $FindingPattern } | Select-Object -First 1)
            if ($msg) { $findings += "${file}:${line}  $($msg.Trim())"; continue }
            $note = ($window | Where-Object { $_ -match $NoticePattern } | Select-Object -First 1)
            if ($note) { $notices += "${file}:${line}  $($note.Trim())" }
        }
    }
    $errors = @($log | Select-String -SimpleMatch "ERROR in").Count
    $toolError = ($log | Select-String -Pattern 'invalid|Usage:|unrecognized' | Select-Object -First 1)
    return @{ Findings = $findings; Notices = $notices; Errors = $errors; ToolError = $toolError; Log = $LogFile }
}

function Write-Notices([hashtable]$Result, [string]$Scope) {
    if ($Result.Notices.Count -eq 0) { return }
    Write-Host "`n[uyarı] $($Result.Notices.Count) unchecked / raw type uyarısı ($Scope) — BULGU DEĞİL, kapıyı kırmaz:" -ForegroundColor Yellow
    $Result.Notices | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
    Write-Host "       Çalışan kodu bozmadan temizlenemez; rules/no-unused-code.md §4.2'ye bak." -ForegroundColor DarkYellow
    Write-Host "       Dokunmadığın dosyalardakileri olduğu gibi bırak, dokunduğun dosyada değerlendir." -ForegroundColor DarkYellow
}

# 1) CANARY — denetleyicinin gercekten calistigini kanitla
$canaryDir = Join-Path $env:TEMP "musgoku-unused-canary"
New-Item -ItemType Directory -Force -Path $canaryDir | Out-Null
$canaryFile = Join-Path $canaryDir "UnusedCanary.java"
[IO.File]::WriteAllLines($canaryFile, @(
    'import java.util.Arrays;',
    'public class UnusedCanary {',
    '    void run() {',
    '        int unusedLocal = 42;',
    '    }',
    '    @SuppressWarnings("unchecked")',
    '    void noCast() { }',
    '    void rawList() {',
    '        java.util.List<String> l = new java.util.ArrayList();',
    '        l.add("x");',
    '        System.out.println(l);',
    '    }',
    '}'
))
$canary = Invoke-Ecj @($canaryFile) (Join-Path $env:TEMP "musgoku-unused-canary.log")
if ($canary.ToolError -or $canary.Findings.Count -ne 3 -or $canary.Notices.Count -lt 1) {
    Write-Host "[FAIL] Canary: 3 bulgu + en az 1 uyari beklendi; $($canary.Findings.Count) bulgu / $($canary.Notices.Count) uyari bulundu. Denetleyici CALISMIYOR; sonuca guvenme." -ForegroundColor Red
    if ($canary.ToolError) { Write-Host "  ecj: $($canary.ToolError)" }
    Write-Host "  Log: $($canary.Log)"
    exit 3
}
Write-Host "[canary] 3/3 bulgu + $($canary.Notices.Count) uyari yakalandi (import + local degisken + gereksiz SuppressWarnings + unchecked) -> denetleyici calisiyor."

# 2) PROJE denetimi
$sources = @("src\main\java")
if (-not $MainOnly -and (Test-Path "src\test\java")) { $sources += "src\test\java" }
$fileCount = @(Get-ChildItem -Path $sources -Recurse -Filter *.java -File).Count
$result = Invoke-Ecj $sources (Join-Path $env:TEMP "musgoku-unused-ecj.log")

if ($result.ToolError) {
    Write-Host "[FAIL] ecj arac hatasi: $($result.ToolError) (log: $($result.Log))" -ForegroundColor Red
    exit 3
}
if ($result.Findings.Count -gt 0) {
    Write-Host "`n[FAIL] $($result.Findings.Count) kullanilmayan kod / gereksiz susturma ($fileCount dosya tarandi):" -ForegroundColor Red
    $result.Findings | ForEach-Object { Write-Host "  $_" }
    if ($result.Errors -gt 0) { Write-Host "(ecj $($result.Errors) derleme hatasi da raporladi - log: $($result.Log))" -ForegroundColor Yellow }
    Write-Notices $result "proje"
    exit 1
}
if ($result.Errors -gt 0) {
    Write-Host "[WARN] Bulgu yok ama ecj $($result.Errors) derleme hatasi raporladi; sonuc guvenilir olmayabilir. Log: $($result.Log)" -ForegroundColor Yellow
    Write-Notices $result "proje"
    exit 2
}
Write-Host "[OK] Kullanilmayan import/local degisken ve gereksiz @SuppressWarnings yok. ($fileCount dosya: $($sources -join ', '))" -ForegroundColor Green
Write-Notices $result "proje"
exit 0
