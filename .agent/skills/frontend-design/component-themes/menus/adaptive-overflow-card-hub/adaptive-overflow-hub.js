/**
 * Adaptive Overflow Card Hub Controller
 * Standard B.9: Scalable Action Groups & Bottom-Sheet Card Hub
 */

(function () {
  'use strict';

  // Sample Datasets: 12 Core Commands vs 100 Scaled Commands
  const DOMAINS = {
    plan: { id: 'plan', label: 'Planlama & Mimari', pillClass: 'plan' },
    debug: { id: 'debug', label: 'Hata Teşhis & Güvenlik', pillClass: 'debug' },
    design: { id: 'design', label: 'Tasarım & Zanaat', pillClass: 'design' },
    release: { id: 'release', label: 'Yayın & Sürüm', pillClass: 'release' },
    accept: { id: 'accept', label: 'Kabul & Doğrulama', pillClass: 'accept' }
  };

  const ITEMS_12 = [
    { id: 'plan', name: '/plan', domain: 'plan', desc: 'Mimari planlama ve adım adım uygulama reçetesi üretir.' },
    { id: 'fix-bug', name: '/fix-bug', domain: 'debug', desc: '6 aşamalı sistematik hata ayıklama döngüsü kurar.' },
    { id: 'ui-polish', name: '/ui-polish', domain: 'design', desc: 'Tasarım sözleşmesi, zanaat tabanı ve anti-slop orkestrasyonu.' },
    { id: 'commitx', name: '/commitx', domain: 'release', desc: 'Peşin onaylı kesintisiz sürüm ve commit süreci.' },
    { id: 'verify-last', name: '/verify-last', domain: 'accept', desc: 'Son geliştirmelerin kapsam ve regresyon denetimi.' },
    { id: 'verify-sprint', name: '/verify-sprint', domain: 'accept', desc: 'Aktif sprint kabul kriterleri ve dikey dilim testi.' },
    { id: 'verify-prd', name: '/verify-prd', domain: 'accept', desc: 'PRD genelinde retrospektif sahte bitti avcılığı.' },
    { id: 'check-security', name: '/check-security', domain: 'debug', desc: 'OWASP güvenlik açıkları ve yetki aşımı kontrolü.' },
    { id: 'seo-apply', name: '/seo-apply', domain: 'design', desc: 'Meta etiketleri, OpenGraph ve JSON-LD şemaları.' },
    { id: 'prelaunch', name: '/prelaunch', domain: 'release', desc: '20 maddelik canlıya alma ve mevzuat denetimi.' },
    { id: 'prelaunch-update', name: '/prelaunch-update', domain: 'release', desc: 'Mevzuat para cezaları ve platform kuralları senkronu.' },
    { id: 'gs-update', name: '/gs-update', domain: 'release', desc: 'Sıfır şişkinlikli cerrahi skill seti güncellemesi.' }
  ];

  // Generate 100 items for the 100-item scalability test
  const ITEMS_100 = [...ITEMS_12];
  const EXTRA_CATEGORIES = ['plan', 'debug', 'design', 'release', 'accept'];
  for (let i = 13; i <= 100; i++) {
    const cat = EXTRA_CATEGORIES[i % EXTRA_CATEGORIES.length];
    ITEMS_100.push({
      id: `cmd-${i}`,
      name: `/action-${i}`,
      domain: cat,
      desc: `Ölçeklenebilirlik denetimi için üretilen ${cat.toUpperCase()} alanındaki ${i}. eylem kartı.`
    });
  }

  // State
  let currentMode = 'preview-and-panel'; // 'panel-only' | 'preview-and-panel'
  let currentDataset = ITEMS_12;
  let activeTriggerEl = null;

  // DOM Elements
  const ribbonEl = document.getElementById('hubRibbon');
  const groupLauncherBtn = document.getElementById('hubGroupLauncher');
  const launcherCountBadge = document.getElementById('hubLauncherCount');
  const previewStripEl = document.getElementById('hubPreviewStrip');
  const moreBtn = document.getElementById('hubBtnMore');
  const moreCountEl = document.getElementById('hubMoreCount');

  const backdropEl = document.getElementById('hubBackdrop');
  const sheetEl = document.getElementById('hubSheet');
  const sheetCountBadge = document.getElementById('hubSheetCount');
  const searchInput = document.getElementById('hubSearchInput');
  const closeBtn = document.getElementById('hubBtnClose');
  const sheetBodyEl = document.getElementById('hubSheetBody');
  const emptyStateEl = document.getElementById('hubEmptyState');

  // Mode & Scale Toggle Buttons
  const btnModePreview = document.getElementById('btnModePreview');
  const btnModePanel = document.getElementById('btnModePanel');
  const btnScale12 = document.getElementById('btnScale12');
  const btnScale100 = document.getElementById('btnScale100');

  // Render Bottom-Sheet Cards
  function renderSheetCards(items) {
    sheetBodyEl.querySelectorAll('.hub-domain-panel').forEach(p => p.remove());

    const groups = {};
    Object.keys(DOMAINS).forEach(k => { groups[k] = []; });
    items.forEach(item => {
      if (groups[item.domain]) {
        groups[item.domain].push(item);
      }
    });

    let totalVisible = 0;

    Object.keys(DOMAINS).forEach(domainKey => {
      const domainInfo = DOMAINS[domainKey];
      const domainItems = groups[domainKey];

      const panel = document.createElement('section');
      panel.className = 'hub-domain-panel';
      panel.dataset.domain = domainKey;

      if (domainItems.length === 0) {
        panel.style.display = 'none';
      } else {
        totalVisible += domainItems.length;
      }

      panel.innerHTML = `
        <div class="hub-domain-header">
          <span class="hub-domain-pill ${domainInfo.pillClass}">${domainInfo.label}</span>
          <span class="hub-domain-count">(${domainItems.length})</span>
        </div>
        <div class="hub-card-grid">
          ${domainItems.map(item => `
            <div class="hub-card" tabindex="0" role="button" data-id="${item.id}" data-name="${item.name.toLowerCase()}" data-desc="${item.desc.toLowerCase()}">
              <div class="hub-card-top">
                <div class="hub-card-name-wrap">
                  <svg class="hub-card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polyline>
                  </svg>
                  <span class="hub-card-name">${escapeHtml(item.name)}</span>
                </div>
                <span class="hub-card-badge">${domainInfo.id.toUpperCase()}</span>
              </div>
              <p class="hub-card-desc">${escapeHtml(item.desc)}</p>
            </div>
          `).join('')}
        </div>
      `;

      sheetBodyEl.insertBefore(panel, emptyStateEl);
    });

    sheetCountBadge.textContent = `${items.length} Komut`;
    launcherCountBadge.textContent = items.length;

    if (totalVisible === 0) {
      emptyStateEl.classList.add('is-visible');
    } else {
      emptyStateEl.classList.remove('is-visible');
    }
  }

  // Adaptive Preview Calculation (Çözüm 2)
  function updateRibbonLayout() {
    if (currentMode === 'panel-only') {
      previewStripEl.style.display = 'none';
      moreBtn.style.display = 'none';
      return;
    }

    previewStripEl.style.display = 'flex';
    previewStripEl.innerHTML = '';

    const containerWidth = ribbonEl.clientWidth;
    const launcherWidth = groupLauncherBtn.offsetWidth || 180;
    const moreBtnReservedWidth = 90;
    const availableWidth = containerWidth - launcherWidth - moreBtnReservedWidth - 32;

    if (availableWidth <= 60) {
      // Very small screen: show more button only
      moreBtn.style.display = 'inline-flex';
      moreCountEl.textContent = `+${currentDataset.length}`;
      return;
    }

    let usedWidth = 0;
    let visibleCount = 0;

    for (let i = 0; i < currentDataset.length; i++) {
      const item = currentDataset[i];
      // Estimate chip width based on character length + padding + icon
      const approxChipWidth = (item.name.length * 8) + 38;

      if (usedWidth + approxChipWidth > availableWidth) {
        break;
      }

      usedWidth += approxChipWidth + 6; // 6px gap
      visibleCount++;

      const chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'hub-chip-action';
      chip.title = item.desc;
      chip.innerHTML = `
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polyline>
        </svg>
        <span class="hub-chip-cmd">${escapeHtml(item.name)}</span>
      `;
      chip.addEventListener('click', (e) => {
        openSheet(e.currentTarget);
        // Highlight matching card in sheet
        setTimeout(() => {
          const card = sheetBodyEl.querySelector(`[data-id="${item.id}"]`);
          if (card) {
            card.focus();
            card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
          }
        }, 150);
      });
      previewStripEl.appendChild(chip);
    }

    const remainingCount = currentDataset.length - visibleCount;
    if (remainingCount > 0) {
      moreBtn.style.display = 'inline-flex';
      moreCountEl.textContent = `+${remainingCount}`;
    } else {
      moreBtn.style.display = 'none';
    }
  }

  // Open & Close Bottom Sheet
  function openSheet(triggerEl) {
    activeTriggerEl = triggerEl || document.activeElement;
    backdropEl.classList.add('is-open');
    sheetEl.classList.add('is-open');
    backdropEl.setAttribute('aria-hidden', 'false');
    sheetEl.setAttribute('aria-hidden', 'false');

    searchInput.value = '';
    filterCards('');
    setTimeout(() => {
      searchInput.focus();
    }, 100);

    document.addEventListener('keydown', handleKeydown);
  }

  function closeSheet() {
    backdropEl.classList.remove('is-open');
    sheetEl.classList.remove('is-open');
    backdropEl.setAttribute('aria-hidden', 'true');
    sheetEl.setAttribute('aria-hidden', 'true');

    document.removeEventListener('keydown', handleKeydown);

    if (activeTriggerEl && typeof activeTriggerEl.focus === 'function') {
      activeTriggerEl.focus();
    }
  }

  function handleKeydown(e) {
    if (e.key === 'Escape') {
      e.preventDefault();
      closeSheet();
    }
  }

  // Filter Cards
  function filterCards(query) {
    const q = query.trim().toLowerCase();
    const panels = sheetBodyEl.querySelectorAll('.hub-domain-panel');
    let anyVisible = false;

    panels.forEach(panel => {
      const cards = panel.querySelectorAll('.hub-card');
      let panelMatchCount = 0;

      cards.forEach(card => {
        const name = card.dataset.name || '';
        const desc = card.dataset.desc || '';
        const match = !q || name.includes(q) || desc.includes(q);

        if (match) {
          card.style.display = 'flex';
          panelMatchCount++;
          anyVisible = true;
        } else {
          card.style.display = 'none';
        }
      });

      if (panelMatchCount === 0) {
        panel.style.display = 'none';
      } else {
        panel.style.display = 'flex';
        panel.querySelector('.hub-domain-count').textContent = `(${panelMatchCount})`;
      }
    });

    if (!anyVisible) {
      emptyStateEl.classList.add('is-visible');
    } else {
      emptyStateEl.classList.remove('is-visible');
    }
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // Event Listeners
  groupLauncherBtn.addEventListener('click', (e) => openSheet(e.currentTarget));
  moreBtn.addEventListener('click', (e) => openSheet(e.currentTarget));
  closeBtn.addEventListener('click', closeSheet);
  backdropEl.addEventListener('click', closeSheet);

  searchInput.addEventListener('input', (e) => {
    filterCards(e.target.value);
  });

  // Mode Toggles
  btnModePreview.addEventListener('click', () => {
    currentMode = 'preview-and-panel';
    btnModePreview.classList.add('active');
    btnModePanel.classList.remove('active');
    updateRibbonLayout();
  });

  btnModePanel.addEventListener('click', () => {
    currentMode = 'panel-only';
    btnModePanel.classList.add('active');
    btnModePreview.classList.remove('active');
    updateRibbonLayout();
  });

  // Scale Toggles
  btnScale12.addEventListener('click', () => {
    currentDataset = ITEMS_12;
    btnScale12.classList.add('active');
    btnScale100.classList.remove('active');
    renderSheetCards(currentDataset);
    updateRibbonLayout();
  });

  btnScale100.addEventListener('click', () => {
    currentDataset = ITEMS_100;
    btnScale100.classList.add('active');
    btnScale12.classList.remove('active');
    renderSheetCards(currentDataset);
    updateRibbonLayout();
  });

  // ResizeObserver for Adaptive Width Calculation
  if ('ResizeObserver' in window) {
    let resizeTimer;
    const ro = new ResizeObserver(() => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(updateRibbonLayout, 50);
    });
    ro.observe(ribbonEl);
  } else {
    window.addEventListener('resize', updateRibbonLayout);
  }

  // Initialize
  renderSheetCards(currentDataset);
  updateRibbonLayout();
})();
