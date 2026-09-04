/**
 * Vercel Serverless Function: /api/enquiry
 *
 * Secure server-side enquiry handler for IsleConnect diagnostic mapping requests.
 * Features:
 *  - Method validation (POST only)
 *  - Honeypot check (_hp_company) to silently drop bot submissions
 *  - Basic in-memory rate limiting (max 5 requests per 10 mins per IP)
 *  - Input sanitization & field validation
 *  - Upstream forwarding to configured destination (FORMSPREE_ENDPOINT or ENQUIRY_WEBHOOK_URL)
 *  - Zero PII in telemetry logs
 */

const RATE_LIMIT_WINDOW_MS = 10 * 60 * 1000;
const MAX_REQUESTS_PER_WINDOW = 5;
const ipHits = new Map();

function isRateLimited(ip) {
  if (!ip) return false;
  const now = Date.now();
  const history = (ipHits.get(ip) || []).filter(t => now - t < RATE_LIMIT_WINDOW_MS);
  if (history.length >= MAX_REQUESTS_PER_WINDOW) {
    return true;
  }
  history.push(now);
  ipHits.set(ip, history);
  return false;
}

export default async function handler(req, res) {
  // CORS & Security headers
  res.setHeader('Access-Control-Allow-Origin', 'https://www.isleconnect.co.uk');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Accept');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ ok: false, error: 'Method not allowed' });
  }

  const clientIp = req.headers['x-forwarded-for'] || req.socket?.remoteAddress || 'unknown';
  if (isRateLimited(clientIp)) {
    return res.status(429).json({ ok: false, error: 'Too many requests. Please try again later or email directly.' });
  }

  try {
    let body = req.body;
    if (typeof body === 'string') {
      try {
        body = JSON.parse(body);
      } catch (e) {
        // Fallback to URLSearchParams if form-encoded
        const params = new URLSearchParams(body);
        body = Object.fromEntries(params.entries());
      }
    }

    const {
      name,
      email,
      organisation,
      website,
      location,
      notes,
      permission,
      _hp_company
    } = body || {};

    // 1. Honeypot check: bots populate invisible fields; humans do not
    if (_hp_company) {
      // Return 200 to confuse bot without doing work
      return res.status(200).json({ ok: true, message: 'Enquiry received.' });
    }

    // 2. Field validation
    if (!name || typeof name !== 'string' || name.trim().length < 2) {
      return res.status(400).json({ ok: false, error: 'Please provide your name.' });
    }

    if (!email || typeof email !== 'string' || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      return res.status(400).json({ ok: false, error: 'Please provide a valid email address.' });
    }

    if (!organisation || typeof organisation !== 'string' || organisation.trim().length < 2) {
      return res.status(400).json({ ok: false, error: 'Please provide your business or organisation name.' });
    }

    // 3. Forward to upstream destination if configured
    const upstreamUrl = process.env.FORMSPREE_ENDPOINT || process.env.ENQUIRY_WEBHOOK_URL || 'https://formspree.io/f/xvgowwzn';
    
    if (upstreamUrl && upstreamUrl.startsWith('http')) {
      const forwardRes = await fetch(upstreamUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          name: name.trim(),
          email: email.trim(),
          organisation: organisation.trim(),
          website: (website || '').trim(),
          location: (location || '').trim(),
          notes: (notes || '').trim(),
          permission: Boolean(permission),
          submittedAt: new Date().toISOString()
        })
      });

      if (!forwardRes.ok) {
        return res.status(502).json({ ok: false, error: 'Upstream gateway error. Please email directly.' });
      }
    }

    return res.status(200).json({ ok: true, message: 'Enquiry received successfully.' });
  } catch (err) {
    return res.status(500).json({ ok: false, error: 'Server error processing enquiry.' });
  }
}
