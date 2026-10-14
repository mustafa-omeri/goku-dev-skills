# Sidebar Navigation Themes

Curated collection of 8 production-grade sidebar navigation themes. When a coding agent is asked to build or refactor a sidebar, navigation drawer, or application shell, it must inspect this catalog first.

## Decision Matrix & Selection Catalog

When requested to create or update a **sidebar**, match the user's intent to one of the themes below:

| Theme Identifier | Design Document | Aesthetic Tone | Complexity | Best Suited For |
| :--- | :--- | :--- | :--- | :--- |
| [`violet-minimal-sidebar`](./violet-minimal-sidebar/index.html) | [Violet Minimal Dark Sidebar](./violet-minimal-sidebar/violet-minimal-sidebar.design.md) | Dark Minimalist / AI Assistant Workspaces | Low-to-Medium | Clean dark-mode AI tools, modern SaaS web apps, and developer portals needing unobtrusive navigation. |
| [`dual-column-indigo-sidebar`](./dual-column-indigo-sidebar/index.html) | [Dual-Column Indigo Drawer Sidebar](./dual-column-indigo-sidebar/dual-column-indigo-sidebar.design.md) | Rich Indigo Modernist / Communication Hub | Medium-to-High | Chat, collaboration, messaging apps (Slack/Discord style) where workspaces live on the left and channels/chats live in the sub-drawer. |
| [`light-saas-dual-rail-sidebar`](./light-saas-dual-rail-sidebar/index.html) | [Light SaaS Dual-Rail Navigation Sidebar](./light-saas-dual-rail-sidebar/light-saas-dual-rail-sidebar.design.md) | Clean B2B SaaS / Precision Enterprise | Medium | Enterprise dashboards, analytics platforms, and cloud consoles requiring clear categorical separation of tools. |
| [`dark-slate-dock-sidebar`](./dark-slate-dock-sidebar/index.html) | [Dark Slate Multi-Tier Dock Sidebar](./dark-slate-dock-sidebar/dark-slate-dock-sidebar.design.md) | Dark Slate Technical / High-Density Operations | Medium | Operations monitoring, DevOps consoles, and media asset managers needing structured contextual navigation. |
| [`collapsible-expandable-sidebar`](./collapsible-expandable-sidebar/index.html) | [Collapsible & Expandable Clean Light Sidebar](./collapsible-expandable-sidebar/collapsible-expandable-sidebar.design.md) | Minimalist Dynamic / Adaptive SaaS | Medium | Dashboards where users frequently need to maximize canvas space (charts, tables, canvas editors) while keeping navigation 1 click away. |
| [`compact-dock-sidebar`](./compact-dock-sidebar/index.html) | [Compact Developer Icon Dock Sidebar](./compact-dock-sidebar/compact-dock-sidebar.design.md) | Ultra-compact Modern Dark / IDE Dock | Low-to-Medium | Developer tools, canvas editors, or split-pane applications where the sidebar must consume minimal horizontal space. |
| [`workspace-profile-sidebar`](./workspace-profile-sidebar/index.html) | [Workspace & Profile-Centric SaaS Sidebar](./workspace-profile-sidebar/workspace-profile-sidebar.design.md) | Modern Professional SaaS / Team Workspace | Medium | SaaS platforms where user profile, role switching, team workspaces, and plan usage/storage limits are primary navigation concerns. |
| [`window-chrome-team-sidebar`](./window-chrome-team-sidebar/index.html) | [macOS Window-Chrome Team Sidebar](./window-chrome-team-sidebar/window-chrome-team-sidebar.design.md) | Desktop App Aesthetic / Collaborative Studio | Medium | Desktop-like web applications, design studios, and collaborative environments highlighting active online team members. |

## How an Agent Uses This Directory

1. **Understand Intent:** Clarify product tone, density requirements, and brand character.
2. **Review Design Doc:** Open the corresponding `<theme-name>.design.md` file to inspect color variables, typography, and layout anatomy.
3. **Inspect Working Code:** Check `index.html` and `styles.css` inside the theme folder to examine exact classes, flex/grid properties, and keyframe transitions.
4. **Adapt to Framework:** Port the CSS patterns and semantic DOM into React / Vite / Tailwind / shadcn as outlined in Section 5 of the design doc.
