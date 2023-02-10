function submitForm() {
  let f = document.getElementById('question-form');
  let formData = new FormData(f);
  fetch(document.URL, {
    method: 'POST',
    body: formData
  })
  .then(response => response.text())
  .then(data => {
    document.getElementById('result').innerHTML = data;
  });
  f.preventDefault()
  return false;
}