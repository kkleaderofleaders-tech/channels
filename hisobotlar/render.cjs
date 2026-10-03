#!/usr/bin/env node
/*
 * Natija maktabi — oylik hisobot PDF generatori.
 *
 *   node hisobotlar/render.cjs <hisobot.json> [chiqish.pdf] [--html]
 *
 * JSON → brendbuk asosidagi HTML (A4) → Playwright/Chromium orqali PDF.
 * JSON formati: hisobotlar/README.md. --html bayrogʻi oraliq HTML faylni ham saqlab qoldiradi.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ROOT = __dirname;
const BRAND = path.join(ROOT, 'brand');
const CSS_PATH = path.join(ROOT, 'shablon', 'hisobot.css');

function loadPlaywright() {
  try { return require('playwright'); } catch (_) { /* global oʻrnatishga qaytamiz */ }
  const globalRoot = execSync('npm root -g').toString().trim();
  return require(path.join(globalRoot, 'playwright'));
}

// Oʻzbek apostrofi: oʻ/gʻ → U+02BB, boshqa harflar orasidagi tutuq belgisi → U+02BC.
function uzApostrophe(s) {
  return String(s)
    .replace(/([OoGg])['`‘’ʼ]/g, '$1ʻ')
    .replace(/([A-Za-zЀ-ӿ])['`’](?=[A-Za-zЀ-ӿ])/g, '$1ʼ');
}

function esc(v) {
  if (v === null || v === undefined) return '';
  return uzApostrophe(v)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

const has = (a) => Array.isArray(a) && a.length > 0;
const fmt = (n, d = 2) => (n === null || n === undefined || n === '' || isNaN(Number(n)) ? '—' : Number(n).toFixed(d).replace(/\.?0+$/, (m) => (m.startsWith('.') ? '' : m)));
const fmtGrade = (n) => (n === null || n === undefined || n === '' ? '—' : Number(n).toFixed(2));

function fileUrl(p) { return 'file://' + p.split(path.sep).map(encodeURIComponent).join('/'); }

function burstSvg() {
  const raw = fs.readFileSync(path.join(BRAND, 'element-chaqnash.svg'), 'utf8');
  const d = raw.match(/\sd="([^"]+)"/)[1];
  return `<svg class="cover__burst" viewBox="0 0 378.75 378.42" aria-hidden="true"><path d="${d}"/></svg>`;
}

function gradeStatus(avg) {
  if (avg === null || avg === undefined) return '';
  if (avg >= 4.5) return '<span class="tag tag--neutral">Aʼlo</span>';
  if (avg >= 3.5) return '<span class="tag tag--neutral">Yaxshi</span>';
  return '<span class="tag tag--brand">Eʼtibor kerak</span>';
}

function delta(cur, prev) {
  if (prev === null || prev === undefined || cur === null || cur === undefined) return '<span class="delta muted">—</span>';
  const d = Number(cur) - Number(prev);
  if (Math.abs(d) < 0.005) return '<span class="delta muted">= 0.00</span>';
  return d > 0
    ? `<span class="delta">▲ ${d.toFixed(2)}</span>`
    : `<span class="delta delta--down">▼ ${Math.abs(d).toFixed(2)}</span>`;
}

function sectionHead(num, title) {
  return `<div class="section__head"><span class="section__num">${String(num).padStart(2, '0')}</span><h2 class="section__title">${esc(title)}</h2></div>`;
}

function render(r) {
  const o = r.oquvchi || {};
  const dv = r.davr || {};
  const stats = (r.korsatkichlar || []).slice(0, 4);
  const sizes = [44, 36, 31, 27]; // mm — pufakchalar turli oʻlchamda
  const tones = ['brand', 'inverse', 'light', 'paper'];
  let n = 0;
  const out = [];

  out.push(`<!doctype html><html lang="uz"><head><meta charset="utf-8">
<title>${esc(`${o.ism || 'Oʻquvchi'} — ${dv.oy || ''} ${dv.yil || ''} oylik hisobot`)}</title>
<link rel="stylesheet" href="${fileUrl(CSS_PATH)}"></head><body>`);

  // Muqova
  out.push(`<header class="cover">
  ${burstSvg()}
  <img class="cover__logo" src="${fileUrl(path.join(BRAND, 'natija-gorizontal-oq.svg'))}" alt="Natija maktabi">
  <div class="cover__text">
    <p class="overline">Oylik hisobot · ${esc(dv.oy)} ${esc(dv.yil)}</p>
    <h1 class="cover__name">${esc(o.ism)}</h1>
    <p class="cover__meta">${esc(o.sinf ? `${o.sinf} sinf` : '')}${o.sinf_rahbari ? ` · Sinf rahbari: ${esc(o.sinf_rahbari)}` : ''}${o.tutor ? ` · Tyutor: ${esc(o.tutor)}` : ''}</p>
    ${r.ota_ona && r.ota_ona.ism ? `<p class="cover__meta" style="font-weight:400">Hurmatli ${esc(r.ota_ona.ism)}!</p>` : ''}
    ${r.namuna ? '<span class="cover__tag">Namuna — haqiqiy maʼlumot emas</span>' : ''}
  </div>
</header>`);

  // Asosiy koʻrsatkichlar
  if (stats.length) {
    out.push('<section class="stats">');
    stats.forEach((s, i) => {
      const size = sizes[i];
      out.push(`<div class="stat stat--${tones[i]}" style="width:${size}mm;height:${size}mm">
  <span class="stat__value" style="font-size:${(size * 0.3).toFixed(1)}mm">${esc(s.qiymat)}</span>
  ${size >= 30 ? `<span class="stat__label">${esc(s.nom)}</span>` : ''}
</div>`);
    });
    out.push('<div class="stats__notes">');
    stats.forEach((s) => out.push(`<p class="stats__note"><b>${esc(s.nom)}:</b> ${esc(s.qiymat)}${s.izoh ? ` — ${esc(s.izoh)}` : ''}</p>`));
    out.push('</div></section>');
  }

  // Umumiy xulosa
  if (r.umumiy_xulosa) {
    out.push(`<section class="section">${sectionHead(++n, 'Umumiy xulosa')}<p class="lead">${esc(r.umumiy_xulosa)}</p></section>`);
  }

  // Fanlar
  if (has(r.fanlar)) {
    const anyClass = r.fanlar.some((f) => f.sinf_ortacha !== undefined && f.sinf_ortacha !== null);
    const anyRank = r.fanlar.some((f) => f.orin != null && f.jami != null);
    out.push(`<section class="section">${sectionHead(++n, 'Fanlar boʻyicha natijalar')}
<table><thead><tr><th>Fan</th><th class="num">Oʻrtacha</th><th style="width:34mm">5 ballik shkala</th><th class="num">Oʻtgan oy</th>${anyClass ? '<th class="num">Sinf</th>' : ''}${anyRank ? '<th class="num">Sinfda oʻrin</th>' : ''}<th class="num">Baholar</th><th>Holat</th></tr></thead><tbody>`);
    for (const f of r.fanlar) {
      const pct = Math.max(0, Math.min(100, (Number(f.ortacha) / 5) * 100));
      const mark = f.sinf_ortacha != null ? `<span class="bar__mark" style="left:calc(${(Number(f.sinf_ortacha) / 5) * 100}% - 1px)"></span>` : '';
      out.push(`<tr>
  <td class="subject">${esc(f.fan)}${f.izoh ? `<span class="row-note">${esc(f.izoh)}</span>` : ''}</td>
  <td class="num"><b>${fmtGrade(f.ortacha)}</b></td>
  <td><div class="bar"><span class="bar__fill" style="width:${pct}%"></span>${mark}</div></td>
  <td class="num">${delta(f.ortacha, f.oldingi_oy)}</td>
  ${anyClass ? `<td class="num muted">${fmtGrade(f.sinf_ortacha)}</td>` : ''}
  ${anyRank ? `<td class="num">${f.orin != null && f.jami != null ? `<b>${esc(f.orin)}</b><span class="muted"> / ${esc(f.jami)}</span>` : '<span class="muted">—</span>'}</td>` : ''}
  <td class="num muted">${esc(f.baholar_soni ?? '—')}</td>
  <td>${gradeStatus(f.ortacha)}</td>
</tr>`);
    }
    out.push(`</tbody></table>
<div class="legend"><span><i class="sw-fill"></i>Farzandingizning oʻrtacha bahosi</span>${anyClass ? '<span><i class="sw-mark"></i>Sinf oʻrtachasi</span>' : ''}<span>Baholar — oy davomida qoʻyilgan baholar soni</span></div>
</section>`);
  }

  // Sinfdagi oʻrin (reyting) — faqat shu oʻquvchining oʻrni, boshqalarning ismi yoʻq
  const rt = r.reyting;
  if (rt && rt.sinf && rt.sinf.orin != null && rt.sinf.jami) {
    const s1 = rt.sinf;
    const dots = Array.from({ length: Math.min(Number(s1.jami), 60) }, (_, i) =>
      `<span class="rank-dot${i + 1 === Number(s1.orin) ? ' rank-dot--me' : ''}"></span>`).join('');
    const prev = s1.oldingi_oy_orin != null
      ? (Number(s1.oldingi_oy_orin) > Number(s1.orin) ? `▲ oʻtgan oy ${esc(s1.oldingi_oy_orin)}-oʻrin`
        : Number(s1.oldingi_oy_orin) < Number(s1.orin) ? `▼ oʻtgan oy ${esc(s1.oldingi_oy_orin)}-oʻrin` : 'oʻtgan oy ham shu oʻrin')
      : '';
    out.push(`<section class="section avoid-break">${sectionHead(++n, 'Sinfdagi oʻrni')}
<div class="rank">
  <div class="rank__main card card--inverse">
    <p class="card__eyebrow">${esc(o.sinf ? `${o.sinf} sinf` : 'Sinf')} · oylik oʻrtacha baho boʻyicha</p>
    <p class="rank__value">${esc(s1.orin)}<span> / ${esc(s1.jami)}</span></p>
    ${s1.guruh ? `<p class="rank__group">${esc(s1.guruh)}</p>` : ''}
    ${prev ? `<p class="small" style="margin-top:6px">${prev}</p>` : ''}
  </div>
  <div class="rank__side">
    <div class="rank-strip" aria-hidden="true">${dots}</div>
    <p class="small muted rank-strip__legend"><span>1-oʻrin</span><span>${esc(s1.jami)}-oʻrin</span></p>
    ${rt.parallel && rt.parallel.orin != null ? `<p class="small" style="margin-top:8px"><b>${esc(rt.parallel.nom || 'Parallel sinflar')}:</b> ${esc(rt.parallel.orin)} / ${esc(rt.parallel.jami)}</p>` : ''}
    ${rt.izoh ? `<p style="margin-top:8px">${esc(rt.izoh)}</p>` : ''}
    ${rt.tavsiya ? `<p class="rank__advice"><b>Tavsiya:</b> ${esc(rt.tavsiya)}</p>` : ''}
  </div>
</div>
<p class="small muted" style="margin-top:6px">Reytingda boshqa oʻquvchilarning ismi va natijasi koʻrsatilmaydi.</p>
</section>`);
  }

  // Davomat + imtihonlar / haftalik ballar
  const d = r.davomat;
  const ex = r.progress_imtihonlar;
  const ws = r.haftalik_ballar;
  if (d || has(ex) || has(ws)) {
    out.push(`<section class="section">${sectionHead(++n, 'Davomat va nazorat')}<div class="grid-2">`);
    if (d) {
      out.push(`<div class="card card--raised"><p class="card__eyebrow">Davomat</p><dl class="kv kv--big">
  ${d.otilgan_darslar != null ? `<dt>Oʻtilgan darslar</dt><dd>${esc(d.otilgan_darslar)}</dd>` : ''}
  <dt>Qoldirilgan darslar</dt><dd>${esc(d.qoldirilgan ?? 0)}</dd>
  <dt>Kechikishlar</dt><dd>${esc(d.kechikkan ?? 0)}</dd>
  ${d.kasal != null ? `<dt>Kasallik sababli</dt><dd>${esc(d.kasal)}</dd>` : ''}
</dl>${d.izoh ? `<p class="small muted" style="margin-top:12px">${esc(d.izoh)}</p>` : ''}</div>`);
    }
    if (has(ex)) {
      out.push(`<div class="card card--outline"><p class="card__eyebrow">Progress imtihonlar</p><dl class="kv">
${ex.map((e) => `<dt>${esc(e.fan)}${e.sana ? ` <span class="small">· ${esc(e.sana)}</span>` : ''}${e.turi ? `<span class="row-note">${esc(e.turi)}</span>` : ''}</dt><dd>${esc(e.natija)}${e.maksimal != null ? ` / ${esc(e.maksimal)}` : ''}</dd>`).join('\n')}
</dl></div>`);
    } else if (has(ws)) {
      out.push(`<div class="card card--outline"><p class="card__eyebrow">Haftalik ballar (oʻrtacha)</p><dl class="kv">
${ws.map((w) => `<dt>${esc(w.nom)}</dt><dd>${esc(w.qiymat)}</dd>`).join('\n')}
</dl></div>`);
    }
    out.push('</div>');
    if (has(ex) && has(ws)) {
      out.push(`<div class="card card--outline" style="margin-top:16px"><p class="card__eyebrow">Haftalik ballar (oʻrtacha)</p><dl class="kv">
${ws.map((w) => `<dt>${esc(w.nom)}</dt><dd>${esc(w.qiymat)}</dd>`).join('\n')}</dl></div>`);
    }
    out.push('</section>');
  }

  // Salomatlik (maktab tibbiyot xonasi maʼlumotlari)
  const h = r.salomatlik;
  if (h) {
    const m = h.olchov || {};
    const rows = [];
    if (m.boy_sm != null) rows.push(['Boʻyi', `${esc(m.boy_sm)} sm`]);
    if (m.vazn_kg != null) rows.push(['Vazni', `${esc(m.vazn_kg)} kg`]);
    if (m.bmi != null) rows.push(['Tana massasi indeksi', esc(m.bmi)]);
    if (h.tibbiy_xona_tashriflari != null) rows.push(['Tibbiyot xonasiga murojaat (oy)', esc(h.tibbiy_xona_tashriflari)]);
    if (h.kasallik_varaqalari != null) rows.push(['Kasallik varaqalari (oy)', esc(h.kasallik_varaqalari)]);
    out.push(`<section class="section avoid-break">${sectionHead(++n, 'Salomatlik')}<div class="grid-2">
<div class="card card--raised"><p class="card__eyebrow">Koʻrsatkichlar${m.sana ? ` · oʻlchov ${esc(m.sana)}` : ''}</p>
<dl class="kv">${rows.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join('')}</dl></div>
<div class="card card--outline"><p class="card__eyebrow">${has(h.korik) ? 'Mutaxassislar koʻrigi' : 'Izoh'}</p>
${has(h.korik) ? `<ul class="list">${h.korik.map((k) => `<li><b>${esc(k.mutaxassis)}</b>${k.sana ? ` <span class="small muted">· ${esc(k.sana)}</span>` : ''}<span class="detail">${esc(k.xulosa)}</span></li>`).join('')}</ul>` : ''}
${h.izoh ? `<p${has(h.korik) ? ' style="margin-top:10px"' : ''}>${esc(h.izoh)}</p>` : ''}
${h.tavsiya ? `<p class="rank__advice"><b>Tavsiya:</b> ${esc(h.tavsiya)}</p>` : ''}
</div></div></section>`);
  }

  // Kuchli tomonlar va kamchiliklar
  const item = (x) => (typeof x === 'string'
    ? `<li>${esc(x)}</li>`
    : `<li><b>${esc(x.sarlavha)}</b>${x.tafsilot ? `<span class="detail">${esc(x.tafsilot)}</span>` : ''}</li>`);
  if (has(r.kuchli_tomonlar) || has(r.kamchiliklar)) {
    out.push(`<section class="section">${sectionHead(++n, 'Yutuqlar va eʼtibor talab qiladigan jihatlar')}<div class="grid-2">`);
    if (has(r.kuchli_tomonlar)) out.push(`<div class="card card--raised"><p class="card__eyebrow">Kuchli tomonlar</p><ul class="list">${r.kuchli_tomonlar.map(item).join('')}</ul></div>`);
    if (has(r.kamchiliklar)) out.push(`<div class="card card--outline"><p class="card__eyebrow">Eʼtibor kerak</p><ul class="list">${r.kamchiliklar.map(item).join('')}</ul></div>`);
    out.push('</div></section>');
  }

  // Qobiliyatlar va kelajak — motivatsion boʻlim
  const qb = r.qobiliyatlar;
  if (qb && has(qb.royxat)) {
    const cols = Math.min(qb.royxat.length, 3);
    out.push(`<section class="section">${sectionHead(++n, 'Qobiliyatlar va kelajak')}
${qb.kirish ? `<p class="lead" style="margin-bottom:12px">${esc(qb.kirish)}</p>` : ''}
<div class="abilities" style="grid-template-columns:repeat(${cols},1fr)">
${qb.royxat.map((a) => `<div class="card card--raised ability">
  ${a.kuch ? `<p class="card__eyebrow">${esc(a.kuch)}</p>` : ''}
  <h3 class="card__title">${esc(a.qobiliyat)}</h3>
  ${a.asos ? `<p class="small muted ability__basis">Asos: ${esc(a.asos)}</p>` : ''}
  <p class="ability__contribution">${esc(a.hissa)}</p>
</div>`).join('\n')}
</div>
${qb.xulosa ? `<p class="ability__closing">${esc(qb.xulosa)}</p>` : ''}
</section>`);
  }

  // Tavsiyalar
  if (has(r.tavsiyalar)) {
    const groups = new Map();
    for (const t of r.tavsiyalar) {
      const who = (typeof t === 'string' ? 'Ota-onaga' : t.kimga) || 'Ota-onaga';
      if (!groups.has(who)) groups.set(who, []);
      groups.get(who).push(typeof t === 'string' ? t : t.matn);
    }
    out.push(`<section class="section">${sectionHead(++n, 'Tavsiyalar')}<div class="recs">`);
    for (const [who, items] of groups) {
      out.push(`<div class="rec-group"><p class="rec-group__who"><span>Tavsiya</span>${esc(who)}</p><ol>${items.map((m) => `<li>${esc(m)}</li>`).join('')}</ol></div>`);
    }
    out.push('</div></section>');
  }

  // Keyingi oy maqsadlari
  if (has(r.keyingi_oy_maqsadlari)) {
    out.push(`<section class="section avoid-break"><div class="card card--brand goals"><p class="card__eyebrow">Keyingi oy uchun</p><h3 class="card__title">Birgalikdagi maqsadlarimiz</h3><ol>${r.keyingi_oy_maqsadlari.map((m) => `<li>${esc(m)}</li>`).join('')}</ol></div></section>`);
  }

  // Qoʻshimcha boʻlimlar (boshqa manbalardan)
  if (has(r.qoshimcha)) {
    for (const q of r.qoshimcha) {
      out.push(`<section class="section">${sectionHead(++n, q.sarlavha)}<p>${esc(q.matn)}</p></section>`);
    }
  }

  // Imzo, manbalar, yakun
  const im = r.imzo || {};
  out.push(`<div class="signoff">
  <div><div class="sign__line"></div><p class="sign__who"><b>${esc(im.sinf_rahbari || o.sinf_rahbari || '')}</b>Sinf rahbari</p></div>
  <div><div class="sign__line"></div><p class="sign__who"><b>${esc(im.direktor_orinbosari) || '&nbsp;'}</b>Oʻquv ishlari boʻyicha direktor oʻrinbosari</p></div>
  <div><div class="sign__line"></div><p class="sign__who"><b>${esc(im.sana || '')}</b>Sana</p></div>
</div>`);
  if (has(r.manbalar)) {
    out.push(`<div class="sources"><b>Maʼlumot manbalari.</b> ${r.manbalar.map(esc).join(' · ')}</div>`);
  }
  out.push(`<div class="closing"><img class="closing__logo" src="${fileUrl(path.join(BRAND, 'natija-bir-qatorli.svg'))}" alt="Natija maktabi"><span class="closing__motto">Ichki kuchdan aniq natijagacha.</span></div>`);
  out.push('</body></html>');
  return out.join('\n');
}

async function main() {
  const args = process.argv.slice(2);
  const keepHtml = args.includes('--html');
  const pos = args.filter((a) => !a.startsWith('--'));
  if (!pos[0]) {
    console.error('Foydalanish: node hisobotlar/render.cjs <hisobot.json> [chiqish.pdf] [--html]');
    process.exit(2);
  }
  const input = path.resolve(pos[0]);
  const data = JSON.parse(fs.readFileSync(input, 'utf8'));
  const outPdf = path.resolve(pos[1] || input.replace(/\.json$/i, '') + '.pdf');
  const htmlPath = outPdf.replace(/\.pdf$/i, '') + '.html';
  fs.mkdirSync(path.dirname(outPdf), { recursive: true });
  fs.writeFileSync(htmlPath, render(data));

  const { chromium } = loadPlaywright();
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    await page.goto(fileUrl(htmlPath), { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    const school = 'Natija maktabi · Oylik hisobot';
    await page.pdf({
      path: outPdf,
      format: 'A4',
      printBackground: true,
      preferCSSPageSize: true,
      displayHeaderFooter: true,
      headerTemplate: '<span></span>',
      footerTemplate: `<div style="width:100%;padding:0 14mm;font-family:Geist,Inter,sans-serif;font-size:7px;color:#5a5a5a;display:flex;justify-content:space-between"><span>${school}</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`,
    });
  } finally {
    await browser.close();
  }
  if (!keepHtml) fs.unlinkSync(htmlPath);
  console.log(outPdf);
}

if (require.main === module) {
  main().catch((e) => { console.error(e); process.exit(1); });
}

module.exports = { render, uzApostrophe };
