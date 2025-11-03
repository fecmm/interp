
const editor = CodeMirror.fromTextArea(document.getElementById('code'), {
    lineNumbers: true,
    mode: "python",
    theme: "dracula",
    autoCloseBrackets: true,
    matchBrackets: true,
    indentUnit: 4,
    tabSize: 4,
    indentWithTabs: true
});


const execEditor = CodeMirror.fromTextArea(document.getElementById('exec'), {
    lineNumbers: true,
    mode: "python",
    theme: "dracula",
    readOnly: true
});


const astEditor = CodeMirror.fromTextArea(document.getElementById('ast'), {
    lineNumbers: true,
    mode: "python",
    theme: "dracula",
    readOnly: true
});

function loadSelectedExample() {
    const select = document.getElementById('example-select');
    const exampleId = select.value;
    if (exampleId) {
        const content = document.getElementById(exampleId).value;
        editor.setValue(content);
    }
}


function clearCode() {
    editor.setValue('');
    execEditor.setValue('');
    astEditor.setValue('');
}


function showTab(tabName) {
    if(tabName === 'exec') {
        execEditor.getWrapperElement().style.display = 'block';
        astEditor.getWrapperElement().style.display = 'none';
    } else {
        execEditor.getWrapperElement().style.display = 'none';
        astEditor.getWrapperElement().style.display = 'block';
    }
}

editor.setOption('extraKeys', {
    Tab: cm => cm.somethingSelected() ? cm.indentSelection('add') : cm.replaceSelection('\t')
});


window.addEventListener('load', () => {
    execEditor.setValue(document.getElementById('exec').value);
    astEditor.setValue(document.getElementById('ast').value);
    showTab('exec'); // Mostra saída por padrão
});


