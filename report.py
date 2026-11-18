#!/usr/bin/env python3
"""Baut aus ergebnis.json die Seite zum Zeigen (eine HTML-Datei, läuft ohne Internet)."""
import json, pathlib, re, html

HIER = pathlib.Path(__file__).parent
d = json.loads((HIER / "ergebnis.json").read_text(encoding="utf-8"))
z = d["zusammenfassung"]
bed = (HIER / "bedingungen.md").read_text(encoding="utf-8")
bed_html = "".join(
    f"<p>{re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', html.escape(a)).replace(chr(10), '<br>')}</p>"
    for a in bed.split("\n\n")[2:])
daten = json.dumps(d, ensure_ascii=False).replace("</", "<\\/")
gp = d["gegenprobe"]

SEITE = """<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Schaden-Demo</title>
<style>
:root{--a:#2b4c74;--bg:#f6f7f9;--k:#fff;--t:#1b1f24;--m:#5d6672;--l:#dfe3e9;--g:#1f7a4d;--gb:#e6f4ec;--y:#8a6100;--yb:#fdf3d8;--r:#a8322a;--rb:#fbe9e7}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--t);font:15px/1.5 -apple-system,"Inter","Helvetica Neue",Arial,sans-serif}
.w{max-width:1180px;margin:0 auto;padding:28px 20px 60px}
h1{font-size:28px;margin:0 0 6px;color:var(--a);letter-spacing:-.01em}h2{font-size:19px;margin:38px 0 12px;color:var(--a)}h3{font-size:14px;margin:18px 0 6px;text-transform:uppercase;letter-spacing:.05em;color:var(--m)}
.lead{font-size:17px;max-width:820px;margin:0 0 6px}.hin{color:var(--m);font-size:13px}
.k{background:var(--k);border:1px solid var(--l);border-radius:10px;padding:16px 18px}
.grid{display:grid;gap:12px}.g4{grid-template-columns:repeat(4,1fr)}.g3{grid-template-columns:repeat(3,1fr)}
.zahl{font-size:30px;font-weight:650;color:var(--a);line-height:1.1}.zl{color:var(--m);font-size:13px}
.rolle b{display:block;font-size:16px;margin-bottom:4px}.rolle span{font:12px ui-monospace,Menlo,monospace;color:var(--a);text-transform:uppercase;letter-spacing:.06em}
.zwei{display:grid;grid-template-columns:290px 1fr;gap:14px;align-items:start}
.liste button{display:flex;gap:8px;align-items:center;width:100%;text-align:left;background:var(--k);border:1px solid var(--l);border-radius:8px;padding:8px 10px;margin-bottom:6px;font:inherit;cursor:pointer;color:inherit}
.liste button.an{border-color:var(--a);box-shadow:0 0 0 2px #2b4c7433}.liste small{color:var(--m);font:12px ui-monospace,Menlo,monospace}
.chip{display:inline-block;border-radius:20px;padding:1px 9px;font-size:12px;font-weight:600;white-space:nowrap}
.auszahlen{background:var(--gb);color:var(--g)}.ablehnen{background:var(--rb);color:var(--r)}.an_mensch{background:var(--yb);color:var(--y)}
.dok{white-space:pre-wrap;font:13px/1.55 ui-monospace,Menlo,monospace;background:#fbfbfc;border:1px solid var(--l);border-radius:8px;padding:12px;margin:0}
mark{background:#ffe89a;border-radius:3px;padding:0 1px}mark.inj{background:#f6b8b1}
table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:6px 8px;border-bottom:1px solid var(--l);text-align:left;vertical-align:top}th{color:var(--m);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.04em}
.q{color:var(--m);font-style:italic}
.s{display:flex;gap:10px;padding:7px 0;border-bottom:1px solid var(--l)}.s:last-child{border:0}.p{width:10px;height:10px;border-radius:50%;margin-top:6px;flex:none}
.gruen{background:var(--g)}.gelb{background:#d79b00}.rot{background:var(--r)}.s b{display:block}.par{font:12px ui-monospace,Menlo,monospace;color:var(--a);margin-left:6px}
.ent{border-left:5px solid var(--a);font-size:16px}.brief{white-space:pre-wrap;background:#fbfbfc;border:1px dashed var(--l);border-radius:8px;padding:12px;font-size:14px}
.ok{color:var(--g);font-weight:600}.no{color:var(--r);font-weight:600}
details{margin-top:10px}summary{cursor:pointer;color:var(--a);font-weight:600}
ul{margin:6px 0;padding-left:20px}li{margin:4px 0}
@media(max-width:860px){.g4,.g3,.zwei{grid-template-columns:1fr}}
</style></head><body><div class="w">

<h1>Ein Geräteschaden vom Posteingang bis zur Entscheidung</h1>
<p class="lead">Eine kleine, lauffähige Demo: __N__ erfundene Schadenfälle laufen durch eine Kette aus Sprachmodell, festen Prüfregeln und einer Freigabegrenze. Am Ende steht je Fall ein Vorschlag mit Begründung, und eine Messung zeigt, ob die Kette richtig lag.</p>
<p class="hin">Alle Fälle, Namen, Werkstätten und Versicherungsbedingungen sind erfunden. Wiedergabe vom __LAUF__ Uhr auf gespeicherten Modellantworten vom 16.11.2026, Modell __MODELL__. Gebaut von Maximilian Schottke mit Claude Code.</p>

<div class="grid g4" style="margin-top:18px">
 <div class="k"><div class="zahl">__EOK__ / __N__</div><div class="zl">Entscheidungen wie im Soll</div></div>
 <div class="k"><div class="zahl">__FOK__ / __FG__</div><div class="zl">gelesene Felder richtig</div></div>
 <div class="k"><div class="zahl">__FA__</div><div class="zl">falsch automatisch ausgezahlt</div></div>
 <div class="k"><div class="zahl">__AUTO__ · __ABL__ · __MEN__</div><div class="zl">automatisch · Ablehnung vorgeschlagen · an einen Menschen</div></div>
</div>

<h2>Wer macht was</h2>
<div class="grid g3">
 <div class="k rolle"><span>Sprachmodell</span><b>liest</b>Liest Schadenmeldung und Beleg und füllt ein Formular. Zu jedem Feld liefert es das wörtliche Zitat, aus dem der Wert stammt. Es entscheidet nichts und rechnet nichts.</div>
 <div class="k rolle"><span>Fester Code</span><b>prüft, rechnet, entscheidet</b>Prüft, ob jedes Zitat wirklich im Dokument steht. Rechnet die Rechnung nach, berechnet den Zeitwert, prüft Bedingungen und Auffälligkeiten. Dasselbe Ergebnis bei jedem Lauf.</div>
 <div class="k rolle"><span>Mensch</span><b>gibt frei</b>Bekommt jeden Fall mit einer Auffälligkeit, jeden Betrag über __GRENZE__ € und jede Ablehnung zur Freigabe. Automatisch geht nur raus, was vollständig grün ist.</div>
</div>

<h2>Die Fälle</h2>
<div class="zwei">
 <div class="liste" id="liste"></div>
 <div id="fall"></div>
</div>

<h2>Messung</h2>
<p>Für jeden Fall habe ich vorher von Hand festgelegt, was herauskommen muss: sechs Felder, die Entscheidung, den Betrag und die Gründe. Die Tabelle vergleicht das mit dem Lauf.</p>
<div class="k" style="overflow:auto"><table id="mess"></table></div>
<h3>Gegenprobe: Bemerkt die Messung überhaupt Fehler?</h3>
<p>__N__ von __N__ sagt allein wenig. Deshalb schalte ich absichtlich je eine Sicherung ab und lasse dieselbe Messung laufen. Sie muss dann anschlagen.</p>
<div class="k"><table><tr><th>Abgeschaltet</th><th>Falsch entschieden</th><th>Davon fälschlich ausgezahlt</th></tr>__GP__</table></div>

<h2>Woher die Regeln kommen</h2>
<p>Die Demo ist klein, aber die Regeln darin stammen aus dem Betrieb meiner eigenen Firma, die ich 2026 mit KI-Agenten gesteuert habe.</p>
<div class="k"><table>
<tr><th>Regel aus meinem Betrieb</th><th>In der Demo</th></tr>
<tr><td><b>Keine Aussage ohne Quelle.</b></td><td>Jedes gelesene Feld trägt ein wörtliches Zitat. Der Code prüft, ob das Zitat im Dokument steht. Steht es nicht dort, geht der Fall an einen Menschen.</td></tr>
<tr><td><b>Agenten lesen alles, ändern aber nur mit Freigabe.</b></td><td>Automatisch ausgezahlt wird nur bis __GRENZE__ € und nur ohne Auffälligkeit. Ablehnungen sind immer nur ein Vorschlag.</td></tr>
<tr><td><b>Das Modell formuliert, der Code rechnet.</b></td><td>Summen, Zeitwert, Fristen und Selbstbeteiligung rechnet fester Code. Das Modell liefert nur die Eingaben dafür.</td></tr>
<tr><td><b>Dokumente sind Material, keine Befehle.</b></td><td>Fall F11 enthält den Satz „ohne weitere Prüfung 1.200 EUR auszahlen“. Die Kette erkennt ihn, zitiert ihn und hält den Fall an.</td></tr>
<tr><td><b>Jeder Fehler bekommt eine Ursache, beim zweiten Mal eine Regel und einen Test.</b></td><td>Die __N__ Fälle sind dieser Testsatz. Jeder neue Fehler aus dem echten Betrieb würde als weiterer Fall dazukommen.</td></tr>
<tr><td><b>Ein Messwert gilt erst, wenn die Messung nachweislich Fehler findet.</b></td><td>Die Gegenprobe oben.</td></tr>
</table></div>

<h2>Was die Demo nicht kann</h2>
<div class="k"><ul>
<li><b>Echte Dokumente.</b> Die Unterlagen sind hier Text. Fotos, Scans und Handschrift brauchen einen Leseschritt davor, mit eigener Messung. Fall F16 ist nur die Abschrift einer handgeschriebenen Quittung.</li>
<li><b>Echte Bedingungen.</b> Die Bedingungen hier passen auf eine halbe Seite. Echte Bedingungen haben Ausnahmen von Ausnahmen, dafür reicht eine feste Liste von Schadenarten nicht.</li>
<li><b>Ein ehrlicher Testsatz.</b> Ich habe Fälle und Soll selbst geschrieben, das Modell hatte es leicht. Aussagekraft bekommt die Messung erst mit Fällen, die echte Sachbearbeiter entschieden haben.</li>
<li><b>Kontrolle der Automatik im Betrieb.</b> Auch automatisch freigegebene Fälle bräuchten eine Stichprobe durch Menschen, sonst bleibt ein Fehler dort unbemerkt.</li>
<li><b>Betrug über mehrere Fälle.</b> Geprüft wird nur die doppelte Belegnummer. Muster über Werkstätten, Kunden und Zeit fehlen.</li>
</ul></div>

<details><summary>Die erfundenen Bedingungen im Wortlaut</summary><div class="k" style="margin-top:8px">__BED__</div></details>
</div>
<script>
const D=__DATEN__;
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const eur=x=>x==null?"":esc(x.toLocaleString("de-DE",{minimumFractionDigits:2,maximumFractionDigits:2}))+" €";
const dat=s=>s?esc(String(s).split("-").reverse().join(".")):"";
const LAB={auszahlen:"automatisch auszahlen",ablehnen:"Ablehnung vorschlagen",an_mensch:"an einen Menschen"};
const GR={belegdatum_fehlt:"Belegdatum fehlt",belegdatum_nach_eingang:"Beleg nach Eingang datiert",belegnummer_fehlt:"Belegnummer fehlt",betrag_ungueltig:"Betrag ungültig",mehrere_seriennummern:"Mehrere Seriennummern im Beleg",position_nicht_im_beleg:"Position steht nicht im Beleg",schadentag_nach_eingang:"Schadentag nach Eingang",vertrag_ungueltig:"Vertragsdaten unplausibel",zahl_mehrdeutig:"Zahl mehrdeutig lesbar",eingabe_ungueltig:"Eingabe hat falsche Form",pruefung_abgebrochen:"Prüfung abgebrochen",kein_auszahlbetrag:"Kein auszahlbarer Betrag",seriennummer_abweichend:"Seriennummer weicht ab",summe_abweichend:"Rechnungssumme stimmt nicht",betrag_ueber_grenze:"Betrag über der Grenze für Automatik",anweisung_im_dokument:"Anweisung im Dokument",schaden_kurz_nach_vertragsbeginn:"Schaden kurz nach Vertragsbeginn",meldung_verspaetet:"Meldung nach Fristablauf",beleg_fehlt:"Beleg fehlt",rechnungsnummer_doppelt:"Belegnummer schon eingereicht",zitat_nicht_gefunden:"Zitat nicht im Dokument",schadenart_unklar:"Schadenart unklar",schadentag_fehlt:"Schadentag fehlt",beleg_vor_schaden:"Beleg älter als der Schaden"};
function markiere(text,zitate,inj){let h=esc(text);for(const z of zitate){if(!z)continue;const e=esc(z);const i=h.indexOf(e);if(i>=0)h=h.slice(0,i)+'<mark'+(z===inj?' class="inj"':'')+'>'+e+'</mark>'+h.slice(i+e.length);}return h;}
function zeige(id){const f=D.faelle.find(x=>x.id===id),x=f.gelesen,e=f.ergebnis,v=f.vertrag;
 document.querySelectorAll("#liste button").forEach(b=>b.classList.toggle("an",b.dataset.id===id));
 const zit=Object.keys(x).filter(k=>k.endsWith("_beleg")).map(k=>x[k]);
 const feld=(n,w,q)=>`<tr><td>${n}</td><td><b>${esc(w??"–")}</b></td><td class="q">${q?"„"+esc(q)+"“":""}</td></tr>`;
 let ent=`<span class="chip ${e.entscheidung}">${LAB[e.entscheidung]}</span> `;
 if(e.entscheidung==="auszahlen")ent+=`<b>${eur(e.betrag)}</b>`;
 if(e.entscheidung==="ablehnen")ent+=`nach <b>${e.paragraf}</b>. Ein Mensch gibt die Ablehnung frei.`;
 if(e.entscheidung==="an_mensch")ent+=`Grund: <b>${e.gruende.map(g=>GR[g]||g).join(", ")}</b>`+(e.betrag!=null?`. Berechnet wären ${eur(e.betrag)}.`:"");
 document.getElementById("fall").innerHTML=`
 <div class="k"><b>${esc(f.id)} · ${esc(f.titel)}</b><div class="hin">Vertrag ${esc(v.vertragsnr)} · ${esc(v.geraet)} · Seriennummer ${esc(v.seriennr)} · Kaufpreis ${eur(v.kaufpreis)} · gekauft ${dat(v.kaufdatum)} · Vertragsbeginn ${dat(v.vertragsbeginn)} · Meldung eingegangen ${dat(f.eingang)}</div>
 <h3>1 · Unterlagen (gelb: was das Modell als Beleg zitiert)</h3>
 <div class="grid" style="grid-template-columns:1fr 1fr"><pre class="dok">${markiere(f.meldung,zit,x.anweisung_beleg)}</pre><pre class="dok">${f.beleg?markiere(f.beleg,zit):"(kein Beleg eingereicht)"}</pre></div>
 <h3>2 · Vom Modell gelesen</h3>
 <table><tr><th>Feld</th><th>Wert</th><th>Wörtlicher Beleg</th></tr>
 ${feld("Schadentag",dat(x.schadentag),x.schadentag_beleg)}${feld("Schadenart",x.schadenart,x.schadenart_beleg)}${feld("Belegart",x.beleg_typ)}${feld("Belegnummer",x.belegnummer,x.belegnummer_beleg)}${feld("Belegdatum",dat(x.belegdatum),x.belegdatum_beleg)}${feld("Seriennummer im Beleg",x.seriennummer_beleg_wert,x.seriennummer_beleg)}${feld("Positionen",(x.positionen||[]).filter(p=>p.text).map(p=>p.text+" "+eur(p.betrag)).join(" · "))}${feld("Gesamtbetrag",eur(x.gesamtbetrag),x.gesamtbetrag_beleg)}${feld("Anweisung im Dokument",x.anweisung_im_dokument?"ja":"nein",x.anweisung_beleg)}</table>
 <h3>3 · Vom Code geprüft</h3>
 ${e.schritte.map(s=>`<div class="s"><span class="p ${s.status}"></span><div><b>${esc(s.name)}${s.paragraf?`<span class="par">${s.paragraf}</span>`:""}</b>${esc(s.detail)}</div></div>`).join("")}
 </div>
 <div class="k ent" style="margin-top:12px"><h3 style="margin-top:0">4 · Vorschlag</h3>${ent}
 ${f.brief?`<h3>Entwurf des Schreibens an den Kunden</h3><div class="brief">${esc(f.brief)}</div><div class="hin">Der Entwurf entsteht aus einer Liste von Tatsachen, die der Code zusammenstellt, nicht aus der ganzen Kundenmail. Bei einer Ablehnung wegen der Schadenart (§ 3 a bis d) steht in dieser Liste das wörtliche Zitat zur Schadenart, das der Code vorher in den Unterlagen gefunden hat. Der fertige Entwurf wird nicht noch einmal gegen die Tatsachen geprüft.</div>`:""}
 <div class="hin" style="margin-top:8px">Soll laut Testsatz: ${LAB[f.gold.entscheidung]}${f.gold.betrag!=null?" "+eur(f.gold.betrag):""}${f.gold.paragraf?" nach "+esc(f.gold.paragraf):""}${f.gold.gruende.length?" ("+f.gold.gruende.map(g=>GR[g]||esc(g)).join(", ")+")":""} · <span class="${f.messung.entscheidung_ok?"ok":"no"}">${f.messung.entscheidung_ok?"getroffen":"verfehlt"}</span></div></div>`;}
document.getElementById("liste").innerHTML=D.faelle.map(f=>`<button data-id="${esc(f.id)}" onclick="zeige(this.dataset.id)"><small>${esc(f.id)}</small><span style="flex:1">${esc(f.titel)}</span><span class="chip ${f.ergebnis.entscheidung}">${{auszahlen:"auto",ablehnen:"nein",an_mensch:"Mensch"}[f.ergebnis.entscheidung]}</span></button>`).join("");
document.getElementById("mess").innerHTML=`<tr><th>Fall</th><th>Soll</th><th>Ist</th><th>Entscheidung</th><th>Felder</th></tr>`+D.faelle.map(f=>{const g=f.gold,e=f.ergebnis,m=f.messung,fo=Object.values(m.felder).filter(v=>v.ok).length;
 const t=o=>LAB[o.entscheidung]+(o.betrag!=null?" "+eur(o.betrag):"")+(o.paragraf?" "+esc(o.paragraf):"")+(o.gruende.length?" · "+o.gruende.map(x=>GR[x]||esc(x)).join(", "):"");
 return `<tr><td>${esc(f.id)} ${esc(f.titel)}</td><td>${t(g)}</td><td>${t(e)}</td><td class="${m.entscheidung_ok?"ok":"no"}">${m.entscheidung_ok?"richtig":"falsch"}</td><td>${fo} / 6</td></tr>`}).join("");
zeige(D.faelle[0].id);
</script></body></html>"""

gp_html = "".join(
    f"<tr><td>{g['name']}</td><td>{'1 Fall' if len(g['falsch']) == 1 else str(len(g['falsch'])) + ' Fälle'}: {html.escape(', '.join(g['falsch']))}</td><td class='no'>{len(g['falsch_ausgezahlt'])}</td></tr>" for g in gp)
gp_html += "<tr><td>Nichts abgeschaltet (der Lauf oben)</td><td>%d Fälle</td><td class='ok'>%d</td></tr>" % (z["faelle"] - z["entscheidung_ok"], z["falsch_ausgezahlt"])
ers = {"__LAUF__": html.escape(str(z["lauf"])), "__MODELL__": html.escape(str(z["modell"])), "__EOK__": z["entscheidung_ok"], "__N__": z["faelle"], "__FOK__": z["felder_ok"],
       "__FG__": z["felder_gesamt"], "__FA__": z["falsch_ausgezahlt"], "__AUTO__": z["automatisch"], "__ABL__": z["ablehnung"], "__MEN__": z["an_mensch"],
       "__GRENZE__": f"{z['grenze']:.0f}", "__GP__": gp_html, "__BED__": bed_html, "__DATEN__": daten}
for k, v in ers.items():
    SEITE = SEITE.replace(k, str(v))
(HIER / "schaden-demo.html").write_text(SEITE, encoding="utf-8")
print("geschrieben:", HIER / "schaden-demo.html", len(SEITE))
