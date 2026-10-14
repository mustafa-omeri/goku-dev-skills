# Login & Authentication Themes

16 diverse authentication screen themes ranging from minimalist glassmorphic cards and split-screen hero layouts to Web3 neon and dual-mode sliding auth switchers.

## Decision Matrix & Selection Catalog

When requested to create or update a **login**, match the user's intent to one of the themes below:

| Theme Identifier | Design Document | Aesthetic Tone | Complexity | Best Suited For |
| :--- | :--- | :--- | :--- | :--- |
| [`floating-orb-minimal-login`](./floating-orb-minimal-login/index.html) | [Floating Orb Minimalist Login](./floating-orb-minimal-login/floating-orb-minimal-login.design.md) | Clean Modern / Elevated Glass | Low-to-Medium | Modern SaaS applications, customer portals, and web utilities wanting clean, distraction-free authentication. |
| [`compact-dark-credentials-login`](./compact-dark-credentials-login/index.html) | [Compact Dark Credentials Authentication Card](./compact-dark-credentials-login/compact-dark-credentials-login.design.md) | Technical Dark / Focused Minimalist | Low | Developer consoles, CLI companion web portals, and dark-theme admin dashboards. |
| [`clean-light-card-login`](./clean-light-card-login/index.html) | [Clean Light Card Authentication](./clean-light-card-login/clean-light-card-login.design.md) | Neutral B2B / Trustworthy Light | Low | Corporate intranets, healthcare portals, education management systems, and standard B2B logins. |
| [`web3-crypto-neon-login`](./web3-crypto-neon-login/index.html) | [Web3 & Crypto Neon Glow Login](./web3-crypto-neon-login/web3-crypto-neon-login.design.md) | Futuristic Web3 / High-Tech Neon | Medium | Cryptocurrency exchanges, DeFi dashboards, NFT platforms, and cyber-themed applications. |
| [`orbiting-blob-security-login`](./orbiting-blob-security-login/index.html) | [Orbiting Blob Security & Trust Login](./orbiting-blob-security-login/orbiting-blob-security-login.design.md) | Playful Modern Security / Animated Vector | Medium | Consumer privacy apps, password managers, cloud security tools, and modern fintech. |
| [`animated-wave-header-login`](./animated-wave-header-login/index.html) | [Animated Wave Header Authentication Card](./animated-wave-header-login/animated-wave-header-login.design.md) | Fluid Dynamic / Modern Consumer Web | Medium | Mobile-friendly web apps, consumer platforms, and lifestyle services wanting visual fluidity. |
| [`split-hero-cloud-storage-login`](./split-hero-cloud-storage-login/index.html) | [Split-Hero Cloud Storage & Transfer Login](./split-hero-cloud-storage-login/split-hero-cloud-storage-login.design.md) | Modern Tech SaaS / Split Hero Showcase | Medium | SaaS tools where communicating the product's value (privacy, encryption, speed) reinforces sign-in confidence. |
| [`conversational-friendly-saas-login`](./conversational-friendly-saas-login/index.html) | [Conversational Friendly SaaS Sign-In](./conversational-friendly-saas-login/conversational-friendly-saas-login.design.md) | Warm Approachable / Conversational Human | Low-to-Medium | Community platforms, creative apps, collaborative whiteboards, and human-centric tools. |
| [`cosmic-orbit-purple-login`](./cosmic-orbit-purple-login/index.html) | [Cosmic Orbit Deep Purple Login](./cosmic-orbit-purple-login/cosmic-orbit-purple-login.design.md) | Cosmic Mystique / Deep Creative Tech | Medium | Creative tools, entertainment services, AI generators, and nighttime media platforms. |
| [`geometric-split-banner-login`](./geometric-split-banner-login/index.html) | [Geometric Split-Banner Modern Login](./geometric-split-banner-login/geometric-split-banner-login.design.md) | Contemporary Geometric / Crisp B2B | Medium | Modern B2B web applications, marketing platforms, and collaborative document apps. |
| [`fintech-secure-split-login`](./fintech-secure-split-login/index.html) | [Fintech Secure Payment Split-Screen Login](./fintech-secure-split-login/fintech-secure-split-login.design.md) | Fintech Security / Trust & Speed | Medium | Payment gateways, fintech apps, banking portals, and accounting software. |
| [`dark-luxury-glass-login`](./dark-luxury-glass-login/index.html) | [Dark Luxury Glassmorphic Login](./dark-luxury-glass-login/dark-luxury-glass-login.design.md) | High-End Luxury / Deep Stealth Black | Medium | Luxury brands, private equity portals, crypto VIP dashboards, and premium membership apps. |
| [`glass-wave-morphism-login`](./glass-wave-morphism-login/index.html) | [Glass Wave-Morphism Authentication Card](./glass-wave-morphism-login/glass-wave-morphism-login.design.md) | Fluid Glassmorphism / Modern Tech | Medium | Next-gen web applications wanting smooth visual personality and frosted-glass depth. |
| [`sliding-dual-auth-toggle-login`](./sliding-dual-auth-toggle-login/index.html) | [Sliding Dual-State Login & Register Toggle](./sliding-dual-auth-toggle-login/sliding-dual-auth-toggle-login.design.md) | Interactive Versatile / Dual-Mode Conversion | Medium-to-High | Landing pages and portals where users must seamlessly switch between login and registration without page reloads. |
| [`animated-pulse-vector-login`](./animated-pulse-vector-login/index.html) | [Animated Pulse Vector Hero Login](./animated-pulse-vector-login/animated-pulse-vector-login.design.md) | Healthtech / Empathy & Precision | Medium | Healthtech, fitness trackers, dating/social platforms, and wellness applications. |
| [`sliding-hero-auth-switcher-login`](./sliding-hero-auth-switcher-login/index.html) | [Sliding Hero Photo Auth Switcher](./sliding-hero-auth-switcher-login/sliding-hero-auth-switcher-login.design.md) | Editorial Lifestyle / Photo Hero Switcher | Medium-to-High | Lifestyle brands, travel portals, high-end commerce, and editorial platforms. |

## How an Agent Uses This Directory

1. **Understand Intent:** Clarify product tone, density requirements, and brand character.
2. **Review Design Doc:** Open the corresponding `<theme-name>.design.md` file to inspect color variables, typography, and layout anatomy.
3. **Inspect Working Code:** Check `index.html` and `styles.css` inside the theme folder to examine exact classes, flex/grid properties, and keyframe transitions.
4. **Adapt to Framework:** Port the CSS patterns and semantic DOM into React / Vite / Tailwind / shadcn as outlined in Section 5 of the design doc.
