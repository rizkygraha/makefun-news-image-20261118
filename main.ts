// A working news-image-daily entry (Node 22, standard library only): its image is
// the entry.png beside this file, and the program copies it to /output/entry.png.
// The image itself was drawn by generate_frontpage_v9.py (Pillow, from stories_v9.json)
// in the agent session that built this entry: a 1024x1024 newspaper front page
// summing up Wednesday 18 November 2026 — 45 stories, 6 continents, one page.
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync } from 'node:fs';
import { join } from 'node:path';

copyFileSync(new URL('./entry.png', import.meta.url), join(process.env.MAKEFUN_OUTPUT_DIR ?? '/output', 'entry.png'));
