# DESIGN SYSTEM
You are building a production-grade, agency-quality web interface. Avoid generic AI design patterns. Follow
these rules strictly.
## 
- Purple/violet gradients (especially #8b5cf6 to #6366f1)
- Generic Tailwind defaults (slate-50/100 backgrounds)
- Hero + 3 feature cards + CTA template
- Soft pastel color palettes
- Rounded-2xl on every component
- "Floating card" with shadow-2xl
- Lucide icons in every section
- Inter font as the only choice
- Centered hero text with two-line headline
- "Trusted by" logo strip
## 
Choose ONE hero color that is unexpected:
- Deep forest green (#1a3a2e)
- Burnt orange (#c2410c)
- Editorial cream (#f5e6d3)
- Newspaper black (#0a0a0a)
- Terracotta (#b85042)
- Electric yellow (#fef08a) — only as accent
Pair with:
- 2-3 neutrals (warm grays, off-white)
- ONE single accent color (use sparingly, max 5% of UI)
- Avoid pure white (#ffffff) — use #fafaf9 or #faf8f5
- Avoid pure black (#000000) — use #0a0a0a or #18181b
## ✍
Use TWO fonts maximum:
**Display font (headlines):** Choose ONE with character:
- Fraunces (serif, modern)
- Editorial New (display serif)
- General Sans (geometric sans)
- Söhne (clean sans)
- Instrument Serif (editorial serif)
- Migra (display serif)
**Body font (paragraphs):** Choose ONE for readability:
- Inter (only if paired with display serif)
- Geist (clean modern)
- IBM Plex Sans (technical)
- Söhne Buch (premium feel)
**Rules:**
- Headlines: tracking-tight, leading-tight
- Body: tracking-normal, leading-relaxed (1.6-1.7)
- Use real font weights: 300, 400, 500, 700 (not 600 unnecessarily)
- Max headline size: 5xl-7xl, not 9xl   ## 
- Use 8px grid system (gap-2, gap-4, gap-6, gap-8...)
- Asymmetric layouts (not always centered)
- Generous whitespace — sections need py-24 or py-32
- Maximum content width: max-w-6xl (not max-w-7xl)
- Text columns: max-w-prose (66 characters per line)
- Use grid-cols-12 for editorial layouts
- Break the grid intentionally — full-bleed images, oversized type
## 
**Buttons:**
- NO rounded-2xl by default
- Use rounded-none or rounded-md for editorial
- Solid background with subtle hover (translate-y-[-1px])
- No shadow on default state
- Use border-2 on secondary buttons
**Cards:**
- Skip cards when possible — use horizontal rules and spacing
- When using: border (1px solid) instead of shadow
- Background slightly off from page background
**Inputs:**
- Underline style preferred (border-b only)
- Or fully bordered with no border-radius
- Focus state: change border color, not box-shadow
**Images:**
- Use real photography or custom illustrations
- NEVER use stock icons as decoration
- Aspect ratios: 4:5 (portrait) or 16:10 (landscape)
- Grayscale filter on hover for editorial feel
## 
- Transitions: 200-300ms duration
- Easing: ease-out for entrance, ease-in for exit
- Hover states: subtle (translate, opacity, color shift)
- NO bouncy spring animations
- NO rotating loaders — use linear progress or skeleton
- Page transitions: fade + slight Y shift (10-20px)
- Use Framer Motion or CSS transitions, not GSAP overkill
## 
- linear.app — clean, technical, monospace details
- stripe.com/press — editorial elegance
- vercel.com — minimal with depth
- cosmos.so — gallery-style, oversized type
- read.cv — typography-first
- areena.co — editorial, art-school feel
- studio.design — agency portfolio aesthetic
When in doubt: "What would Linear or Stripe do?"
## 
Before delivering, verify:
- [ ] No purple/violet anywhere
- [ ] No default Tailwind soft shadows
- [ ] Typography has character (not just Inter)
- [ ] Asymmetric or editorial layout
- [ ] Real content, not Lorem Ipsum
- [ ] Hover states are subtle
- [ ] One unexpected design choice (oversized type, full-bleed, etc.)