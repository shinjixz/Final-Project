import { EMOTION_LABELS, keywordEmotion } from './keyword_fallback.js';

// The AI library is imported lazily inside getAIPipeline(): if the CDN is down
// the rest of the page still works and the keyword fallback takes over.
const TRANSFORMERS_CDN = 'https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.2';
const MAX_TEXT_LENGTH = 1000;
const MAX_IMAGE_BYTES = 10 * 1024 * 1024;

const $ = id => document.getElementById(id);

let currentLang = 'TH';
let paletteAnimationTimer = null;
let sentimentPipeline = null;

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
        return alert("ไม่มีข้อมูลจานสี!");
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

    navigator.clipboard.writeText(codeResult);
    alert(`คัดลอกโค้ดรูปแบบ ${format} เรียบร้อยแล้ว!`);
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
    if (!palette || palette.length === 0) return alert("ไม่มีข้อมูลจานสี!");
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
    if (!palette || palette.length === 0) return alert("ไม่มีข้อมูลจานสี!");
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(palette, null, 2));
    const a = document.createElement("a");
    a.href = dataStr;
    a.download = filename;
    a.click();
}

function copyFigmaTokens(palette) {
    if (!palette || palette.length === 0) return alert("ไม่มีข้อมูลจานสี!");
    const figmaTokens = {};
    palette.forEach((item, i) => {
        const hex = typeof item === 'string' ? item : item.hex;
        const role = slugifyRole(typeof item === 'object' ? item.role : '', i);
        figmaTokens[role] = { value: hex, type: "color" };
    });
    navigator.clipboard.writeText(JSON.stringify(figmaTokens, null, 2));
    alert("คัดลอก Figma Color Tokens เรียบร้อยแล้ว!");
}

// ==========================================
// 🖼️ IMAGE COLOR EXTRACTION HELPERS
// ==========================================

function extractRGBColors(ctx, width, height, count) {
    const hexList = [];
    const rgbList = [];
    const stepX = Math.floor(width / (count + 1));
    const stepY = Math.floor(height / 2);

    for (let i = 1; i <= count; i++) {
        const p = ctx.getImageData(i * stepX, stepY, 1, 1).data;
        const hex = '#' + ((1 << 24) + (p[0] << 16) + (p[1] << 8) + p[2]).toString(16).slice(1);
        hexList.push(hex);
        rgbList.push({ r: p[0], g: p[1], b: p[2] });
    }
    return { hexList, rgbList };
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
        subTitle: 'ระบบวิเคราะห์อารมณ์จากข้อความพร้อมแนะนำจานสีสำหรับงานออกแบบ UI/UX',
        inputLabel: 'กรอกข้อความภาษาอังกฤษเพื่อวิเคราะห์อารมณ์ด้วย AI Model',
        placeholder: 'พิมพ์ความรู้สึกของคุณ เช่น I feel sad หรือ I feel happy...',
        analyzeBtn: 'วิเคราะห์อารมณ์ (Analyze)',
        uploadBtn: 'อัปโหลดรูปภาพ (Extract Image)',
        paletteTitle: 'ชุดจานสีที่แนะนำ',
        historyTitle: 'ประวัติการวิเคราะห์ (History)',
        clearHistory: 'ล้างประวัติ',
        emptyHistory: 'ยังไม่มีประวัติการวิเคราะห์',
        modalTitle: 'ยืนยันการล้างประวัติ',
        modalDesc: 'คุณแน่ใจหรือไม่ว่าต้องการลบประวัติการวิเคราะห์ทั้งหมด? รายการที่ลบแล้วจะไม่สามารถกู้คืนได้',
        modalCancel: 'ยกเลิก',
        modalConfirm: 'ลบประวัติ',
        copySuccess: 'คัดลอกสี'
    },
    EN: {
        langBtn: 'TH',
        subTitle: 'Text Sentiment Analysis & Color Palette Recommendation',
        inputLabel: 'Enter English text to analyze sentiment via AI Model',
        placeholder: 'i feel happy or feel sad...',
        analyzeBtn: 'Analyze Sentiment',
        uploadBtn: 'Upload Image (Extract)',
        paletteTitle: 'Recommended Color Palette',
        historyTitle: 'Analysis History',
        clearHistory: 'Clear History',
        emptyHistory: 'No analysis history found',
        modalTitle: 'Confirm Clear History',
        modalDesc: 'Are you sure you want to delete all analysis history? Deleted items cannot be restored.',
        modalCancel: 'Cancel',
        modalConfirm: 'Delete All',
        copySuccess: 'Copied color'
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
    const t = translations[currentLang];

    if ($('langToggleBtn'))$('langToggleBtn').innerText = t.langBtn;
    if ($('subTitle'))$('subTitle').innerText = t.subTitle;
    if ($('inputLabel'))$('inputLabel').innerText = t.inputLabel;
    if ($('textInput'))$('textInput').placeholder = t.placeholder;
    if ($('analyzeBtn') && !$('analyzeBtn').disabled)$('analyzeBtn').innerText = t.analyzeBtn;
    if ($('uploadTriggerBtn'))$('uploadTriggerBtn').innerText = t.uploadBtn;
    if ($('paletteTitle'))$('paletteTitle').innerText = t.paletteTitle;
    if ($('historyTitle'))$('historyTitle').innerText = t.historyTitle;
    if ($('clearHistoryBtn'))$('clearHistoryBtn').innerText = t.clearHistory;
    
    if ($('modalTitle'))$('modalTitle').innerText = t.modalTitle;
    if ($('modalDesc'))$('modalDesc').innerText = t.modalDesc;
    if ($('modalCancelBtn'))$('modalCancelBtn').innerText = t.modalCancel;
    if ($('modalConfirmBtn'))$('modalConfirmBtn').innerText = t.modalConfirm;

    renderHistoryList();
}

const renderSwatches = colors => {
    return `<div class="palette-grid">` + (colors || []).map(c => {
        const hex = typeof c === 'string' ? c : c.hex;
        const role = typeof c === 'object' && c.role ? c.role : 'COLOR';
        return `
            <div class="color-card" onclick="navigator.clipboard.writeText('${hex}'); alert('${translations[currentLang].copySuccess} ${hex}!')" title="Click to copy">
                <div class="color-swatch-box" style="background-color: ${hex}"></div>
                <div class="color-info">
                    <span class="color-hex">${hex}</span>
                    <span class="color-role">${role}</span>
                </div>
            </div>
        `;
    }).join('') + `</div>`;
};

async function getAIPipeline() {
    if (!sentimentPipeline) {
        if ($('emotionLabel'))$('emotionLabel').innerText = "Loading AI...";
        const { pipeline, env } = await import(TRANSFORMERS_CDN);
        env.allowLocalModels = false;
        sentimentPipeline = await pipeline('zero-shot-classification', 'Xenova/distilbert-base-uncased-mnli');
    }
    return sentimentPipeline;
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

function hexToSoftRgba(hex, opacity = 0.22) {
    let c = hex.replace('#', '');
    if (c.length === 3) c = c.split('').map(x => x + x).join('');
    const num = parseInt(c, 16);
    const r = (num >> 16) & 255;
    const g = (num >> 8) & 255;
    const b = num & 255;
    return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

function startPaletteBackgroundAnimation(colorList) {
    if (paletteAnimationTimer) clearInterval(paletteAnimationTimer);
    if (!colorList || colorList.length === 0) return;

    let currentIndex = 0;
    const hexList = colorList.map(c => typeof c === 'string' ? c : c.hex);

    const changeBg = () => {
        const hexColor = hexList[currentIndex];
        document.body.style.backgroundColor = hexToSoftRgba(hexColor, 0.25);
        currentIndex = (currentIndex + 1) % hexList.length;
    };

    changeBg();
    paletteAnimationTimer = setInterval(changeBg, 3500);
}

function saveToHistory(type, inputContent, emotion, confidence, palette) {
    const newItem = {
        type,
        content: inputContent,
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

async function renderHistoryList() {
    const historyContainer = $('historyList');
    if (!historyContainer) return;

    let historyData = [];

    try {
        historyData = JSON.parse(localStorage.getItem('sentiment_history') || '[]');
    } catch (e) {
        historyData = [];
    }

    if (!historyData || historyData.length === 0) {
        historyContainer.innerHTML = `<p class="history-empty" style="text-align:center; color:#94a3b8; padding:15px 0;">${translations[currentLang].emptyHistory}</p>`;
        return;
    }

    window.currentHistoryData = historyData;

    historyContainer.innerHTML = historyData.map((item, index) => {
        const timeString = item.createdAt 
            ? new Date(item.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
            : '';

        let paletteArray = [];
        if (Array.isArray(item.palette)) {
            paletteArray = item.palette;
        } else if (typeof item.palette === 'string') {
            try { paletteArray = JSON.parse(item.palette); } catch (e) { paletteArray = []; }
        }

        const hexList = paletteArray.map(c => typeof c === 'string' ? c : c.hex);
        const isImage = item.type === 'image';

        return `
            <div class="history-item" data-index="${index}">
                <div class="history-info" style="display:flex; align-items:center; gap:10px; pointer-events:none;">
                    <span class="history-tag ${item.type || 'text'}" style="font-size:0.7rem; padding:3px 8px; border-radius:6px; font-weight:bold; background:${isImage ? '#fce7f3' : '#dbeafe'}; color:${isImage ? '#9d174d' : '#1e40af'};">
                        ${(item.type || 'TEXT').toUpperCase()}
                    </span>
                    <span class="history-text">${isImage ? '🖼 ' : ''}${item.content.length > 30 ? item.content.substring(0, 30) + '...' : item.content}</span>
                    <span class="history-time" style="font-size:0.75rem; color:#94a3b8;">${timeString}</span>
                </div>
                <div class="history-result" style="display:flex; align-items:center; gap:10px; pointer-events:none;">
                    <strong class="history-emotion">${item.emotion || '-'}</strong>
                    <div class="history-mini-palette" style="display:flex; gap:3px;">
                        ${hexList.slice(0, 5).map(c => `<div class="mini-swatch" style="background:${c}"></div>`).join('')}
                    </div>
                </div>
            </div>
        `;
    }).join('');

    document.querySelectorAll('.history-item').forEach(itemEl => {
        itemEl.addEventListener('click', (e) => {
            const idx = e.currentTarget.getAttribute('data-index');
            if (window.currentHistoryData && window.currentHistoryData[idx]) {
                loadHistoryItem(window.currentHistoryData[idx]);
            }
        });
    });
}

function loadHistoryItem(item) {
    let paletteArray = [];
    if (Array.isArray(item.palette)) paletteArray = item.palette;
    else if (typeof item.palette === 'string') {
        try { paletteArray = JSON.parse(item.palette); } catch (e) { paletteArray = []; }
    }

    if (item.type === 'text') {
        clearImageResult();
        if ($('textInput'))$('textInput').value = item.content;
        updateUIResult(item.emotion, item.confidence || '-');
    } else if (item.type === 'image') {
        if ($('textInput'))$('textInput').value = '';
        if ($('extractedPaletteSection'))$('extractedPaletteSection').style.display = 'block';
        if ($('imagePreview'))$('imagePreview').src = item.content;
        
        updateUIResult(item.emotion, item.confidence || '-', paletteArray);
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function updateUIResult(emotionKey, confidence, customPalette = null) {
    const resultData = emotionRules[emotionKey] || emotionRules['JOY'];

    if ($('emotionLabel'))$('emotionLabel').innerText = emotionKey;
    if ($('confidenceValue'))$('confidenceValue').innerText = confidence;
    if ($('themeName'))$('themeName').innerText = resultData.theme;
    if ($('fontPairing'))$('fontPairing').innerText = resultData.font;
    if ($('usageContext'))$('usageContext').innerText = resultData.context;

    activePaletteData = customPalette || resultData.palette;

    if ($('paletteDisplay')) {$('paletteDisplay').innerHTML = renderSwatches(activePaletteData);
    }

    if (resultData.fontFamily) {
        document.body.style.fontFamily = resultData.fontFamily;
    }

    startPaletteBackgroundAnimation(activePaletteData);
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
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);

                    const rgbData = extractRGBColors(ctx, canvas.width, canvas.height, 8);
                    const imageEmotion = analyzeColorSentiment(rgbData.rgbList);
                    // Colour-tone rule, not an AI model: no fake percentage.
                    const confidence = t('ประเมินจากโทนสี', 'Colour-tone estimate');
                    
                    updateUIResult(imageEmotion, confidence, rgbData.hexList);
                    saveToHistory('image', imageDataUrl, imageEmotion, confidence, rgbData.hexList);
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
                    if ($('emotionLabel'))$('emotionLabel').innerText = '-';
                    if ($('confidenceValue'))$('confidenceValue').innerText = '0%';
                    showAlert(t('โมเดล AI โหลดไม่สำเร็จ และโหมดสำรองไม่พบคำบ่งบอกอารมณ์ในข้อความนี้ ลองเขียนให้ชัดขึ้นหรือลองใหม่เมื่อออนไลน์',
                        'AI model unavailable and the offline fallback found no emotion words. Try clearer text or retry when online.'));
                } else {
                    const topEmotion = fallback.label.toUpperCase();
                    const confidenceScore = (fallback.score * 100).toFixed(1) + '% (offline)';
                    updateUIResult(topEmotion, confidenceScore);
                    saveToHistory('text', text, topEmotion, confidenceScore, emotionRules[topEmotion]?.palette);
                    showAlert(t('ใช้โหมดสำรองแบบ keyword เพราะโหลดโมเดล AI ไม่สำเร็จ (ผลอาจแม่นยำน้อยกว่า)',
                        'Using offline keyword mode because the AI model could not load (less accurate).'));
                }
            } finally {
                analyzeBtn.disabled = false;
            }
        });
    }

    updateLanguageUI();
});