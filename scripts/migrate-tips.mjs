/**
 * tips.ts → content/tips/*.md 마이그레이션 스크립트
 * 실행: node scripts/migrate-tips.mjs
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");

// tips.ts를 읽어서 배열 파싱
const tipsPath = path.join(ROOT, "src/web/src/lib/data/tips.ts");
const tipsSource = fs.readFileSync(tipsPath, "utf-8");

// 각 팁 객체를 추출 (정규식으로 slug, title, description, content, tags 파싱)
const tipRegex = /\{\s*slug:\s*"([^"]+)",\s*title:\s*"([^"]+)",\s*description:\s*\n?\s*"([^"]+)",\s*content:\s*`([\s\S]*?)`,\s*tags:\s*\[([^\]]+)\]/g;

const outDir = path.join(ROOT, "content/tips");
fs.mkdirSync(outDir, { recursive: true });

let count = 0;
let match;
while ((match = tipRegex.exec(tipsSource)) !== null) {
  const [, slug, title, description, content, tagsRaw] = match;
  const tags = tagsRaw
    .split(",")
    .map((t) => t.trim().replace(/^"|"$/g, ""))
    .filter(Boolean);

  const frontmatter = [
    "---",
    `slug: "${slug}"`,
    `title: "${title}"`,
    `description: "${description}"`,
    `tags: [${tags.map((t) => `"${t}"`).join(", ")}]`,
    `category: "general"`,
    `source: "editorial"`,
    `publishedAt: "2026-01-15"`,
    `reviewStatus: "published"`,
    "---",
    "",
  ].join("\n");

  const md = frontmatter + content.trim() + "\n";
  const filePath = path.join(outDir, `${slug}.md`);
  fs.writeFileSync(filePath, md, "utf-8");
  count++;
  console.log(`  ✅ ${slug}.md`);
}

console.log(`\n총 ${count}개 팁 마이그레이션 완료 → ${outDir}`);
