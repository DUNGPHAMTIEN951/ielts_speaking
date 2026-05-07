const fs = require('fs');
const path = require('path');

const dataFile = path.join('d:', 'Ton_nhi', 'ielts_splits', 'ielts_all_data.js');
const content = fs.readFileSync(dataFile, 'utf8');

// Mock window object
const window = {};
// Evaluate the script
try {
    eval(content);
    const data = window.ALL_IELTS_DATA;
    process.stdout.write(JSON.stringify(data));
} catch (e) {
    // Try without window if it failed
    try {
        let cleanContent = content.replace('window.ALL_IELTS_DATA =', 'var ALL_IELTS_DATA =');
        cleanContent += '; ALL_IELTS_DATA;';
        const data = eval(cleanContent);
        process.stdout.write(JSON.stringify(data));
    } catch (e2) {
        process.stderr.write(e2.toString());
        process.exit(1);
    }
}
