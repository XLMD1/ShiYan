# Frontend Visual Polish Design

## Goal

Upgrade the Vue front end from a plain student-project interface into a more polished operational data-analysis tool while preserving the existing workflow, routes, API calls, and page responsibilities.

## Scope

The visual polish applies to the existing front-end application only. It should not change backend behavior, API contracts, database models, spider scripts, authentication flow, or uploaded dataset behavior.

Primary scope:

- Global theme tokens, typography, page background, cards, buttons, forms, tables, focus states, and motion.
- Top navigation styling and active route feedback.
- Upload page layout, online data fetch buttons, upload drop zone, upload success summary, field tags, and preview panel.
- Reusable table and uploader components so dashboard/history/preview surfaces inherit the same visual quality.

Secondary scope:

- Existing dashboard, clean, analysis, history, and visualize pages may benefit from global styles without structural rewrites.
- Keep page density suitable for a data tool. Avoid landing-page hero sections, decorative blobs, large marketing copy, or heavy gradients.

## Design Direction

Use a restrained analytics-dashboard style:

- Dark navy navigation for product identity and contrast.
- Cool gray application background with subtle grid/radial texture.
- White panels with thin borders, soft shadows, and 6-8px radius.
- Teal accent for success/progress/data actions.
- Amber accent for active fetching and warning states.
- Compact, scan-friendly spacing for repeated data operations.

The interface should feel more deliberate but still appropriate for a school project demo: practical, readable, and easy to explain during acceptance.

## Motion

Motion should be subtle and CSS-only:

- Page sections fade and translate in slightly on load.
- Cards lift gently on hover.
- Buttons show hover lift and a small shine/ripple-like highlight.
- Upload drop zone animates its dashed border and background on hover/drag/uploading.
- Progress bar uses a shimmer overlay while uploading.
- Field tags and action chips highlight on hover without shifting layout.

Respect `prefers-reduced-motion` by disabling non-essential animation.

## Files To Modify

- `frontend/src/style.css`
  - Add design tokens and global component polish.
  - Improve body background, cards, buttons, form controls, tables, focus rings, and motion utilities.

- `frontend/src/components/NavBar.vue`
  - Polish top navigation, active links, user badge, and logout button.

- `frontend/src/components/FileUploader.vue`
  - Improve upload drop zone visual hierarchy, icon treatment, hover/drag/uploading states, and progress animation.

- `frontend/src/components/DataTable.vue`
  - Improve table shell, sticky header, row hover, pagination controls, and empty/loading states.

- `frontend/src/views/UploadView.vue`
  - Rework upload page presentation around the existing data-fetch/upload/success/preview workflow.
  - Add small icon labels using text symbols to avoid a new icon dependency.
  - Keep all existing functions and API calls unchanged.

## Non-Goals

- Do not introduce a new UI library.
- Do not add new runtime dependencies.
- Do not redesign the backend-generated chart option format.
- Do not change routes, store APIs, authentication behavior, or data-fetch source names.
- Do not modify generated backend CSV files.

## Verification

Run:

```bash
cd frontend
npm run build
```

Then verify in browser:

- Desktop upload page renders without text overlap.
- Mobile width keeps fetch buttons, upload zone, summary cards, and action buttons usable.
- Existing login-protected routing still sends unauthenticated users to `/login`.
- No visible regressions in dashboard table, preview table, and navigation.

