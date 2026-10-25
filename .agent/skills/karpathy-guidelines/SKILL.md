---
name: karpathy-guidelines
description: >
  Yaygın kodlama hatalarını azaltan davranış kuralları ve hakemlik: gereksiz karmaşıklıktan kaçınma, cerrahi değişiklik, varsayımları yüzeye çıkarma, 3 aşamalı konsensüs (council). Tetikleyiciler: "bu çok karmaşık", "basitleştir", "gereksiz kod", "varsayım ne", "llm council", "overcomplicated", "simplify this", "surface assumptions", "peer review". Tetiklenmez: mimari kararlar `musgoku`, tasarım kararları tasarım skill setine aittir. Tam sözlük: .agent/rules/skill-trigger-routing.md
license: MIT
---

# Karpathy Guidelines

Behavioral guidelines to reduce common LLM coding mistakes, derived from [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876) on LLM coding pitfalls and the [LLM Council](https://github.com/karpathy/llm-council) multi-agent deliberation architecture.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

---

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

---

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

---

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

Before modifying shared code (Blast Radius / Pre-Edit Impact Analysis):

- Before altering any shared function, class, type, component, or DB schema, search the codebase (`grep`) for all references.
- Know who calls it before you touch it. If your change alters behavior or signature, update all callers in the same batch or preserve backward compatibility.

When your changes create orphans:

- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

---

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

## 5. Council Deliberation (3-Aşamalı Konsensüs & Kör Hakemlik)

**Karmaşık kararlarda tek model önyargısına kapılma. Anonim akran değerlendirmesi ve sentez yürüt.**

Büyük mimari tercihlerde, riskli refactoring kararlarında veya belirsiz tasarım ikilemlerinde Andrej Karpathy'nin 3 aşamalı konsey protokolü uygulanır:

1. **Stage 1 (First Opinions):** Bağımsız 2-3 alternatif çözüm üretilir (`Option A`, `Option B`, `Option C`).
2. **Stage 2 (Anonymized Peer Review):** Çözümler harflendirilerek kimliği gizlenir (körleme); alt ajanlara veya modellere güçlü/zayıf yönler ve Karpathy sadelik filtresi üzerinden inceletilip sıralanır (`FINAL RANKING:`).
3. **Stage 3 (Chairman Synthesis):** Başkan ajan, akran eleştirilerini ve konsensüs tablosunu inceleyerek çelişkileri ayıklar; en yalın ve sağlam nihai sentezi üretir.

Detaylı rehber ve prompt şablonları için:
- **Hakemlik Rehberi:** `references/llm-council-deliberation.md`
- **Sıralama ve Konsensüs Aracı:** `scripts/council_ranker.py`

```bash
# Örnek konsensüs çalışmasını çalıştır
python .agent/skills/karpathy-guidelines/scripts/council_ranker.py --sample
```

---

## 6. Action-First & Token-Dense Output (Zero-Fluff & Prose Compression)

**Bilişsel yükü düşür, dolgu cümlelerini sıfırla, teknik kesinliği tam koru.**

Derived from [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) and [juliusbrussee/caveman](https://github.com/juliusbrussee/caveman):

1. **Lead with Action:** Açılış cümlesi doğrudan yapılacak işi veya dosya/satırı belirtir; gereksiz giriş (preamble) ve özet (recap) cümleleri yasaktır.
2. **Cap Lists to 5:** Bilişsel aşırı yüklenmeyi önlemek için listeler tek seferde en fazla 5 maddeyle sınırlandırılır.
3. **Single Concrete Next Step:** Karar felcini önlemek için ucu açık sorular yerine tek bir net sonraki adım sunulur.
4. **Prose Compression (Caveman Heuristic):** Kod, tipler ve diff'ler %100 eksiksiz korunur; açıklayıcı metinler ise yüksek yoğunluklu (high-density) tutulur.

Detaylı rehberler:
- **Action-First & ADHD Formatting:** `references/action-first-communication.md`
- **Token-Efficient Prose Compression:** `references/token-efficient-communication.md`
