// Cloudflare Worker: expande un link corto de Google Maps (goo.gl) a su URL
// completa. Sigue los redirects a mano y PARA en cuanto llega a /maps/, sin
// tocar www.google.com (que a IPs de datacenter le sirve un CAPTCHA /sorry/).
// Devuelve JSON {url: "..."} con CORS.

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
};

const UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36";

function json(obj, status) {
  return new Response(JSON.stringify(obj), {
    status: status || 200,
    headers: { "Access-Control-Allow-Origin": "*", "Content-Type": "application/json" },
  });
}

export default {
  async fetch(request) {
    if (request.method === "OPTIONS") return new Response(null, { headers: CORS });

    const link = new URL(request.url).searchParams.get("url");
    if (!link) return json({ error: "falta el parametro url" }, 400);

    try {
      let current = link;
      let finalUrl = link;
      for (let i = 0; i < 6; i++) {
        const r = await fetch(current, {
          redirect: "manual",
          headers: { "User-Agent": UA },
        });
        const loc = r.headers.get("location");
        if (!loc) break;
        finalUrl = new URL(loc, current).toString();
        // En cuanto tenemos la URL de /maps/ paramos: no seguimos a google.com.
        if (/\/maps\//.test(finalUrl)) break;
        current = finalUrl;
      }
      // Fallback: si acabo en /sorry/ o consent, la URL real esta en ?continue=
      const p = new URL(finalUrl);
      if (p.pathname.startsWith("/sorry") || p.hostname.startsWith("consent.")) {
        const cont = p.searchParams.get("continue");
        if (cont) finalUrl = cont;
      }
      return json({ url: finalUrl });
    } catch (e) {
      return json({ error: String(e) }, 502);
    }
  },
};
