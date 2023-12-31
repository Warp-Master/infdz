const showButton = document.getElementById('dialog-show');
const dialog = document.getElementById('dialog');
const importBox = document.getElementById('dialog-importbox')
const confirmBtn = document.getElementById('dialog-confirm');
const closeBtn = document.getElementById('dialog-close')
const clearBtn = document.getElementById('dialog-clear')
const regexp = /(?<num>\d+)[.:](!=$)?(?<ans>[\s\S]*?)(?=\n\d+[.:]|$)/g;
const inputRemoveRE = /[^.:;a-zа-я\-\d\n]/gi;
confirmBtn.value = importBox.value;

// "Update details" button opens the <dialog> modally
showButton.addEventListener('click', () => {
    dialog.showModal();
});

importBox.addEventListener('change', (e) => {
    confirmBtn.value = importBox.value;
});

function clearInputs(doc) {
    let inputs = doc.querySelectorAll('.ansForm input');
    for (const inp of inputs) {
        inp.value = '';
    }
}

// "Confirm" button of form triggers "close" on dialog because of [method="dialog"]
dialog.addEventListener('close', (e) => {
    let results = dialog
        .returnValue
        .replace(inputRemoveRE, '')
        .matchAll(regexp);

    for (const res of results) {
        let elem = document.getElementById(`question-${res.groups.num}`);
        let inputs = elem.querySelectorAll('.ansForm input');
        let answers = res.groups.ans.split('\n').filter(ans => ans !== null && ans !== '' && ans !== '-');
        for (let i = 0; i < Math.min(inputs.length, answers.length); ++i) {
            inputs[i].value = answers[i];
        }
        // console.log(inputs, res.groups.ans.split('\n'));
    }
});

confirmBtn.addEventListener('click', (e) => {
    // clear old inputs before
    clearInputs(document);
});

clearBtn.addEventListener('click', (e) => {
    clearInputs(document);
});

closeBtn.addEventListener('click', (e) => {
    window.dialog.close();
});
