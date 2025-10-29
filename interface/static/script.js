const textarea = document.getElementById('code');
textarea.addEventListener('keydown', function(e) {
    if (e.key === 'Tab') {
        e.preventDefault();
        let start = this.selectionStart;
        let end = this.selectionEnd;
        this.value = this.value.substring(0, start) + "\t" + this.value.substring(end);
        this.selectionStart = this.selectionEnd = start + 1;
    }
});

