export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  if (req.method === 'OPTIONS') return res.status(200).end();

  const { name, plan } = req.body || {};

  await fetch('https://api.onesignal.com/notifications', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Key os_v2_app_migz42o4jjauhmahkdtuvyy6efgm6ks7oyqukpniigngyun4racnmfcmz33jolppvaplvdrc742oerj6axpyiinjdggjjgou27ckoya'
    },
    body: JSON.stringify({
      app_id: '620d9e69-dc4a-4143-b007-50e74ae31e21',
      included_segments: ['All'],
      headings: { he: 'הרשמה חדשה' },
      contents: { he: `${name} נרשמ/ה למנוי ${plan} — ממתין לאישור תשלום` }
    })
  });

  res.status(200).json({ ok: true });
}
