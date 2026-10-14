# Card Component Themes

10 curated card component themes covering pricing grids, interactive 3D flip metrics, job listings, bio widgets, travel cards, and article previews.

## Decision Matrix & Selection Catalog

When requested to create or update a **card**, match the user's intent to one of the themes below:

| Theme Identifier | Design Document | Aesthetic Tone | Complexity | Best Suited For |
| :--- | :--- | :--- | :--- | :--- |
| [`dark-profile-bio-card`](./dark-profile-bio-card/index.html) | [Dark Minimalist Profile Bio Card](./dark-profile-bio-card/dark-profile-bio-card.design.md) | Dark Sophistication / Modern Creator | Low | About Us pages, speaker profiles, author cards, and developer community bio widgets. |
| [`pricing-tier-grid-cards`](./pricing-tier-grid-cards/index.html) | [Multi-Tier SaaS Pricing Table Cards](./pricing-tier-grid-cards/pricing-tier-grid-cards.design.md) | High-Conversion SaaS / Transparent B2B | Medium | Pricing pages, upgrade paywalls, subscription tier selection for SaaS products. |
| [`interactive-flip-metric-card`](./interactive-flip-metric-card/index.html) | [Interactive 3D Flip Metric KPI Card](./interactive-flip-metric-card/interactive-flip-metric-card.design.md) | Tactile Analytics / Interactive Dashboard | Medium | Dashboard KPI metrics where users want high-level numbers on top and can flip to inspect historical trend or breakdown. |
| [`vibrant-social-creator-card`](./vibrant-social-creator-card/index.html) | [Vibrant Social Creator Profile Card](./vibrant-social-creator-card/vibrant-social-creator-card.design.md) | Creative Studio / Vibrant Warmth | Low-to-Medium | Creative directories, social influencer bios, design team listings with Dribbble/Codepen links. |
| [`career-job-listing-card`](./career-job-listing-card/index.html) | [Career Job Listing & Opportunity Card](./career-job-listing-card/career-job-listing-card.design.md) | Modern HR / Professional Recruitment | Low-to-Medium | Careers pages, job search boards, recruitment listings with remote badges and salary ranges. |
| [`destination-travel-card`](./destination-travel-card/index.html) | [Destination Travel & Experience Card](./destination-travel-card/destination-travel-card.design.md) | Warm Editorial / Lifestyle Exploration | Low-to-Medium | Travel booking platforms, real estate discovery, city guides, and lifestyle blog cards. |
| [`dark-user-profile-widget-card`](./dark-user-profile-widget-card/index.html) | [Dark User Profile & Activity Widget Card](./dark-user-profile-widget-card/dark-user-profile-widget-card.design.md) | Dark Technical / SaaS Account Widget | Medium | User account dropdown menus, team directory cards, and user management widgets in dark apps. |
| [`expandable-summary-metric-card`](./expandable-summary-metric-card/index.html) | [Expandable Summary & Detail Metric Card](./expandable-summary-metric-card/expandable-summary-metric-card.design.md) | Analytical Modern / Interactive Summary | Medium | Financial statement cards, order summaries, and metric inspection panels. |
| [`editorial-article-preview-card`](./editorial-article-preview-card/index.html) | [Editorial Article & Story Preview Card](./editorial-article-preview-card/editorial-article-preview-card.design.md) | Refined Editorial / Natural Horizon | Low | Travel blogs, news portals, outdoor brand stories, and editorial journal articles. |
| [`portfolio-creator-profile-card`](./portfolio-creator-profile-card/index.html) | [Portfolio Creator Profile & Bio Card](./portfolio-creator-profile-card/portfolio-creator-profile-card.design.md) | Soft Pastel Blue / Agency Creative | Low | Design agency rosters, consultant profile cards, portfolio introductions, and speaker listings. |

## How an Agent Uses This Directory

1. **Understand Intent:** Clarify product tone, density requirements, and brand character.
2. **Review Design Doc:** Open the corresponding `<theme-name>.design.md` file to inspect color variables, typography, and layout anatomy.
3. **Inspect Working Code:** Check `index.html` and `styles.css` inside the theme folder to examine exact classes, flex/grid properties, and keyframe transitions.
4. **Adapt to Framework:** Port the CSS patterns and semantic DOM into React / Vite / Tailwind / shadcn as outlined in Section 5 of the design doc.
