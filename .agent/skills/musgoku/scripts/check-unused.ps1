<#
.SYNOPSIS
  Java / Spring Boot kullanilmayan kod, gereksiz @Autowired ve olu sinif denetimi.

.DESCRIPTION
  javac (mvn compile / test-compile) su bulgulari URETMEZ:
    - "The import X is never used"                       (unusedImport)
    - "The value of the local variable X is not used"    (unusedLocal)
    - "The value of the field X is not used"             (unusedPrivate / @Slf4j)
    - "Unnecessary @SuppressWarnings("X")"               (warningToken)
    - Tek constructor / parametre uzerinde gereksiz @Autowired
    - Test siniflarinda kullanilmayan package-private @Autowired alanlar
    - Referanssiz olu (dead) DTO / yardimci siniflar
  Bu script Eclipse JDT (ecj) + Lombok javaagent ile statik Spring/Java taramasini
  birlikte calistirir.

  IKI AYRI CIKTI - karistirma:
    * BULGU  (exit 1) : unusedImport, unusedLocal, unusedPrivate, @Slf4j unused log,
                         gereksiz @SuppressWarnings, gereksiz @Autowired, olu siniflar.
    * UYARI  (exit 0'da bile yazilir, kapiyi KIRMAZ):
                         unchecked / raw type. Bkz. rules/no-unused-code.md #4.2.

  Exit: 0 = OK · 1 = bulgu var · 2 = ecj derleme hatasi · 3 = canary/arac hatasi

.EXAMPLE
  pwsh -NoProfile -File .agent/skills/musgoku/scripts/check-unused.ps1
  pwsh -NoProfile -File .agent/skills/musgoku/scripts/check-unused.ps1 -MainOnly
  pwsh -NoProfile -File .agent/skills/musgoku/scripts/check-unused.ps1 -StaticOnly
#>
param(
    [switch]$MainOnly,
    [switch]$StaticOnly,
    [string]$ProjectRoot = "",
    [string]$EcjVersion = "3.38.0"
)

$ErrorActionPreference = "Stop"
if ($ProjectRoot) {
    $root = (Resolve-Path $ProjectRoot).Path
} else {
    $root = (Resolve-Path "$PSScriptRoot\..\..\..\..").Path
}
Set-Location $root

function Strip-JavaComments([string]$Text) {
    return [regex]::Replace($Text, '/\*[\s\S]*?\*/|//[^\r\n]*', {
        param($m)
        return ($m.Value -replace '[^\r\n]', ' ')
    })
}

function Get-LineNumber([string]$Text, [int]$Index) {
    if ($Index -le 0) { return 1 }
    return ([regex]::Matches($Text.Substring(0, $Index), "`n")).Count + 1
}

function Invoke-SpringStaticChecks([string]$RootDir, [bool]$IncludeTests, [bool]$CheckSlf4j) {
    $findings = New-Object System.Collections.Generic.List[string]
    $mainDir = Join-Path $RootDir "src\main\java"
    $testDir = Join-Path $RootDir "src\test\java"
    $resDir  = Join-Path $RootDir "src\main\resources"

    $mainFiles = if (Test-Path $mainDir) { @(Get-ChildItem -Path $mainDir -Recurse -Filter "*.java" -File) } else { @() }
    $testFiles = if ($IncludeTests -and (Test-Path $testDir)) { @(Get-ChildItem -Path $testDir -Recurse -Filter "*.java" -File) } else { @() }
    $allJavaFiles = @($mainFiles + $testFiles)

    # Tum dosya iceriklerini (yorumsuz) ve kaynak dosya metinlerini tek geciste hazirla
    $fileContents = @{}
    foreach ($f in $allJavaFiles) {
        $raw = Get-Content $f.FullName -Raw -Encoding UTF8
        $fileContents[$f.FullName] = Strip-JavaComments $raw
    }

    $resContents = @{}
    if (Test-Path $resDir) {
        foreach ($rf in @(Get-ChildItem -Path $resDir -Recurse -File)) {
            try {
                $resContents[$rf.FullName] = Get-Content $rf.FullName -Raw -Encoding UTF8
            } catch {
                # binary resource atlanir
            }
        }
    }

    $springStereotypeRe = '@(SpringBootApplication|Configuration|RestController|Controller|ControllerAdvice|RestControllerAdvice|Service|Component|Repository|Entity|Table|MappedSuperclass|Embeddable|Aspect|WebFilter|ServletComponentScan|Converter|Mapper)\b'
    $frameworkExtendRe  = 'extends\s+\w*(Repository|Filter|Exception|RuntimeException|OncePerRequestFilter|WebMvcConfigurer|HandlerInterceptor)\b'
    $frameworkImplRe    = 'implements\s+[^{]*\b(CommandLineRunner|ApplicationRunner|Filter|Converter|Serializer|Deserializer|Formatter|WebSocketConfigurer|WebSocketMessageBrokerConfigurer)\b'

    # 1) src/main/java: Gereksiz @Autowired, @Slf4j unused log ve referanssiz olu siniflar
    foreach ($f in $mainFiles) {
        $rel = $f.FullName.Replace("$RootDir\", "")
        $clean = $fileContents[$f.FullName]
        $clsName = [System.IO.Path]::GetFileNameWithoutExtension($f.Name)

        # 1a) Constructor/metot parametresinde gereksiz @Autowired (@Autowired(required = false) haric)
        foreach ($m in [regex]::Matches($clean, '(?<=[(,]\s*)@Autowired(?!\s*\([^)]*required\s*=\s*false\b)\b')) {
            $ln = Get-LineNumber $clean $m.Index
            $findings.Add("${rel}:${ln}  Redundant @Autowired on parameter (Spring 4.3+ injects automatically)")
        }

        # 1b) Tek constructor uzerinde gereksiz @Autowired (@Autowired(required = false) haric)
        $ctorMatches = [regex]::Matches($clean, "(?m)^[ \t]*(?:(?:public|protected|private)\s+)?$([regex]::Escape($clsName))\s*\(")
        if ($ctorMatches.Count -eq 1) {
            foreach ($m in [regex]::Matches($clean, "@Autowired(?!\s*\([^)]*required\s*=\s*false\b)\s*(?:(?:public|protected|private)\s+)?$([regex]::Escape($clsName))\s*\(")) {
                $ln = Get-LineNumber $clean $m.Index
                $findings.Add("${rel}:${ln}  Redundant @Autowired on single constructor")
            }
        }

        # 1c) @Slf4j var ama 'log.' hic cagrilmamis (StaticOnly modunda)
        if ($CheckSlf4j) {
            $slfMatch = [regex]::Match($clean, '@(Slf4j|Log4j2)\b')
            if ($slfMatch.Success -and ($clean -notmatch '\blog\.')) {
                $ln = Get-LineNumber $clean $slfMatch.Index
                $findings.Add("${rel}:${ln}  @Slf4j tanimli ama 'log' alani hic kullanilmiyor")
            }
        }

        # 1d) Referanssiz olu sinif taramasi (Spring bean/entity/exception/config haric)
        if ($f.Name -in @("package-info.java", "module-info.java")) { continue }
        if ($f.Name -match '(Test|Tests|IT|Application|Config|Properties|Exception)\.java$') { continue }
        if ($clean -match $springStereotypeRe -or $clean -match $frameworkExtendRe -or $clean -match $frameworkImplRe) { continue }
        if ($clean -match '\bpublic\s+static\s+void\s+main\s*\(') { continue }

        $declMatch = [regex]::Match($clean, "(?:public\s+)?(?:final\s+|abstract\s+|sealed\s+)?(?:class|interface|enum|record)\s+$([regex]::Escape($clsName))\b")
        if ($declMatch.Success) {
            $wordRe = "\b$([regex]::Escape($clsName))\b"
            $externalRef = $false
            foreach ($entry in $fileContents.GetEnumerator()) {
                if ($entry.Key -eq $f.FullName) { continue }
                if ($entry.Value -match $wordRe) { $externalRef = $true; break }
            }
            if (-not $externalRef) {
                foreach ($resVal in $resContents.Values) {
                    if ($resVal -match $wordRe) { $externalRef = $true; break }
                }
            }
            if (-not $externalRef) {
                $ln = Get-LineNumber $clean $declMatch.Index
                $findings.Add("${rel}:${ln}  The class ${clsName} appears unused (0 external references)")
            }
        }
    }

    # 2) src/main/java + src/test/java: private olmayan (@Autowired package-private/protected) kullanilmayan alanlar
    foreach ($f in $allJavaFiles) {
        $rel = $f.FullName.Replace("$RootDir\", "")
        $clean = $fileContents[$f.FullName]
        $fieldPattern = '@Autowired(?:\s*\([^)]*\))?\s+(?:protected\s+)?(?!(?:private|public|static)\b)[A-Za-z_][\w<>\[\],.? \t]*?\s+([a-zA-Z_]\w*)\s*;'
        foreach ($m in [regex]::Matches($clean, $fieldPattern)) {
            $fieldName = $m.Groups[1].Value
            $occ = ([regex]::Matches($clean, "\b$([regex]::Escape($fieldName))\b")).Count
            if ($occ -le 1) {
                $ln = Get-LineNumber $clean $m.Index
                $findings.Add("${rel}:${ln}  The value of the @Autowired field ${fieldName} is not used")
            }
        }
        if ($CheckSlf4j -and ($testFiles -contains $f)) {
            $slfMatch = [regex]::Match($clean, '@(Slf4j|Log4j2)\b')
            if ($slfMatch.Success -and ($clean -notmatch '\blog\.')) {
                $ln = Get-LineNumber $clean $slfMatch.Index
                $findings.Add("${rel}:${ln}  @Slf4j tanimli ama 'log' alani hic kullanilmiyor")
            }
        }
    }

    return @($findings)
}

if ($StaticOnly) {
    $staticFindings = Invoke-SpringStaticChecks -RootDir $root -IncludeTests (-not $MainOnly) -CheckSlf4j $true
    if ($staticFindings.Count -gt 0) {
        Write-Host "`n[FAIL] $($staticFindings.Count) kullanilmayan kod / gereksiz @Autowired bulgusu (-StaticOnly):" -ForegroundColor Red
        $staticFindings | ForEach-Object { Write-Host "  $_" }
        exit 1
    }
    Write-Host "[OK] Statik Spring/Java denetimi temiz (-StaticOnly)." -ForegroundColor Green
    exit 0
}

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

$cpEntries = @($cp -split ';' | Where-Object { $_ -and (Test-Path $_) })
$cpJars = @($cpEntries | Where-Object { $_ -like '*.jar' })
$cpSkipped = @($cpEntries | Where-Object { $_ -notlike '*.jar' })
if ($cpSkipped.Count -gt 0) {
    Write-Host ("[WARN] {0} classpath girdisi .jar degil, ECJ'den cikarildi (bozuk/eksik artifact):" -f $cpSkipped.Count) -ForegroundColor Yellow
    $cpSkipped | ForEach-Object { Write-Host "       $_" -ForegroundColor DarkYellow }
    Write-Host "       Bu bir DENETIM ARACI sorunudur, kod hatasi değil. Düzeltme: bagimlilik kaldirilmali ya da dogru repo/surum eklenmeli." -ForegroundColor DarkYellow
}
if ($cpJars.Count -eq 0) { throw "Classpath'te hic jar yok — denetim calistirilamaz" }
$cp = ($cpJars -join ';')

$FindingPattern = 'is never used|is not used|Unnecessary @SuppressWarnings'
$NoticePattern  = 'unchecked|raw type'

function Invoke-Ecj([string[]]$Sources, [string]$LogFile) {
    & $javaExe "-javaagent:$lombokJar=ECJ" -jar $ecjJar `
        -21 -encoding UTF-8 -proceedOnError -d none `
        -warn:unusedImport,unusedLocal,unusedPrivate,warningToken,unchecked `
        -cp "$lombokJar;$cp" @Sources 2>&1 | Out-File $LogFile -Encoding utf8
    $log = @(Get-Content $LogFile)
    $findings = @()
    $notices = @()
    for ($i = 0; $i -lt $log.Count; $i++) {
        if ($log[$i] -match '^\d+\. WARNING in (.+) \(at line (\d+)\)') {
            $file = $Matches[1].Replace("$root\", ""); $line = $Matches[2]
            $window = $log[($i + 1)..([Math]::Min($i + 4, $log.Count - 1))]
            $msg = ($window | Where-Object { $_ -match $FindingPattern } | Select-Object -First 1)
            if ($msg) {
                $findings += "${file}:${line}  $($msg.Trim())"; continue
            }
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

# 2) PROJE denetimi (ECJ + Spring statik tarama)
$sources = @("src\main\java")
if (-not $MainOnly -and (Test-Path "src\test\java")) { $sources += "src\test\java" }
$fileCount = @(Get-ChildItem -Path $sources -Recurse -Filter *.java -File).Count
$result = Invoke-Ecj $sources (Join-Path $env:TEMP "musgoku-unused-ecj.log")

if ($result.ToolError) {
    Write-Host "[FAIL] ecj arac hatasi: $($result.ToolError) (log: $($result.Log))" -ForegroundColor Red
    exit 3
}

$staticFindings = Invoke-SpringStaticChecks -RootDir $root -IncludeTests (-not $MainOnly) -CheckSlf4j $false
$allFindings = @($result.Findings) + @($staticFindings)

if ($allFindings.Count -gt 0) {
    Write-Host "`n[FAIL] $($allFindings.Count) kullanilmayan kod / gereksiz @Autowired / susturma ($fileCount dosya tarandi):" -ForegroundColor Red
    $allFindings | ForEach-Object { Write-Host "  $_" }
    if ($result.Errors -gt 0) { Write-Host "(ecj $($result.Errors) derleme hatasi da raporladi - log: $($result.Log))" -ForegroundColor Yellow }
    Write-Notices $result "proje"
    exit 1
}
if ($result.Errors -gt 0) {
    Write-Host "[WARN] Bulgu yok ama ecj $($result.Errors) derleme hatasi raporladi; sonuc guvenilir olmayabilir. Log: $($result.Log)" -ForegroundColor Yellow
    Write-Notices $result "proje"
    exit 2
}
Write-Host "[OK] Kullanilmayan import/degisken, gereksiz @Autowired, olu sinif ve gereksiz @SuppressWarnings yok. ($fileCount dosya: $($sources -join ', '))" -ForegroundColor Green
Write-Notices $result "proje"
exit 0
