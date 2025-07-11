const conversations = [
  {
    id: "q001",
    date: "2025-06-24",
    short: "What is a codon cube?",
    full: `**Q:** What is a codon cube?\n\n**A:** A codon cube is a 3D representation of the 64 possible codons in DNA, arranged by their nucleotide positions...`
  },
  {
    id: "q002",
    date: "2025-06-28",
    short: "How does spiking neural timing work?",
    full: `**Q:** How does timing work in spiking neurons?\n\n**A:** Timing is everything. In spiking neural nets, information is encoded in the delay between spikes...`
  },
  // More entries...
];

const container = document.getElementById("timeline-container");

conversations.forEach((item, i) => {
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerText = item.short;
  bubble.onclick = () => {
    const modal = document.createElement("div");
    modal.className = "modal";
    modal.innerHTML = `
      <div class="modal-content">
        <span class="close-button" onclick="this.parentElement.parentElement.remove()">×</span>
        <h3>${item.date}</h3>
        <pre>${item.full}</pre>
      </div>
    `;
    document.body.appendChild(modal);
  };
  container.appendChild(bubble);
});
