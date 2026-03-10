/** OpenSearch description — 브라우저 주소창 검색 통합 */

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "https://pillright.com";

export function GET() {
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<OpenSearchDescription xmlns="http://a9.com/-/spec/opensearch/1.1/">
  <ShortName>약잘알</ShortName>
  <Description>약/영양제 상호작용 체커 — 약잘알 (PillRight)</Description>
  <InputEncoding>UTF-8</InputEncoding>
  <Url type="text/html" template="${SITE_URL}/check?q={searchTerms}" />
  <Image width="16" height="16" type="image/x-icon">${SITE_URL}/favicon.ico</Image>
</OpenSearchDescription>`;

  return new Response(xml, {
    headers: {
      "Content-Type": "application/opensearchdescription+xml; charset=utf-8",
      "Cache-Control": "public, max-age=86400",
    },
  });
}
