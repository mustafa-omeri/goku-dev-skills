# Walkthrough — Java/Spring Boot Kullanılmayan Kod & `@Autowired` Kapı Düzeltmesi ve `ocai` Temizliği

## Özet & Kök Neden
- **Neden kalıntılar kalıyordu?** `ocai/.agent/skills/musgoku/scripts/check-unused.ps1` yapıştırılan 5 ECJ bulgusunu zaten yakalıyordu; ancak:
  1. `run_all_gates.py` Java kapılarını (`check-unused.ps1` ve `mvn clean test-compile`) hiç çağırmıyordu.
  2. `no-unused-code.md`, `development-workflow.md` ve `commitx/SKILL.md` `mvn clean compile -DskipTests` diyerek `src/test/java` kapsamını atlıyordu.
  3. `check-unused.ps1` tek constructor/parametre gereksiz `@Autowired` eklerini, package-private test `@Autowired` alanlarını, `@Slf4j` unused `log` bildirimlerini ve referanssız ölü sınıfları taramıyordu.

## Yapılan Değişiklikler
### `skillSetWorks`
- `.agent/skills/musgoku/scripts/run_all_gates.py`: `pom.xml` bulunduğunda `check-unused.ps1` kapısını varsayılan akışta, `mvn clean test-compile` kapısını `--include-slow` altında çalıştırır.
- `.agent/skills/musgoku/scripts/check-unused.ps1`: ECJ (`unusedImport,unusedLocal,unusedPrivate,warningToken,unchecked`) yanında `-StaticOnly`, `-ProjectRoot`, gereksiz parametre/tek-constructor `@Autowired`, package-private test `@Autowired`, `@Slf4j` unused `log` ve Spring stereotype muafiyetli ölü sınıf tespiti eklendi.
- `.agent/rules/no-unused-code.md`, `.agent/rules/development-workflow.md`, `.agent/AGENTS.md`, `.agent/skills/commitx/SKILL.md`, `.agent/skills/verify-last/SKILL.md`: `mvn clean test-compile` ve `check-unused.ps1` zorunluluğu hizalandı.
- `tests/test_java_unused_gates.py` & `tests/run_all.py`: 5 TDD regresyon testi eklendi.

### `ocai` (`C:\devtools\vscodeWS\peopleside-culture\ocai`)
- `delivery.py --only ocai` ile güncellenmiş `.agent/` paketi (`1249/1249` dosya byte-byte eşit) dağıtıldı.
- **5 ECJ test bulgusu temizlendi:** `TenantRlsIsolationIT.java` & `ComplementarySuppressionAndReportIT.java` (`JsonNode` import), `OcaiScoreParityGoldenMasterIT.java` (`jdbcTemplate` + import), `UnifiedAttemptAndKvkkIT.java` (`attemptEngineService`, `complianceService` + importlar).
- **Gereksiz `@Autowired` temizlendi:** `WebSocketConfig.java:39-40` (`JwtTokenProvider`, `UserDetailsService`).
- **`12` kullanılmayan `@Slf4j` temizlendi:** `OcaiApplication`, `JwtAuthenticationFilter`, `CategoryController`, `RetentionPurgeJob`, `AdminDashboardController`, `CompanyDashboardController`, `DashboardRouterController`, `EmployeeDashboardController`, `NotificationController`, `CompanyReportPermissionController`, `OrgProfileSnapshotJob`, `AdminDemoPermissionController`.
- **`14` ölü (referanssız) sınıf silindi:** `CoreGlobalExceptionHandler`, `CategoryWebSocketEventDTO`, `CompanyWebSocketEventDTO`, `PendingReminderProjection`, `MailWebSocketEventDTO`, `ActivationVerifyRequest`, `AssignDepartmentSectionRequest`, `AssignDepartmentSectionV2Request`, `BulkUpdateUserStatusRequest`, `BulkUpdateUserStatusResponse`, `UpdateUserStatusRequest`, `UserCategoryStatsDTO`, `UserWebSocketEventDTO`, `PasswordGenerator`. (`PasswordResetUtil`, `EmbeddingModelRegistry`, `AssessmentPlanRepository` Spring bileşeni olarak korundu.)
- `ocai/knowledge-base.md` ve `ocai/HANDOFF.md` (`OCAI-CLEAN-001`) kalıcı olarak güncellendi.

## Doğrulama Sonuçları
- `ocai`: `.\mvnw.cmd -B clean test-compile` (`552` main + `51` test -> `BUILD SUCCESS`) ve `pwsh -NoProfile -File .agent/skills/musgoku/scripts/check-unused.ps1` (`603` dosya -> `[OK]`).
- `skillSetWorks`: `tests/run_all.py`, `rules_gates.py --strict`, `run_all_gates.py` final doğrulaması ile teyit edildi.
