---
description: This instruction file provides guidelines for documenting and managing bug fixing history.
---

<critical>Note: This is a living document and will be updated as we refine our processes. Always refer back to this for the latest guidelines. Update whenever necessary. Anytime you discover a new bug or issue, document it here to maintain a comprehensive history.</critical>

# Bug History — H³ Project

Document every bug found and fixed during development. Include root cause, fix applied, and lesson learned so they don't recur.

---

## BUG-001: Maps Service — Mutation of module-level seed data globals

**Service:** `hhh-maps-service` | **PR:** #2 (SETUP-2: Seed test locations) | **Severity:** Medium

**Symptom:** `seed_locations()` passed the module-level `SYSTEMS` list directly to service calls, mutating global state. Running the seed script twice would corrupt data.

**Root cause:** `SYSTEMS` and child locations were module-level dataclass instances. Passing them directly to `create()` allowed the service to mutate the original objects (e.g., setting `id` on them).

**Fix:** Used `dataclasses.replace(system)` to create copies before passing to `create()`. Applied the same fix in tests where `fake_create` was mutating the location argument.

**Lesson:** Always copy dataclass instances before passing them to functions that may mutate them. Use `dataclasses.replace()` for shallow copies.

---

## BUG-002: Maps Service — Missing `__main__` entrypoint for seed script

**Service:** `hhh-maps-service` | **PR:** #2 | **Severity:** Low

**Symptom:** `python -m src.infrastructure.seed.seed_locations` didn't work — no `if __name__ == "__main__"` block.

**Fix:** Added `if __name__ == "__main__"` block that instantiates `Settings`, creates the DI injector, and calls `seed_locations(service)`.

---

## BUG-003: Contracts Service — `Requirements` model diverges from design spec

**Service:** `hhh-contracts-service` | **PR:** #8 (CS-1: Enrich domain model) | **Severity:** High

**Symptom:** Copilot-generated `Requirements` dataclass had invented fields (`is_shareable`, `max_players`, `cooldown_minutes`, `is_illegal`) instead of the spec-defined fields (`required_ship_tags`, `max_crew_size`).

**Root cause:** LLM hallucinated plausible-looking fields that weren't in the design spec or issue description.

**Fix (pending):** Replace `Requirements` fields with `min_reputation: int = 0`, `required_ship_tags: list[str] = field(default_factory=list)`, `max_crew_size: int = 1`. Also add missing `Contract` fields: `collateral_uec: float = 0.0`, `deadline: datetime | None = None`.

**Status:** ✅ Fixed. `Requirements` now has correct fields. `Contract` has `collateral_uec` and `deadline`. `HaulingOrder` uses `commodity_id` instead of `commodity`.

**Lesson:** Always validate Copilot-generated domain models against the design spec before merging. Cross-reference with `copilot.instructions.md` and `domain-models.instructions.md`.

---

## BUG-004: Cross-repo — Frontend contract types completely misaligned with backend DTOs

**Services:** `hhh-backoffice-frontend`, `hhh-frontend`, `hhh-contracts-service` | **Severity:** Critical

**Symptom:** Creating a contract from either frontend returns HTTP 422 with multiple validation errors. The request payload uses field names and structures that don't exist in the backend `ContractCreateDTO`.

**Error:** `Field required` for `faction`, `reward_uec`, `hauling_orders[0].commodity`, `hauling_orders[0].scu_min`, `hauling_orders[0].scu_max`, `hauling_orders[0].max_container_scu`.

**Root cause:** Both frontends were generated with an entirely different field schema than the backend DTOs. The mismatches are:

| Frontend field | Backend field | Issue |
|---|---|---|
| _(missing)_ | `faction` (required) | Frontend never sends it |
| `reward_aUEC` | `reward_uec` | Name mismatch |
| `collateral_aUEC` | _(not in DTO)_ | Frontend-only field |
| `contractor_name` | _(not in DTO)_ | Frontend-only field |
| `contractor_logo_url` | _(not in DTO)_ | Frontend-only field |
| `deadline_minutes` | _(not in DTO)_ | Frontend-only field |
| `max_acceptances` | _(not in DTO)_ | Frontend-only field |
| `cargo_name` | `commodity` | HaulingOrder name mismatch |
| `cargo_quantity_scu` | `scu_min` + `scu_max` | Single field vs two fields |
| _(missing)_ | `max_container_scu` (required) | Frontend never sends it |
| `required_ship_tags`, `max_crew_size` | `is_shareable`, `max_players`, `cooldown_minutes`, `is_illegal` | Requirements completely different on both sides (neither matches spec; see BUG-003) |

Additionally, the backend `Requirements` model still has the hallucinated fields from BUG-003 (unfixed), while the frontend Requirements is closer to the design spec but still not sending what the backend expects.

**Fix (pending):** Three-part fix required:
1. **Backend (CS-9):** Fix `Requirements` domain model + DTO + mapper per design spec (resolves BUG-003). Add missing `collateral_uec` and `deadline` fields to `Contract` + DTOs.
2. **Backoffice frontend (BO-5):** Align `contract.ts` types, form components, and API client to match the corrected backend schema.
3. **Player frontend (FE-5):** Same alignment for the player-facing frontend types and form.

**Status:** ✅ Fixed. All three parts resolved — backend DTOs, backoffice types, and player frontend types are now aligned with the design spec.

**Lesson:** When generating frontend types and backend DTOs separately, always cross-validate them against each other AND the design spec before merging. A shared schema or OpenAPI spec would prevent this class of bugs entirely.

---

## BUG-005: Maps Service — Missing CORS middleware blocks all frontend location features

**Service:** `hhh-maps-service` | **Issue:** hhh-maps-service#13 | **Severity:** Critical

**Symptom:** Both frontends (localhost:3000 and localhost:3001) get CORS errors on every `/locations/*` request. Backoffice location management, hauling order location autocomplete, and all frontend location features are completely broken.

**Root cause:** `src/main.py` in `create_app()` never configures `CORSMiddleware`. Every other service (contracts, commodities, ships, etc.) already has CORS configured — maps-service was the only one missing it.

**Fix (pending):** Add `CORSMiddleware` to `create_app()` with `allow_origins=["http://localhost:3000", "http://localhost:3001"]`, `allow_methods=["*"]`, `allow_headers=["*"]`. Reference: `hhh-commodities-service/src/main.py` has the correct pattern.

**Status:** ✅ Fixed. CORS middleware added to maps-service `create_app()`.

**Lesson:** When scaffolding a new service, use an existing service as a template and verify all middleware is present. CORS is easy to miss because the backend works fine — the error only appears in browser requests.

---

## BUG-006: Frontend — Wrong default API ports for locations and commodities

**Service:** `hhh-frontend` | **Issue:** hhh-frontend#15 | **Severity:** Critical

**Symptom:** Location and commodity API calls silently reach the wrong services because the default ports are swapped.

**Root cause:** In `src/api/locations.ts`, the default `LOCATIONS_API_URL` uses port **8002** (ships-service) instead of **8003** (maps-service). In `src/api/commodities.ts`, the default uses port **8003** (maps-service) instead of **8007** (commodities-service). The port assignments were mixed up during code generation.

**Fix (pending):** Correct `locations.ts` default port to 8003 and `commodities.ts` default port to 8007. Also fix search endpoint paths: `/locations?q=` → `/locations/search?q=` and `/commodities?q=` → `/commodities/search?q=`.

**Status:** ✅ Fixed. Ports corrected and search endpoint paths updated.

**Lesson:** Always validate API client default ports against the service port table in `copilot.instructions.md`. Add a comment with the service name next to each port constant.

---

## BUG-007: Frontend — Wrong search endpoint paths in API clients

**Service:** `hhh-frontend` | **Issue:** hhh-frontend#15 | **Severity:** High

**Symptom:** Search in the frontend returns unfiltered results because the query parameter is ignored by the wrong endpoint.

**Root cause:** `src/api/locations.ts` calls `/locations?q=...` but the maps-service search endpoint is `GET /locations/search?q=...`. Same issue in `src/api/commodities.ts`: calls `/commodities?q=...` instead of `/commodities/search?q=...`. The `?q=` parameter on the list endpoint is ignored, so it silently returns all results.

**Fix (pending):** Update search functions to use `/locations/search?q=...` and `/commodities/search?q=...`.

**Status:** ✅ Fixed. Search functions now use correct `/search` paths.

**Lesson:** Cross-check frontend API client paths against the actual backend router definitions. The backoffice frontend (`hhh-backoffice-frontend/src/api/locations.ts`) has the correct paths — should have been used as reference.

---

## BUG-008: Backoffice — Contract type uses `action` instead of `faction`

**Service:** `hhh-backoffice-frontend` | **Issue:** hhh-backoffice-frontend#23 | **Severity:** Critical

**Symptom:** Creating or updating a contract from the backoffice returns HTTP 422 because the payload sends `action` instead of `faction`. The backend `ContractCreateDTO` requires `faction` (no default).

**Root cause:** `src/types/contract.ts` defines `Contract` with `action: string` instead of `faction: string`. This propagates through `ContractCreate`, the `GeneralTab` form component, and the `ContractEditPage` validation logic. Likely a typo or hallucination during code generation.

**Fix (pending):** Rename `action` → `faction` in `src/types/contract.ts`, update `GeneralTab.tsx` form label and field binding, update `ContractEditPage.tsx` validation and form initialization.

**Status:** ✅ Fixed. Backoffice contract types now use `faction`.

**Lesson:** When generating TypeScript types for backend DTOs, verify field names match exactly. Run a test request against the backend to validate the payload schema before merging frontend code.

---

## BUG-009: Auth Service — RSI bio parser regex outdated after RSI HTML change

**Service:** `hexadian-auth-service` | **Issue:** hexadian-auth-service#7 | **Severity:** Critical

**Symptom:** `POST /auth/verify/confirm` always returns `{"verified": false}` even when the verification code is correctly placed in the user's RSI profile bio.

**Root cause:** The RSI website changed its HTML structure. The bio field used to be:
```html
<span class="value" id="bioval">...bio...</span>
```
But it changed to:
```html
<div class="entry bio">
  <span class="label">Bio</span>
  <div class="value">...bio...</div>
</div>
```
The regex `<span\s+class="value"\s+id="bioval">(.*?)</span>` no longer matched, so `fetch_profile_bio()` silently returned `None`, causing every verification to fail.

**Fix:** Updated `_BIO_PATTERN` in `rsi_profile_fetcher_impl.py` to:
```python
_BIO_PATTERN = re.compile(
    r'<div\s+class="entry\s+bio">.*?<div\s+class="value">\s*(.*?)\s*</div>',
    re.DOTALL,
)
```

**Status:** ✅ Fixed (hotfix applied directly, formal PR pending in hexadian-auth-service#7).

**Lesson:** External HTML scraping is inherently fragile. When a scraper-based feature stops working, always fetch the live HTML and compare against the expected regex. Consider adding an integration test that hits the real RSI endpoint periodically to detect HTML changes early.

---

## BUG-010: Auth Service — OAuth token exchange fails with offset-naive vs offset-aware datetime TypeError

**Service:** `hexadian-auth-service` | **Severity:** Critical

**Symptom:** `POST /auth/token/exchange` returns HTTP 500. Login on the auth-portal succeeds and redirects back to the backoffice callback, but the code exchange fails with:
```
TypeError: can't compare offset-naive and offset-aware datetimes
```

**Root cause:** PyMongo returns `datetime` objects without timezone info (naive UTC). `auth_service_impl.py` compares these against `datetime.now(tz=UTC)` (aware). Python raises `TypeError` on naive/aware comparisons. Affected in two places: refresh token expiry check (line 124) and auth code expiry check (line 283).

**Fix:** Added `replace(tzinfo=UTC)` in `AuthCodePersistenceMapper.to_domain()` and `RefreshTokenPersistenceMapper.to_domain()` — whenever `expires_at` is loaded with no tzinfo, it is tagged as UTC before being returned to the domain.

**Lesson:** PyMongo always returns naive UTC datetimes. Any comparison with `datetime.now(tz=UTC)` will crash. Fix at the persistence mapper layer (single responsibility) rather than at every comparison site. Pattern: `doc["expires_at"].replace(tzinfo=UTC) if doc["expires_at"].tzinfo is None else doc["expires_at"]`.

---

## BUG-011: All Repos — Branch protection required checks frozen due to missing `app_id`

**Service:** All 12 repositories | **Severity:** Critical

**Symptom:** Required status checks in branch protection show "Expected — Waiting for status to be reported" indefinitely, even after the CI workflow completes successfully. The PR merge button stays blocked.

**Root cause:** When setting required status checks via the GitHub API using the `contexts` array (legacy) or `checks` array with `app_id: null`, GitHub must auto-resolve which app produces each check. For check names that have been previously reported on `main`, this works. For **new** check names (e.g., after renaming a CI job), GitHub cannot resolve the app and falls back to looking for a **commit status** (legacy Status API) instead of a **check run** (Check Runs API). Since GitHub Actions produces check runs, the match never happens — the check stays "pending" forever.

**Affected checks (initial discovery):** `Auth Portal Tests & Coverage` and `Backoffice: Tests & Coverage` on `hexadian-auth-service` PR #91. These were new job names introduced by the coverage enforcement PR.

**Broader audit:** All 12 repos had `app_id: null` on every required check. Only `hexadian-auth-service` was immediately affected (new check names), but any future CI job rename on any repo would trigger the same freeze.

**Fix:** Set `app_id: 15368` (GitHub Actions) explicitly on all required status checks across all 12 repos via:

```bash
# Example for a Python backend service
gh api repos/Hexadian-Corporation/<repo>/branches/main/protection/required_status_checks \
  --method PATCH --input payload.json
```

Where `payload.json` contains:
```json
{
  "strict": true,
  "checks": [
    {"context": "Lint & Format", "app_id": 15368},
    {"context": "Tests & Coverage", "app_id": 15368},
    {"context": "Validate PR Title", "app_id": 15368},
    {"context": "Secret Scan", "app_id": 15368}
  ]
}
```

**Status:** ✅ Fixed across all 12 repos.

**Lesson:** Always set `app_id: 15368` (GitHub Actions) explicitly when configuring required status checks via the API. Never rely on `app_id: null` auto-resolution — it silently breaks for any check name that hasn't been previously reported on the default branch. See `gh-workflow.instructions.md` for the canonical configuration patterns.

**Corollary — never rename CI jobs via PR.** Even with the correct `app_id`, GitHub cannot match a required check name that has never been reported on `main`. If a PR renames a CI job (e.g., `Auth Portal Tests` → `Auth Portal Tests & Coverage`), the new name will freeze as "Expected — Waiting for status" because branch protection can't resolve it. Fix: push the CI rename directly to `main`, then update branch protection to the new name.

---

## BUG-012: Cross-service — JWT secret mismatch between auth-service and HHH services

**Service:** All backend services | **Severity:** High

**Symptom:** HHH services rejected valid JWTs issued by auth-service with signature verification failures.

**Root cause:** Auth-service used `HHH_AUTH_JWT_SECRET` while other services expected `JWT_SECRET`. Environment variable naming convention was inconsistent across services.

**Fix:** Standardized all services to use the same JWT secret env var. Updated `docker-compose.yml` files to pass the correct variable name.

**Lesson:** When multiple services share a secret, define the env var name in a single source of truth (e.g., `copilot.instructions.md`) and reference it everywhere.

---

## BUG-013: Ships, Graphs, Routes Services — Missing CORS middleware blocks all frontend requests

**Service:** `hhh-ships-service`, `hhh-graphs-service`, `hhh-routes-service` | **Severity:** High

**Symptom:** Frontend could not reach ships, graphs, or routes APIs. Browser console showed CORS preflight errors.

**Root cause:** These services were scaffolded without `CORSMiddleware` in `main.py`. Only maps, contracts, and commodities had it.

**Fix:** Added `CORSMiddleware` with the standard configuration to all three services' `main.py`.

**Lesson:** When scaffolding a new service, always copy the CORS middleware setup from an existing service. Add a checklist item to the service scaffold template.

---

## BUG-014: All Repos — PR close/reopen breaks GitHub `closingIssuesReferences` linkage

**Scope:** All repos | **Severity:** Medium

**Symptom:** After closing and reopening a PR, the `Closes #N` keyword in the description no longer auto-closes the linked issue when the PR is merged.

**Root cause:** GitHub removes the `closingIssuesReferences` linkage when a PR is closed. Reopening the PR does not restore the linkage, even though the `Closes #N` text is still in the description.

**Fix:** After reopening a PR, edit the description (remove and re-add the `Closes #N` line) to re-establish the linkage. Alternatively, merge and close the issue manually.

**Lesson:** Never close a PR that has `Closes #N` unless you intend to abandon it. If you must close/reopen, always re-edit the description to restore the linkage.

---

## BUG-015: Maps Service — `location_distances` unique index missing `travel_type`

**Service:** `hhh-maps-service` | **PR:** #59 | **Severity:** High

**Symptom:** Maps service container crashed on startup with `DuplicateKeyError` during `seed_distances()`. The seed creates two `LocationDistance` records per pair of locations (one per `travel_type`: `quantum` and `scm`), but the unique index only covered `(from_location_id, to_location_id)`, so the second insert always failed.

**Root cause:** The `LocationDistance` model uses a `travel_type` field to store separate records per travel type, but the unique index in `dependencies.py` was defined as `[("from_location_id", 1), ("to_location_id", 1)]` without including `travel_type`. This diverged from the model's design — the original issue #28 spec had a single-record design with both travel times in one document, but the implementation chose separate records per `travel_type`.

**Fix applied:**
1. Changed the unique index to `[("from_location_id", 1), ("to_location_id", 1), ("travel_type", 1)]` in `dependencies.py`.
2. Added a migration step to drop the old index (`from_location_id_1_to_location_id_1`) if it exists before creating the new one.
3. Updated both integration tests (`test_indexes.py`) and unit tests (`test_dependencies.py`) to expect the new 3-field index.

**Lesson:** When a domain model stores separate records distinguished by a discriminator field (like `travel_type`), the unique index must include that discriminator. Always verify that unique constraints match the actual data cardinality — one record per natural key.

---

## BUG-016: Project Board — PowerShell codepage corrupts GitHub issue bodies (UTF-8 mojibake)

**Scope:** 47 backend issues across 7 repos | **Severity:** Critical

**Symptom:** A PowerShell script that read issue bodies via `gh issue view --json body`, appended text, and wrote them back via `gh issue edit --body-file` caused all Unicode characters to become garbled. Characters like `→`, `—`, `⚡` turned into `├ö├ç├Â`, `ÔÇö`, `ÔåÆ`. Affected 47 backend issues.

**Root cause:** PowerShell's default codepage (`cp1252`) mishandles UTF-8 output from `gh`. When the script piped `gh` output through PowerShell string processing and wrote to a temp file, the UTF-8 bytes were re-encoded through the Windows codepage, producing double-encoded mojibake. The script also had a loop bug that iterated ~95 times instead of 48 (processing some issues twice).

**Fix applied:**
1. Used GitHub's `userContentEdits` GraphQL API to retrieve the pre-corruption body from each issue's edit history (filtering edits before the corruption timestamp `2026-03-21T20:00:00Z`).
2. Wrote a Python restoration script (`tmp/restore_issues.py`) that wrote bodies using `open(path, "w", encoding="utf-8", newline="\n")` and restored via `gh issue edit --body-file`.
3. All 47 issues restored successfully (0 failures). Verified with sampling: proper Unicode characters, no mojibake.

**Lesson:** **Never use PowerShell** for reading/modifying/writing GitHub issue bodies or any UTF-8 content from `gh` CLI. Always use Python with explicit `encoding="utf-8"`. Recovery is possible via the `userContentEdits` GraphQL API which preserves full edit history.

---

## BUG-017: Project Board — `addSubIssue` API auto-adds issues to board without field values

**Scope:** 16 issues across 7 repos | **Severity:** Medium

**Symptom:** After using the `addSubIssue` GraphQL mutation to set blocking relationships between async migration issues and open backend issues, 16 issues appeared on the project board with `Status=Backlog` and no Priority or Complexity set. The user saw unexpected items cluttering the Backlog column.

**Root cause:** The `addSubIssue` API, when linking an issue as a sub-issue of a parent that is on a project board, automatically adds the child issue to the same board if it isn't already there. The auto-added items get the default `Status=Backlog` with no Priority or Complexity. The 16 affected issues were **stale duplicates** — original issues that were never closed when replacement issues (with higher numbers) were created and implemented via PRs.

**Fix applied:**
1. Verified via `git log --grep` that 11 of 16 had matching squash merge commits in their repos (already implemented).
2. Confirmed via `gh issue list --state all` that all 16 had a counterpart: either a CLOSED duplicate (implemented via PR) or a properly-configured OPEN duplicate.
3. Closed all 15 true duplicates as "not planned" with a comment linking to the counterpart (`Duplicate of #N`).
4. Removed all 15 as sub-issues from their async migration parent issues via `removeSubIssue`.
5. Removed all 15+1 from the project board via `deleteProjectV2Item`.
6. Configured the 1 remaining non-duplicate (maps#45) with proper board fields (`Status=Blocked`, `Priority=Medium`, `Complexity=Low`).
7. Also closed maps#65 (duplicate of maps#66 async migration issue created by error).

**Lesson:** The `addSubIssue` API silently adds child issues to the parent's project board with default field values. Before bulk-adding sub-issue relationships, verify that all target issues are legitimate (not stale duplicates) and expect that they will appear on the board. After bulk operations, audit the board for unexpected entries. Always close original issues when creating replacements.