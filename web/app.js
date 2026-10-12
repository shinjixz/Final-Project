import { EMOTION_LABELS, keywordEmotion } from './keyword_fallback.js';

// The AI library is imported lazily inside getAIPipeline(): if the CDN is down
// the rest of the page still works and the keyword fallback takes over.
const TRANSFORMERS_CDN = 'https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.2';
const MAX_TEXT_LENGTH = 1000;
const MAX_IMAGE_BYTES = 10 * 1024 * 1024;

const $ = id => document.getElementById(id);

let currentLang = 'TH';
let pipelinePromise = null;   // shared model download (started once)
let modelStatus = 'idle';      // idle | loading | ready | failed
const MODEL_WAIT_MS = 15000;   // max wait per click before using the fallback

let activePaletteData = [];

// ==========================================
// 🛠 COLOR CONVERSION & EXPORT HELPERS
// ==========================================

function hexToRgb(hex) {
    let cleanHex = hex.replace('#', '');
    if (cleanHex.length === 3) cleanHex = cleanHex.split('').map(x => x + x).join('');
    const num = parseInt(cleanHex, 16);
    return {
        r: (num >> 16) & 255,
        g: (num >> 8) & 255,
        b: num & 255
    };
}

function hexToHsl(hex) {
    let { r, g, b } = hexToRgb(hex);
    r /= 255; g /= 255; b /= 255;
    const max = Math.max(r, g, b), min = Math.min(r, g, b);
    let h, s, l = (max + min) / 2;

    if (max === min) {
        h = s = 0;
    } else {
        const d = max - min;
        s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
        switch (max) {
            case r: h = (g - b) / d + (g < b ? 6 : 0); break;
            case g: h = (b - r) / d + 2; break;
            case b: h = (r - g) / d + 4; break;
        }
        h /= 6;
    }
    return {
        h: Math.round(h * 360),
        s: Math.round(s * 100),
        l: Math.round(l * 100)
    };
}

function slugifyRole(role, index) {
    if (!role) return `color-${index + 1}`;
    return role.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
}

function copyPaletteCode(format) {
    if (!activePaletteData || activePaletteData.length === 0) {
        return toast(translations[currentLang].noPalette);
    }

    let codeResult = '';

    switch (format) {
        case 'HEX':
            codeResult = activePaletteData.map(c => typeof c === 'string' ? c : c.hex).join(', ');
            break;

        case 'RGB':
            codeResult = activePaletteData.map(c => {
                const hex = typeof c === 'string' ? c : c.hex;
                const { r, g, b } = hexToRgb(hex);
                return `rgb(${r}, ${g}, ${b})`;
            }).join('\n');
            break;

        case 'HSL':
            codeResult = activePaletteData.map(c => {
                const hex = typeof c === 'string' ? c : c.hex;
                const { h, s, l } = hexToHsl(hex);
                return `hsl(${h}, ${s}%, ${l}%)`;
            }).join('\n');
            break;

        case 'TAILWIND':
            codeResult = activePaletteData.map((c, i) => {
                const hex = typeof c === 'string' ? c : c.hex;
                const role = slugifyRole(typeof c === 'object' ? c.role : '', i);
                return `bg-[${hex}] /* ${role} */`;
            }).join('\n');
            break;

        case 'CSS_VARS':
            codeResult = ':root {\n' + activePaletteData.map((c, i) => {
                const hex = typeof c === 'string' ? c : c.hex;
                const role = slugifyRole(typeof c === 'object' ? c.role : '', i);
                return `  --color-${role}: ${hex};`;
            }).join('\n') + '\n}';
            break;
    }

    copyText(codeResult, format);
}

function createASEBuffer(palette) {
    const blocks = [];

    function encodeString(str) {
        const buf = new Uint8Array((str.length + 1) * 2);
        const view = new DataView(buf.buffer);
        for (let i = 0; i < str.length; i++) {
            view.setUint16(i * 2, str.charCodeAt(i), false);
        }
        view.setUint16(str.length * 2, 0, false);
        return buf;
    }

    palette.forEach((item) => {
        const hex = typeof item === 'string' ? item : item.hex;
        const name = (typeof item === 'object' && item.role) ? `${item.role} (${hex})` : hex;
        const { r, g, b } = hexToRgb(hex);

        const nameBuf = encodeString(name);
        const entryLen = 2 + nameBuf.length + 4 + 12 + 2;
        const block = new Uint8Array(2 + 4 + entryLen);
        const view = new DataView(block.buffer);

        let offset = 0;
        view.setUint16(offset, 0x0001, false); offset += 2;
        view.setUint32(offset, entryLen, false); offset += 4;

        view.setUint16(offset, name.length + 1, false); offset += 2;
        block.set(nameBuf, offset); offset += nameBuf.length;

        block.set([82, 71, 66, 32], offset); offset += 4;

        view.setFloat32(offset, r / 255, false); offset += 4;
        view.setFloat32(offset, g / 255, false); offset += 4;
        view.setFloat32(offset, b / 255, false); offset += 4;

        view.setUint16(offset, 0, false);
        blocks.push(block);
    });

    const totalBlockLen = blocks.reduce((sum, b) => sum + b.length, 0);
    const fullBuffer = new Uint8Array(12 + totalBlockLen);
    const headerView = new DataView(fullBuffer.buffer);

    fullBuffer.set([65, 83, 69, 70], 0);
    headerView.setUint16(4, 1, false);
    headerView.setUint16(6, 0, false);
    headerView.setUint32(8, blocks.length, false);

    let currentOffset = 12;
    blocks.forEach(b => {
        fullBuffer.set(b, currentOffset);
        currentOffset += b.length;
    });

    return fullBuffer.buffer;
}

function downloadASE(palette, filename = "palette.ase") {
    if (!palette || palette.length === 0) return toast(translations[currentLang].noPalette);
    const buffer = createASEBuffer(palette);
    const blob = new Blob([buffer], { type: "application/octet-stream" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

function downloadJSON(palette, filename = "palette.json") {
    if (!palette || palette.length === 0) return toast(translations[currentLang].noPalette);
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(palette, null, 2));
    const a = document.createElement("a");
    a.href = dataStr;
    a.download = filename;
    a.click();
}

function copyFigmaTokens(palette) {
    if (!palette || palette.length === 0) return toast(translations[currentLang].noPalette);
    const figmaTokens = {};
    palette.forEach((item, i) => {
        const hex = typeof item === 'string' ? item : item.hex;
        const role = slugifyRole(typeof item === 'object' ? item.role : '', i);
        figmaTokens[role] = { value: hex, type: "color" };
    });
    copyText(JSON.stringify(figmaTokens, null, 2), 'Figma tokens');
}

// ==========================================
// 🖼️ IMAGE COLOR EXTRACTION HELPERS
// ==========================================

// Dominant colours: sample a downscaled copy, bucket similar colours,
// then pick the most common buckets that are clearly different from each other.
function extractRGBColors(ctx, width, height, count) {
    const data = ctx.getImageData(0, 0, width, height).data;
    const buckets = new Map();
    for (let i = 0; i < data.length; i += 4) {
        if (data[i + 3] < 128) continue; // skip transparent pixels
        const key = (data[i] >> 4) << 8 | (data[i + 1] >> 4) << 4 | (data[i + 2] >> 4);
        const b = buckets.get(key) || { n: 0, r: 0, g: 0, b: 0 };
        b.n++; b.r += data[i]; b.g += data[i + 1]; b.b += data[i + 2];
        buckets.set(key, b);
    }
    const ranked = [...buckets.values()]
        .map(b => ({ n: b.n, r: Math.round(b.r / b.n), g: Math.round(b.g / b.n), b: Math.round(b.b / b.n) }))
        .sort((x, y) => y.n - x.n);
    const dist = (a, c) => Math.hypot(a.r - c.r, a.g - c.g, a.b - c.b);
    const picked = [];
    for (const minDist of [60, 35, 15, 0]) {
        for (const c of ranked) {
            if (picked.length >= count) break;
            if (!picked.includes(c) && picked.every(p => dist(p, c) >= minDist)) picked.push(c);
        }
        if (picked.length >= count) break;
    }
    const rgbList = picked.map(({ r, g, b }) => ({ r, g, b }));
    const hexList = rgbList.map(({ r, g, b }) =>
        '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase());
    return { hexList, rgbList };
}

// Small JPEG copy of the image for the history list (keeps localStorage small).
function makeThumbnail(img, maxSide = 320) {
    const scale = Math.min(1, maxSide / Math.max(img.width, img.height));
    const canvas = document.createElement('canvas');
    canvas.width = Math.max(1, Math.round(img.width * scale));
    canvas.height = Math.max(1, Math.round(img.height * scale));
    canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg', 0.75);
}

function analyzeColorSentiment(rgbColors) {
    let totalR = 0, totalG = 0, totalB = 0;
    rgbColors.forEach(color => {
        totalR += color.r;
        totalG += color.g;
        totalB += color.b;
    });

    const count = rgbColors.length;
    const brightness = ((totalR / count) * 299 + (totalG / count) * 587 + (totalB / count) * 114) / 1000;

    if (brightness < 80) return 'FEAR';
    if (totalR > totalG * 1.3 && totalR > totalB * 1.3) return 'ANGER';
    if (totalB > totalR * 1.1 && brightness < 150) return 'SADNESS';
    if (totalG > totalR && totalB > totalR) return 'JOY';
    return 'JOY';
}

function clearImageResult() {
    if ($('extractedPaletteSection'))$('extractedPaletteSection').style.display = 'none';
    if ($('imagePreview'))$('imagePreview').src = '';
    if ($('imageInput'))$('imageInput').value = '';
}

// ==========================================
// 🌐 DICTIONARY & CONFIGS
// ==========================================

const translations = {
    TH: {
        langBtn: 'EN',
        title: 'เปลี่ยนความรู้สึกให้เป็นจานสี',
        subTitle: 'พิมพ์ประโยคภาษาอังกฤษที่บอกความรู้สึก หรือใช้รูปภาพ แล้วรับจานสี 8 สี พร้อมธีมและฟอนต์ที่เข้ากัน',
        inputLabel: 'ข้อความภาษาอังกฤษ',
        placeholder: 'เช่น I am so excited about our new project!',
        analyzeBtn: 'วิเคราะห์ข้อความ',
        analyzing: 'กำลังวิเคราะห์…',
        uploadBtn: 'ใช้สีจากรูปภาพ',
        paletteTitle: 'จานสีที่แนะนำ',
        resultEmpty: 'ผลลัพธ์จะแสดงที่นี่ ลองพิมพ์ประโยคด้านบนแล้วกดวิเคราะห์',
        copyHint: 'คลิกที่สีเพื่อคัดลอกรหัส',
        copyAs: 'คัดลอกเป็น',
        download: 'ดาวน์โหลด',
        theme: 'ธีม',
        fonts: 'ฟอนต์',
        usage: 'เหมาะกับ',
        historyTitle: 'ประวัติล่าสุด',
        clearHistory: 'ล้างประวัติ',
        emptyHistory: 'ยังไม่มีประวัติ ผลการวิเคราะห์ 10 รายการล่าสุดจะเก็บไว้ที่นี่',
        imageItem: 'รูปภาพ',
        modalTitle: 'ล้างประวัติทั้งหมด?',
        modalDesc: 'ประวัติทั้งหมดในเบราว์เซอร์นี้จะถูกลบ และกู้คืนไม่ได้',
        modalCancel: 'ยกเลิก',
        modalConfirm: 'ล้างประวัติ',
        copied: 'คัดลอกแล้ว',
        noPalette: 'ยังไม่มีจานสี วิเคราะห์ข้อความหรือรูปภาพก่อน',
        footer: 'ประมวลผลบนเบราว์เซอร์ของคุณ ข้อความและรูปภาพไม่ถูกส่งออกไปที่เซิร์ฟเวอร์'
    },
    EN: {
        langBtn: 'TH',
        title: 'Turn a feeling into a palette',
        subTitle: 'Write an English sentence about how you feel, or use an image, and get an 8-colour palette with a matching theme and fonts.',
        inputLabel: 'English text',
        placeholder: 'e.g. I am so excited about our new project!',
        analyzeBtn: 'Analyze text',
        analyzing: 'Analyzing…',
        uploadBtn: 'Use colours from an image',
        paletteTitle: 'Suggested palette',
        resultEmpty: 'Your result will appear here. Type a sentence above and press Analyze.',
        copyHint: 'Click a colour to copy its code',
        copyAs: 'Copy as',
        download: 'Download',
        theme: 'Theme',
        fonts: 'Fonts',
        usage: 'Good for',
        historyTitle: 'Recent',
        clearHistory: 'Clear history',
        emptyHistory: 'No history yet. Your last 10 results will be kept here.',
        imageItem: 'Image',
        modalTitle: 'Clear all history?',
        modalDesc: 'All history in this browser will be deleted and cannot be restored.',
        modalCancel: 'Cancel',
        modalConfirm: 'Clear history',
        copied: 'Copied',
        noPalette: 'No palette yet. Analyze some text or an image first.',
        footer: 'Runs in your browser. Your text and images are never sent to a server.'
    }
};

const emotionRules = {
    JOY: { 
        palette: [
            { hex: '#FFD700', role: 'Main' },
            { hex: '#FF8C00', role: 'Primary' },
            { hex: '#FF69B4', role: 'Accent 1' },
            { hex: '#00BFFF', role: 'Accent 2' },
            { hex: '#32CD32', role: 'Success' },
            { hex: '#FFE4B5', role: 'Soft Bg' },
            { hex: '#FFF8DC', role: 'Light Bg' },
            { hex: '#2C3E50', role: 'Dark Text' }
        ], 
        theme: 'Vibrant Sunburst', 
        font: 'Poppins / Montserrat', 
        fontFamily: "'Poppins', 'Montserrat', sans-serif",
        context: 'E-Commerce, Festival Branding, Mobile UI' 
    },
    SADNESS: { 
        palette: [
            { hex: '#1C2541', role: 'Primary' },
            { hex: '#3A506B', role: 'Secondary' },
            { hex: '#5BC0BE', role: 'Accent' },
            { hex: '#6C757D', role: 'Muted Text' },
            { hex: '#ADB5BD', role: 'Border' },
            { hex: '#D9E2EC', role: 'Soft Surface' },
            { hex: '#F0F4F8', role: 'Light Bg' },
            { hex: '#0F172A', role: 'Dark Text' }
        ], 
        theme: 'Melancholic Mist', 
        font: 'Lora / Merriweather', 
        fontFamily: "'Lora', 'Merriweather', serif",
        context: 'Editorial Blogs, Personal Portfolios, Mental Health Apps' 
    },
    ANGER: { 
        palette: [
            { hex: '#D00000', role: 'Primary' },
            { hex: '#9D0208', role: 'Dark Primary' },
            { hex: '#E85D04', role: 'Accent 1' },
            { hex: '#FAA307', role: 'Accent 2' },
            { hex: '#370617', role: 'Dark Surface' },
            { hex: '#FFCCD5', role: 'Soft Red' },
            { hex: '#FFF0F3', role: 'Light Bg' },
            { hex: '#2B2D42', role: 'Dark Text' }
        ], 
        theme: 'Fiery Passion', 
        font: 'Oswald / Roboto', 
        fontFamily: "'Oswald', 'Roboto', sans-serif",
        context: 'Sports Apps, Gaming Dashboards, High-Energy Campaign' 
    },
    FEAR: { 
        palette: [
            { hex: '#2B1E3A', role: 'Dark Bg' },
            { hex: '#4A3E3D', role: 'Primary' },
            { hex: '#2C3539', role: 'Surface' },
            { hex: '#5C5470', role: 'Secondary' },
            { hex: '#B8C0C2', role: 'Muted Text' },
            { hex: '#8D99AE', role: 'Accent' },
            { hex: '#EDF2F4', role: 'Light Text' },
            { hex: '#111827', role: 'Deep Base' }
        ], 
        theme: 'Mystic Shadow', 
        font: 'Cinzel / Inter', 
        fontFamily: "'Cinzel', 'Inter', serif",
        context: 'Cybersecurity Platforms, Horror Content, Security Tools' 
    },
    LOVE: { 
        palette: [
            { hex: '#FF758F', role: 'Primary' },
            { hex: '#FF4D6D', role: 'Accent' },
            { hex: '#C9184A', role: 'Deep Red' },
            { hex: '#FFB3C1', role: 'Soft Pink' },
            { hex: '#FFF0F3', role: 'Light Bg' },
            { hex: '#800F2F', role: 'Text Dark' },
            { hex: '#FFCCD5', role: 'Card Bg' },
            { hex: '#590D22', role: 'Header' }
        ], 
        theme: 'Romantic Bloom', 
        font: 'Playfair Display / Great Vibes', 
        fontFamily: "'Playfair Display', serif",
        context: 'Wedding Sites, Lifestyle Apps, Relationship Platforms' 
    },
    SURPRISE: { 
        palette: [
            { hex: '#7209B7', role: 'Primary' },
            { hex: '#3F37C9', role: 'Secondary' },
            { hex: '#4CC9F0', role: 'Accent 1' },
            { hex: '#F72585', role: 'Accent 2' },
            { hex: '#4895EF', role: 'Info' },
            { hex: '#E0AAFF', role: 'Soft Purple' },
            { hex: '#F7F0F5', role: 'Light Bg' },
            { hex: '#10002B', role: 'Dark Text' }
        ], 
        theme: 'Electric Wonder', 
        font: 'Plus Jakarta Sans / Space Grotesk', 
        fontFamily: "'Plus Jakarta Sans', 'Space Grotesk', sans-serif",
        context: 'Entertainment Apps, Banners, Interactive Art' 
    }
};

function updateLanguageUI() {
    const tr = translations[currentLang];
    document.documentElement.lang = currentLang === 'TH' ? 'th' : 'en';
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (tr[key]) el.innerText = tr[key];
    });
    if ($('langToggleBtn'))$('langToggleBtn').innerText = tr.langBtn;
    if ($('subTitle'))$('subTitle').innerText = tr.subTitle;
    if ($('inputLabel'))$('inputLabel').innerText = tr.inputLabel;
    if ($('textInput'))$('textInput').placeholder = tr.placeholder;
    if ($('analyzeBtn') && !$('analyzeBtn').disabled)$('analyzeBtn').innerText = tr.analyzeBtn;
    if ($('uploadTriggerBtn'))$('uploadTriggerBtn').innerText = tr.uploadBtn;
    if ($('paletteTitle'))$('paletteTitle').innerText = tr.paletteTitle;
    if ($('historyTitle'))$('historyTitle').innerText = tr.historyTitle;
    if ($('clearHistoryBtn'))$('clearHistoryBtn').innerText = tr.clearHistory;
    if ($('modalTitle'))$('modalTitle').innerText = tr.modalTitle;
    if ($('modalDesc'))$('modalDesc').innerText = tr.modalDesc;
    if ($('modalCancelBtn'))$('modalCancelBtn').innerText = tr.modalCancel;
    if ($('modalConfirmBtn'))$('modalConfirmBtn').innerText = tr.modalConfirm;
    renderHistoryList();
}

function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, ch => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[ch]));
}

let toastTimer = null;
function toast(message) {
    const el = $('toast');
    if (!el) return;
    el.innerText = message;
    el.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove('show'), 1800);
}

async function copyText(text, label) {
    try {
        await navigator.clipboard.writeText(text);
        toast(`${translations[currentLang].copied} ${label}`);
    } catch (e) {
        toast(text);
    }
}

const renderSwatches = colors => {
    return `<div class="strip">` + (colors || []).map(c => {
        const hex = (typeof c === 'string' ? c : c.hex).toUpperCase();
        const role = typeof c === 'object' && c.role ? c.role : '';
        return `
            <button type="button" class="chip" data-hex="${escapeHtml(hex)}" aria-label="${escapeHtml(hex)} ${escapeHtml(role)}">
                <span class="chip-color" style="background:${escapeHtml(hex)}"></span>
                <span class="chip-meta">
                    <span class="chip-hex">${escapeHtml(hex)}</span>
                    ${role ? `<span class="chip-role">${escapeHtml(role)}</span>` : ''}
                </span>
            </button>`;
    }).join('') + `</div>`;
};

function setModelStatus(text) {
    const el = $('modelStatus');
    if (el) el.innerText = text || '';
}

// Start downloading the model once, in the background. Progress is shown
// under the buttons; a failure resets the promise so the next click retries.
function loadAIPipeline() {
    if (pipelinePromise) return pipelinePromise;
    modelStatus = 'loading';
    setModelStatus(t('กำลังโหลดโมเดล AI... (ครั้งแรกอาจใช้เวลา 1–2 นาที)', 'Loading AI model... (first time may take 1–2 minutes)'));
    const files = {};
    pipelinePromise = (async () => {
        const { pipeline, env } = await import(TRANSFORMERS_CDN);
        env.allowLocalModels = false;
        return pipeline('zero-shot-classification', 'Xenova/distilbert-base-uncased-mnli', {
            quantized: true,
            progress_callback: (p) => {
                if (p.status === 'progress' && p.total) {
                    files[p.file] = [p.loaded, p.total];
                    const [done, total] = Object.values(files)
                        .reduce(([d, t], [l, tt]) => [d + l, t + tt], [0, 0]);
                    setModelStatus(t(`กำลังดาวน์โหลดโมเดล AI ${Math.floor(done / total * 100)}% (ครั้งแรกเท่านั้น)`,
                        `Downloading AI model ${Math.floor(done / total * 100)}% (first time only)`));
                }
            }
        });
    })().then(model => {
        modelStatus = 'ready';
        setModelStatus(t('✅ โมเดล AI พร้อมใช้งาน', '✅ AI model ready'));
        return model;
    }).catch(err => {
        modelStatus = 'failed';
        pipelinePromise = null;
        setModelStatus(t('⚠️ โหลดโมเดล AI ไม่สำเร็จ ใช้โหมดสำรองแทน', '⚠️ AI model failed to load, using fallback'));
        throw err;
    });
    return pipelinePromise;
}

// Wait for the model, but never longer than MODEL_WAIT_MS.
async function getAIPipeline() {
    const timeout = new Promise((_, reject) => setTimeout(
        () => reject(new Error('MODEL_TIMEOUT')), MODEL_WAIT_MS));
    return Promise.race([loadAIPipeline(), timeout]);
}


// ==========================================
// 🛟 UI HELPERS
// ==========================================

function showAlert(message) {
    const box = $('alertBox');
    if (!box) return;
    box.innerText = message || '';
    box.style.display = message ? 'block' : 'none';
}

function t(th, en) {
    return currentLang === 'TH' ? th : en;
}

function relativeLuminance(hex) {
    const { r, g, b } = hexToRgb(hex);
    const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
}

// Use the palette colour that reads best on white as the page accent.
function applyAccent(colorList) {
    const hexList = (colorList || []).map(c => typeof c === 'string' ? c : c.hex);
    if (!hexList.length) return;
    const best = hexList.reduce((a, b) => (relativeLuminance(a) < relativeLuminance(b) ? a : b));
    const contrast = 1.05 / (relativeLuminance(best) + 0.05);
    const vivid = hexList.find(h => 1.05 / (relativeLuminance(h) + 0.05) >= 4.5 && hexToHsl(h).s >= 35);
    const accent = vivid || (contrast >= 4.5 ? best : '#16181D');
    document.documentElement.style.setProperty('--accent', accent);
}

function saveToHistory(type, inputContent, emotion, confidence, palette, thumb = null) {
    const newItem = {
        type,
        content: inputContent,
        thumb,
        emotion,
        confidence,
        palette,
        createdAt: new Date().toISOString()
    };

    try {
        const localData = JSON.parse(localStorage.getItem('sentiment_history') || '[]');
        localData.unshift(newItem);
        if (localData.length > 10) localData.pop();
        localStorage.setItem('sentiment_history', JSON.stringify(localData));
    } catch (e) {
        // Quota full (large images) or storage blocked: keep working without history.
        console.error("LocalStorage error:", e);
        showAlert(t('บันทึกประวัติไม่ได้ (พื้นที่เบราว์เซอร์เต็มหรือถูกปิด) แต่ผลวิเคราะห์ยังใช้ได้ตามปกติ',
            'Could not save history (browser storage full or blocked); results still work.'));
    }

    renderHistoryList();
}

function openConfirmModal() {
    if ($('confirmModal'))$('confirmModal').style.display = 'flex';
}

function closeConfirmModal() {
    if ($('confirmModal'))$('confirmModal').style.display = 'none';
}

function executeClearHistory() {
    try { localStorage.removeItem('sentiment_history'); } catch (e) { console.error(e); }
    renderHistoryList();
    closeConfirmModal();
}

function parsePalette(palette) {
    if (Array.isArray(palette)) return palette;
    if (typeof palette === 'string') {
        try { return JSON.parse(palette); } catch (e) { return []; }
    }
    return [];
}

function historyImageSrc(item) {
    if (item.thumb) return item.thumb;
    // Older entries stored the full image as `content`.
    if (typeof item.content === 'string' && item.content.startsWith('data:image')) return item.content;
    return '';
}

function renderHistoryList() {
    const list = $('historyList');
    if (!list) return;
    const tr = translations[currentLang];

    let historyData = [];
    try {
        historyData = JSON.parse(localStorage.getItem('sentiment_history') || '[]');
    } catch (e) {
        historyData = [];
    }
    if (!Array.isArray(historyData) || historyData.length === 0) {
        list.innerHTML = `<li class="history-empty">${escapeHtml(tr.emptyHistory)}</li>`;
        return;
    }
    window.currentHistoryData = historyData;

    list.innerHTML = historyData.map((item, index) => {
        const time = item.createdAt
            ? new Date(item.createdAt).toLocaleString(currentLang === 'TH' ? 'th-TH' : 'en-GB',
                { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
            : '';
        const hexList = parsePalette(item.palette).map(c => typeof c === 'string' ? c : c.hex);
        const isImage = item.type === 'image';
        const src = isImage ? historyImageSrc(item) : '';
        const label = isImage
            ? (item.content && !String(item.content).startsWith('data:') ? item.content : tr.imageItem)
            : item.content;
        const visual = isImage && src
            ? `<img class="history-thumb" src="${escapeHtml(src)}" alt="">`
            : `<span class="history-glyph" aria-hidden="true">${isImage ? '▣' : '“'}</span>`;
        const emotion = String(item.emotion || '-').toLowerCase();

        return `
            <li>
                <button type="button" class="history-item" data-index="${index}">
                    ${visual}
                    <span class="history-main">
                        <span class="history-text">${escapeHtml(label)}</span>
                        <span class="history-meta"><strong>${escapeHtml(emotion)}</strong> ${escapeHtml(time)}</span>
                    </span>
                    <span class="mini-strip" aria-hidden="true">
                        ${hexList.slice(0, 8).map(c => `<span style="background:${escapeHtml(c)}"></span>`).join('')}
                    </span>
                </button>
            </li>`;
    }).join('');

    list.querySelectorAll('.history-item').forEach(el => {
        el.addEventListener('click', () => {
            const item = window.currentHistoryData?.[el.dataset.index];
            if (item) loadHistoryItem(item);
        });
    });
}

function loadHistoryItem(item) {
    const paletteArray = parsePalette(item.palette);
    showAlert('');
    if (item.type === 'image') {
        if ($('textInput'))$('textInput').value = '';
        const src = historyImageSrc(item);
        if ($('imagePreview'))$('imagePreview').src = src;
        if ($('extractedPaletteSection'))$('extractedPaletteSection').style.display = src ? 'block' : 'none';
        updateUIResult(item.emotion, item.confidence || '-', paletteArray);
    } else {
        clearImageResult();
        if ($('textInput'))$('textInput').value = item.content;
        updateUIResult(item.emotion, item.confidence || '-');
    }
    $('resultSection')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function updateUIResult(emotionKey, confidence, customPalette = null) {
    const key = String(emotionKey || '').toUpperCase();
    const resultData = emotionRules[key] || emotionRules['JOY'];

    $('resultSection')?.classList.remove('is-empty');
    if ($('emotionLabel'))$('emotionLabel').innerText = key.toLowerCase();
    if ($('confidenceValue'))$('confidenceValue').innerText = confidence;
    if ($('themeName'))$('themeName').innerText = resultData.theme;
    if ($('fontPairing'))$('fontPairing').innerText = resultData.font;
    if ($('usageContext'))$('usageContext').innerText = resultData.context;

    activePaletteData = customPalette || resultData.palette;
    if ($('paletteDisplay'))$('paletteDisplay').innerHTML = renderSwatches(activePaletteData);
    applyAccent(activePaletteData);
}

// ==========================================
// 🚀 DOM LOADED & EVENT LISTENERS
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    const langToggleBtn = $('langToggleBtn');
    const analyzeBtn = $('analyzeBtn');
    const textInput = $('textInput');
    const uploadTriggerBtn = $('uploadTriggerBtn');
    const imageInput = $('imageInput');
    const clearHistoryBtn = $('clearHistoryBtn');

    if (clearHistoryBtn) clearHistoryBtn.addEventListener('click', openConfirmModal);

    // Click a colour chip to copy its HEX code.
    $('paletteDisplay')?.addEventListener('click', (e) => {
        const chip = e.target.closest('.chip');
        if (chip) copyText(chip.dataset.hex, chip.dataset.hex);
    });

    // Ctrl/Cmd + Enter analyses the text.
    textInput?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) analyzeBtn?.click();
    });

    // Close the confirm dialog with Escape or a click outside it.
    $('confirmModal')?.addEventListener('click', (e) => { if (e.target.id === 'confirmModal') closeConfirmModal(); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeConfirmModal(); });
    if ($('modalCancelBtn'))$('modalCancelBtn').addEventListener('click', closeConfirmModal);
    if ($('modalConfirmBtn'))$('modalConfirmBtn').addEventListener('click', executeClearHistory);

    $('exportAseBtn')?.addEventListener('click', () => downloadASE(activePaletteData));
    $('exportJsonBtn')?.addEventListener('click', () => downloadJSON(activePaletteData));$('exportFigmaBtn')?.addEventListener('click', () => copyFigmaTokens(activePaletteData));

    $('copyHexBtn')?.addEventListener('click', () => copyPaletteCode('HEX'));
    $('copyRgbBtn')?.addEventListener('click', () => copyPaletteCode('RGB'));$('copyHslBtn')?.addEventListener('click', () => copyPaletteCode('HSL'));
    $('copyTailwindBtn')?.addEventListener('click', () => copyPaletteCode('TAILWIND'));$('copyCssVarBtn')?.addEventListener('click', () => copyPaletteCode('CSS_VARS'));

    if (uploadTriggerBtn && imageInput) {
        uploadTriggerBtn.addEventListener('click', (e) => {
            e.preventDefault();
            imageInput.click();
        });
    }

    if (imageInput) {
        imageInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            showAlert('');
            if (!file.type.startsWith('image/')) {
                showAlert(t('กรุณาเลือกไฟล์รูปภาพเท่านั้น', 'Please choose an image file.'));
                imageInput.value = '';
                return;
            }
            if (file.size > MAX_IMAGE_BYTES) {
                showAlert(t('ไฟล์รูปใหญ่เกิน 10 MB', 'Image is larger than 10 MB.'));
                imageInput.value = '';
                return;
            }

            if (textInput) textInput.value = '';

            const reader = new FileReader();
            reader.onload = (event) => {
                const imageDataUrl = event.target.result;
                if ($('imagePreview'))$('imagePreview').src = imageDataUrl;
                if ($('extractedPaletteSection'))$('extractedPaletteSection').style.display = 'block';

                const img = new Image();
                img.onload = () => {
                    // Analyse a downscaled copy: fast even for large photos.
                    const scale = Math.min(1, 160 / Math.max(img.width, img.height));
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d', { willReadFrequently: true });
                    canvas.width = Math.max(1, Math.round(img.width * scale));
                    canvas.height = Math.max(1, Math.round(img.height * scale));
                    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

                    const rgbData = extractRGBColors(ctx, canvas.width, canvas.height, 8);
                    const imageEmotion = analyzeColorSentiment(rgbData.rgbList);
                    // Colour-tone rule, not an AI model: no fake percentage.
                    const confidence = t('ประเมินจากโทนสี', 'Colour-tone estimate');
                    
                    updateUIResult(imageEmotion, confidence, rgbData.hexList);
                    saveToHistory('image', file.name, imageEmotion, confidence, rgbData.hexList, makeThumbnail(img));
                };
                img.onerror = () => showAlert(t('เปิดไฟล์รูปนี้ไม่ได้ (ไฟล์อาจเสียหาย)', 'Could not open this image (file may be corrupted).'));
                img.src = imageDataUrl;
            };
            reader.readAsDataURL(file);
        });
    }

    if (langToggleBtn) {
        langToggleBtn.addEventListener('click', () => {
            currentLang = currentLang === 'TH' ? 'EN' : 'TH';
            updateLanguageUI();
        });
    }

    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', async () => {
            const text = textInput ? textInput.value.trim() : '';
            showAlert('');
            if (!text) {
                showAlert(t('กรุณากรอกข้อความก่อนวิเคราะห์', 'Please enter some text first.'));
                return;
            }
            if (text.length > MAX_TEXT_LENGTH) {
                showAlert(t(`ข้อความยาวเกิน ${MAX_TEXT_LENGTH} ตัวอักษร`, `Text is longer than ${MAX_TEXT_LENGTH} characters.`));
                return;
            }

            clearImageResult();
            analyzeBtn.disabled = true;
            analyzeBtn.innerText = translations[currentLang].analyzing;

            try {
                const classifier = await getAIPipeline();
                const output = await classifier(text, EMOTION_LABELS);
                if (!output?.labels?.length) throw new Error('Empty model output');
                const topEmotion = output.labels[0].toUpperCase();
                const confidenceScore = (output.scores[0] * 100).toFixed(1) + "%";
                updateUIResult(topEmotion, confidenceScore);
                saveToHistory('text', text, topEmotion, confidenceScore, emotionRules[topEmotion]?.palette);
            } catch (err) {
                // AI model / CDN unavailable -> honest keyword fallback, never a fake result.
                console.warn('AI model unavailable, using keyword fallback:', err);
                const fallback = keywordEmotion(text);
                if (!fallback.label) {
                    showAlert(err?.message === 'MODEL_TIMEOUT'
                        ? t('โมเดล AI ยังดาวน์โหลดไม่เสร็จ และโหมดสำรองไม่พบคำบ่งบอกอารมณ์ในข้อความนี้ — รอให้ขึ้น ✅ แล้วกดวิเคราะห์อีกครั้ง',
                            'AI model is still downloading and the offline mode found no emotion words — wait for ✅ and analyze again.')
                        : t('โมเดล AI โหลดไม่สำเร็จ และโหมดสำรองไม่พบคำบ่งบอกอารมณ์ในข้อความนี้ ลองเขียนให้ชัดขึ้นหรือลองใหม่เมื่อออนไลน์',
                            'AI model unavailable and the offline fallback found no emotion words. Try clearer text or retry when online.'));
                } else {
                    const topEmotion = fallback.label.toUpperCase();
                    const confidenceScore = (fallback.score * 100).toFixed(1) + '% (offline)';
                    updateUIResult(topEmotion, confidenceScore);
                    saveToHistory('text', text, topEmotion, confidenceScore, emotionRules[topEmotion]?.palette);
                    showAlert(err?.message === 'MODEL_TIMEOUT'
                        ? t('โมเดล AI ยังดาวน์โหลดไม่เสร็จ จึงใช้โหมดสำรองไปก่อน — รอให้ขึ้น ✅ แล้วกดวิเคราะห์อีกครั้ง',
                            'AI model is still downloading, so the offline mode was used — wait for ✅ and analyze again.')
                        : t('ใช้โหมดสำรองแบบ keyword เพราะโหลดโมเดล AI ไม่สำเร็จ (ผลอาจแม่นยำน้อยกว่า)',
                            'Using offline keyword mode because the AI model could not load (less accurate).'));
                }
            } finally {
                analyzeBtn.disabled = false;
                analyzeBtn.innerText = translations[currentLang].analyzeBtn;
            }
        });
    }

    updateLanguageUI();
    // Start the model download right away so it is ready by the first click.
    loadAIPipeline().catch(() => { /* status already shown; fallback handles it */ });
});