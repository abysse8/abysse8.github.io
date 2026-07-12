// Single source of truth for homepage content.
// Edit here, never in components.

export const site = {
  handle: "abysse8",
  name: "J.G.",
  email: "julienabdougonzales@gmail.com",
  github: "https://github.com/abysse8",
  headline: "I build systems where firmware meets learning algorithms.",
  sub: "Reverse-engineering industrial bus protocols, closing real-time control loops, and wiring AI pipelines to physical hardware — from the transistor to the transformer.",
};

export const stats = [
  { value: 3, suffix: "", label: "proprietary RS485 protocols reverse-engineered" },
  { value: 10, prefix: "<", suffix: " ms", label: "PID stabilization on STM32" },
  { value: 17, suffix: "", label: "production bus units validated by custom PCB" },
  { value: 30, prefix: "20 min → ", suffix: " s", label: "CV tailoring, automated end-to-end" },
];

export type Project = {
  tag: string;
  title: string;
  href: string;
  description: string;
  stack: string[];
  featured?: boolean;
};

export const projects: Project[] = [
  {
    tag: "Featured · Protocol lab",
    title: "ESP32 Display Panel",
    href: "https://github.com/abysse8/esp32-display-panel",
    description:
      "Unified ESP32 firmware and RS485 protocol laboratory driving Lumiplan, Mobitec, and Hanover transit destination signs — three proprietary bus protocols reverse-engineered from live captures.",
    stack: ["C++", "PlatformIO", "RS485", "ESP32-S3"],
    featured: true,
  },
  {
    tag: "Control systems",
    title: "Drone Flight Controller",
    href: "https://github.com/abysse8", // TODO: real repo URL (projects.md points at yourusername/)
    description:
      "Real-time PID stabilization loop on STM32 with complementary-filtered MPU6050 fusion over I2C. Settles in under 10 ms.",
    stack: ["C", "STM32", "I2C"],
  },
  {
    tag: "AI automation",
    title: "CoverGemini",
    href: "https://github.com/abysse8/CoverGemini",
    description:
      "Mobile-to-cloud pipeline turning a job post into a tailored LaTeX CV PDF: iOS Shortcuts → Gemini → Flask → pdflatex, in 30 seconds.",
    stack: ["Python", "Gemini", "LaTeX"],
  },
  {
    tag: "Full-stack IoT",
    title: "Grow-Room Telemetry",
    href: "https://github.com/abysse8/esp8266-soil-node",
    description:
      "End-to-end sensing stack: ESP8266 soil nodes over MQTT into Node/Express + SQLite, visualized in a React dashboard — plus an ESP32 pan/tilt camera.",
    stack: ["ESP8266", "MQTT", "React"],
  },
  {
    tag: "Industrial hardware",
    title: "Continuity Test Sensor",
    href: "https://github.com/abysse8",
    description:
      "Custom KiCad PCB for Electro Faisceau detecting faulty crimps through precise voltage-drop measurement — automated harness validation for 17 production buses.",
    stack: ["KiCad", "Analog"],
  },
  {
    tag: "Research",
    title: "LODeNNS · ICONS 2022",
    href: "https://github.com/abysse8/LODeNNS",
    description:
      "Neuromorphic spike-timing-dependent plasticity with nearest-neighbour dynamics — where the hardware obsession meets the learning-algorithm question.",
    stack: ["SNN", "STDP", "Python"],
  },
];

export const rooms = [
  { href: "/projects/", title: "Projects & Prototypes", blurb: "Simulations, physical builds, microcontroller hacks.", ready: true },
  { href: "/ideas/", title: "Ideas & Fragments", blurb: "Raw sketches and wild concepts that might just make sense.", ready: true },
  { href: "/presentations/", title: "Presentation Gallery", blurb: "Decks where research met the classroom and tried to sing.", ready: true },
  { href: "/cv/", title: "Digital CV", blurb: "Background, roles, skills, contact — everything professional.", ready: true },
  { href: "/notes/", title: "Course Notes", blurb: "Derivations, circuit theory, biophysics, ML — scratchpad and archive.", ready: false },
  { href: "/papers/", title: "Papers & Extracts", blurb: "Annotated scans from papers that shifted my worldview.", ready: false },
  { href: "/hall-of-fame/", title: "Hall of Fame", blurb: "Talks, debates, and theses that cracked something open.", ready: false },
  { href: "/ask/", title: "Ask the Curator", blurb: "A timeline of research questions — click a moment in time.", ready: false },
];

// Real commands from real repos — the terminal must never lie.
export type TermStep = { text: string; kind: "prompt" | "cmd" | "out" | "ok" };

export const terminalScript: TermStep[] = [
  { text: "$ ", kind: "prompt" },
  { text: "pio run -e mobitec -t upload\n", kind: "cmd" },
  { text: "Compiling ESP32-S3 firmware… ", kind: "out" },
  { text: "done ✓\n", kind: "ok" },
  { text: "$ ", kind: "prompt" },
  { text: "rs485-sniff --baud 4800 --parity even\n", kind: "cmd" },
  { text: '[0x86] addr=06  "LIGNE 12 → GARE CENTRALE"\n', kind: "out" },
  { text: "checksum ok · 42 frames captured\n", kind: "ok" },
  { text: "$ ", kind: "prompt" },
  { text: "python covergen.py --job-post offer.txt\n", kind: "cmd" },
  { text: "job post → Gemini → LaTeX → PDF ", kind: "out" },
  { text: "28.4 s ✓\n", kind: "ok" },
];
