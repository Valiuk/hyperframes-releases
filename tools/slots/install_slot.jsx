/*
  install_slot.jsx — встановлює один слот (скін) у шаблон Hyperframes «Phone Slot Spin».
  Hyperframes · https://github.com/Valiuk/hyperframes-releases

  Як користуватися:
    1. Відкрий у After Effects шаблон Phone Slot Spin (або «легку» копію, зроблену export_variation.jsx).
    2. File › Scripts › Run Script File… → цей файл (він має лежати поруч із slot.json і папками symbols, FrameGrids).
    3. Вкажи розмір символів і натисни «Встановити». Слот отримає наступний вільний номер на слайдері Slot.

  Що робить:
    • символ N.png → pragmatic_symbol_N, а Symbol_N завжди бере pragmatic_symbol_N — номери збігаються з сайтом
      і з «Конструктором прокрутів»; якщо в шаблоні символів більше, ніж у слота, вони повторюються по колу;
    • фон → pragmatic_BG, лого → pragmatic_Logo;
    • рамки під усі 25 сіток (3…7 барабанів × 3…7 рядів) → Frame_grid, і 5×3 у Frame;
    • у компах, яких слот не має (тексти, баланс тощо), ставить копію скіна 1 з помаранчевою міткою.
  Повторний запуск безпечний: оновлює слот, а не дублює. Усе — один крок Undo (Ctrl+Z).
*/
(function () {
    var REF_SLOT = 1;
    var proj = app.project;
    if (!proj) { alert("Спершу відкрий шаблон Phone Slot Spin."); return; }

    // ---------------- дані слота ----------------
    var base = File($.fileName).parent;
    var mf = File(base.fsName + "/slot.json");
    if (!mf.exists) {
        var fo = Folder.selectDialog("Вибери папку слота (де лежить slot.json)"); if (!fo) return;
        base = fo; mf = File(base.fsName + "/slot.json");
        if (!mf.exists) { alert("У цій папці немає slot.json."); return; }
    }
    mf.encoding = "UTF-8"; mf.open("r"); var txt = mf.read(); mf.close();
    var S; try { S = eval("(" + txt + ")"); } catch (e) { alert("Не вдалося прочитати slot.json: " + e); return; }

    // ---------------- утиліти ----------------
    function compAny(n) { for (var i = 1; i <= proj.numItems; i++) if (proj.item(i) instanceof CompItem && proj.item(i).name === n) return proj.item(i); return null; }
    function allComps() { var a = []; for (var i = 1; i <= proj.numItems; i++) if (proj.item(i) instanceof CompItem) a.push(proj.item(i)); return a; }
    function tr(l) { return l.property("ADBE Transform Group"); }
    function opac(l) { return tr(l).property("ADBE Opacity"); }
    var RX_MY = new RegExp("myLayerIndex\\s*=\\s*(\\d+)"), RX_EQ = new RegExp("===\\s*(\\d+)");
    function slotOf(L) {
        var ex = opac(L).expression;
        if (!ex || ex.indexOf('effect("Slot")') === -1) return 0;
        if (ex.indexOf("thisLayer.index") !== -1) return L.index;
        var m = ex.match(RX_MY) || ex.match(RX_EQ);
        return m ? parseInt(m[1], 10) : 0;
    }
    function isIndexSwitch(L) { var ex = opac(L).expression; return ex && ex.indexOf('effect("Slot")') !== -1 && ex.indexOf("thisLayer.index") !== -1; }
    function guideBox(comp) {
        var xs = [], ys = [];
        try { var g = comp.guides; for (var i = 0; i < g.length; i++) (g[i].orientationType === 0 ? ys : xs).push(g[i].position); } catch (e) {}
        function span(a) { if (a.length < 2) return null; var mn = a[0], mx = a[0]; for (var k = 1; k < a.length; k++) { if (a[k] < mn) mn = a[k]; if (a[k] > mx) mx = a[k]; } return [mn, mx]; }
        var sx = span(xs), sy = span(ys);
        if (!sx || !sy || sx[1] - sx[0] > comp.width * 0.9 || sy[1] - sy[0] > comp.height * 0.9) return { x1: 100, x2: 412, y1: 100, y2: 412 };
        return { x1: sx[0], x2: sx[1], y1: sy[0], y2: sy[1] };
    }
    function fit(L, comp, mode, bx, mult) {
        var w = L.source.width, h = L.source.height;
        bx = bx || [0, 0, w, h];
        var b = mode === "guides" ? guideBox(comp) : { x1: 0, x2: comp.width, y1: 0, y2: comp.height };
        var sx = (b.x2 - b.x1) / bx[2], sy = (b.y2 - b.y1) / bx[3];
        var s = (mode === "cover" ? Math.max(sx, sy) : Math.min(sx, sy)) * 100 * (mult || 1);
        var ap = [bx[0] + bx[2] / 2, bx[1] + bx[3] / 2], pos = [(b.x1 + b.x2) / 2, (b.y1 + b.y2) / 2], sc = [s, s];
        if (L.threeDLayer) { ap.push(0); pos.push(0); sc.push(100); }
        tr(L).property("ADBE Anchor Point").setValue(ap);
        tr(L).property("ADBE Scale").setValue(sc);
        tr(L).property("ADBE Position").setValue(pos);
    }
    function placeFrame(L, r) {           // r = [x, y, w, h, pngW, pngH] у координатах рамки 1331 × 1331
        var off = Math.max(0, (L.containingComp.width - 1331) / 2), k = r[2] / r[4] * 100;
        tr(L).property("ADBE Scale").setValue([k, k]);
        tr(L).property("ADBE Position").setValue([r[0] + r[2] / 2 + off, r[1] + r[3] / 2 + off]);
    }
    var HEAD7 = 'var ctl = comp("render").layer(1);\n' +
        'var C = Math.min(7, Math.max(3, Math.round(ctl.effect("Reels")("Slider"))));\n' +
        'var R = Math.min(7, Math.max(3, Math.round(ctl.effect("Rows")("Slider"))));\n';

    // ---------------- перевірка шаблону ----------------
    var switchers = [], maxSlot = 0, mySlot = 0;
    var comps = allComps();
    for (var c = 0; c < comps.length; c++) {
        var cc = comps[c], idx = [];
        for (var j = 1; j <= cc.numLayers; j++) {
            var L = cc.layer(j), s = slotOf(L);
            if (!s) continue;
            if (s > maxSlot) maxSlot = s;
            if (isIndexSwitch(L)) idx.push(L);
            if (L.name === S.layer || L.name.indexOf("FG_" + S.code + " ") === 0) mySlot = s;
        }
        if (idx.length && cc.name !== "Frame_grid") switchers.push({ comp: cc, layers: idx });
    }
    if (!switchers.length || !compAny("pragmatic_symbol_1")) {
        alert("Це не схоже на шаблон Phone Slot Spin: не знайдено компів-перемикачів слотів.\nВідкрий шаблон і запусти скрипт ще раз."); return;
    }
    var update = mySlot > 0, SLOT = update ? mySlot : maxSlot + 1;

    // ---------------- діалог ----------------
    var dlg = new Window("dialog", "Hyperframes · " + S.name);
    dlg.alignChildren = "fill";
    dlg.add("statictext", undefined, update ? (S.name + " уже є в проєкті (Slot " + SLOT + ") — буде оновлено.")
                                            : (S.name + " стане слотом №" + SLOT + " на слайдері Slot."));
    dlg.add("statictext", undefined, "Символів у слоті: " + S.count + ". Рамок: 25 сіток (3–7 × 3–7).");
    var gp = dlg.add("group"); gp.add("statictext", undefined, "Розмір символів відносно лінійки, %:");
    var et = gp.add("edittext", undefined, "80"); et.characters = 4;
    var cbSw = dlg.add("checkbox", undefined, "Після встановлення перемкнути слайдер Slot на цей слот"); cbSw.value = !update;
    var gb = dlg.add("group"); gb.alignment = "right";
    gb.add("button", undefined, "Скасувати", { name: "cancel" });
    gb.add("button", undefined, update ? "Оновити" : "Встановити", { name: "ok" });
    if (dlg.show() !== 1) return;
    var PCT = (parseFloat(et.text) || 80) / 100;

    app.beginUndoGroup("Install slot: " + S.name);
    var folder = null, cache = {}, missing = [], made = [];
    function folderOf() {
        if (folder) return folder;
        var root = null;
        for (var i = 1; i <= proj.numItems; i++) if (proj.item(i) instanceof FolderItem && proj.item(i).name === "Hyperframes slots") root = proj.item(i);
        if (!root) root = proj.items.addFolder("Hyperframes slots");
        folder = proj.items.addFolder(S.name); folder.parentFolder = root; return folder;
    }
    function footage(rel) {
        if (cache[rel]) return cache[rel];
        var f = File(base.fsName + "/" + rel);
        if (!f.exists) { missing.push(rel); return null; }
        var ft = proj.importFile(new ImportOptions(f)); ft.parentFolder = folderOf();
        cache[rel] = ft; return ft;
    }

    // ---------------- 1. pragmatic_symbol_N / Symbol_N до кількості символів слота ----------------
    var p9 = compAny("pragmatic_symbol_9"), donor = null;
    for (var k = 1; k <= 9 && !donor; k++) donor = compAny("Symbol_" + k);
    for (var n = 1; n <= S.count; n++) {
        var pc = compAny("pragmatic_symbol_" + n);
        if (!pc && p9) { pc = p9.duplicate(); pc.name = "pragmatic_symbol_" + n; pc.parentFolder = p9.parentFolder; made.push(pc.name); }
        var sc = compAny("Symbol_" + n);
        if (!sc && donor && pc) { sc = donor.duplicate(); sc.name = "Symbol_" + n; sc.parentFolder = donor.parentFolder; made.push(sc.name); }
        if (sc && pc) for (var j = 1; j <= sc.numLayers; j++) {        // Symbol_N завжди бере pragmatic_symbol_N
            var Lj = sc.layer(j);
            if (Lj.source && /^pragmatic_symbol_\d+$/.test(Lj.source.name) && Lj.source !== pc) Lj.replaceSource(pc, false);
        }
    }
    // нові компи теж стають перемикачами
    if (made.length) {
        switchers = [];
        comps = allComps();
        for (var c = 0; c < comps.length; c++) {
            var idx = [];
            for (var j = 1; j <= comps[c].numLayers; j++) if (isIndexSwitch(comps[c].layer(j))) idx.push(comps[c].layer(j));
            if (idx.length && comps[c].name !== "Frame_grid") switchers.push({ comp: comps[c], layers: idx });
        }
    }
    function refOf(sw) { for (var k = 0; k < sw.layers.length; k++) if (sw.layers[k].index === REF_SLOT) return sw.layers[k]; return sw.layers[0]; }

    // ---------------- 2. шари слота ----------------
    var added = 0, updated = 0, todo = [];
    for (var s = 0; s < switchers.length; s++) {
        var sw = switchers[s], comp = sw.comp, ref = refOf(sw), cfg = null;
        var m = comp.name.match(/^pragmatic_symbol_(\d+)$/);
        if (m) { var fi = ((parseInt(m[1], 10) - 1) % S.count) + 1; cfg = { file: "symbols/" + fi + ".png", mode: "guides", box: S.box[fi - 1], mult: PCT * (S.mult || 1) }; }
        else if (comp.name === "pragmatic_BG") cfg = { file: "bg.jpg", mode: "cover" };
        else if (comp.name === "pragmatic_Logo") cfg = { file: "logo.png", mode: "contain", box: S.logobox, mult: 0.95 };
        else if (comp.name === "Frame") cfg = { file: "FrameGrids/g5x3.png", frame: "5x3" };

        var mine = null; for (var j = 1; j <= comp.numLayers; j++) if (comp.layer(j).name === S.layer) mine = comp.layer(j);
        if (mine) {
            if (cfg && !cfg.frame) {
                var nf = footage(cfg.file);
                if (nf) { if (mine.source !== nf) mine.replaceSource(nf, false); fit(mine, comp, cfg.mode, cfg.box, cfg.mult); updated++; }
            }
            continue;
        }
        var nl = null;
        if (cfg) {
            var ft = footage(cfg.file); if (!ft) continue;
            nl = comp.layers.add(ft); nl.moveToEnd();
            if (ref.threeDLayer) nl.threeDLayer = true;
            if (cfg.frame) placeFrame(nl, S.frames[cfg.frame]); else fit(nl, comp, cfg.mode, cfg.box, cfg.mult);
            nl.name = S.layer; added++;
        } else {
            nl = ref.duplicate(); nl.moveToEnd(); nl.name = S.layer; nl.label = 11;
            todo.push(comp.name);
        }
        nl.startTime = ref.startTime; nl.inPoint = ref.inPoint; nl.outPoint = ref.outPoint;
        opac(nl).expression = opac(ref).expression.replace(/thisLayer\.index/g, String(SLOT));
    }

    // ---------------- 3. рамки під усі сітки ----------------
    var fgrid = compAny("Frame_grid"), fmsg = "";
    if (fgrid) {
        var sub = null, fl = null;
        for (var j = 1; j <= fgrid.numLayers; j++) if (fgrid.layer(j).name.indexOf("FG_" + S.code + " ") === 0) { fl = fgrid.layer(j); sub = fl.source; }
        if (!sub) {
            sub = proj.items.addComp("FG_" + S.code, fgrid.width, fgrid.height, fgrid.pixelAspect, fgrid.duration, fgrid.frameRate);
            sub.parentFolder = folderOf();
            fl = fgrid.layers.add(sub, fgrid.duration);
            fl.name = "FG_" + S.code + " (Slot " + SLOT + ")";
            opac(fl).expression = 'Math.round(comp("render").layer(1).effect("Slot")("Slider")) === ' + SLOT + ' ? 100 : 0;';
        }
        var have = {}; for (var j = 1; j <= sub.numLayers; j++) have[sub.layer(j).name] = true;
        var cnt = 0;
        for (var key in S.frames) {
            if (!S.frames.hasOwnProperty(key) || have[key]) continue;
            var ft = footage("FrameGrids/g" + key + ".png"); if (!ft) continue;
            var ly = sub.layers.add(ft, fgrid.duration);
            placeFrame(ly, S.frames[key]); ly.name = key;
            var cr = key.split("x");
            opac(ly).expression = HEAD7 + '(C == ' + cr[0] + ' && R == ' + cr[1] + ') ? 100 : 0;';
            cnt++;
        }
        fmsg = cnt ? "Рамки: додано " + cnt + " сіток." : "Рамки: усі сітки вже на місці.";
    } else fmsg = "Frame_grid не знайдено — рамка лише 5×3 (у шаблоні без системи сіток).";

    // ---------------- 4. слайдер ----------------
    var swMsg = "";
    if (cbSw.value) {
        try {
            var sl = compAny("render").layer(1).effect("Slot")("Slider");
            if (sl.numKeys === 0) { sl.setValue(SLOT); swMsg = "\nСлайдер Slot = " + SLOT + "."; }
            else swMsg = "\nНа слайдері Slot є ключі — перемкни на " + SLOT + " вручну.";
        } catch (e) {}
    }

    app.endUndoGroup();
    alert(S.name + (update ? " оновлено" : " встановлено") + " як Slot " + SLOT + "." + swMsg +
          "\n\nДодано шарів: " + added + (updated ? ", оновлено: " + updated : "") + ".\n" + fmsg +
          (made.length ? "\nСтворено компи: " + made.join(", ") + "." : "") +
          (missing.length ? "\n\nНе знайдено файлів:\n  " + missing.join("\n  ") : "") +
          (todo.length ? "\n\nУ цих компах стоїть копія скіна " + REF_SLOT + " (помаранчеві шари) — заміни, якщо треба:\n  " + todo.join("\n  ") : ""));
})();
