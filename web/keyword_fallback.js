// Offline emotion fallback used when the AI model / CDN is unavailable.
// Same lexicon and scoring as src/emotion_client.py (KeywordEmotionClient);
// tests/test_web.py checks that both give identical results.

export const EMOTION_LABELS = ['fear', 'anger', 'sadness', 'joy', 'love', 'surprise'];

export const KEYWORD_LEXICON = {
    joy: ['happy', 'joy', 'glad', 'excited', 'great', 'awesome', 'fun', 'amazing', 'wonderful', 'delighted', 'cheerful', 'bright', 'yay'],
    sadness: ['sad', 'lonely', 'gloomy', 'cry', 'depressed', 'miss', 'unhappy', 'tired', 'hopeless', 'sorrow', 'down', 'lost'],
    anger: ['angry', 'furious', 'mad', 'hate', 'annoyed', 'rage', 'irritated', 'terrible', 'worst', 'unfair', 'bad'],
    fear: ['afraid', 'scared', 'fear', 'anxious', 'worried', 'nervous', 'terrified', 'panic', 'dark', 'horror'],
    love: ['love', 'adore', 'darling', 'sweet', 'romantic', 'heart', 'care', 'beloved', 'kiss', 'crush'],
    surprise: ['surprise', 'surprised', 'unexpected', 'wow', 'shocked', 'suddenly', 'unbelievable', 'amazed', 'cannot believe']
};

export function keywordEmotion(text) {
    const lower = text.toLowerCase();
    const words = lower.match(/[a-z']+/g) || [];
    const counts = {};
    let total = 0;
    for (const label of EMOTION_LABELS) {
        counts[label] = KEYWORD_LEXICON[label].reduce((sum, kw) => sum + (kw.includes(' ')
            ? lower.split(kw).length - 1
            : words.filter(w => w === kw).length), 0);
        total += counts[label];
    }
    if (total === 0) return { label: null, score: 0 };
    const label = EMOTION_LABELS.reduce((best, l) => (counts[l] > counts[best] ? l : best), EMOTION_LABELS[0]);
    const evidence = counts[label] / (counts[label] + 1);
    return { label, score: (counts[label] / total) * evidence };
}
