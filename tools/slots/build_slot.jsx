/*
  build_slot.jsx — збирає екран слот-гри з нуля в After Effects (без великого шаблону).
  Hyperframes · https://github.com/Valiuk/hyperframes-releases

  Як користуватися:
    1. Розпакуй архів слота (поруч мають лежати slot.json, symbols/, FrameGrids/, bg.jpg, logo.png).
    2. After Effects → File › Scripts › Run Script File… → build_slot.jsx.
    3. Вибери розмір символів і натисни «Зібрати». Скрипт створить новий проєкт з композицією «render».

  Що виходить (1080 × 1920):
    • render — фон, лого, рамка й барабани; на шарі «Controls» слайдери Reels (3–7), Rows (3–7) і Crop rows;
    • Slot — барабани: Column_1…7 (стрічки по 9 символів) і «Null 2», ключі якого крутять усі барабани
      з затримкою Delay між ними (за замовчуванням три прокрути, останній — довгий);
    • Symbol_N → pragmatic_symbol_N → картинка symbols/N.png: номер символа = номер на сайті й у Конструкторі;
    • Frame_grid — рамки під 25 сіток, перемикаються слайдерами самі.
  Свої прокрути й виграшні комбінації — «Конструктор прокрутів» + apply_spin_plan.jsx (сумісні з цим проєктом).
  Усе — один крок Undo (Ctrl+Z).
*/
(function () {
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

    // ---------------- геометрія (як у шаблоні Phone Slot Spin, × 1.25) ----------------
    var W = 1080, H = 1920, FPS = 30, DUR = 20;
    var CX = 540, CY = 925;                 // центр сітки
    var ZW = 950, ZH = 750, PMAX = 237.5;   // зона барабанів і максимальна клітинка
    var FSX = 80.25, FSY = 88.5;            // масштаб рамки
    var FCX = 665.5, FCY = 714.914, FPAD = 300, FSIZE = 1331 + 2 * FPAD;
    var STEP = 266, ROWS = 9, CH = STEP * ROWS, CW = 256;   // стрічка барабана
    var MAXC = 7;

    // ---------------- діалог ----------------
    var dlg = new Window("dialog", "Hyperframes · " + S.name);
    dlg.alignChildren = "fill";
    dlg.add("statictext", undefined, "Збере новий проєкт з екраном гри " + S.name + " (" + S.count + " символів).");
    var g1 = dlg.add("group"); g1.add("statictext", undefined, "Розмір символів відносно клітинки, %:");
    var etP = g1.add("edittext", undefined, "80"); etP.characters = 4;
    var g2 = dlg.add("group"); g2.add("statictext", undefined, "Барабани:");
    var ddC = g2.add("dropdownlist", undefined, ["3", "4", "5", "6", "7"]); ddC.selection = 2;
    g2.add("statictext", undefined, "Ряди:");
    var ddR = g2.add("dropdownlist", undefined, ["3", "4", "5", "6", "7"]); ddR.selection = 0;
    var cbNew = dlg.add("checkbox", undefined, "Створити новий проєкт (рекомендовано)"); cbNew.value = true;
    var gb = dlg.add("group"); gb.alignment = "right";
    gb.add("button", undefined, "Скасувати", { name: "cancel" });
    gb.add("button", undefined, "Зібрати", { name: "ok" });
    if (dlg.show() !== 1) return;
    var PCT = (parseFloat(etP.text) || 80) / 100;
    var C0 = parseInt(ddC.selection.text, 10), R0 = parseInt(ddR.selection.text, 10);

    if (cbNew.value) { app.newProject(); if (!app.project) return; }
    var proj = app.project;
    function compAny(n) { for (var i = 1; i <= proj.numItems; i++) if (proj.item(i) instanceof CompItem && proj.item(i).name === n) return proj.item(i); return null; }
    if (compAny("render") || compAny("Slot")) {
        if (!confirm("У проєкті вже є композиції render / Slot. Скрипти Конструктора працюватимуть з першою за списком.\nВсе одно зібрати?")) return;
    }

    app.beginUndoGroup("Build slot: " + S.name);
    function tr(l) { return l.property("ADBE Transform Group"); }
    function fx(l, match, name) { var e = l.property("ADBE Effect Parade").addProperty(match); if (name) e.name = name; return e; }
    function slider(l, name, v) { var e = fx(l, "ADBE Slider Control", name); e.property(1).setValue(v); return e; }
    function folder(name, parent) { var f = proj.items.addFolder(name); if (parent) f.parentFolder = parent; return f; }
    var root = folder("Hyperframes · " + S.name), fComps = folder("comps", root), fSym = folder("symbols", root), fAss = folder("assets", root), fFr = folder("frames", root);
    var missing = [];
    function imp(rel, fld) {
        var f = File(base.fsName + "/" + rel);
        if (!f.exists) { missing.push(rel); return null; }
        var ft = proj.importFile(new ImportOptions(f)); ft.parentFolder = fld || fAss; return ft;
    }
    function fitIn(L, x1, y1, x2, y2, bx, mult, cover) {
        var w = L.source.width, h = L.source.height; bx = bx || [0, 0, w, h];
        var sx = (x2 - x1) / bx[2], sy = (y2 - y1) / bx[3];
        var s = (cover ? Math.max(sx, sy) : Math.min(sx, sy)) * 100 * (mult || 1);
        tr(L).property("ADBE Anchor Point").setValue([bx[0] + bx[2] / 2, bx[1] + bx[3] / 2]);
        tr(L).property("ADBE Scale").setValue([s, s]);
        tr(L).property("ADBE Position").setValue([(x1 + x2) / 2, (y1 + y2) / 2]);
    }
    var HEAD = 'var ctl = comp("render").layer("Controls");\n' +
        'var C = Math.min(7, Math.max(3, Math.round(ctl.effect("Reels")("Slider"))));\n' +
        'var R = Math.min(7, Math.max(3, Math.round(ctl.effect("Rows")("Slider"))));\n' +
        'var p = Math.min(' + ZW + ' / C, ' + ZH + ' / R, ' + PMAX + ');\n';

    // ---------------- 1. символи ----------------
    var syms = [];
    for (var n = 1; n <= S.count; n++) {
        var ft = imp("symbols/" + n + ".png", fSym); if (!ft) continue;
        var pc = proj.items.addComp("pragmatic_symbol_" + n, 512, 512, 1, DUR, FPS); pc.parentFolder = fSym;
        try { pc.addGuide(0, 100); pc.addGuide(0, 412); pc.addGuide(1, 100); pc.addGuide(1, 412); } catch (e) {}
        var L = pc.layers.add(ft); L.name = S.layer;
        fitIn(L, 100, 100, 412, 412, S.box[n - 1], PCT * (S.mult || 1));
        var sc = proj.items.addComp("Symbol_" + n, CW, CW, 1, DUR, FPS); sc.parentFolder = fSym;
        var sl = sc.layers.add(pc); tr(sl).property("ADBE Scale").setValue([50, 50]);
        syms[n] = sc;
    }

    // ---------------- 2. стрічки барабанів ----------------
    var cols = [];
    for (var c = 1; c <= MAXC; c++) {
        var cc = proj.items.addComp("Column_" + c, CW, CH, 1, DUR, FPS); cc.parentFolder = fComps;
        var ctrl = cc.layers.addNull(); ctrl.name = "Control"; ctrl.enabled = false;
        slider(ctrl, "Start Position", STEP / 2 - STEP);   // перший ряд (центр) = STEP/2
        slider(ctrl, "Base Offset", CW);
        slider(ctrl, "Offset Adjustment", STEP - CW);
        for (var r = 0; r < ROWS; r++) {
            var id = ((c * 4 + r * 7 + (c % 3) * r) % S.count) + 1;
            if (!syms[id]) continue;
            var rl = cc.layers.add(syms[id]); rl.moveToEnd();
            tr(rl).property("ADBE Position").setValue([CW / 2, STEP / 2 + r * STEP]);
            rl.name = "Ряд " + (r + 1);
        }
        cols.push(cc);
    }

    // ---------------- 3. Slot: барабани + нуль, що їх крутить ----------------
    var slot = proj.items.addComp("Slot", W, H, 1, DUR, FPS); slot.parentFolder = fComps;
    var nul = slot.layers.addNull(); nul.name = "Null 2"; nul.enabled = false;
    var nOff = fx(nul, "ADBE Offset", "Offset"); var shift = nOff.property("ADBE Offset-0001");
    slider(nul, "Delay", 0.1);
    var Y0 = CH / 2;
    shift.setValue([CW / 2, Y0]);
    var spins = [[1.0, 1.0, 15, 0.6], [4.0, 1.0, 12, 0.6], [7.0, 2.0, 24, 0.8]];   // старт, тривалість, рядів, пік
    var y = Y0, keys = [];
    for (var s = 0; s < spins.length; s++) {
        var t = spins[s][0], d = spins[s][1], a = y + spins[s][2] * STEP;
        keys.push([t, y, 0]); keys.push([t + d * spins[s][3], a + STEP / 2, 1]); keys.push([t + d, a, 2]);
        y = a;
    }
    for (var k = 0; k < keys.length; k++) shift.setValueAtTime(keys[k][0], [CW / 2, keys[k][1]]);
    function ease(k, inI, outI) {
        var a = new KeyframeEase(0, inI), b = new KeyframeEase(0, outI);
        try { shift.setTemporalEaseAtKey(k, [a, a], [b, b]); } catch (e) { try { shift.setTemporalEaseAtKey(k, [a], [b]); } catch (e2) {} }
    }
    for (var k = 1; k <= shift.numKeys; k++) {
        var role = keys[k - 1][2];
        if (role === 0) { shift.setInterpolationTypeAtKey(k, KeyframeInterpolationType.HOLD, KeyframeInterpolationType.BEZIER); ease(k, 33, 55); }
        if (role === 1) { shift.setInterpolationTypeAtKey(k, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER); ease(k, 25, 33); }
        if (role === 2) { shift.setInterpolationTypeAtKey(k, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.HOLD); ease(k, 60, 33); }
    }
    var COL_EXPR =
        'var n = thisComp.layer("Null 2");\n' +
        'var ctrl = n.effect("Offset")("Shift Center To");\n' +
        'var delaySec = n.effect("Delay")("Slider");\n' +
        'var col = parseInt(thisLayer.source.name.replace(/[^0-9]/g, ""), 10);\n' +
        'var delay = (col - 2) * delaySec;\n' +
        'value + (ctrl.valueAtTime(time - delay) - ctrl.valueAtTime(0));';
    for (var c = 0; c < cols.length; c++) {
        var CL = slot.layers.add(cols[c]); CL.moveToEnd();
        var off = fx(CL, "ADBE Offset", "Offset").property("ADBE Offset-0001");
        off.setValue([CW / 2, Y0]); off.expression = COL_EXPR;
        var T = tr(CL);
        T.property("ADBE Position").expression = HEAD +
            'var n = parseInt(thisLayer.source.name.replace(/[^0-9]/g, ""), 10);\n' +
            '[' + CX + ' + (n - (C + 1) / 2) * p, ' + CY + ' + ((R % 2 == 0) ? p / 2 : 0)];';
        T.property("ADBE Scale").expression = HEAD + 'var s = p / ' + STEP + ' * 100;\n[s, s];';
        T.property("ADBE Opacity").expression = HEAD +
            'var n = parseInt(thisLayer.source.name.replace(/[^0-9]/g, ""), 10);\n(n <= C) ? value : 0;';
    }

    // ---------------- 4. рамки ----------------
    var fg = proj.items.addComp("Frame_grid", FSIZE, FSIZE, 1, DUR, FPS); fg.parentFolder = fComps;
    var fc = 0;
    for (var key in S.frames) {
        if (!S.frames.hasOwnProperty(key)) continue;
        var fi = imp("FrameGrids/g" + key + ".png", fFr); if (!fi) continue;
        var r = S.frames[key], ly = fg.layers.add(fi), k = r[2] / r[4] * 100;
        tr(ly).property("ADBE Scale").setValue([k, k]);
        tr(ly).property("ADBE Position").setValue([r[0] + r[2] / 2 + FPAD, r[1] + r[3] / 2 + FPAD]);
        ly.name = key;
        var cr = key.split("x");
        tr(ly).property("ADBE Opacity").expression = HEAD + '(C == ' + cr[0] + ' && R == ' + cr[1] + ') ? 100 : 0;';
        fc++;
    }

    // ---------------- 5. render ----------------
    var render = proj.items.addComp("render", W, H, 1, DUR, FPS); render.parentFolder = root;
    var bg = imp("bg.jpg");
    if (bg) { var bl = render.layers.add(bg); bl.name = "BG"; fitIn(bl, 0, 0, W, H, null, 1, true); }
    var fl = render.layers.add(fg); fl.name = "Frame";
    tr(fl).property("ADBE Anchor Point").setValue([FCX + FPAD, FCY + FPAD]);
    tr(fl).property("ADBE Position").setValue([CX, CY]);
    tr(fl).property("ADBE Scale").setValue([FSX, FSY]);
    var sl = render.layers.add(slot); sl.name = "Slot";
    var mk = sl.property("ADBE Mask Parade").addProperty("ADBE Mask Atom"); mk.name = "Grid rows";
    mk.property("ADBE Mask Shape").expression = HEAD +
        'var on = ctl.effect("Crop rows")("Checkbox") == 1;\n' +
        'var hh = on ? R * p / 2 : 5000, hw = 5000;\n' +
        'createPath([[' + CX + ' - hw, ' + CY + ' - hh], [' + CX + ' + hw, ' + CY + ' - hh], [' + CX + ' + hw, ' + CY + ' + hh], [' + CX + ' - hw, ' + CY + ' + hh]], [], [], true);';
    var lg = imp("logo.png");
    if (lg) { var ll = render.layers.add(lg); ll.name = "Logo"; fitIn(ll, 110, 70, 970, 380, S.logobox, 1); }
    var ctl = render.layers.addNull(); ctl.name = "Controls"; ctl.enabled = false;
    slider(ctl, "Reels", C0); slider(ctl, "Rows", R0);
    var cb = fx(ctl, "ADBE Checkbox Control", "Crop rows"); cb.property(1).setValue(1);
    slider(ctl, "Slot", 1);
    ctl.moveToBeginning();
    try { ctl.comment = "Slot: 1 = " + S.name; } catch (e) {}

    app.endUndoGroup();
    render.openInViewer();
    alert(S.name + " зібрано.\n\nКомпозиція render (1080 × 1920): фон, лого, рамка, барабани.\n" +
          "Сітка — слайдери Reels і Rows на шарі Controls. Прокрути — ключі шару «Null 2» у композиції Slot (3 прокрути, 1–9 с).\n" +
          "Рамок: " + fc + " з 25." +
          (missing.length ? "\n\nНе знайдено файлів:\n  " + missing.join("\n  ") : "") +
          "\n\nСвої прокрути й комбінації — Конструктор прокрутів + apply_spin_plan.jsx." +
          "\nЗбережи проєкт поруч із папкою слота, щоб не загубити посилання на файли.");
})();
