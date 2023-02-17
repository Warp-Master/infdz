const showButton = document.getElementById('showDialog');
const favDialog = document.getElementById('dialog');
const importBox = document.getElementById('importbox')
const confirmBtn = favDialog.querySelector('#confirmBtn');
const regexp = /(?<num>\d+)[.:](!=$)?(?<ans>[\s\S]*?)(?=\n\d+[.:]|$)/g;
confirmBtn.value = importBox.value;

// "Update details" button opens the <dialog> modally
showButton.addEventListener('click', () => {
    favDialog.showModal();
});

importBox.addEventListener('change', (e) => {
    confirmBtn.value = importBox.value;
});

// "Confirm" button of form triggers "close" on dialog because of [method="dialog"]
favDialog.addEventListener('close', () => {
    let results = favDialog
        .returnValue
        .replace(/ /g, '')
        .matchAll(regexp);
    for (const res of results) {
        let elem = document.getElementById(`question-${res.groups.num}`);
        let inputs = elem.querySelectorAll('.ansForm input');
        let answers = res.groups.ans.split('\n');
        for (let i = 0; i < Math.min(inputs.length, answers.length); ++i) {
            if (answers[i] !== null && answers[i] !== '') {
                inputs[i].value = answers[i];
            }
        }
        // console.log(inputs, res.groups.ans.split('\n'));
    }
});
