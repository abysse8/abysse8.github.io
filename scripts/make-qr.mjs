// Generates the poster QR code for the tutoring page: npm run qr
// Error correction H (~30 % of the code can be damaged or covered).
import QRCode from "qrcode";
import { writeFile } from "node:fs/promises";

const url = "https://abysse8.github.io/cours/";
const out = "public/qr-cours.svg";

const svg = await QRCode.toString(url, { type: "svg", errorCorrectionLevel: "H", margin: 4 });
await writeFile(out, svg);
console.log(`${out} ← ${url}`);
