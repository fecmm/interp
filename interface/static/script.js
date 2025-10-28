const editor = document.getElementById("editor");

const palavrasChave = [
    "inicio", "fim", "se", "senao", "enquanto", "para", "funcao", "retorna"
];

function escapeHTML(text) {
    return text.replace(/&/g, "&amp;")
               .replace(/</g, "&lt;")
               .replace(/>/g, "&gt;");
}

function destacarSintaxe(texto) {
    // Comentários
    texto = texto.replace(/#.*$/gm, match => `<span class="comment">${match}</span>`);

    // Strings
    texto = texto.replace(/(["'])(?:(?=(\\?))\2.)*?\1/g, match => `<span class="string">${match}</span>`);

    // Números
    texto = texto.replace(/\b\d+(\.\d+)?\b/g, match => `<span class="number">${match}</span>`);

    // Palavras-chave
    palavrasChave.forEach(p => {
        const regex = new RegExp("\\b" + p + "\\b", "g");
        texto = texto.replace(regex, `<span class="keyword">${p}</span>`);
    });

    // Operadores
    texto = texto.replace(/[\+\-\*\/=<>!]+/g, match => `<span class="operator">${match}</span>`);

    return texto;
}

// Atualiza o editor com cores
editor.addEventListener("input", () => {
    const cursorPos = window.getSelection().getRangeAt(0);
    const posOffset = cursorPos.startOffset;

    editor.innerHTML = destacarSintaxe(escapeHTML(editor.innerText));

    // Tenta restaurar o cursor (aproximado)
    const range = document.createRange();
    const sel = window.getSelection();
    range.setStart(editor.childNodes[0] || editor, posOffset);
    range.collapse(true);
    sel.removeAllRanges();
    sel.addRange(range);
});

// Enviar código
document.getElementById("executar").addEventListener("click", () => {
    const codigo = editor.innerText;
    fetch("/executar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ codigo })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("saida").textContent = data.resultado;
    })
    .catch(err => {
        document.getElementById("saida").textContent = "Erro ao executar: " + err;
    });
});
