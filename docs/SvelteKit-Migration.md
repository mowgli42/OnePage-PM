# SvelteKit migration (deferred)

The app currently uses **Svelte 4 + Vite** with a small `frontend/src/lib/router.js` helper for `?view=` and `?plan_id=` URL state.

A full SvelteKit migration would provide:

- File-based routing (`/oppm/[planId]`, `/todos`)
- Built-in API proxy in `hooks.server.js`
- Optional SSR for shareable plan links

**Recommended approach when ready:**

1. `npm create svelte@latest` in a branch; copy `src/components`, `src/stores`, `src/lib`.
2. Move `/_/backend` proxy to `vite.config.js` / adapter-node.
3. Replace `router.js` with SvelteKit `+page.svelte` and `$page.url.searchParams`.
4. Keep FastAPI backend unchanged.

Until then, the lightweight router covers deep links without a framework migration.
