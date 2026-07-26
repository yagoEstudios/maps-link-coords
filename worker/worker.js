// Cloudflare Worker: expande un link corto de Google Maps (goo.gl) a su URL
// completa siguiendo la redireccion. Devuelve JSON {url: "..."} con CORS.
// El navegador lo usa para los links cortos; luego PythonAnywhere saca las coords.

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
};

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
      const r = await fetch(link, {
        redirect: "follow",
        headers: {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
          "Cookie": "SOCS=CAISHAgBEhJnd3NfMjAyMzA4MTAtMF9SQzIaAmVuIAEaBgiA_LyrBg",
        },
      });
      let finalUrl = r.url;
      const parsed = new URL(finalUrl);
      if (parsed.hostname.startsWith("consent.")) {
        const cont = parsed.searchParams.get("continue");
        if (cont) finalUrl = cont;
      }
      return json({ url: finalUrl });
    } catch (e) {
      return json({ error: String(e) }, 502);
    }
  },
};
